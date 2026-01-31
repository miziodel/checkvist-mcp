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

    async def add_task(self, list_id, content, parent_id=None, position=None, parse=False):
        new_task = {
            "id": self._get_next_id(),
            "content": content,
            "list_id": int(list_id),
            "status": 0,
            "parent_id": int(parent_id) if parent_id else None,
            "priority": 0,
            "tags": [],
            "due_date": None
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


    async def move_task_hierarchy(self, list_id, task_id, target_list_id, target_parent_id=None):
        """Mock hierarchical move by moving the task and all its descendants."""
        def get_descendant_ids(pid):
            descendants = []
            for t in self.tasks:
                if t["parent_id"] == pid:
                    descendants.append(t["id"])
                    descendants.extend(get_descendant_ids(t["id"]))
            return descendants

        target_ids = [int(task_id)] + get_descendant_ids(int(task_id))
        
        for t in self.tasks:
            if t["id"] in target_ids:
                t["list_id"] = int(target_list_id)
                if t["id"] == int(task_id):
                    t["parent_id"] = int(target_parent_id) if target_parent_id else None
        
        return {"status": "ok"}

    async def move_task(self, list_id, task_id, parent_id):
        """Move a task to a new parent within the same list."""
        for t in self.tasks:
            if t["id"] == int(task_id):
                t["parent_id"] = int(parent_id) if parent_id else None
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

    async def delete_task(self, list_id, task_id):
        target_id = int(task_id)
        def get_descendant_ids(pid):
            ids = []
            for t in self.tasks:
                if t.get("parent_id") == pid:
                    ids.append(t["id"])
                    ids.extend(get_descendant_ids(t["id"]))
            return ids
        
        ids_to_delete = [target_id] + get_descendant_ids(target_id)
        self.tasks = [t for t in self.tasks if t["id"] not in ids_to_delete]
        return {"status": "ok"}

    async def update_task(self, list_id, task_id, content=None, priority=None, tags=None, due_date=None):
        for t in self.tasks:
            if t["id"] == int(task_id):
                if content: t["content"] = content
                if priority is not None: t["priority"] = priority
                if tags is not None:
                    if isinstance(tags, str):
                        # API style: comma separated string
                        t["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    else:
                        t["tags"] = tags
                if due_date: t["due_date"] = due_date
                return t
        raise ValueError("Task not found")

    async def rename_checklist(self, list_id, name):
        for l in self.lists:
            if l["id"] == int(list_id):
                l["name"] = name
                return l
        raise ValueError("List not found")

@pytest.fixture
def stateful_client(mocker):
    client = StatefulMockClient()
    mocker.patch("src.server.get_client", return_value=client)
    # Reset rate limit counter for each test
    import src.server
    src.server.TOOL_CALL_COUNT = 0
    return client
