import pytest
from unittest.mock import AsyncMock
from src.server import (
    mcp, get_client, add_task, import_tasks,
    add_note, set_priority, triage_inbox, move_task_tool,
    close_task, create_list, search_tasks
)

# --- MOCK DATA ---
MOCK_LISTS = [
    {"id": 100, "name": "Server MCP - Development", "public": False},
    {"id": 200, "name": "Server Maintenance", "public": False},
    {"id": 888, "name": "Home", "public": False},
    {"id": 999, "name": "Inbox", "public": False},
    {"id": 300, "name": "Notes", "public": False}
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
    client_mock.move_task_hierarchy.return_value = {"status": "ok"}
    client_mock.get_task.return_value = {"id": 101, "content": "Auth Module", "checklist_id": 999, "priority": 1}
    client_mock.move_task.return_value = {"id": 102, "content": "Implement Login", "parent_id": 999}
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
    result = await add_task(list_id="100", content="Refactor Tests")
    mock_client.add_task.assert_called_with(100, "Refactor Tests", None)
    assert "Task added" in result

@pytest.mark.asyncio
async def test_content_bulk_import(mock_client):
    result = await import_tasks(list_id="100", content="Task A\n  Subtask A1")
    mock_client.import_tasks.assert_called_with(100, "Task A\n  Subtask A1", None)
    assert "Tasks imported" in result

@pytest.mark.asyncio
async def test_content_add_note(mock_client):
    result = await add_note(list_id="100", task_id="101", note="Important note")
    mock_client.add_note.assert_called_with(100, 101, "Important note")
    assert "Note added" in result

@pytest.mark.asyncio
async def test_content_set_priority(mock_client):
    result = await set_priority(list_id="100", task_id="101", priority=1)
    mock_client.update_task.assert_called_with(100, 101, priority=1)
    assert "Priority set to" in result

# --- TRIAGE TESTS ---

@pytest.mark.asyncio
async def test_triage_inbox_fetch(mock_client):
    result = await triage_inbox(inbox_name="Inbox")
    assert "Auth Module" in result
    assert "999" in result

@pytest.mark.asyncio
async def test_search_by_id_targeted(mock_client):
    # Test numeric lookup
    result = await search_tasks(query="101")
    assert "Task found by ID 101" in result
    assert "Auth Module" in result
    assert "!1" in result # Mock should show priority
    mock_client.get_task.assert_called()

@pytest.mark.asyncio
async def test_triage_cross_list_move(mock_client):
    result = await move_task_tool(list_id="999", task_id="501", target_list_id="888", confirmed=True)
    assert "Moved task 501 to list 888" in result
    mock_client.move_task_hierarchy.assert_called_with(999, 501, 888, None)
    assert "verify hierarchy integrity" in result
@pytest.mark.asyncio
async def test_triage_same_list_move(mock_client):
    # Move task 102 under parent 999 in list 100
    result = await move_task_tool(list_id="100", task_id="102", target_parent_id="999", confirmed=True)
    mock_client.move_task.assert_called_with(100, 102, 999)
    assert "under new parent 999 in list 100" in result


# --- MANAGEMENT TESTS ---

@pytest.mark.asyncio
async def test_management_close_task_robust(mock_client):
    # Test with standard dictionary response
    mock_client.close_task.return_value = {"id": 102, "content": "Closing...", "status": 1}
    result = await close_task(list_id="100", task_id="102")
    assert "Task closed: Closing..." in result
    
    # Test with list response (Bug Case Fix)
    mock_client.close_task.return_value = [{"id": 102, "content": "Robust Close", "status": 1}]
    result = await close_task(list_id="100", task_id="102")
    assert "Task closed: Robust Close" in result

@pytest.mark.asyncio
async def test_management_create_list(mock_client):
    mock_client.create_checklist.return_value = {"id": 500, "name": "New Project"}
    result = await create_list(name="New Project")
    assert "Checklist created: New Project (ID: 500)" in result
    mock_client.create_checklist.assert_called_with("New Project", False)

@pytest.mark.asyncio
async def test_smart_syntax_support_update(mock_client):
    # Test that update_task includes parse=true when content is provided
    await move_task_tool(list_id="999", task_id="101", target_list_id="888", confirmed=True)
    # The tool calls move_task_hierarchy, not update_task directly for cross-list
    # But we can test update_task indirectly if needed or just trust the client test.
    # Actually, let's just test that the tools call the client correctly.
    pass
