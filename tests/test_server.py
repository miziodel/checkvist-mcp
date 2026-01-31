import pytest
import os
import time
from unittest.mock import MagicMock, patch, AsyncMock
from src.server import mcp, ARCHIVE_TAG
import asyncio


@pytest.mark.asyncio
async def test_list_checklists_resource():
    # Mock environment variables
    os.environ["CHECKVIST_USERNAME"] = "test@example.com"
    os.environ["CHECKVIST_API_KEY"] = "fake_key"
    
    # Mock the client
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.authenticate = AsyncMock(return_value=True)
    mock_client.get_checklists = AsyncMock(return_value=[{"id": 1, "name": "List 1"}])
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import list_checklists
        result = await list_checklists()
        assert "- List 1 (ID: 1)" in result

@pytest.mark.asyncio
async def test_get_list_content_resource():
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    task = {"id": 10, "content": "Task 1", "status": 0, "parent_id": None}
    mock_client.get_tasks = AsyncMock(return_value=[task])
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import get_list_content
        result = await get_list_content("1")
        assert "Task 1" in result


@pytest.mark.asyncio
async def test_add_task_tool():
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.add_task = AsyncMock(return_value={"id": 12, "content": "New Task"})
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import add_task
        result = await add_task("1", "New Task")
        assert "Task added: New Task (ID: 12)" in result
        mock_client.add_task.assert_called_with(1, "New Task", None)

@pytest.mark.asyncio
async def test_add_task_smart_syntax_routing():
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.add_task = AsyncMock(return_value={"id": 12, "content": "Task #tag"})
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import add_task
        # Single line with #tag should use import_tasks for reliability
        mock_client.import_tasks = AsyncMock(return_value=[{"id": 12, "content": "Task"}])
        result = await add_task("1", "Task #tag")
        assert "via import" in result
        mock_client.import_tasks.assert_called_with(1, "Task #tag", None)

@pytest.mark.asyncio
async def test_search_tasks_tool():
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    task = {"id": 10, "content": "Find me", "list_name": "L1", "list_id": 1, "parent_id": None}
    mock_client.search_tasks = AsyncMock(return_value=[task])
    mock_client.get_tasks = AsyncMock(return_value=[task])
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import search_tasks
        result = await search_tasks("Find")
        assert "Find me" in result


@pytest.mark.asyncio
async def test_create_list_tool():
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.create_checklist = AsyncMock(return_value={"id": 500, "name": "New Project"})
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import create_list
        result = await create_list(name="New Project")
        assert "Checklist created: New Project (ID: 500)" in result

# --- RISK MITIGATION & SAFETY TESTS ---

@pytest.mark.asyncio
async def test_recursive_logical_deletion_archive_task(stateful_client):
    """SAFE-001: Verify archive_task adds '#deleted' tag recursively."""
    from src.server import archive_task, get_list_content, get_tree
    
    # 1. Setup: Parent (100) -> Child (1001)
    await stateful_client.add_task(100, "Parent", parent_id=None)
    parent_id = stateful_client.tasks[-1]["id"]
    await stateful_client.add_task(100, "Child", parent_id=parent_id)
    child_id = stateful_client.tasks[-1]["id"]
    
    # 2. Archive parent
    result = await archive_task("100", str(parent_id))
    assert "successfully archived" in result
    
    # 3. Verify both have the tag
    parent = next(t for t in stateful_client.tasks if t["id"] == parent_id)
    child = next(t for t in stateful_client.tasks if t["id"] == child_id)
    assert ARCHIVE_TAG in parent["tags"]
    assert ARCHIVE_TAG in child["tags"]
    
    # 4. Verify they are filtered out
    tree_content = await get_tree("100")
    assert "Parent" not in tree_content
    assert "Child" not in tree_content
    """SAFE-002: Verify XML delimiters are present in tool output."""
    from src.server import get_list_content
    
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.get_tasks = AsyncMock(return_value=[{"id": 10, "content": "Sensitive Task", "status": 0}])
    
    with patch("src.server.get_client", return_value=mock_client):
        result = await get_list_content("1")
        assert "<user_data>" in result
        assert "</user_data>" in result
        assert "Sensitive Task" in result

@pytest.mark.asyncio
async def test_api_rate_limit_warning():
    """SAFE-003: Verify rate limit warning appears after 10 calls."""
    from src.server import check_rate_limit, list_checklists
    import src.server
    
    # Reset globals manually for test
    src.server.TOOL_CALL_COUNT = 0
    src.server.LAST_CALL_TIME = time.time()
    
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.get_checklists = AsyncMock(return_value=[])
    
    with patch("src.server.get_client", return_value=mock_client):
        # Call 10 times - should be fine
        for _ in range(10):
            await list_checklists()
            
        # 11th call should trigger warning
        result = await list_checklists()
        assert "[!WARNING]" in result
        assert "High API usage detected" in result

