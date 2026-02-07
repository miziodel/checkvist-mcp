import pytest
import httpx
import time
import json
import respx
from httpx import Response
from unittest.mock import MagicMock, patch, AsyncMock
from src.server import move_task_tool, search_tasks, archive_task, apply_template, ARCHIVE_TAG
from src.client import CheckvistClient

# --- BUG FIXES & ROBUSTNESS ---

@pytest.mark.asyncio
async def test_bug_001_robust_task_operations(stateful_client):
    """BUG-001: Handle API returning list instead of dict for closing/archiving."""
    from src.server import close_task
    with patch("tests.conftest.StatefulMockClient.close_task", new_callable=AsyncMock) as mock_close:
        mock_close.return_value = [{"id": 2, "content": "Robust Close", "status": 1}]
        result = await close_task("100", "2")
        data = json.loads(result)
        assert "Task closed: Robust Close" in data["message"]

@pytest.mark.asyncio
async def test_bug_002_handle_204_no_content():
    """BUG-002: Bypasses JSON parsing on HTTP 204."""
    client = CheckvistClient("user", "key")
    response = MagicMock(spec=httpx.Response)
    response.status_code = 204
    response.content = b""
    result = await client._parse_checkvist_response(response)
    assert result == {}

@pytest.mark.asyncio
async def test_bug_003_tag_robustness_dict_format(stateful_client):
    """BUG-003: Handle tags returned as dictionary in archive_task."""
    task_id = 2
    for t in stateful_client.tasks:
        if t["id"] == task_id:
            t["tags"] = {"urgent": "metadata"} # Dict instead of list
            
    result = await archive_task("100", str(task_id))
    data = json.loads(result)
    assert data["success"] is True
    assert "successfully archived" in data["message"]
    assert "updated 1 items" in data["message"]
    task = next(t for t in stateful_client.tasks if t["id"] == task_id)
    assert ARCHIVE_TAG in task["tags"]
    assert "urgent" in task["tags"]

@pytest.mark.asyncio
async def test_bug_004_hierarchy_loss_on_move():
    """BUG-004: Hierarchy Loss on Cross-List Move.
    Moving a parent should keep children nested.
    """
    from tests.conftest import StatefulMockClient
    client = StatefulMockClient()
    client.tasks = [
        {"id": 1, "content": "Parent", "list_id": 100, "status": 0, "parent_id": None},
        {"id": 2, "content": "Child", "list_id": 100, "status": 0, "parent_id": 1}
    ]
    with patch("src.server.get_client", return_value=client):
        await move_task_tool(list_id="100", task_id="1", target_list_id="200", confirmed=True)
        parent = next(t for t in client.tasks if t["id"] == 1)
        assert parent["list_id"] == 200
        child = next(t for t in client.tasks if t["id"] == 2)
        assert child["list_id"] == 200
        assert child["parent_id"] == 1

@pytest.mark.asyncio
async def test_bug_005_search_scope_includes_tags(stateful_client):
    """BUG-005: Search Scope Includes Tags."""
    await stateful_client.update_task(100, 2, tags="urgent")
    result = await search_tasks(query="urgent")
    data = json.loads(result)
    assert data["success"] is True
    # In JSON mode, breadcrumb and task_id are in the list of results
    assert any("Setup API" in t["breadcrumb"] for t in data["data"])
    assert any(t["task_id"] == 2 for t in data["data"])

@pytest.mark.asyncio
async def test_none_priority_regression(stateful_client):
    """Verify search handles None priority without TypeError."""
    for t in stateful_client.tasks:
        t["priority"] = None
    result = await search_tasks(query="Setup")
    data = json.loads(result)
    assert any("Setup API" in t["breadcrumb"] for t in data["data"])

# --- WORKFLOW REGRESSIONS ---

@pytest.mark.asyncio
async def test_proc_006_template_verification_error(stateful_client):
    """PROC-006: Return clear error for empty template list."""
    from src.server import apply_template
    empty_list_id = "555"
    stateful_client.lists.append({"id": 555, "name": "Empty"})
    result = await apply_template(template_list_id=empty_list_id, target_list_id="100", confirmed=True)
    data = json.loads(result)
    assert data["success"] is False
    assert "Template list 555 is empty" in data["message"]

# --- SAFETY & SECURITY REGRESSIONS ---

@pytest.mark.asyncio
async def test_safe_001_recursive_logical_deletion(stateful_client):
    """SAFE-001: Verify archive_task adds '#deleted' tag recursively."""
    from src.server import get_tree
    await stateful_client.add_task(100, "Parent", parent_id=None)
    parent_id = stateful_client.tasks[-1]["id"]
    await stateful_client.add_task(100, "Child", parent_id=parent_id)
    child_id = stateful_client.tasks[-1]["id"]
    
    await archive_task("100", str(parent_id))
    parent = next(t for t in stateful_client.tasks if t["id"] == parent_id)
    child = next(t for t in stateful_client.tasks if t["id"] == child_id)
    assert ARCHIVE_TAG in parent["tags"]
    assert ARCHIVE_TAG in child["tags"]
    
    tree_result = await get_tree("100")
    tree_data = json.loads(tree_result)
    assert "Parent" not in tree_data["data"]

