import pytest
import respx
from httpx import Response
from src.client import CheckvistClient

@pytest.mark.asyncio
async def test_authenticate_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    
    with respx.mock:
        # Mock the login call with regex to handle query parameters flexibly
        respx.post(url__regex=r"https://checkvist.com/auth/login.json.*").mock(
            return_value=Response(200, text='"mock_token_123"')
        )
        
        success = await client.authenticate()
        
        assert success is True
        assert client.token == "mock_token_123"
        assert client.client.headers["X-Client-Token"] == "mock_token_123"

@pytest.mark.asyncio
async def test_authenticate_failure():
    client = CheckvistClient(username="test@example.com", api_key="wrong_api_key")
    
    with respx.mock:
        # Mock failed login
        respx.post("https://checkvist.com/auth/login.json").mock(
            return_value=Response(401)
        )
        
        success = await client.authenticate()
        
        assert success is False
        assert client.token is None

@pytest.mark.asyncio
async def test_get_checklists_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        respx.get("https://checkvist.com/checklists.json").mock(
            return_value=Response(200, json=[{"id": 1, "name": "List 1"}, {"id": 2, "name": "List 2"}])
        )
        
        checklists = await client.get_checklists()
        
        assert len(checklists) == 2
        assert checklists[0]["name"] == "List 1"
        assert checklists[1]["id"] == 2

@pytest.mark.asyncio
async def test_get_tasks_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        respx.get("https://checkvist.com/checklists/1/tasks.json").mock(
            return_value=Response(200, json=[{"id": 10, "content": "Task 1"}, {"id": 11, "content": "Task 2"}])
        )
        
        tasks = await client.get_tasks(1)
        
        assert len(tasks) == 2
        assert tasks[0]["content"] == "Task 1"

@pytest.mark.asyncio
async def test_add_task_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        respx.post("https://checkvist.com/checklists/1/tasks.json").mock(
            return_value=Response(201, json={"id": 12, "content": "New Task"})
        )
        
        task = await client.add_task(1, "New Task")
        
        assert task["id"] == 12
        assert task["content"] == "New Task"

@pytest.mark.asyncio
async def test_update_task_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        respx.put("https://checkvist.com/checklists/1/tasks/12.json").mock(
            return_value=Response(200, json={"id": 12, "content": "Updated Task"})
        )
        
        task = await client.update_task(1, 12, content="Updated Task")
        
        assert task["content"] == "Updated Task"

@pytest.mark.asyncio
async def test_close_task_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        respx.post("https://checkvist.com/checklists/1/tasks/12/close.json").mock(
            return_value=Response(200, json={"id": 12, "status": 1})
        )
        
        task = await client.close_task(1, 12)
        
        assert task["status"] == 1

@pytest.mark.asyncio
async def test_search_tasks_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        # Mock getting lists
        respx.get("https://checkvist.com/checklists.json").mock(
            return_value=Response(200, json=[{"id": 1, "name": "List 1"}])
        )
        # Mock getting tasks for List 1
        respx.get("https://checkvist.com/checklists/1/tasks.json").mock(
            return_value=Response(200, json=[{"id": 10, "content": "Find me"}, {"id": 11, "content": "Ignore me"}])
        )
        
        results = await client.search_tasks("Find")
        
        assert len(results) == 1
        assert results[0]["content"] == "Find me"

@pytest.mark.asyncio
async def test_create_checklist_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        respx.post("https://checkvist.com/checklists.json").mock(
            return_value=Response(201, json={"id": 500, "name": "New Project"})
        )
        
        checklist = await client.create_checklist("New Project")
        
        assert checklist["id"] == 500
        assert checklist["name"] == "New Project"
