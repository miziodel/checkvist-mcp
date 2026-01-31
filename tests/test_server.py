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
async def test_logical_deletion_archive_task(stateful_client):
    """SAFE-001: Verify archive_task adds '#deleted' tag and filters it out."""
    from src.server import archive_task, get_list_content
    
    # 1. Archive a task
    list_id = "200"
    task_id = "1" # "Latte" in stateful_client
    
    result = await archive_task(list_id, task_id)
    assert f"successfully archived with tag #{ARCHIVE_TAG}" in result
    
    # Verify tag was added in the mock client
    task = next(t for t in stateful_client.tasks if t["id"] == int(task_id))
    assert ARCHIVE_TAG in task["tags"]
    
    # 2. Verify it's filtered out from get_list_content
    content = await get_list_content(list_id)
    assert "Latte" not in content

@pytest.mark.asyncio
async def test_prompt_injection_delimiters():
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