@pytest.mark.asyncio
async def test_safe_002_user_data_wrapping(stateful_client):
    """SAFE-002: Verify XML delimiters are present in tool output."""
    from src.server import get_list_content
    result = await get_list_content("100")
    assert "<user_data>" in result
    assert "</user_data>" in result

@pytest.mark.asyncio
async def test_safe_003_api_rate_limit_warning():
    """SAFE-003: Verify rate limit warning appears after 10 calls."""
    from src.server import list_checklists
    import src.server
    src.server.TOOL_CALL_COUNT = 10
    src.server.LAST_CALL_TIME = time.time()
    
    mock_client = AsyncMock(spec=CheckvistClient)
    mock_client.token = "token"
    mock_client.get_checklists.return_value = []
    
    with patch("src.server.get_client", return_value=mock_client):
        result = await list_checklists()
        assert "[!WARNING]" in result

@pytest.mark.asyncio
async def test_safe_004_breadcrumbs_visibility(stateful_client):
    """SAFE-004: Verify breadcrumbs in search and list content."""
    from src.server import get_list_content
    await stateful_client.add_task(100, "Configure Auth", parent_id=2)
    result = await get_list_content("100")
    assert "Setup API > Configure Auth" in result
    search_res = await search_tasks("Configure")
    search_data = json.loads(search_res)
    assert any("Setup API > Configure Auth" in t["breadcrumb"] for t in search_data["data"])

@pytest.mark.asyncio
async def test_safe_005_triage_safeguards(stateful_client):
    """SAFE-005: Verify triage safeguards request confirmation."""
    from src.server import migrate_incomplete_tasks, apply_template
    res1 = await move_task_tool("100", "2", target_list_id="200")
    assert "[!IMPORTANT]" in res1
    res3 = await migrate_incomplete_tasks("100", "200")
    assert "[!IMPORTANT]" in res3
    res4 = await apply_template("999", "100")
    assert "[!IMPORTANT]" in res4

@pytest.mark.asyncio
async def test_bug_006_archive_task_list_wrapped_response():
    """BUG-006: Verify archive_task handles list-wrapped responses."""
    mock_client = AsyncMock(spec=CheckvistClient)
    mock_client.token = "token"
    # Mock get_tasks to return simple structure
    mock_client.get_tasks.return_value = [{"id": 1, "content": "Task 1", "tags": []}]
    mock_client.update_task = AsyncMock()
    
    with patch("src.server.get_client", return_value=mock_client):
        result = await archive_task("100", "1")
        data = json.loads(result)
        assert "successfully archived" in data["message"]
        mock_client.update_task.assert_called()

@pytest.mark.asyncio
async def test_bug_006_repro_attribute_error():
    """BUG-006: Specifically reproduce the 'list' has no attribute 'get' error fix."""
    mock_client = AsyncMock(spec=CheckvistClient)
    mock_client.token = "token"
    mock_client.get_tasks.return_value = [{"id": 1, "content": "P", "parent_id": None}]
    mock_client.update_task = AsyncMock()
    
    with patch("src.server.get_client", return_value=mock_client):
        # We need to mock 'next' to return a list for target_task
        with patch("src.server.next", return_value=[{"id": 1, "content": "P", "tags": []}]):
            result = await archive_task("100", "1")
            data = json.loads(result)
            assert "successfully archived" in data["message"]

@pytest.mark.asyncio
async def test_bug_007_template_hierarchy_preservation():
    """BUG-007: Verify apply_template maintains hierarchy in import_tasks."""
    mock_client = AsyncMock(spec=CheckvistClient)
    mock_client.token = "token"
    # Setup a hierarchy: 1 -> 2 -> 3
    mock_client.get_tasks.return_value = [
        {"id": 1, "content": "Root", "parent_id": 0},
        {"id": 2, "content": "Child", "parent_id": 1},
        {"id": 3, "content": "Grandchild", "parent_id": 2}
    ]
    mock_client.import_tasks = AsyncMock()
    
    with patch("src.server.get_client", return_value=mock_client):
        await apply_template("999", "100", confirmed=True)
        
        args, _ = mock_client.import_tasks.call_args
        content = args[1]
        expected = "Root\n  Child\n    Grandchild"
        assert content == expected

@pytest.mark.asyncio
async def test_bug_008_reopen_task_list_response(stateful_client):
    """BUG-008: Handle API returning list instead of dict for reopen_task."""
    from src.server import reopen_task
    with patch("tests.conftest.StatefulMockClient.reopen_task", new_callable=AsyncMock) as mock_reopen:
        mock_reopen.return_value = [{"id": 2, "content": "Reopened", "status": 0}]
        result = await reopen_task("100", "2")
        data = json.loads(result)
        assert "Task reopened: Reopened" in data["message"]

