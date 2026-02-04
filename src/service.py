import asyncio
import logging
from typing import List, Dict, Any, Optional
from cachetools import TTLCache
from .client import CheckvistClient

logger = logging.getLogger(__name__)

class CheckvistService:
    def __init__(self, client: CheckvistClient):
        self.client = client
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
            if l["id"] == list_id:
                return l["name"]
        return "Unknown"

    async def invalidate_list_cache(self):
        self.list_cache.pop("lists", None)

    async def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Enhanced search: Optimized N+1 and checks tags (Fix BUG-005)."""
        client = await self._get_authed_client()
        lists = await self.get_checklists()
        
        all_matches = []
        query_lower = query.lower()
        
        # Step 1: Efficient fetching (N lists)
        for cl in lists:
            await asyncio.sleep(0.05) 
            try:
                tasks = await client.get_tasks(cl["id"])
                
                # Step 2: Build local map for breadcrumbs within this list
                task_map = {t["id"]: t for t in tasks}
                
                # Pre-calculate children count
                children_map = {}
                for t in tasks:
                    pid = t.get("parent_id")
                    if pid:
                        children_map[pid] = children_map.get(pid, 0) + 1
                
                for task in tasks:
                    # Search in content OR tags (Fix BUG-005) OR ID exact match
                    content_match = query_lower in task.get("content", "").lower()
                    id_match = str(task["id"]) == query.strip()
                    tags = task.get("tags", [])
                    # Handle both list and dict tags (Robustness BUG-002)
                    tag_list = tags if isinstance(tags, list) else list(tags.keys()) if isinstance(tags, dict) else []
                    tag_match = any(query_lower in str(tag).lower() for tag in tag_list)
                    
                    if content_match or tag_match or id_match:
                        # Add indicators
                        notes_count = task.get("notes_count", 0)
                        comments_count = task.get("comments_count", 0)
                        child_count = children_map.get(task["id"], 0)
                        
                        indicators = []
                        if notes_count > 0: indicators.append("[N]")
                        if comments_count > 0: indicators.append("[C]")
                        if child_count > 0: indicators.append(f"[F: {child_count}]")
                        
                        ind_str = " ".join(indicators) + " " if indicators else ""
                        
                        # Add decorators for search result strings
                        meta = []
                        priority = task.get('priority')
                        if priority is not None and int(priority) > 0: 
                            meta.append(f"!{priority}")
                        if task.get('due_date'): meta.append(f"^{task['due_date']}")
                        for tag in tag_list:
                             if tag != "deleted": meta.append(f"#{tag}")
                        
                        meta_str = " " + " ".join(meta) if meta else ""
                        task["list_name"] = cl["name"]
                        task["list_id"] = cl["id"]
                        task["has_notes"] = notes_count > 0
                        task["has_comments"] = comments_count > 0
                        task["child_count"] = child_count
                        
                        breadcrumb = self._build_breadcrumb_from_map(task["id"], task_map)
                        task["breadcrumb"] = f"{ind_str}{breadcrumb}{meta_str}"
                        all_matches.append(task)
            except Exception as e:
                logger.error(f"Search failed for list {cl['id']}: {e}")
                
        return all_matches[:10] # Cap to 10 context-rich results for better focus

    async def get_task_enriched(self, list_id: int, task_id: int, include_children: bool = False, depth: int = 2) -> Dict[str, Any]:
        """Fetch task details including notes, comments, and optional child tree."""
        client = await self._get_authed_client()
        task = await client.get_task(list_id, task_id)
        
        # Polymorphic handling: API might return a list [task] or dict
        if isinstance(task, list):
            if not task:
                raise ValueError(f"Task {task_id} not found (empty response)")
            task = task[0]
            
        if not isinstance(task, dict):
             raise ValueError(f"Invalid task response format: {type(task)}")
        
        # Build breadcrumbs (requires list context)
        all_tasks = await client.get_tasks(list_id)
        task_map = {t['id']: t for t in all_tasks}
        breadcrumb = self._build_breadcrumb_from_map(task_id, task_map)
        
        # Prepare result
        result = {
            "task": task,
            "breadcrumb": breadcrumb,
            "notes": task.get("notes", ""),
            "comments": task.get("comments", []),
            "children_tree": None
        }
        
        if include_children:
            # Build hierarchy for the branch
            task_nodes = {t['id']: {'data': t, 'children': []} for t in all_tasks}
            for t in all_tasks:
                pid = t.get('parent_id')
                if pid and pid in task_nodes:
                    task_nodes[pid]['children'].append(task_nodes[t['id']])
            
            if task_id in task_nodes:
                def truncate_tree(node, current_depth):
                    if current_depth >= depth:
                        return {"data": node['data'], "children": [], "truncated": True}
                    return {
                        "data": node['data'],
                        "children": [truncate_tree(c, current_depth + 1) for c in node['children']]
                    }
                result["children_tree"] = truncate_tree(task_nodes[task_id], 0)
                
        return result

    def _build_breadcrumb_from_map(self, task_id: int, task_map: Dict[int, Any]) -> str:
        path = []
        current = task_map.get(task_id)
        while current:
            path.insert(0, current.get('content', 'Unknown'))
            pid = current.get('parent_id')
            current = task_map.get(pid) if pid else None
        return " > ".join(path)

    async def move_task_hierarchical(self, list_id: int, task_id: int, target_list_id: int, target_parent_id: Optional[int] = None):
        """Logic for recursive move to prevent hierarchy loss (Fix BUG-004)."""
        client = await self._get_authed_client()
        result = await client.move_task_hierarchy(list_id, task_id, target_list_id, target_parent_id)
        return result

    async def reopen_task(self, list_id: int, task_id: int) -> Dict[str, Any]:
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
        all_tasks = await client.get_tasks(list_id)
        
        # 1. Identify target task and its descendants
        def get_descendants(pid, tasks):
            descendants = []
            for t in tasks:
                if t.get('parent_id') == pid:
                    descendants.append(t)
                    descendants.extend(get_descendants(t['id'], tasks))
            return descendants
            
        target_task = next((t for t in all_tasks if t['id'] == task_id), None)
        if not target_task:
            raise ValueError(f"Task {task_id} not found in list {list_id}")
            
        descendants = get_descendants(task_id, all_tasks)
        targets = [target_task] + descendants
        
        # 2. Apply tag to all
        count = 0
        for t in targets:
            # Handle possible list-wrapped items in 'all_tasks' (defensive)
            if isinstance(t, list) and len(t) > 0:
                t = t[0]
            
            raw_tags = t.get('tags', [])
            if isinstance(raw_tags, list):
                tag_list = raw_tags
            elif isinstance(raw_tags, dict):
                tag_list = list(raw_tags.keys())
            elif isinstance(raw_tags, str) and raw_tags:
                tag_list = [tag.strip() for tag in raw_tags.split(',')]
            else:
                tag_list = []
                
            if "deleted" not in tag_list:
                tag_list.append("deleted")
                await client.update_task(list_id, t['id'], tags=",".join(tag_list))
                count += 1
                
        return f"Task {task_id} and {len(descendants)} subtasks successfully archived (updated {count} items)."

    async def get_tree(self, list_id: int, depth: int = 1) -> List[Dict[str, Any]]:
        client = await self._get_authed_client()
        tasks = await client.get_tasks(list_id)
        
        # Build hierarchy
        task_map = {t['id']: {'data': t, 'children': []} for t in tasks}
        roots = []
        
        for t in tasks:
            if "deleted" in t.get('tags', []): continue
            
            pid = t.get('parent_id')
            # Normalize root detection (Fix BUG-003)
            is_root = pid is None or pid == 0 or pid == ""
            
            if not is_root and pid in task_map:
                task_map[pid]['children'].append(task_map[t['id']])
            else:
                roots.append(task_map[t['id']])

        # Apply depth truncation recursively
        def truncate_node(node, current_depth):
            if current_depth >= depth - 1:
                return {'data': node['data'], 'children': []}
            
            return {
                'data': node['data'],
                'children': [truncate_node(child, current_depth + 1) for child in node['children']]
            }

        return [truncate_node(root, 0) for root in roots]

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
                tasks = await client.get_tasks(cl["id"])
                for t in tasks:
                    if "deleted" in t.get('tags', []): continue
                    
                    # 1. Capture Wins (Closed recently)
                    # Checkvist field is usually updated_at or status_changed_at
                    # We'll use updated_at since status change updates it
                    update_str = t.get('updated_at')
                    if not update_str: continue
                    
                    try:
                        updated_dt = datetime.strptime(update_str, "%Y/%m/%dT%H:%M:%SZ")
                    except ValueError:
                        try:
                            # Handle hyphenated ISO format used in mocks/some contexts
                            updated_dt = datetime.strptime(update_str, "%Y-%m-%dT%H:%M:%SZ")
                        except ValueError:
                            try:
                                updated_dt = datetime.strptime(update_str, "%Y/%m/%d %H:%M:%S +0000")
                            except: continue

                    if t.get('status', 0) == 1: # Closed
                        if updated_dt >= last_week:
                            wins.append(f"- {t['content']} (in **{cl['name']}**)")
                    else: # Open
                        # 2. Identify Stale Tasks
                        if updated_dt < stale_threshold:
                            stale.append(f"- {t['content']} (in **{cl['name']}**, last update: {updated_dt.strftime('%b %d')})")
                        
                        # 3. Identify Blocked (Has tag #blocked or similar)
                        tags = t.get('tags', [])
                        tag_list = tags if isinstance(tags, list) else list(tags.keys()) if isinstance(tags, dict) else []
                        if any(kw in str(tag).lower() for tag in tag_list for kw in ["blocked", "waiting"]):
                            blocked.append(f"- {t['content']} (in **{cl['name']}**, tag: {tag_list})")
                            
            except Exception as e:
                logger.error(f"Summary failed for list {cl['id']}: {e}")

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
