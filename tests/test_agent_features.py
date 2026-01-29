import pytest
import os
from unittest.mock import MagicMock, patch, AsyncMock
from httpx import Response
import respx
from client import CheckvistClient
from server import triage_inbox, get_tree, resurface_ideas, move_task_tool

# --- Client Tests ---

@pytest.mark.asyncio
async def test_get_task_breadcrumbs():
    client = CheckvistClient(username="test", api_key="key")
    client.token = "token"
    
    # Mock data: Grandparent -> Parent -> Child
    tasks = [
        {"id": 1, "content": "Grandparent", "parent_id": None},
        {"id": 2, "content": "Parent", "parent_id": 1},
        {"id": 3, "content": "Child", "parent_id": 2},
    ]
    
    with respx.mock:
        respx.get("https://checkvist.com/checklists/100/tasks.json").mock(
            return_value=Response(200, json=tasks)
        )
        
        breadcrumbs = await client.get_task_breadcrumbs(100, 3)
        assert breadcrumbs == "Grandparent > Parent > Child"

@pytest.mark.asyncio
async def test_move_task():
    client = CheckvistClient(username="test", api_key="key")
    client.token = "token"
    
    with respx.mock:
        respx.put("https://checkvist.com/checklists/100/tasks/3.json").mock(
            return_value=Response(200, json={"id": 3, "parent_id": 99})
        )
        
        res = await client.move_task(100, 3, 99)
        assert res["parent_id"] == 99

# --- Server Tools Tests ---

@pytest.mark.asyncio
async def test_triage_inbox():
    mock_client = MagicMock()
    mock_client.token = "token"
    mock_client.get_checklists = AsyncMock(return_value=[{"id": 1, "name": "Inbox"}])
    mock_client.get_tasks = AsyncMock(return_value=[
        {"id": 10, "content": "Keep me", "status": 0},
        {"id": 11, "content": "Done task", "status": 1} # Should be ignored
    ])
    
    with patch("server.get_client", return_value=mock_client):
        result = await triage_inbox()
        assert "Keep me" in result
        assert "Done task" not in result

@pytest.mark.asyncio
async def test_get_tree_depth():
    mock_client = MagicMock()
    mock_client.token = "token"
    # Task 1 -> Task 2 -> Task 3
    tasks = [
        {"id": 1, "content": "Root", "parent_id": None, "status": 0},
        {"id": 2, "content": "Child", "parent_id": 1, "status": 0},
        {"id": 3, "content": "Grandchild", "parent_id": 2, "status": 0},
    ]
    mock_client.get_tasks = AsyncMock(return_value=tasks)
    
    with patch("server.get_client", return_value=mock_client):
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
async def test_resurface_ideas():
    mock_client = MagicMock()
    mock_client.token = "token"
    mock_client.get_checklists = AsyncMock(return_value=[{"id": 1, "name": "Old Ideas"}])
    mock_client.get_tasks = AsyncMock(return_value=[
        {"id": 10, "content": "Forgotten Idea", "status": 0}
    ])
    
    with patch("server.get_client", return_value=mock_client):
        with patch("random.shuffle"): # Deterministic
            result = await resurface_ideas()
            assert "Forgotten Idea" in result
