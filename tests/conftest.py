import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

class StatefulMockClient:
    """A mock client that maintains memory of lists and tasks to verify workflows."""
    def __init__(self):
        self.lists = [
            {"id": 100, "name": "Work", "public": False},
            {"id": 200, "name": "Spesa", "public": False},
            {"id": 999, "name": "Inbox", "public": False}
        ]
        self.tasks = [
            {"id": 1, "content": "Latte", "list_id": 200, "status": 0, "parent_id": None, "updated_at": "2026/01/01 12:00:00 +0000"},
            {"id": 2, "content": "Setup API", "list_id": 100, "status": 0, "parent_id": None, "updated_at": "2026/01/01 12:00:00 +0000"}
        ]
        self.token = "mock_token"
        self._next_id = 1000

    def _get_next_id(self):
        self._next_id += 1
        return self._next_id

    async def authenticate(self):
        return True

    async def get_checklists(self):
        from src.models import Checklist
        return [Checklist(**cl) for cl in self.lists]

    async def get_tasks(self, list_id):
        from src.models import Task
        return [Task(**t) for t in self.tasks if t["list_id"] == int(list_id)]

    async def import_tasks(self, list_id, content, parent_id=None, position=None):
        from src.models import Task
        # Simplified: treats each line as a separate task
        lines = content.strip().split("\n")
        new_tasks = []
        for line in lines:
            t = await self.add_task(list_id, line.strip(), parent_id)
            new_tasks.append(t)
        return new_tasks

    async def add_task(self, list_id, content, parent_id=None, position=None, parse=False):
        from src.models import Task
        new_task_dict = {
            "id": self._get_next_id(),
            "content": content,
            "list_id": int(list_id),
            "status": 0,
            "parent_id": int(parent_id) if parent_id else None,
            "priority": 0,
            "tags": [],
            "due_date": None,
            "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        self.tasks.append(new_task_dict)
        return Task(**new_task_dict)

    async def close_task(self, list_id, task_id):
        from src.models import Task
        for t in self.tasks:
            if t["id"] == int(task_id):
                t["status"] = 1
                return Task(**t)
        raise ValueError("Task not found")

    async def reopen_task(self, list_id, task_id):
        from src.models import Task
        for t in self.tasks:
            if t["id"] == int(task_id):
                t["status"] = 0
                return Task(**t)
        raise ValueError("Task not found")

    async def add_note(self, list_id, task_id, note):
        return {"id": 1, "comment": note}

    async def move_task_hierarchy(self, list_id, task_id, target_list_id, target_parent_id=None):
        target_ids = [int(task_id)]
        
        # 1. Find all descendants to move (BFS)
        to_move = {int(task_id)}
        queue = [int(task_id)]
        
        while queue:
            curr_id = queue.pop(0)
            children = [t["id"] for t in self.tasks if t["parent_id"] == curr_id]
            for child_id in children:
                if child_id not in to_move:
                    to_move.add(child_id)
                    queue.append(child_id)
            
        # 2. Move them all to the new list
        for t in self.tasks:
            if t["id"] in to_move:
                t["list_id"] = int(target_list_id)
                # Only update parent_id for the root moved task
                if t["id"] == int(task_id):
                    t["parent_id"] = int(target_parent_id) if target_parent_id else None
                    
        return {"status": "ok"}

    async def move_task(self, list_id, task_id, parent_id):
        from src.models import Task
        for t in self.tasks:
            if t["id"] == int(task_id):
                t["parent_id"] = int(parent_id) if parent_id else None
                return Task(**t)
        raise ValueError("Task not found")

    async def search_tasks(self, query):
        from src.models import Task
        results = []
        for t in self.tasks:
            content_lower = t.get("content", "").lower()
            tags = t.get("tags", [])
            tag_match = any(query.lower() in str(tag).lower() for tag in tags)
            if query.lower() in content_lower or tag_match or str(t["id"]) == query:
                results.append(Task(**t))
        return results

    async def get_task(self, list_id, task_id):
        from src.models import Task
        for t in self.tasks:
            if t["id"] == int(task_id):
                return Task(**t)
        raise ValueError("Task not found")

    async def delete_task(self, list_id, task_id):
        self.tasks = [t for t in self.tasks if t["id"] != int(task_id)]
        return {"status": "ok"}

    async def update_task(self, list_id, task_id, content=None, priority=None, tags=None, due_date=None):
        from src.models import Task
        for t in self.tasks:
            if t["id"] == int(task_id):
                if content: t["content"] = content
                if priority is not None: t["priority"] = priority
                if tags is not None:
                    if isinstance(tags, str):
                        t["tags"] = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    else:
                        t["tags"] = tags
                if due_date: t["due_date"] = due_date
                return Task(**t)
        raise ValueError("Task not found")

    async def get_due_tasks(self):
        from src.models import Task
        return [Task(**t) for t in self.tasks if t.get("due_date")]

    async def search_global(self, query):
        return await self.search_tasks(query)

    async def bulk_tag_tasks(self, list_id, task_ids, tags):
        for tid in task_ids:
            await self.update_task(list_id, tid, tags=tags)
        return {"status": "ok"}

    async def bulk_move_tasks(self, list_id, task_ids, target_list_id, target_parent_id=None):
        for tid in task_ids:
            await self.move_task_hierarchy(list_id, tid, target_list_id, target_parent_id)
        return {"status": "ok"}

    async def set_task_styling(self, list_id, task_id, mark=None):
        return {"status": "ok"}

    async def rename_checklist(self, list_id, name):
        from src.models import Checklist
        for l in self.lists:
            if l["id"] == int(list_id):
                l["name"] = name
                return Checklist(**l)
        raise ValueError("List not found")

@pytest.fixture
def stateful_client(mocker):
    client = StatefulMockClient()
    mocker.patch("src.server.get_client", return_value=client)
    import src.server
    src.server.TOOL_CALL_COUNT = 0
    src.server.service = None
    return client