@pytest.mark.asyncio
async def test_get_tree_filters_deleted(stateful_client):
    """Verify get_tree also filters logically deleted tasks."""
    from src.server import archive_task, get_tree
    
    list_id = "100"
    task_id = "2" # "Setup API"
    
    # Archive it
    await archive_task(list_id, task_id)
    
    # Get tree
    result = await get_tree(list_id, depth=1)
    assert "Setup API" not in result

@pytest.mark.asyncio
async def test_breadcrumbs_in_output(stateful_client):
    """SAFE-004: Verify breadcrumbs appear in search and list content."""
    from src.server import get_list_content, search_tasks
    
    # 1. Add a nested task to Work list (ID: 100)
    # Root: Setup API (ID: 2) -> Child: Configure Auth (ID: 1001)
    await stateful_client.add_task(100, "Configure Auth", parent_id=2)
    
    # 2. Verify get_list_content shows breadcrumb
    result = await get_list_content("100")
    assert "Setup API > Configure Auth" in result
    
    # 3. Verify search_tasks shows breadcrumb
    search_res = await search_tasks("Configure")
    assert "Setup API > Configure Auth" in search_res

@pytest.mark.asyncio
async def test_triage_safeguards(stateful_client):
    """SAFE-005: Verify triage safeguards request confirmation."""
    from src.server import move_task_tool, migrate_incomplete_tasks, apply_template
    
    # 1. Test move_task_tool
    res1 = await move_task_tool("100", "2", target_list_id="200")
    assert "[!IMPORTANT]" in res1
    assert "Please confirm" in res1
    
    # Verify it works with confirmed=True
    res2 = await move_task_tool("100", "2", target_list_id="200", confirmed=True)
    assert f"moved task 2" in res2.lower()
    assert "from list 100 to list 200" in res2.lower()
    
    # 2. Test migrate_incomplete_tasks
    res3 = await migrate_incomplete_tasks("100", "200")
    assert "[!IMPORTANT]" in res3
    
    # 3. Test apply_template
    res4 = await apply_template("999", "100")
    assert "[!IMPORTANT]" in res4

@pytest.mark.asyncio
async def test_review_data_wrapping(stateful_client):
    """SAFE-002 (Enhanced): Verify get_review_data also uses XML wrapping."""
    from src.server import get_review_data
    
    result = await get_review_data(timeframe="daily")
    assert "<user_data>" in result
    assert "Review Report (daily)" in result
    assert "Work" in result

@pytest.mark.asyncio
async def test_archive_task_robustness():
    """BUG-001: Verify archive_task handles list response from get_task."""
    from src.server import archive_task
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    # Note: archive_task now uses get_tasks(list_id) to handle recursion
    mock_client.get_tasks = AsyncMock(return_value=[{"id": 10, "content": "Task", "tags": []}])
    mock_client.update_task = AsyncMock(return_value={})
    
    with patch("src.server.get_client", return_value=mock_client):
        result = await archive_task("1", "10")
        assert "successfully archived" in result
        mock_client.update_task.assert_called_with(1, 10, tags=ARCHIVE_TAG)
@pytest.mark.asyncio
async def test_archive_task_dict_tags_robustness():
    """BUG-003: Verify archive_task handles tags as a dict."""
    from src.server import archive_task
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.get_tasks = AsyncMock(return_value=[
        {"id": 10, "content": "Task", "tags": {"existing": "tag"}}
    ])
    mock_client.update_task = AsyncMock(return_value={})
    
    with patch("src.server.get_client", return_value=mock_client):
        result = await archive_task("1", "10")
        assert "successfully archived" in result
        # Should convert dict keys and add ARCHIVE_TAG
        args, kwargs = mock_client.update_task.call_args
        tags = kwargs.get('tags', "")
        assert ARCHIVE_TAG in tags
        assert "existing" in tags

@pytest.mark.asyncio
async def test_add_task_smart_syntax_expanded_routing():
    """META-006: Verify !! and [id:...] trigger parse=True."""
    from src.server import add_task
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.add_task = AsyncMock(return_value={"id": 12, "content": "Task"})
    
    with patch("src.server.get_client", return_value=mock_client):
        # Case: Internal Link [id:123]
        mock_client.import_tasks = AsyncMock(return_value=[{"id": 12, "content": "Task"}])
        await add_task("1", "Check [id:123]")
        mock_client.import_tasks.assert_called_with(1, "Check [id:123]", None)
        
        # Case: High priority !!
        await add_task("1", "Urgent !!1")
        # !!1 should be pre-processed to !1
        mock_client.import_tasks.assert_called_with(1, "Urgent !1", None)

        # Case: Aggressive priority !!!
        await add_task("1", "Very Urgent !!!2")
        # !!!2 should be pre-processed to !2
        mock_client.import_tasks.assert_called_with(1, "Very Urgent !2", None)

@pytest.mark.asyncio
async def test_add_note_robustness():
    """META-001 (Robustness): Verify add_note returns error message on failure."""
    from src.server import add_note
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.add_note = AsyncMock(side_effect=Exception("403 Forbidden"))
    
    with patch("src.server.get_client", return_value=mock_client):
        result = await add_note("1", "10", "New note")
        assert "Error adding note" in result
        assert "403 Forbidden" in result
