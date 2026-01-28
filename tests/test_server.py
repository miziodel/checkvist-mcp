import pytest
import os
from unittest.mock import MagicMock, patch, AsyncMock
from server import mcp
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
    
    with patch("server.get_client", return_value=mock_client):
        from server import list_checklists
        result = await list_checklists()
        assert "- List 1 (ID: 1)" in result

@pytest.mark.asyncio
async def test_get_list_content_resource():
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.get_tasks = AsyncMock(return_value=[{"id": 10, "content": "Task 1", "status": 0}])
    
    with patch("server.get_client", return_value=mock_client):
        from server import get_list_content
        result = await get_list_content("1")
        assert "- [ ] Task 1" in result

@pytest.mark.asyncio
async def test_add_task_tool():
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.add_task = AsyncMock(return_value={"id": 12, "content": "New Task"})
    
    with patch("server.get_client", return_value=mock_client):
        from server import add_task
        result = await add_task("1", "New Task")
        assert "Task added: New Task (ID: 12)" in result

@pytest.mark.asyncio
async def test_search_tasks_tool():
    mock_client = MagicMock()
    mock_client.token = "mock_token"
    mock_client.search_tasks = AsyncMock(return_value=[{"id": 10, "content": "Find me", "list_name": "L1", "list_id": 1}])
    
    with patch("server.get_client", return_value=mock_client):
        from server import search_tasks
        result = await search_tasks("Find")
        assert "- Find me [List: L1 (ID: 1), Task ID: 10]" in result
