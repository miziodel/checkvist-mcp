import asyncio
import logging
from typing import List, Dict, Any, Optional
from cachetools import TTLCache
from .client import CheckvistClient
from .syntax import SyntaxParser
from .models import Task, Checklist

logger = logging.getLogger(__name__)

class CheckvistService:
    def __init__(self, client: CheckvistClient):
        self.client = client
        self.parser = SyntaxParser()
        # Cache for list metadata (name, id) to avoid N+1 lookups
        self.list_cache = TTLCache(maxsize=100, ttl=15)
        # Cache for list contents to avoid redundant fetches for breadcrumbs
        self.list_content_cache = TTLCache(maxsize=10, ttl=30)

    async def _get_authed_client(self) -> CheckvistClient:
        if not self.client.token:
            await self.client.authenticate()
        return self.client


    async def get_checklists(self) -> List[Dict[str, Any]]:
        client = await self._get_authed_client()
        if "lists" in self.list_cache:
            return self.list_cache["lists"]
        
        lists = await client.get_checklists()
        self.list_cache["lists"] = lists
        return lists

    async def get_list_name(self, list_id: int) -> str:
        lists = await self.get_checklists()
        for l in lists:
            if l.id == list_id:
                return l.name
        return "Unknown"

    async def invalidate_cache(self, list_id: Optional[int] = None):
        """Invalidate specific list cache or all caches."""
        if list_id:
            self.list_content_cache.pop(list_id, None)
        else:
            self.list_content_cache.clear()
            self.list_cache.clear()

    async def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Enhanced search using Checkvist's native global index."""
        client = await self._get_authed_client()
        
        # Use high-performance global search
        raw_results = await client.search_global(query)
        
        # Enrich results with breadcrumbs and indicators
        all_matches = []
        
        # Group results by checklist to fetch trees efficiently
        by_list = {}
        for r in raw_results:
            l_id = r.checklist_id
            if l_id:
                if l_id not in by_list: by_list[l_id] = []
                by_list[l_id].append(r)
        
        for l_id, tasks in by_list.items():
            try:
                # Fetch full list to build breadcrumbs efficiently
                all_tasks = await client.get_tasks(l_id)
                task_map = {t.id: t for t in all_tasks}
                
                # Pre-calculate children count
                children_map = {}
                for t in all_tasks:
                    pid = t.parent_id
                    if pid:
                        children_map[pid] = children_map.get(pid, 0) + 1
                
                list_name = await self.get_list_name(l_id)
                
                for task in tasks:
                    t_id = task.id
                    # Indicators via Pydantic model
                    child_count = children_map.get(t_id, 0)
                    
                    indicators = []
                    if task.has_notes: indicators.append("[N]")
                    if task.has_comments: indicators.append("[C]")
                    if child_count > 0: indicators.append(f"[F: {child_count}]")
                    ind_str = " ".join(indicators) + " " if indicators else ""
                    
                    # Metadata string from models
                    meta = []
                    if task.priority > 0: 
                        meta.append(f"!{task.priority}")
                    if task.due_date: meta.append(f"^{task.due_date}")
                    for tag in task.tags:
                         if tag != "deleted": meta.append(f"#{tag}")
                    meta_str = " " + " ".join(meta) if meta else ""
                    
                    task_dict = task.model_dump()
                    task_dict["list_name"] = list_name
                    task_dict["list_id"] = l_id
                    task_dict["breadcrumb"] = f"{ind_str}{self._build_breadcrumb_from_map(t_id, task_map)}{meta_str}"
                    all_matches.append(task_dict)
            except Exception as e:
                logger.error(f"Search enrichment failed for list {l_id}: {e}")
                # Fallback: add raw results if enrichment fails
                for task in tasks:
                    task_dict = task.model_dump()
                    task_dict["list_name"] = "Unknown"
                    task_dict["list_id"] = l_id
                    task_dict["breadcrumb"] = task.content
                    all_matches.append(task_dict)
                    
        if not all_matches and len(query) >= 3:
            logger.info(f"Global search returned no results for '{query}', falling back to local list iteration.")
            lists = await self.get_checklists()
            
            async def process_list_local(cl):
                try:
                    tasks = await client.get_tasks(cl.id)
                    query_lower = query.lower()
                    matches = []
                    task_map = {t.id: t for t in tasks}
                    for task in tasks:
                        content_match = query_lower in task.content.lower()
                        tag_match = any(query_lower in t.lower() for t in task.tags)
                        if content_match or tag_match:
                            task_dict = task.model_dump()
                            task_dict["list_name"] = cl.name
                            task_dict["list_id"] = cl.id
                            task_dict["breadcrumb"] = self._build_breadcrumb_from_map(task.id, task_map)
                            matches.append(task_dict)
                    return matches
                except: return []

            local_results = await asyncio.gather(*[process_list_local(cl) for cl in lists])
            for matches in local_results:
                all_matches.extend(matches)
                    
        return self._truncate_list(all_matches, limit=10)

    def _truncate_list(self, items: List[Any], limit: int = 100) -> List[Any]:
        """
        [B1] Context Guard: Truncate list if it exceeds the safety limit.
        Adds a truncation warning if items are removed.
        """
        if len(items) <= limit:
            return items
        
        logger.warning(f"Context Guard: Truncating list from {len(items)} to {limit} items.")
        return items[:limit]

    async def bulk_tag_tasks(self, list_id: int, task_ids: List[int], tags: str):
        """Service wrapper for bulk tagging."""
        client = await self._get_authed_client()
        return await client.bulk_tag_tasks(list_id, task_ids, tags)

    async def bulk_move_tasks(self, list_id: int, task_ids: List[int], target_list_id: int, target_parent_id: int = None):
        """Service wrapper for bulk moving."""
        client = await self._get_authed_client()
        return await client.bulk_move_tasks(list_id, task_ids, target_list_id, target_parent_id)

    async def set_task_styling_by_priority(self, list_id: int, task_id: int, priority: int):
        """Maps numeric priority to visual styling (marks)."""
        client = await self._get_authed_client()
        # Mapping: 1->fg1 (Red), 2->fg2 (Orange), 3->fg3 (Green), etc.
        # Checkvist usually supports up to fg9 (grey/neutral)
        if 1 <= priority <= 9:
            mark = f"fg{priority}"
            return await client.set_task_styling(list_id, task_id, mark=mark)
        elif priority == 0:
            return await client.set_task_styling(list_id, task_id, mark="fg9")
        return None

    async def get_task_enriched(self, list_id: int, task_id: int, include_children: bool = False, depth: int = 2) -> Dict[str, Any]:
        """Fetch task details including notes, comments, and optional child tree."""
        client = await self._get_authed_client()
        task = await client.get_task(list_id, task_id)
        if isinstance(task, list) and task:
            task = task[0]
        
        # Build breadcrumbs (requires list context)
        all_tasks = await client.get_tasks(list_id)
        task_map = {t.id: t for t in all_tasks}
        breadcrumb = self._build_breadcrumb_from_map(task_id, task_map)
        
        # Prepare result
        result = {
            "task": task.model_dump(),
            "breadcrumb": breadcrumb,
            "notes": task.notes or "",
            "comments": task.comments if task.comments else [],
            "children_tree": None
        }
        
        if include_children:
            # Build hierarchy for the branch
            task_nodes = {t.id: {'data': t, 'children': []} for t in all_tasks}
            for t in all_tasks:
                pid = t.parent_id
                if pid and pid in task_nodes:
                    task_nodes[pid]['children'].append(task_nodes[t.id])
            
            if task_id in task_nodes:
                def truncate_tree(node, current_depth):
                    if current_depth >= depth:
                        return {"data": node['data'].model_dump(), "children": [], "truncated": True}
                    return {
                        "data": node['data'].model_dump(),
                        "children": [truncate_tree(c, current_depth + 1) for c in node['children']]
                    }
                result["children_tree"] = truncate_tree(task_nodes[task_id], 0)
                
        return result

    def _build_breadcrumb_from_map(self, task_id: int, task_map: Dict[int, Task]) -> str:
        path = []
        current = task_map.get(task_id)
        while current:
            path.insert(0, current.content)
            pid = current.parent_id
            current = task_map.get(pid) if pid else None
        return " > ".join(path)

    async def import_tasks_smart(self, list_id: int, content: str, parent_id: Optional[int] = None) -> List[Task]:
        """
        Import tasks in bulk, then polyfill features not supported by native import (^date, @user).
        """
        client = await self._get_authed_client()
        
        # Pre-process shorthands for native import
        content = content.replace("!!1", "!1")

        # 1. Native import (handles hierarchy, tags, priority)
        await client.import_tasks(list_id, content, parent_id)
        
        # Checkvist import returns raw status for bulk ops. 
        # We need to re-fetch the list to get the new tasks and polyfill them.
        # This is a bit inefficient but necessary because native bulk import doesn't return created IDs.
        all_tasks = await client.get_tasks(list_id)
        
        # We try to find the newly imported tasks.
        # For simplicity, we filter for tasks without due dates that match the input content lines.
        lines = content.strip().split("\n")
        
        # Only polyfill if we find matches. 
        # This is a "best effort" polyfill.
        for line in lines:
            parsed = self.parser.parse(line)
            if not parsed.due and not parsed.user:
                continue
                
            # Find the task that was just created
            # We look for a task with matching content that doesn't have a due date yet
            match = next((t for t in all_tasks if t.content.strip() == parsed.content and not t.due_date), None)
            
            if match:
                update_data = {}
                if parsed.due:
                    update_data["due_date"] = parsed.due
                # Note: user mapping is skipped for now as per plan focus on dates/tags
                
                if update_data:
                    await client.update_task(list_id, match.id, **update_data)
        
        return all_tasks

    async def move_task_hierarchical(self, list_id: int, task_id: int, target_list_id: int, target_parent_id: Optional[int] = None):
        """Logic for recursive move to prevent hierarchy loss (Fix BUG-004)."""
        client = await self._get_authed_client()
        result = await client.move_task_hierarchy(list_id, task_id, target_list_id, target_parent_id)
        return result

    async def reopen_task(self, list_id: int, task_id: int) -> Task:
        """Reopen a task with robust response handling."""
        client = await self._get_authed_client()
        response = await client.reopen_task(list_id, task_id)
        
        # Handle list-wrapped response
        if isinstance(response, list) and len(response) > 0:
            return response[0]
        return response

    async def archive_task(self, list_id: int, task_id: int) -> str:
        """Recursive archiving with robust tag and response handling (Fix BUG-002)."""
        client = await self._get_authed_client()
        # Invalidate cache for this list
        if list_id in self.list_content_cache:
            self.list_content_cache.pop(list_id, None)
        all_tasks = await client.get_tasks(list_id)
        
        # 1. Identify target task and its descendants
        target_task = next((t for t in all_tasks if t.id == task_id), None)
        if not target_task:
            raise ValueError(f"Task {task_id} not found in list {list_id}")
            
        def get_descendants(pid, tasks):
            descendants = []
            pid = str(pid) # Normalize for comparison
            for t in tasks:
                t_pid = str(t.parent_id) if t.parent_id is not None else ""
                if t_pid == pid:
                    descendants.append(t)
                    descendants.extend(get_descendants(t.id, tasks))
            return descendants
            
        descendants = get_descendants(task_id, all_tasks)
        targets = [target_task] + descendants
        
        # 2. Apply tag to all
        count = 0
        errors = []
        
        for t in targets:
            try:
                if "deleted" not in t.tags:
                    new_tags = t.tags + ["deleted"]
                    await client.update_task(list_id, t.id, tags=",".join(new_tags))
                    count += 1
            except Exception as e:
                logger.error(f"Failed to archive task {t.id}: {e}")
                errors.append(f"Task {t.id} ({t.content}): {e}")
                
        summary = f"Archived {count}/{len(targets)} tasks."
        if errors:
            error_details = "\n- ".join(errors)
            return f"{summary}\n\n> [!WARNING]\n> {len(errors)} tasks failed to archive:\n- {error_details}"
                
        return f"Task {task_id} and its {len(descendants)} descendants successfully archived ({count} items updated)."

    async def add_task(self, list_id: int, content: str, parent_id: int = None, parse: bool = True) -> Task:
        client = await self._get_authed_client()
        # Invalidate cache for this list
        if list_id in self.list_content_cache:
            self.list_content_cache.pop(list_id, None)
        task = await client.add_task(list_id, content, parent_id=parent_id, parse=parse)
        return task

    async def update_task(self, list_id: int, task_id: int, **kwargs) -> Task:
        client = await self._get_authed_client()
        # Invalidate cache for this list
        if list_id in self.list_content_cache:
            self.list_content_cache.pop(list_id, None)
        task = await client.update_task(list_id, task_id, **kwargs)
        return task

    async def move_task(self, list_id: int, task_id: int, target_list_id: int, target_parent_id: Optional[int] = None) -> Task:
        client = await self._get_authed_client()
        # Invalidate cache for source and target lists
        if list_id in self.list_content_cache:
            self.list_content_cache.pop(list_id, None)
        if target_list_id in self.list_content_cache:
            self.list_content_cache.pop(target_list_id, None)
        task = await client.move_task(list_id, task_id, target_list_id, target_parent_id)
        return task

    async def get_tree(self, list_id: int, depth: int = 1) -> List[Dict[str, Any]]:
        client = await self._get_authed_client()
        tasks = await client.get_tasks(list_id)
        
        # Build hierarchy
        task_nodes = {t.id: {'data': t, 'children': []} for t in tasks}
        roots = []
        
        for t in tasks:
            if "deleted" in t.tags: 
                # logger.debug(f"Skipping deleted task {t.id} ({t.content})")
                continue
            
            pid = t.parent_id
            # Normalize root detection (Fix BUG-003)
            is_root = pid is None or pid == 0 or pid == ""
            
            if is_root:
                roots.append(task_nodes[t.id])
            elif pid in task_nodes:
                task_nodes[pid]['children'].append(task_nodes[t.id])
            # Else: Orphaned task (parent excluded/archived), so we hide it too.

        # Apply depth truncation recursively
        def truncate_node(node, current_depth):
            if current_depth >= depth - 1:
                return {'data': node['data'].model_dump(), 'children': []}
            
            return {
                'data': node['data'].model_dump(),
                'children': [truncate_node(child, current_depth + 1) for child in node['children']]
            }

        truncated_roots = [truncate_node(root, 0) for root in roots]
        return self._truncate_list(truncated_roots, limit=50) # Tighter limit for tree structures

    async def get_weekly_summary(self) -> str:
        """
        Analyze tasks across checklists to generate a Productivity Architect's weekly report.
        Identifies wins (completed last 7d) and stale tasks (open, 14d+ no update).
        """
        from datetime import datetime, timedelta
        
        client = await self._get_authed_client()
        checklists = await self.get_checklists()
        
        now = datetime.utcnow()
        last_week = now - timedelta(days=7)
        stale_threshold = now - timedelta(days=14)
        
        wins = []
        stale = []
        blocked = []
        
        # Process top 10 checklists to avoid timeout/rate limits
        for cl in checklists[:10]:
            await asyncio.sleep(0.05)
            try:
                tasks = await client.get_tasks(cl.id)
                for t in tasks:
                    if "deleted" in t.tags: continue
                    
                    # 1. Capture Wins (Closed recently)
                    # Checkvist field is usually updated_at or status_changed_at
                    # We'll use updated_at since status change updates it
                    update_str = t.updated_at
                    if not update_str: continue
                    
                    try:
                        # API uses YYYY/MM/DD... usually
                        updated_dt = datetime.strptime(update_str, "%Y/%m/%dT%H:%M:%SZ")
                    except ValueError:
                        try:
                            # Handle hyphenated ISO format used in mocks/some contexts
                            updated_dt = datetime.strptime(update_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            try:
                                updated_dt = datetime.strptime(update_str, "%Y/%m/%d %H:%M:%S +0000")
                            except: continue

                    if t.status == 1: # Closed
                        if updated_dt >= last_week:
                            wins.append(f"- {t.content} (in **{cl.name}**)")
                    else: # Open
                        # 2. Identify Stale Tasks
                        if updated_dt < stale_threshold:
                            stale.append(f"- {t.content} (in **{cl.name}**, last update: {updated_dt.strftime('%b %d')})")
                        
                        # 3. Identify Blocked (Has tag #blocked or similar)
                        if any(kw in t.content.lower() or any(kw in tag.lower() for tag in t.tags) 
                               for kw in ["blocked", "waiting"]):
                            blocked.append(f"- {t.content} (in **{cl.name}**, tags: {t.tags})")
                            
            except Exception as e:
                logger.error(f"Summary failed for list {cl.id}: {e}")

        # Build Markdown Report
        report = ["# 📊 Weekly Review Assistant Report"]
        report.append(f"Period: {last_week.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
        
        report.append("\n## 🏆 Recent Wins (Last 7 Days)")
        if wins: report.extend(wins[:15]) # Limit to top 15
        else: report.append("_No tasks completed recently. Time to refocus?_")
        
        report.append("\n## ⚠️ Stale Tasks (No updates for 14+ Days)")
        if stale: report.extend(stale[:10])
        else: report.append("_All open tasks have been touched recently. Great maintenance!_")
        
        report.append("\n## 🛑 Blocked / Waiting")
        if blocked: report.extend(blocked[:10])
        else: report.append("_No tasks marked as blocked._")
        
        report.append("\n## 💡 Architecture Insights")
        if not wins and stale:
            report.append("- **Focus Alert**: You have many stale tasks and zero wins. Consider a 'De-cluttering' session.")
        elif len(wins) > 10:
            report.append("- **Velocity High**: You're on a roll. Don't forget to celebrate your wins!")
        
        return "\n".join(report)
