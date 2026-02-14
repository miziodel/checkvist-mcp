import httpx
import logging
from typing import List, Any, Dict

logger = logging.getLogger(__name__)

from src.exceptions import (
    CheckvistAuthError,
    CheckvistAPIError,
    CheckvistRateLimitError,
    CheckvistResourceNotFoundError,
    CheckvistConnectionError,
    CheckvistConnectionError,
    CheckvistPartialSuccessError
)
from src.models import Task, Checklist, Comment

class CheckvistClient:
    BASE_URL = "https://checkvist.com"

    def __init__(self, username: str, api_key: str):
        self.username = username
        self.api_key = api_key
        self.token = None
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=httpx.Timeout(10.0))

    async def close(self):
        """ Close the underlying HTTP client. """
        await self.client.aclose()
        
    async def _handle_request(self, method: str, url: str, **kwargs):
        """ Wrapper for all requests to handle exceptions globally """
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return await self._parse_checkvist_response(response)
        except httpx.ConnectError as e:
            raise CheckvistConnectionError(f"Failed to connect to Checkvist: {e}") from e
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 401:
                raise CheckvistAuthError("Authentication failed: Invalid credentials or token expired") from e
            if status == 429:
                raise CheckvistRateLimitError("Rate limit exceeded", status_code=429) from e
            if status == 404:
                raise CheckvistResourceNotFoundError(f"Resource not found: {url}", status_code=404) from e
            if status >= 500:
                raise CheckvistAPIError(f"Checkvist Server Error: {e}", status_code=status) from e
            # Fallback for other errors (400, 403, etc)
            raise CheckvistAPIError(f"API Error ({status}): {e}", status_code=status) from e
        except Exception as e:
            # Re-raise CheckvistErrors as is
            if isinstance(e, (CheckvistAuthError, CheckvistAPIError, CheckvistConnectionError, CheckvistResourceNotFoundError, CheckvistRateLimitError, CheckvistPartialSuccessError)):
                raise
            raise CheckvistAPIError(f"Unexpected error: {e}") from e

    async def _parse_checkvist_response(self, response: httpx.Response):
        """
        Parses JSON and detects "Soft Errors" hidden in HTTP 200 responses.
        Returns the parsed data (list or dict) or raises a CheckvistError.
        """
        # 1. Handle 204 or empty body
        if response.status_code == 204 or not response.content.strip():
            return {}

        # 2. Try parsing JSON
        try:
            data = response.json()
        except Exception:
            # Not JSON - could be the JS response from /paste endpoint or others
            # If status is 200-299, we treat it as successful
            if 200 <= response.status_code < 300:
                return {"status": "ok", "message": "Success (non-JSON response)", "text": response.text}
            return {"error": "Invalid JSON response", "status_code": response.status_code, "text": response.text}

        # 3. Detect "Soft Errors" in dict responses
        if isinstance(data, dict):
            # Checkvist error fields (can be "error" or "message")
            error_text = data.get("error") or data.get("message")
            if error_text and isinstance(error_text, str) and ("error" in data or "Found" in error_text or "Forbidden" in error_text):
                # Map specific messages to exceptions
                low_text = error_text.lower()
                if "forbidden" in low_text or "not authorized" in low_text:
                    raise CheckvistAuthError(f"API Error: {error_text}")
                if "not found" in low_text:
                    raise CheckvistResourceNotFoundError(f"API Error: {error_text}", status_code=response.status_code)
                # Generic API error for 200 OK with error field
                raise CheckvistAPIError(f"API Error: {error_text}", status_code=response.status_code)

        return data

    def _to_task(self, data: Any) -> Task:
        """Helper to instantiate a Task from potentially polymorphic (list/dict) response."""
        if isinstance(data, list) and data:
            data = data[0]
        if not isinstance(data, dict):
            # Fallback if API returned something totally unexpected
            logger.error(f"Unexpected API response for task: {data}")
            raise CheckvistAPIError(f"Unexpected API response type for task: {type(data)}. Content: {str(data)[:100]}")
        return Task(**data)

    async def authenticate(self) -> bool:
        """ Authenticate with Checkvist and get a token. """
        try:
            response = await self.client.post(
                "/auth/login.json?version=2",
                params={"username": self.username, "remote_key": self.api_key}
            )
            
            if response.status_code == 200:
                self.token = response.json()
                self.client.headers["X-Client-Token"] = self.token
                return True
            elif response.status_code == 401:
                raise CheckvistAuthError(f"Authentication failed: {response.text}")
            else:
                raise CheckvistAPIError(f"Authentication error: {response.text}", status_code=response.status_code)
                
        except httpx.ConnectError as e:
             raise CheckvistConnectionError(f"Connection failed: {e}") from e
        except Exception as e:
            logger.exception("Error during authentication")
            # If we already raised a specific error, let it bubble
            if isinstance(e, (CheckvistAuthError, CheckvistAPIError, CheckvistConnectionError)):
                raise
            raise CheckvistAuthError(f"Unexpected auth error: {e}") from e

    async def get_checklists(self) -> List[Checklist]:
        """ Get all checklists for the user. """
        data = await self._handle_request("GET", "/checklists.json")
        return [Checklist(**cl) for cl in data]

    async def get_tasks(self, list_id: int) -> List[Task]:
        """ Get all tasks in a checklist with notes and tags. """
        params = {"with_notes": "true", "with_tags": "true"}
        data = await self._handle_request("GET", f"/checklists/{list_id}/tasks.json", params=params)
        return [Task(**t) for t in data]

    async def create_checklist(self, name: str, public: bool = False) -> Checklist:
        """ Create a new checklist. """
        data = {
            "checklist[name]": name,
            "checklist[public]": str(public).lower()
        }
        res = await self._handle_request("POST", "/checklists.json", data=data)
        return Checklist(**res)

    async def add_task(self, list_id: int, content: str, parent_id: int = None, position: int = None, parse: bool = False) -> Task:
        """ Add a new task to a checklist. """
        data = {"task[content]": content}
        if parent_id:
            data["task[parent_id]"] = parent_id
        if position:
            data["task[position]"] = position
        if parse:
            data["parse"] = "true"
            
        res = await self._handle_request("POST", f"/checklists/{list_id}/tasks.json", data=data)
        return self._to_task(res)

    async def close_task(self, list_id: int, task_id: int) -> Task:
        """ Mark a task as closed. """
        res = await self._handle_request("POST", f"/checklists/{list_id}/tasks/{task_id}/close.json")
        return self._to_task(res)

    async def reopen_task(self, list_id: int, task_id: int) -> Task:
        """ Reopen a closed task. """
        res = await self._handle_request("POST", f"/checklists/{list_id}/tasks/{task_id}/reopen.json")
        return self._to_task(res)

    async def get_task(self, list_id: int, task_id: int) -> Task:
        """ Get a specific task with notes and tags. """
        params = {"with_notes": "true", "with_tags": "true"}
        res = await self._handle_request("GET", f"/checklists/{list_id}/tasks/{task_id}.json", params=params)
        return self._to_task(res)

    async def get_task_breadcrumbs(self, list_id: int, task_id: int):
        """ Get the breadcrumb path for a task. 
            Note: This fetches the whole list to build the tree efficiently.
        """
        # Fetch all tasks in list to build tree
        # This is heavy but necessary for accurate breadcrumbs without N+1 API calls
        all_tasks = await self.get_tasks(list_id)
        
        # Build map
        task_map = {t.id: t for t in all_tasks}
        
        if task_id not in task_map:
            raise ValueError(f"Task {task_id} not found in list {list_id}")
            
        breadcrumbs = []
        current = task_map[task_id]
        
        while current:
            breadcrumbs.insert(0, current.content)
            parent_id = current.parent_id
            if parent_id and parent_id in task_map:
                current = task_map[parent_id]
            else:
                current = None
                
        return " > ".join(breadcrumbs)

    async def move_task(self, list_id: int, task_id: int, parent_id: int) -> Task:
        """ Move a task to a new parent within the same list. """
        data = {"task[parent_id]": parent_id}
        res = await self._handle_request("PUT", f"/checklists/{list_id}/tasks/{task_id}.json", data=data)
        return self._to_task(res)


    async def move_task_hierarchy(self, list_id: int, task_id: int, target_list_id: int, target_parent_id: int = None):
        """ Move a task and all its children to a different checklist. 
            Uses the undocumented /paste endpoint found via UI forensics. 
            Splits operation into two steps because /paste ignores target_parent_id across lists.
        """
        # Step 1: Move to target list (lands at root)
        url = f"/checklists/{list_id}/tasks/{task_id}/paste"
        params = {
            "move_to": target_list_id,
            "task_ids": task_id
        }
            
        # Use _handle_request for consistency and automatic exception mapping
        response_data = await self._handle_request("POST", url, params=params)
        
        # Step 2: If a target parent was specified, move it under that parent in the new list
        if target_parent_id:
            try:
                await self.move_task(target_list_id, task_id, target_parent_id)
            except Exception as e:
                # We don't raise immediately because the task HAS been moved to the new list 
                # (Step 1 succeeded). We raise a PartialSuccessError instead.
                raise CheckvistPartialSuccessError(
                    f"Task {task_id} moved to list {target_list_id}, but re-parenting under {target_parent_id} failed: {e}",
                    partial_data={"task_id": task_id, "target_list_id": target_list_id, "target_parent_id": target_parent_id}
                )

        return response_data

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
            
        # Returns raw status for bulk ops
        return await self._handle_request("POST", f"/checklists/{list_id}/import.json", data=params)

    async def add_note(self, list_id: int, task_id: int, note: str) -> Comment:
        """ Add a comment/note to a specific task. """
        data = {"comment[comment]": note}
        res = await self._handle_request("POST", f"/checklists/{list_id}/tasks/{task_id}/comments.json", data=data)
        return Comment(**res)

    async def update_task(self, list_id: int, task_id: int, content: str = None, priority: int = None, tags: str = None, due_date: str = None) -> Task:
        """ Update task details. Supports smart syntax if content is provided. """
        data = {}
        if content: 
            data["task[content]"] = content
            data["parse"] = "true" # Enable smart syntax parsing for content updates
        if priority is not None: data["task[priority]"] = priority
        if tags: data["task[tags]"] = tags
        if due_date: data["task[due_date]"] = due_date
            
        res = await self._handle_request("PUT", f"/checklists/{list_id}/tasks/{task_id}.json", data=data)
        return self._to_task(res)

    async def rename_checklist(self, list_id: int, name: str) -> Checklist:
        """ Rename an existing checklist. """
        data = {"checklist[name]": name}
        res = await self._handle_request("PUT", f"/checklists/{list_id}.json", data=data)
        return Checklist(**res)

    async def delete_checklist(self, list_id: int):
        """ Delete a checklist. """
        return await self._handle_request("DELETE", f"/checklists/{list_id}.json")

    async def delete_task(self, list_id: int, task_id: int):
        """ Delete a task. """
        return await self._handle_request("DELETE", f"/checklists/{list_id}/tasks/{task_id}.json")

    async def get_due_tasks(self) -> List[Task]:
        """ Get all tasks with due dates across all checklists. 
            Uses discovered endpoint /checklists/due.json.
        """
        data = await self._handle_request("GET", "/checklists/due.json")
        return [self._to_task(t) for t in data]

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
                tasks = await self.get_tasks(cl.id)
                for task in tasks:
                    if query.lower() in task.content.lower():
                        # We might need to keep raw dicts or hybrid for search results 
                        # if they are used by server.py tools. Let's see.
                        # Actually, keeping them as Tasks is better.
                        # But wait, we are adding extra fields here.
                        # Pydantic models usually ignore extra fields unless Config allow.
                        # Our Task model doesn't have list_name/list_id.
                        all_matches.append(task)
            except Exception as e:
                logger.error(f"Failed to search list {cl['id']}: {e}")
                
        # Limit results to avoid token explosion
        return all_matches[:20]

    async def search_global(self, query: str) -> List[Task]:
        """ Global search using Checkvist's native index. """
        res = await self._handle_request("GET", "/search/everywhere.json", params={"what": query})
        
        # Native search returns {"commands": [...tasks...]}
        data = []
        if isinstance(res, dict):
            data = res.get("commands") or res.get("tasks") or []
        elif isinstance(res, list):
            data = res
            
        return [self._to_task(t) for t in data]

    async def bulk_tag_tasks(self, list_id: int, task_ids: List[int], tags: str):
        """ 
        Apply tags to multiple tasks in a single atomic transaction.
        Uses the discovered /tags.js endpoint.
        """
        if not task_ids:
            return {"status": "ok", "message": "No tasks to tag"}
            
        # The UI uses the first task_id in the path
        base_task_id = task_ids[0]
        data = {
            "task_ids": ",".join(map(str, task_ids)),
            "tags": tags
        }
        return await self._handle_request("POST", f"/checklists/{list_id}/tasks/{base_task_id}/tags.js", data=data)

    async def bulk_move_tasks(self, list_id: int, task_ids: List[int], target_list_id: int, target_parent_id: int = None):
        """
        Move multiple tasks to a new list/parent using native move.json endpoint.
        """
        data = {
            "move_to": target_list_id,
            "task_ids[]": task_ids
        }
        if target_parent_id:
            data["parent_id"] = target_parent_id
            
        return await self._handle_request("POST", f"/checklists/{list_id}/tasks/move.json", data=data)

    async def set_task_styling(self, list_id: int, task_id: int, mark: str = None):
        """
        Set styling (marks/colors) for a task.
        mark: fg1 (red), fg2 (orange), fg3 (green), ..., fg9 (grey/neutral)
        """
        data = {
            "details[id]": task_id,
            "details[mark]": mark
        }
        return await self._handle_request("POST", "/details", data=data)
