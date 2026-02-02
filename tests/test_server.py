import pytest
import os
import time
import json
from unittest.mock import MagicMock, patch, AsyncMock
from src.server import mcp, ARCHIVE_TAG
from src.client import CheckvistClient
from src.response import StandardResponse
import asyncio

def test_standard_response_success():
    """Verify success response formatting."""
    resp_str = StandardResponse.success("Success message", data={"id": 123})
    resp = json.loads(resp_str)
    assert resp["success"] is True
    assert resp["message"] == "Success message"
    assert resp["data"]["id"] == 123

def test_standard_response_error():
    """Verify error response formatting."""
    resp_str = StandardResponse.error(
        message="Failed",
        action="test_action",
        next_steps="Try again",
        error_details="Detailed error"
    )
    resp = json.loads(resp_str)
    assert resp["success"] is False
    assert resp["message"] == "Failed"
    assert resp["action"] == "test_action"
    assert resp["next_steps"] == "Try again"
    assert resp["error_details"] == "Detailed error"


@pytest.mark.asyncio
async def test_list_checklists_resource():
    # Mock environment variables
    os.environ["CHECKVIST_USERNAME"] = "test@example.com"
    os.environ["CHECKVIST_API_KEY"] = "fake_key"
    
    # Mock the client
    mock_client = AsyncMock(spec=CheckvistClient)
    mock_client.token = "mock_token"
    mock_client.authenticate.return_value = True
    mock_client.get_checklists.return_value = [{"id": 1, "name": "List 1"}]
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import list_checklists
        result = await list_checklists()
        assert "- List 1 (ID: 1)" in result

@pytest.mark.asyncio
async def test_get_list_content_resource():
    mock_client = AsyncMock(spec=CheckvistClient)
    mock_client.token = "mock_token"
    task = {"id": 10, "content": "Task 1", "status": 0, "parent_id": None}
    mock_client.get_tasks.return_value = [task]
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import get_list_content
        result = await get_list_content("1")
        assert "Task 1" in result


@pytest.mark.asyncio
async def test_get_tree_filters_deleted(stateful_client):
    """Verify get_tree filters logically deleted tasks."""
    from src.server import archive_task, get_tree
    await archive_task("100", "2")
    result = await get_tree("100", depth=1)
    data = json.loads(result)
    assert "Setup API" not in data["data"]

@pytest.mark.asyncio
async def test_review_data_wrapping(stateful_client):
    """Verify get_review_data uses XML wrapping."""
    from src.server import get_review_data
    result = await get_review_data(timeframe="daily")
    data = json.loads(result)
    assert data["success"] is True
    assert "Review Stats (daily)" in data["message"]
    # Check if data contains list stats
    assert any(l["list"] == "Work" for l in data["data"])
