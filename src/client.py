import httpx
import logging

logger = logging.getLogger(__name__)

class CheckvistClient:
    BASE_URL = "https://checkvist.com"

    def __init__(self, username: str, api_key: str):
        self.username = username
        self.api_key = api_key
        self.token = None
        self.client = httpx.AsyncClient(base_url=self.BASE_URL)

    async def _safe_json(self, response: httpx.Response):
        """ Safely parse JSON or return an empty dict if the body is empty (e.g. 204 No Content). """
        if response.status_code == 204 or not response.content.strip():
            return {}
        try:
            return response.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {response.text}. Error: {e}")
            return {}

    async def authenticate(self) -> bool:
        """ Authenticate with Checkvist and get a token. """
        try:
            response = await self.client.post(
                "/auth/login.json?version=2",
                params={"username": self.username, "remote_key": self.api_key}
            )
            if response.status_code == 200:
                # The response is just the token string in JSON
                self.token = response.json()
                self.client.headers["X-Client-Token"] = self.token
                return True
            else:
                logger.error(f"Authentication failed with status {response.status_code}")
                return False
        except Exception as e:
            logger.exception("Error during authentication")
            return False

    async def get_checklists(self):
        """ Get all checklists for the user. """
        response = await self.client.get("/checklists.json")
        response.raise_for_status()
        return await self._safe_json(response)

    async def get_tasks(self, list_id: int):
        """ Get all tasks in a checklist. """
        response = await self.client.get(f"/checklists/{list_id}/tasks.json")
        response.raise_for_status()
        return await self._safe_json(response)

    async def create_checklist(self, name: str, public: bool = False):
        """ Create a new checklist. """
        params = {
            "checklist[name]": name,
            "checklist[public]": str(public).lower()
        }
        response = await self.client.post("/checklists.json", params=params)
        response.raise_for_status()
        return await self._safe_json(response)

    async def add_task(self, list_id: int, content: str, parent_id: int = None, position: int = None):
        """ Add a new task to a checklist. """
        data = {"task[content]": content}
        if parent_id:
            data["task[parent_id]"] = parent_id
        if position:
            data["task[position]"] = position
            
        response = await self.client.post(f"/checklists/{list_id}/tasks.json", params=data)
        response.raise_for_status()
        return await self._safe_json(response)

    async def close_task(self, list_id: int, task_id: int):
        """ Mark a task as closed. """
        response = await self.client.post(f"/checklists/{list_id}/tasks/{task_id}/close.json")
        response.raise_for_status()
        return await self._safe_json(response)

    async def reopen_task(self, list_id: int, task_id: int):
        """ Reopen a closed task. """
        response = await self.client.post(f"/checklists/{list_id}/tasks/{task_id}/reopen.json")
        response.raise_for_status()
        return await self._safe_json(response)

    async def get_task(self, list_id: int, task_id: int):
        """ Get a specific task. """
        response = await self.client.get(f"/checklists/{list_id}/tasks/{task_id}.json")
        response.raise_for_status()
        return await self._safe_json(response)

    async def get_task_breadcrumbs(self, list_id: int, task_id: int):
        """ Get the breadcrumb path for a task. 
            Note: This fetches the whole list to build the tree efficiently.
        """
        # Fetch all tasks in list to build tree
        # This is heavy but necessary for accurate breadcrumbs without N+1 API calls
        all_tasks = await self.get_tasks(list_id)
        
        # Build map
        task_map = {t['id']: t for t in all_tasks}
        
        if task_id not in task_map:
            raise ValueError(f"Task {task_id} not found in list {list_id}")
            
        breadcrumbs = []
        current = task_map[task_id]
        
        while current:
            breadcrumbs.insert(0, current['content'])
            parent_id = current.get('parent_id')
            if parent_id and parent_id in task_map:
                current = task_map[parent_id]
            else:
                current = None
                
        return " > ".join(breadcrumbs)

    async def move_task(self, list_id: int, task_id: int, parent_id: int):
        """ Move a task to a new parent within the same list. """
        data = {"task[parent_id]": parent_id}
        response = await self.client.put(f"/checklists/{list_id}/tasks/{task_id}.json", params=data)
        response.raise_for_status()
        return await self._safe_json(response)


    async def move_task_hierarchy(self, list_id: int, task_id: int, target_list_id: int, target_parent_id: int = None):
        """ Move a task and all its children to a different checklist. 
            Uses the undocumented /paste endpoint found via UI forensics. 
        """
        # Pattern: POST /checklists/{source_list_id}/tasks/{task_id}/paste
        # Params: move_to={target_list_id}&task_ids={task_id}
        url = f"/checklists/{list_id}/tasks/{task_id}/paste"
        params = {
            "move_to": target_list_id,
            "task_ids": task_id
        }
        if target_parent_id:
            params["target_parent_id"] = target_parent_id
            
        response = await self.client.post(url, params=params)
        response.raise_for_status()
        
        # The paste endpoint returns a JS-like response (text/javascript), not JSON.
        # We treat 200 OK as success.
        try:
            return await self._safe_json(response)
        except Exception:
            # Fallback for JS responses
            return {"status": "ok", "message": "Hierarchy moved successfully"}

    async def import_tasks(self, list_id: int, content: str, parent_id: int = None, position: int = None):
        """ Import tasks in bulk using Checkvist's hierarchical text format. """
        params = {
            "import_content": content,
            "parse_tasks": 1 # Use numeric 1 as per some API examples
        }
        if parent_id:
            params["parent_id"] = parent_id
        if position:
            params["position"] = position
            
        response = await self.client.post(f"/checklists/{list_id}/import.json", params=params)
        response.raise_for_status()
        return await self._safe_json(response)

    async def add_note(self, list_id: int, task_id: int, note: str):
        """ Add a comment/note to a specific task. """
        data = {"comment[comment]": note}
        response = await self.client.post(f"/checklists/{list_id}/tasks/{task_id}/comments.json", params=data)
        response.raise_for_status()
        return await self._safe_json(response)

    async def update_task(self, list_id: int, task_id: int, content: str = None, priority: int = None, tags: str = None, due_date: str = None):
        """ Update task details. Supports smart syntax if content is provided. """
        params = {}
        if content: 
            params["task[content]"] = content
            params["parse"] = "true" # Enable smart syntax parsing for content updates
        if priority is not None: params["task[priority]"] = priority
        if tags: params["task[tags]"] = tags
        if due_date: params["task[due_date]"] = due_date
            
        response = await self.client.put(f"/checklists/{list_id}/tasks/{task_id}.json", params=params)
        response.raise_for_status()
        return await self._safe_json(response)

    async def rename_checklist(self, list_id: int, name: str):
        """ Rename an existing checklist. """
        data = {"checklist[name]": name}
        response = await self.client.put(f"/checklists/{list_id}.json", params=data)
        response.raise_for_status()
        return await self._safe_json(response)

    async def delete_checklist(self, list_id: int):
        """ Delete a checklist. """
        response = await self.client.delete(f"/checklists/{list_id}.json")
        response.raise_for_status()
        return await self._safe_json(response)

    async def delete_task(self, list_id: int, task_id: int):
        """ Delete a task. """
        response = await self.client.delete(f"/checklists/{list_id}/tasks/{task_id}.json")
        response.raise_for_status()
        return await self._safe_json(response)

    async def search_tasks(self, query: str):
        """ Search for tasks using Checkvist's search logic where possible, 
            or a safer iteration.
            
            WARNING: This is still expensive if many lists exist.
            Added rate limiting protection (simple sleep).
        """
        import asyncio
        checklists = await self.get_checklists()
        all_matches = []
        
        for cl in checklists:
            # Simple rate limit prevention
            await asyncio.sleep(0.1) 
            try:
                tasks = await self.get_tasks(cl["id"])
                for task in tasks:
                    if query.lower() in task.get("content", "").lower():
                        task["list_name"] = cl["name"]
                        task["list_id"] = cl["id"]
                        all_matches.append(task)
            except Exception as e:
                logger.error(f"Failed to search list {cl['id']}: {e}")
                
        # Limit results to avoid token explosion
        return all_matches[:20]

    async def close(self):
        await self.client.aclose()
