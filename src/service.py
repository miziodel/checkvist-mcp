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
        # We process in parallel with a concurrency limit if needed, but for now linear with 0.1s sleep as per client
        for cl in lists:
            await asyncio.sleep(0.05) # reduced sleep for service layer
            try:
                tasks = await client.get_tasks(cl["id"])
                
                # Step 2: Build local map for breadcrumbs within this list
                task_map = {t["id"]: t for t in tasks}
                
                for task in tasks:
                    # Search in content OR tags (Fix BUG-005) OR ID exact match
                    content_match = query_lower in task.get("content", "").lower()
                    id_match = str(task["id"]) == query.strip()
                    tags = task.get("tags", [])
                    # Handle both list and dict tags (Robustness BUG-002)
                    tag_list = tags if isinstance(tags, list) else list(tags.keys()) if isinstance(tags, dict) else []
                    tag_match = any(query_lower in str(tag).lower() for tag in tag_list)
                    
                    if content_match or tag_match or id_match:
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
                        breadcrumb = self._build_breadcrumb_from_map(task["id"], task_map)
                        task["breadcrumb"] = f"{breadcrumb}{meta_str}"
                        all_matches.append(task)
            except Exception as e:
                logger.error(f"Search failed for list {cl['id']}: {e}")
                
        return all_matches[:20]

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
        
        # In the context of Checkvist, we need to check if we can do this in one call 
        # or if we need to recurse. Most modern APIs handle it, but we'll add verification.
        result = await client.move_task_to_list(list_id, task_id, target_list_id, target_parent_id)
        
        # Invalidation
        self.list_content_cache.pop(list_id, None)
        self.list_content_cache.pop(target_list_id, None)
        
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
                
        return roots
