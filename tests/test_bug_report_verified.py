import pytest
import httpx
import time
from httpx import Response
from unittest.mock import MagicMock, patch, AsyncMock
from src.server import mcp, ARCHIVE_TAG

@pytest.mark.asyncio
async def test_bug_001_robust_task_closing(stateful_client):
    """BUG-001: Handle API returning list instead of dict for closing/archiving."""
    from src.server import close_task
    
    # Mock return as a list
    # Use mocker to patch the instance method on the actual client being used
    with patch("tests.conftest.StatefulMockClient.close_task", new_callable=AsyncMock) as mock_close:
        mock_close.return_value = [{"id": 2, "content": "Robust Close", "status": 1}]
        
        result = await close_task("100", "2")
        assert "Task closed: Robust Close" in result

@pytest.mark.asyncio
async def test_bug_002_handle_204_no_content():
    """BUG-002: Bypasses JSON parsing on HTTP 204."""
    from src.client import CheckvistClient
    client = CheckvistClient("user", "key")
    
    response = MagicMock(spec=httpx.Response)
    response.status_code = 204
    response.content = b""
    
    result = await client._safe_json(response)
    assert result == {}

@pytest.mark.asyncio
async def test_bug_003_tag_robustness_dict_format(stateful_client):
    """BUG-003: Handle tags returned as dictionary in archive_task."""
    from src.server import archive_task
    
    # Manually corrupt tag format in mock to simulate API variability
    task_id = 2
    for t in stateful_client.tasks:
        if t["id"] == task_id:
            t["tags"] = {"urgent": "metadata"} # Dict instead of list
            
    result = await archive_task("100", str(task_id))
    assert f"successfully archived with tag #{ARCHIVE_TAG}" in result
    
    # Verify it fixed the format and added the tag
    task = next(t for t in stateful_client.tasks if t["id"] == task_id)
    assert ARCHIVE_TAG in task["tags"]
    assert "urgent" in task["tags"]

@pytest.mark.asyncio
async def test_proc_006_template_verification_error(stateful_client):
    """PROC-006: Return clear error for empty template list."""
    from src.server import apply_template
    
    # Create empty list
    empty_list_id = "555"
    stateful_client.lists.append({"id": 555, "name": "Empty"})
    
    result = await apply_template(template_list_id=empty_list_id, target_list_id="100", confirmed=True)
    assert "Error: Template list 555 is empty" in result

@pytest.mark.asyncio
async def test_targeted_task_id_search(stateful_client):
    """Verify bug fix: Targeted lookup when query is a numeric ID."""
    from src.server import search_tasks
    
    # Query for ID 2 (Setup API)
    result = await search_tasks(query="2")
    assert "Task found by ID 2 in list 'Work'" in result
    assert "Setup API" in result

@pytest.mark.asyncio
async def test_api_rate_limit_warning_regression():
    """SAFE-003: Ensure rate limit warning still works."""
    from src.server import list_checklists
    import src.server
    
    src.server.TOOL_CALL_COUNT = 10
    src.server.LAST_CALL_TIME = time.time()
    
    mock_client = MagicMock()
    mock_client.token = "token"
    mock_client.get_checklists = AsyncMock(return_value=[])
    
    with patch("src.server.get_client", return_value=mock_client):
        result = await list_checklists()
        assert "[!WARNING]" in result
