import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.server import (
    get_client, add_task, import_tasks,
    add_note, update_task, triage_inbox, move_task_tool,
    close_task, create_list, search_tasks, get_tree, resurface_ideas,
    get_list_content, list_checklists
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
    {"id": 101, "content": "Auth Module", "parent_id": None, "priority": 1, "list_id": 999, "tags": []},
    {"id": 102, "content": "Implement Login", "parent_id": 101, "status": 0, "list_id": 100},
    {"id": 103, "content": "Setup OAuth", "parent_id": 101, "status": 1, "list_id": 100}
]

@pytest.fixture
def mock_client(mocker):
    client_mock = AsyncMock()
    client_mock.token = "mock_token"
    client_mock.get_checklists.return_value = MOCK_LISTS
    client_mock.get_tasks.side_effect = lambda l_id: [t for t in MOCK_TASKS if t.get("list_id") == int(l_id)]
    client_mock.add_task.return_value = {"id": 106, "content": "New Task"}
    client_mock.move_task_hierarchy.return_value = {"status": "ok"}
    client_mock.get_task.return_value = {"id": 101, "content": "Auth Module", "checklist_id": 999, "priority": 1}
    client_mock.move_task.return_value = {"id": 102, "content": "Implement Login", "parent_id": 999}
    client_mock.import_tasks.return_value = [{"id": 201, "content": "Imported 1"}]
    client_mock.add_note.return_value = {"id": 1, "comment": "Mock Note"}
    client_mock.update_task.return_value = {"id": 101, "priority": 1}
    client_mock.create_checklist.return_value = {"id": 500, "name": "New Project"}
    
    mocker.patch("src.server.get_client", return_value=client_mock)
    return client_mock

# --- DISCOVERY TESTS ---

@pytest.mark.asyncio
async def test_list_checklists_tool(mock_client):
    result = await list_checklists()
    assert "- Server MCP - Development (ID: 100)" in result
    assert "- Inbox (ID: 999)" in result

@pytest.mark.asyncio
async def test_get_list_content_tool(mock_client):
    result = await get_list_content("100")
    assert "Implement Login" in result
    assert "(ID: 102)" in result

# --- CONTENT TESTS ---

@pytest.mark.asyncio
async def test_add_task_tool(mock_client):
    result = await add_task(list_id="100", content="Refactor Tests")
    mock_client.add_task.assert_called_with(100, "Refactor Tests", None)
    assert "Task added" in result

@pytest.mark.asyncio
async def test_add_task_smart_syntax_routing(mock_client):
    # Single line with #tag should use import_tasks
    mock_client.import_tasks = AsyncMock(return_value=[{"id": 12, "content": "Task"}])
    result = await add_task("100", "Task #tag")
    assert "via import" in result
    mock_client.import_tasks.assert_called_with(100, "Task #tag", None)

@pytest.mark.asyncio
async def test_add_task_smart_syntax_expanded_routing(mock_client):
    """Verify !! and [id:...] trigger parse=True via import_tasks."""
    mock_client.import_tasks = AsyncMock(return_value=[{"id": 12, "content": "Task"}])
    
    # Case: Internal Link [id:123]
    await add_task("100", "Check [id:123]")
    mock_client.import_tasks.assert_called_with(100, "Check [id:123]", None)
    
    # Case: High priority !!
    await add_task("100", "Urgent !!1")
    # !!1 should be pre-processed to !1
    mock_client.import_tasks.assert_called_with(100, "Urgent !1", None)

@pytest.mark.asyncio
async def test_import_tasks_tool(mock_client):
    result = await import_tasks(list_id="100", content="Task A\n  Subtask A1")
    mock_client.import_tasks.assert_called_with(100, "Task A\n  Subtask A1", None)
    assert "Tasks imported" in result

@pytest.mark.asyncio
async def test_add_note_tool(mock_client):
    result = await add_note(list_id="100", task_id="101", note="Important note")
    mock_client.add_note.assert_called_with(100, 101, "Important note")
    assert "Note added" in result

@pytest.mark.asyncio
async def test_add_note_robustness(mock_client):
    mock_client.add_note.side_effect = Exception("403 Forbidden")
    result = await add_note("100", "101", "New note")
    assert "Error adding note" in result
    assert "403 Forbidden" in result

@pytest.mark.asyncio
async def test_update_task_tool(mock_client):
    result = await update_task(list_id="100", task_id="101", priority=1)
    mock_client.update_task.assert_called_with(100, 101, content=None, priority=1, due_date=None, tags=None)
    assert "Task 101 updated" in result

# --- TRIAGE & SEARCH TESTS ---

@pytest.mark.asyncio
async def test_triage_inbox_tool(mock_client):
    result = await triage_inbox(inbox_name="Inbox")
    assert "Auth Module" in result
    assert "999" in result

@pytest.mark.asyncio
async def test_search_tasks_tool(mock_client):
    result = await search_tasks(query="Auth")
    assert "Auth Module" in result
    assert "Task ID: 101" in result

@pytest.mark.asyncio
async def test_search_by_id_targeted(mock_client):
    result = await search_tasks(query="101")
    assert "Auth Module" in result
    assert "Task ID: 101" in result
    assert "!1" in result

@pytest.mark.asyncio
async def test_move_task_cross_list(mock_client):
    result = await move_task_tool(list_id="999", task_id="101", target_list_id="888", confirmed=True)
    assert "Moved task 101" in result
    mock_client.move_task_hierarchy.assert_called_with(999, 101, 888, None)

@pytest.mark.asyncio
async def test_move_task_same_list(mock_client):
    result = await move_task_tool(list_id="100", task_id="102", target_parent_id="101", confirmed=True)
    mock_client.move_task.assert_called_with(100, 102, 101)
    assert "under new parent 101" in result

# --- MANAGEMENT TESTS ---

@pytest.mark.asyncio
async def test_close_task_tool(mock_client):
    mock_client.close_task.return_value = {"id": 102, "content": "Closing...", "status": 1}
    result = await close_task(list_id="100", task_id="102")
    assert "Task closed: Closing..." in result

@pytest.mark.asyncio
async def test_create_list_tool(mock_client):
    result = await create_list(name="New Project")
    assert "Checklist created: New Project (ID: 500)" in result
    mock_client.create_checklist.assert_called_with("New Project", False)

# --- WORKFLOW TESTS ---

@pytest.mark.asyncio
async def test_get_tree_depth(mock_client):
    # Mock data with hierarchy
    tasks = [
        {"id": 1, "content": "Root", "parent_id": None, "status": 0, "list_id": 100},
        {"id": 2, "content": "Child", "parent_id": 1, "status": 0, "list_id": 100},
        {"id": 3, "content": "Grandchild", "parent_id": 2, "status": 0, "list_id": 100},
    ]
    mock_client.get_tasks.side_effect = lambda l_id: tasks if int(l_id) == 100 else []
    
    # Test Depth 1 (Root only)
    res1 = await get_tree("100", depth=1)
    assert "Root" in res1
    assert "Child" not in res1
    
    # Test Depth 2 (Root + Child)
    res2 = await get_tree("100", depth=2)
    assert "Root" in res2
    assert "Child" in res2
    assert "Grandchild" not in res2

@pytest.mark.asyncio
async def test_resurface_ideas_tool(mock_client):
    with patch("random.shuffle"): # Deterministic
        result = await resurface_ideas()
        assert "Auth Module" in result or "Implement Login" in result or "Setup OAuth" in result
