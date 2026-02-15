import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from src.server import (
    get_client, add_task, import_tasks, search_list,
    add_note, update_task, triage_inbox, move_task_tool,
    close_task, create_list, search_tasks, get_tree, resurface_ideas,
    get_list_content, list_checklists, get_upcoming_tasks, get_task
)
from src.models import Task, Checklist

# --- MOCK DATA ---
MOCK_LISTS = [
    Checklist(id=100, name="Server MCP - Development", public=False),
    Checklist(id=200, name="Server Maintenance", public=False),
    Checklist(id=888, name="Home", public=False),
    Checklist(id=999, name="Inbox", public=False),
    Checklist(id=300, name="Notes", public=False)
]

MOCK_TASKS = [
    Task(id=101, content="Auth Module", parent_id=None, priority=1, checklist_id=999, tags=[]),
    Task(id=102, content="Implement Login", parent_id=101, status=0, checklist_id=100),
    Task(id=103, content="Setup OAuth", parent_id=101, status=1, checklist_id=100)
]

@pytest.fixture
def mock_client(mocker):
    # Reset global service to ensure a fresh mock client is used in every test
    import src.server
    src.server._service = None
    
    client_mock = AsyncMock()
    client_mock.token = "mock_token"
    client_mock.get_checklists.return_value = MOCK_LISTS
    # Default side_effect for most tests
    client_mock.get_tasks.side_effect = lambda l_id: [t for t in MOCK_TASKS if t.checklist_id == int(l_id)]
    client_mock.add_task.return_value = Task(id=106, content="New Task", checklist_id=int(100))
    client_mock.move_task_hierarchy.return_value = {"status": "ok"}
    client_mock.get_task.return_value = Task(id=101, content="Auth Module", checklist_id=999, priority=1)
    client_mock.move_task.return_value = Task(id=102, content="Implement Login", checklist_id=int(999), parent_id=999)
    client_mock.import_tasks.return_value = [Task(id=201, content="Imported 1", checklist_id=int(100))]
    client_mock.add_note.return_value = {"id": 1, "comment": "Mock Note"}
    client_mock.update_task.return_value = Task(id=101, priority=1, content="Auth Module", checklist_id=int(999))
    client_mock.create_checklist.return_value = Checklist(id=500, name="New Project")
    
    mocker.patch("src.server.get_client", return_value=client_mock)
    client_mock.get_due_tasks.return_value = [
        {"id": 101, "content": "Due Task", "due": "2026/12/31", "checklist_id": 100}
    ]
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
    mock_client.add_task.assert_called_with(100, "Refactor Tests", parent_id=None, parse=True)
    data = json.loads(result)
    assert data["success"] is True
    assert "Task added" in data["message"]

@pytest.mark.asyncio
async def test_add_task_smart_syntax_routing(mock_client):
    # Single line with #tag should use import_tasks
    mock_client.import_tasks = AsyncMock(return_value=[{"id": 12, "content": "Task"}])
    result = await add_task("100", "Task #tag")
    data = json.loads(result)
    assert data["success"] is True
    assert "with smart syntax" in data["message"]
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
    data = json.loads(result)
    assert data["success"] is True
    assert "Tasks imported" in data["message"]

@pytest.mark.asyncio
async def test_add_note_tool(mock_client):
    result = await add_note(list_id="100", task_id="101", note="Important note")
    mock_client.add_note.assert_called_with(100, 101, "Important note")
    data = json.loads(result)
    assert data["success"] is True
    assert "Note added" in data["message"]

@pytest.mark.asyncio
async def test_add_note_robustness(mock_client):
    mock_client.add_note.side_effect = Exception("403 Forbidden")
    result = await add_note("100", "101", "New note")
    data = json.loads(result)
    assert data["success"] is False
    assert "Failed to add note" in data["message"]
    assert "403 Forbidden" in data["error_details"]

@pytest.mark.asyncio
async def test_update_task_tool(mock_client):
    result = await update_task(list_id="100", task_id="101", priority=1)
    mock_client.update_task.assert_called_with(100, 101, content=None, priority=1, due_date=None, tags=None)
    data = json.loads(result)
    assert data["success"] is True
    assert "Task 101 updated" in data["message"]

# --- TRIAGE & SEARCH TESTS ---

@pytest.mark.asyncio
async def test_triage_inbox_tool(mock_client):
    result = await triage_inbox(inbox_name="Inbox")
    data = json.loads(result)
    assert data["success"] is True
    assert any(t["content"] == "Auth Module" for t in data["data"])
    assert any(t["breadcrumb"] == "Auth Module" for t in data["data"])

