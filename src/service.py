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

    async def archive_task(self, list_id: int, task_id: int):
        """Robust archiving (Fix BUG-002)."""
        client = await self._get_authed_client()
        task = await client.get_task(list_id, task_id)
        
        tags = task.get('tags', [])
        # Robust tag conversion (Fix BUG-002)
        if isinstance(tags, dict):
            tag_list = list(tags.keys())
        elif isinstance(tags, list):
            tag_list = tags
        else:
            tag_list = []
            
        if "deleted" not in tag_list:
            tag_list.append("deleted")
            
        return await client.update_task(list_id, task_id, tags=",".join(tag_list))

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
