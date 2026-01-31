import pytest
from unittest.mock import AsyncMock, MagicMock

class StatefulMockClient:
    """A mock client that maintains memory of lists and tasks to verify workflows."""
    def __init__(self):
        self.lists = [
            {"id": 100, "name": "Work", "public": False},
            {"id": 200, "name": "Spesa", "public": False},
            {"id": 999, "name": "Inbox", "public": False}
        ]
        self.tasks = [
            {"id": 1, "content": "Latte", "list_id": 200, "status": 0, "parent_id": None},
            {"id": 2, "content": "Setup API", "list_id": 100, "status": 0, "parent_id": None}
        ]
        self.token = "mock_token"
        self._next_id = 1000

    def _get_next_id(self):
        self._next_id += 1
        return self._next_id

    async def authenticate(self):
        return True

    async def get_checklists(self):
        return self.lists

    async def get_tasks(self, list_id):
        return [t for t in self.tasks if t["list_id"] == int(list_id)]

    async def import_tasks(self, list_id, content, parent_id=None, position=None):
        # Simplified: treats each line as a separate task
        lines = content.strip().split("\n")
        new_tasks = []
        for line in lines:
            t = await self.add_task(list_id, line.strip(), parent_id)
            new_tasks.append(t)
        return new_tasks

    async def add_task(self, list_id, content, parent_id=None, position=None):
        new_task = {
            "id": self._get_next_id(),
            "content": content,
            "list_id": int(list_id),
            "status": 0,
            "parent_id": int(parent_id) if parent_id else None
        }
        self.tasks.append(new_task)
        return new_task

    async def close_task(self, list_id, task_id):
        for t in self.tasks:
            if t["id"] == int(task_id):
                t["status"] = 1
                return t
        raise ValueError("Task not found")

    async def reopen_task(self, list_id, task_id):
        for t in self.tasks:
            if t["id"] == int(task_id):
                t["status"] = 0
                return t
        raise ValueError("Task not found")

    async def add_note(self, list_id, task_id, note):
        # Mock doesn't store notes but simulates success
        return {"id": 1, "comment": note}

    async def move_task_to_list(self, list_id, task_id, target_list_id, target_parent_id=None):
        for t in self.tasks:
            if t["id"] == int(task_id):
                t["list_id"] = int(target_list_id)
                t["parent_id"] = int(target_parent_id) if target_parent_id else None
                return t
        raise ValueError("Task not found")

    async def search_tasks(self, query):
        results = []
        for t in self.tasks:
            if query.lower() in t["content"].lower():
                # Add list name for context
                l_name = next((l["name"] for l in self.lists if l["id"] == t["list_id"]), "Unknown")
                results.append({**t, "list_name": l_name})
        return results

    async def get_task(self, list_id, task_id):
        for t in self.tasks:
            if t["id"] == int(task_id):
                return t
        raise ValueError("Task not found")

    async def update_task(self, list_id, task_id, content=None, priority=None, tags=None, due_date=None):

        for t in self.tasks:
            if t["id"] == int(task_id):
                if content: t["content"] = content
                if priority is not None: t["priority"] = priority
                if tags: t["tags"] = tags
                if due_date: t["due_date"] = due_date
                return t
        raise ValueError("Task not found")

@pytest.fixture
def stateful_client(mocker):
    client = StatefulMockClient()
    mocker.patch("src.server.get_client", return_value=client)
    return client
