import pytest
import os
import sys
from unittest.mock import AsyncMock

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.server import mcp, get_client

# --- MOCK DATA ---
MOCK_LISTS = [
    {"id": 100, "name": "Server MCP - Development", "public": False},
    {"id": 200, "name": "Server Maintenance", "public": False},
    {"id": 888, "name": "Home", "public": False},
    {"id": 999, "name": "Inbox", "public": False}
]

MOCK_TASKS = [
    {"id": 101, "content": "Auth Module", "parent_id": None},
    {"id": 102, "content": "Implement Login", "parent_id": 101, "status": 0},
    {"id": 103, "content": "Setup OAuth", "parent_id": 101, "status": 1}
]

@pytest.fixture
def mock_client(mocker):
    client_mock = AsyncMock()
    client_mock.token = "mock_token"
    client_mock.get_checklists.return_value = MOCK_LISTS
    client_mock.get_tasks.return_value = MOCK_TASKS
    client_mock.add_task.return_value = {"id": 106, "content": "New Task"}
    client_mock.move_task_to_list.return_value = {"id": 501, "content": "Buy Milk"}
    client_mock.import_tasks.return_value = [{"id": 201, "content": "Imported 1"}]
    client_mock.add_note.return_value = {"id": 1, "comment": "Mock Note"}
    client_mock.update_task.return_value = {"id": 101, "priority": 1}
    
    mocker.patch("src.server.get_client", return_value=client_mock)
    return client_mock

# --- DISCOVERY TESTS ---
# ... (existing discovery tests)

# --- CONTENT TESTS ---

@pytest.mark.asyncio
async def test_content_add_task_contextual(mock_client):
    from src.server import add_task
    result = await add_task(list_id="100", content="Refactor Tests")
    mock_client.add_task.assert_called_with(100, "Refactor Tests", None)
    assert "Task added" in result

@pytest.mark.asyncio
async def test_content_bulk_import(mock_client):
    from src.server import import_tasks
    result = await import_tasks(list_id="100", content="Task A\n  Subtask A1")
    mock_client.import_tasks.assert_called_with(100, "Task A\n  Subtask A1", None)
    assert "Tasks imported" in result

@pytest.mark.asyncio
async def test_content_add_note(mock_client):
    from src.server import add_note
    result = await add_note(list_id="100", task_id="101", note="Important note")
    mock_client.add_note.assert_called_with(100, 101, "Important note")
    assert "Note added" in result

@pytest.mark.asyncio
async def test_content_set_priority(mock_client):
    from src.server import set_priority
    result = await set_priority(list_id="100", task_id="101", priority=1)
    mock_client.update_task.assert_called_with(100, 101, priority=1)
    assert "Priority updated" in result

# --- TRIAGE TESTS ---

@pytest.mark.asyncio
async def test_triage_inbox_fetch(mock_client):
    from src.server import triage_inbox
    result = await triage_inbox(inbox_name="Inbox")
    assert "Auth Module" in result # MOCK_TASKS is used in get_tasks
    assert "999" in result

@pytest.mark.asyncio
async def test_triage_cross_list_move(mock_client):
    from src.server import move_task_tool
    result = await move_task_tool(list_id="999", task_id="501", target_list_id="888")
    mock_client.move_task_to_list.assert_called_with(999, 501, 888, None)
    assert "from list 999 to list 888" in result
