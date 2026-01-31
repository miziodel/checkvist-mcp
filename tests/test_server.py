import pytest
import os
import time
from unittest.mock import MagicMock, patch, AsyncMock
from src.server import mcp, ARCHIVE_TAG
from src.client import CheckvistClient
import asyncio


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
    assert "Setup API" not in result

@pytest.mark.asyncio
async def test_review_data_wrapping(stateful_client):
    """Verify get_review_data uses XML wrapping."""
    from src.server import get_review_data
    result = await get_review_data(timeframe="daily")
    assert "<user_data>" in result
    assert "Review Report (daily)" in result