@pytest.mark.asyncio
async def test_search_tasks_includes_metadata(mock_client):
    """Verify search_tasks returns breadcrumbs and [N], [C], [F] indicators."""
    # Mock search_global to return the tasks
    mock_client.search_global.return_value = [
        Task(id=101, content="Auth Module", checklist_id=999, comments_count=2, notes_count=1)
    ]
    mock_client.get_tasks.side_effect = lambda l_id: [
        Task(id=101, content="Auth Module", parent_id=None, list_id=999, comments_count=2, notes_count=1),
        Task(id=102, content="Child", parent_id=101, list_id=999)
    ]
    result = await search_tasks(query="Auth")
    data = json.loads(result)
    assert data["success"] is True
    # Verify indicators in breadcrumb
    sample = data["data"][0]
    assert "[N]" in sample["breadcrumb"]
    assert "[C]" in sample["breadcrumb"]
    assert "[F: 1]" in sample["breadcrumb"]
    assert "Auth Module" in sample["breadcrumb"]

@pytest.mark.asyncio
async def test_get_task_details_tool(mock_client):
    """Verify get_task tool returns notes, comments, and breadcrumbs."""
    mock_client.get_task.return_value = Task(
        id=101, 
        content="Auth Module", 
        checklist_id=999,
        notes="System auth specs",
        comments=[{"comment": "Fixed bug #1"}, {"comment": "Added OAuth"}]
    )
    # Mock tasks for breadcrumb resolution
    mock_client.get_tasks.side_effect = lambda l_id: [
        Task(id=101, content="Auth Module", parent_id=None, checklist_id=999)
    ]
    
    result = await get_task(list_id="999", task_id="101")
    data = json.loads(result)
    assert data["success"] is True
    assert "System auth specs" in data["data"]["details"]
    assert "Fixed bug #1" in data["data"]["details"]
    assert "Auth Module" in data["data"]["details"] # Breadcrumb

@pytest.mark.asyncio
async def test_get_task_with_children_tree(mock_client):
    """Verify get_task(include_children=True) returns the sub-tree."""
    mock_client.get_task.return_value = Task(id=1, content="Parent", checklist_id=100)
    mock_client.get_tasks.side_effect = lambda l_id: [
        Task(id=1, content="Parent", parent_id=None, checklist_id=100),
        Task(id=2, content="Child 1", parent_id=1, checklist_id=100),
        Task(id=3, content="Child 2", parent_id=1, checklist_id=100)
    ]
    
    result = await get_task(list_id="100", task_id="1", include_children=True)
    data = json.loads(result)
    assert data["success"] is True
    assert "tree" in data["data"]
    assert "Child 1" in data["data"]["tree"]
    assert "Child 2" in data["data"]["tree"]

@pytest.mark.asyncio
async def test_move_task_cross_list(mock_client):
    result = await move_task_tool(list_id="999", task_id="101", target_list_id="888", confirmed=True)
    data = json.loads(result)
    assert data["success"] is True
    assert "Moved task 101" in data["message"]
    mock_client.move_task_hierarchy.assert_called_with(999, 101, 888, None)

@pytest.mark.asyncio
async def test_move_task_same_list(mock_client):
    result = await move_task_tool(list_id="100", task_id="102", target_parent_id="101", confirmed=True)
    mock_client.move_task.assert_called_with(100, 102, 101)
    data = json.loads(result)
    assert data["success"] is True
    assert "under new parent 101" in data["message"]

# --- MANAGEMENT TESTS ---

@pytest.mark.asyncio
async def test_close_task_tool(mock_client):
    mock_client.close_task.return_value = Task(id=102, content="Closing...", status=1, checklist_id=100)
    result = await close_task(list_id="100", task_id="102")
    data = json.loads(result)
    assert data["success"] is True
    assert "Task closed: Closing..." in data["message"]

@pytest.mark.asyncio
async def test_create_list_tool(mock_client):
    result = await create_list(name="New Project")
    data = json.loads(result)
    assert data["success"] is True
    assert "Checklist created: New Project" in data["message"]
    assert data["data"]["id"] == 500
    mock_client.create_checklist.assert_called_with("New Project", False)

# --- WORKFLOW TESTS ---

