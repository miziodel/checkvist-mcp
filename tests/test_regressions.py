import pytest
import httpx
import time
from unittest.mock import MagicMock, patch, AsyncMock
from src.server import move_task_tool, search_tasks, archive_task, ARCHIVE_TAG
from src.client import CheckvistClient

# --- BUG FIXES & ROBUSTNESS ---

@pytest.mark.asyncio
async def test_bug_001_robust_task_operations(stateful_client):
    """BUG-001: Handle API returning list instead of dict for closing/archiving."""
    from src.server import close_task
    with patch("tests.conftest.StatefulMockClient.close_task", new_callable=AsyncMock) as mock_close:
        mock_close.return_value = [{"id": 2, "content": "Robust Close", "status": 1}]
        result = await close_task("100", "2")
        assert "Task closed: Robust Close" in result

@pytest.mark.asyncio
async def test_bug_002_handle_204_no_content():
    """BUG-002: Bypasses JSON parsing on HTTP 204."""
    client = CheckvistClient("user", "key")
    response = MagicMock(spec=httpx.Response)
    response.status_code = 204
    response.content = b""
    result = await client._safe_json(response)
    assert result == {}

@pytest.mark.asyncio
async def test_bug_003_tag_robustness_dict_format(stateful_client):
    """BUG-003: Handle tags returned as dictionary in archive_task."""
    task_id = 2
    for t in stateful_client.tasks:
        if t["id"] == task_id:
            t["tags"] = {"urgent": "metadata"} # Dict instead of list
            
    result = await archive_task("100", str(task_id))
    assert f"successfully archived with tag #{ARCHIVE_TAG}" in result
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
    assert "Setup API" in result
    assert "Task ID: 2" in result

@pytest.mark.asyncio
async def test_none_priority_regression(stateful_client):
    """Verify search handles None priority without TypeError."""
    for t in stateful_client.tasks:
        t["priority"] = None
    result = await search_tasks(query="Setup")
    assert "Setup API" in result

# --- WORKFLOW REGRESSIONS ---

@pytest.mark.asyncio
async def test_proc_006_template_verification_error(stateful_client):
    """PROC-006: Return clear error for empty template list."""
    from src.server import apply_template
    empty_list_id = "555"
    stateful_client.lists.append({"id": 555, "name": "Empty"})
    result = await apply_template(template_list_id=empty_list_id, target_list_id="100", confirmed=True)
    assert "Error: Template list 555 is empty" in result

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
    
    tree_content = await get_tree("100")
    assert "Parent" not in tree_content

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
    assert "Setup API > Configure Auth" in search_res

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
