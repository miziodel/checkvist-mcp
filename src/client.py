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
        return response.json()

    async def get_tasks(self, list_id: int):
        """ Get all tasks in a checklist. """
        response = await self.client.get(f"/checklists/{list_id}/tasks.json")
        response.raise_for_status()
        return response.json()

    async def add_task(self, list_id: int, content: str, parent_id: int = None, position: int = None):
        """ Add a new task to a checklist. """
        data = {"task[content]": content}
        if parent_id:
            data["task[parent_id]"] = parent_id
        if position:
            data["task[position]"] = position
            
        response = await self.client.post(f"/checklists/{list_id}/tasks.json", params=data)
        response.raise_for_status()
        return response.json()

    async def update_task(self, list_id: int, task_id: int, content: str = None, priority: int = None):
        """ Update an existing task. """
        data = {}
        if content:
            data["task[content]"] = content
        if priority is not None:
            data["task[priority]"] = priority
            
        response = await self.client.put(f"/checklists/{list_id}/tasks/{task_id}.json", params=data)
        response.raise_for_status()
        return response.json()

    async def close_task(self, list_id: int, task_id: int):
        """ Mark a task as closed. """
        response = await self.client.post(f"/checklists/{list_id}/tasks/{task_id}/close.json")
        response.raise_for_status()
        return response.json()

    async def reopen_task(self, list_id: int, task_id: int):
        """ Reopen a closed task. """
        response = await self.client.post(f"/checklists/{list_id}/tasks/{task_id}/reopen.json")
        response.raise_for_status()
        return response.json()

    async def search_tasks(self, query: str):
        """ Search for tasks across all lists by content. """
        checklists = await self.get_checklists()
        all_matches = []
        for cl in checklists:
            tasks = await self.get_tasks(cl["id"])
            for task in tasks:
                if query.lower() in task.get("content", "").lower():
                    # Add list info to task for context
                    task["list_name"] = cl["name"]
                    task["list_id"] = cl["id"]
                    all_matches.append(task)
        return all_matches

    async def close(self):
        await self.client.aclose()