@pytest.mark.asyncio
@respx.mock
async def test_bug_009_import_tasks_payload_hygiene():
    """BUG-009: Verify import_tasks uses POST data (body) instead of query params."""
    client = CheckvistClient("user", "key")
    client.token = "token"
    
    # Mock the response using respx
    route = respx.post("https://checkvist.com/checklists/100/import.json").mock(
        return_value=Response(200, json={"status": "ok"})
    )
    
    await client.import_tasks("100", "task content")
    
    # Check that request was called with POST and data
    assert route.called
    request = route.calls.last.request
    assert request.method == "POST"
    
    # Verify content in body
    body = request.read().decode()
    assert "import_content=task+content" in body or "import_content=task content" in body

@pytest.mark.asyncio
async def test_template_root_detection_robustness(stateful_client):
    """Verify apply_template handles string '0' and cyclic references safely."""
    # String '0'
    stateful_client.tasks = [{"id": 11, "content": "Root", "list_id": 999, "status": 0, "parent_id": "0"}]
    res = await apply_template(template_list_id="999", target_list_id="100", confirmed=True)
    data = json.loads(res)
    assert data["success"] is True
    assert "Template applied" in data["message"]
    
    # Cyclic (should fallback to all tasks or handle gracefully)
    stateful_client.tasks = [
        {"id": 1, "content": "A", "list_id": 999, "status": 0, "parent_id": 2},
        {"id": 2, "content": "B", "list_id": 999, "status": 0, "parent_id": 1}
    ]
    res = await apply_template(template_list_id="999", target_list_id="100", confirmed=True)
    data = json.loads(res)
    # Check if failed with specific message or succeeded
    assert data["success"] is True or "No valid tasks found" in data["message"]

@pytest.mark.asyncio
async def test_safe_006_resource_shutdown():
    """SAFE-006: Verify that shutdown() closes the client session."""
    from src.server import get_client, shutdown
    import src.server
    import httpx
    
    # Initialize client
    c = get_client()
    c.client = AsyncMock(spec=httpx.AsyncClient)
    
    # Call shutdown
    await shutdown()
    
    # Verify client.aclose() was called
    c.client.aclose.assert_called_once()
    assert src.server.client is None

@pytest.mark.asyncio
async def test_server_lifespan_lifecycle():
    """Verify that server lifespan correctly calls shutdown on exit."""
    from src.server import server_lifespan, get_client
    import src.server
    import httpx
    
    # Setup client
    c = get_client()
    c.client = AsyncMock(spec=httpx.AsyncClient)
    
    # Execute lifespan
    async with server_lifespan(None):
        # Server is "running"
        assert src.server.client is not None
        
    # After exiting block, client should be closed and set to None
    c.client.aclose.assert_called_once()
    assert src.server.client is None

@pytest.mark.asyncio
async def test_safe_id_validation():
    """Verify that tools handle non-numeric IDs gracefully."""
    from src.server import add_task, move_task_tool
    
    # Test add_task with invalid list_id
    res = await add_task("INVALID", "test content")
    data = json.loads(res)
    assert data["success"] is False
    assert "Invalid list ID" in data["message"]
    assert "numeric" in data.get("next_steps", "").lower()
    
    # Test move_task_tool with invalid target_list_id
    res = await move_task_tool("100", "200", target_list_id="TRASH", confirmed=True)
    data = json.loads(res)
    assert data["success"] is False
    assert "Invalid target list ID" in data["message"]

@pytest.mark.asyncio
@respx.mock
async def test_bug_010_move_task_cross_list_parent_id():
    """BUG-010: Verify that move_task_tool handles cross-list parenting correctly."""
    client = CheckvistClient("user", "key")
    client.token = "mock_token"
    
    # 1. Mock the /paste endpoint (Step 1 of fix)
    paste_route = respx.post("https://checkvist.com/checklists/100/tasks/1/paste").mock(
        return_value=Response(200, content=b"Paste OK")
    )
    
    # 2. Mock the /update endpoint (Step 2 of fix)
    update_route = respx.put("https://checkvist.com/checklists/200/tasks/1.json").mock(
        return_value=Response(200, json={"id": 1, "parent_id": 2001, "content": "Moved Task"})
    )
    
    with patch("src.server.get_client", return_value=client):
        result = await move_task_tool(
            list_id="100", 
            task_id="1", 
            target_list_id="200", 
            target_parent_id="2001", 
            confirmed=True
        )
        
        assert paste_route.called
        assert update_route.called
        
        # Verify the update call set the parent_id correctly
        update_data = update_route.calls.last.request.read().decode()
        assert "task%5Bparent_id%5D=2001" in update_data or "task[parent_id]=2001" in update_data
        
        data = json.loads(result)
        assert data["success"] is True