@pytest.mark.asyncio
async def test_get_tree_depth(mock_client):
    # Mock data with hierarchy
    tasks = [
        Task(id=1, content="Root", parent_id=None, status=0, checklist_id=100),
        Task(id=2, content="Child", parent_id=1, status=0, checklist_id=100),
        Task(id=3, content="Grandchild", parent_id=2, status=0, checklist_id=100),
    ]
    mock_client.get_tasks.side_effect = lambda l_id: tasks if int(l_id) == 100 else []
    
    # Test Depth 1 (Root only)
    res1 = await get_tree("100", depth=1)
    data1 = json.loads(res1)
    assert "Root" in data1["data"]
    assert "Child" not in data1["data"]
    
    # Test Depth 2 (Root + Child)
    res2 = await get_tree("100", depth=2)
    data2 = json.loads(res2)
    assert "Root" in data2["data"]
    assert "Child" in data2["data"]
    assert "Grandchild" not in data2["data"]

@pytest.mark.asyncio
async def test_resurface_ideas_tool(mock_client):
    with patch("random.shuffle"): # Deterministic, stays [100, 200, 888]
        result = await resurface_ideas()
        data = json.loads(result)
        assert data["success"] is True
        # First 3 lists are 100, 200, 888. List 100 has 'Implement Login'.
        valid_breadcrumbs = ["Auth Module", "Implement Login", "Setup OAuth"]
        assert any(item["breadcrumb"] in valid_breadcrumbs for item in data["data"])

@pytest.mark.asyncio
async def test_search_list_json_format(mock_client):
    """Verify search_list returns correct JSON structure."""
    with patch('src.server.check_rate_limit', return_value=""):
        result = await search_list("Server")
        data = json.loads(result)
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert any(l["name"] == "Server Maintenance" for l in data["data"])

@pytest.mark.asyncio
async def test_add_task_error_json_format():
    """Verify add_task handles exceptions with proper JSON error response."""
    with patch('src.server.get_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_client.token = "fake_token"
        mock_client.add_task.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        result = await add_task("1", "New Task")
        data = json.loads(result)
        assert data["success"] is False
        assert data["action"] == "add_task"
        assert data["error_details"] == "API Error"

@pytest.mark.asyncio
async def test_get_task_standard_response_crash_repro(mock_client, mocker):
    """Reproduce crash when get_task encounters an unexpected exception."""
    # Force an Exception in the service layer to trigger the broken error handling
    mocker.patch("src.server.get_service", side_effect=Exception("Database Failure"))
    
    # This should return a nice JSON error, but previously crashed with TypeError
    result = await get_task(list_id="100", task_id="1")
    data = json.loads(result)
    assert data["success"] is False
    assert "Database Failure" in data["error_details"]
    assert "next_steps" in data
    assert "Check the task ID" in data["next_steps"]

@pytest.mark.asyncio
async def test_get_task_list_response_handled(mock_client):
    """Verify get_task handles cases where the API returns a list instead of a dict."""
    # Mock get_task to return a list (polymorphic response)
    mock_client.get_task.return_value = [Task(id=101, content="Task in List", checklist_id=999)]
    
    # This should succeed by extracting the first element
    result = await get_task(list_id="999", task_id="101")
    data = json.loads(result)
    assert data["success"] is True
    assert "Task in List" in data["data"]["details"]
@pytest.mark.asyncio
async def test_bulk_tag_tasks_tool(mock_client):
    from src.server import bulk_tag_tasks
    result = await bulk_tag_tasks(list_id="100", task_ids=["101", "102"], tags="tag1,tag2")
    data = json.loads(result)
    assert data["success"] is True
    mock_client.bulk_tag_tasks.assert_called_with(100, [101, 102], "tag1,tag2")

@pytest.mark.asyncio
async def test_bulk_move_tasks_tool(mock_client):
    from src.server import bulk_move_tasks
    result = await bulk_move_tasks(list_id="100", task_ids=["101", "102"], target_list_id="200")
    data = json.loads(result)
    assert data["success"] is True
    mock_client.bulk_move_tasks.assert_called_with(100, [101, 102], 200, None)

@pytest.mark.asyncio
async def test_set_task_priority_styling(mock_client):
    # This should use update_task which in turn should trigger styling in the service/client
    result = await update_task(list_id="100", task_id="101", priority=1)
    data = json.loads(result)
    assert data["success"] is True
    # The client's set_task_styling should be called eventually
    mock_client.set_task_styling.assert_called_with(100, 101, mark="fg1")
