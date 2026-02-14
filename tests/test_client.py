import pytest
import respx
import httpx
from httpx import Response
from src.client import CheckvistClient
from src.exceptions import CheckvistAuthError
from src.models import Task, Checklist
from unittest.mock import MagicMock

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
        
        with pytest.raises(CheckvistAuthError):
            await client.authenticate()
        
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
        assert isinstance(checklists[0], Checklist)
        assert checklists[0].name == "List 1"
        assert checklists[1].id == 2

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
        assert isinstance(tasks[0], Task)
        assert tasks[0].content == "Task 1"

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
        
        assert isinstance(task, Task)
        assert task.id == 12
        assert task.content == "New Task"

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
        
        assert task.content == "Updated Task"

@pytest.mark.asyncio
async def test_close_task_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        respx.post("https://checkvist.com/checklists/1/tasks/12/close.json").mock(
            return_value=Response(200, json={"id": 12, "status": 1, "content": "Task 12"})
        )
        
        task = await client.close_task(1, 12)
        
        assert task.status == 1

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
        assert results[0].content == "Find me"

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
    
        assert checklist.id == 500
        assert checklist.name == "New Project"

@pytest.mark.asyncio
async def test_safe_json_204():
    client = CheckvistClient("user", "key")
    response = MagicMock(spec=httpx.Response)
    response.status_code = 204
    response.content = b""
    
    result = await client._parse_checkvist_response(response)
    assert result == {}

@pytest.mark.asyncio
async def test_safe_json_empty_body():
    client = CheckvistClient("user", "key")
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.content = b"  "
    
    result = await client._parse_checkvist_response(response)
    assert result == {}

@pytest.mark.asyncio
async def test_safe_json_valid_body():
    client = CheckvistClient("user", "key")
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.content = b'{"id": 123, "content": "test"}'
    response.json.return_value = {"id": 123, "content": "test"}
    
    result = await client._parse_checkvist_response(response)
    assert result == {"id": 123, "content": "test"}

@pytest.mark.asyncio
async def test_safe_json_invalid_json():
    client = CheckvistClient("user", "key")
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.content = b'invalid json'
    response.text = 'invalid json'
    response.json.side_effect = Exception("Parsing error")
    
    result = await client._parse_checkvist_response(response)
    assert result["status"] == "ok"
    assert "Success" in result["message"]
    assert result["text"] == 'invalid json'

@pytest.mark.asyncio
async def test_rename_checklist_success():
    client = CheckvistClient(username="test@example.com", api_key="fake_api_key")
    client.token = "mock_token_123"
    client.client.headers["X-Client-Token"] = "mock_token_123"
    
    with respx.mock:
        respx.put("https://checkvist.com/checklists/1.json").mock(
            return_value=Response(200, json={"id": 1, "name": "Renamed List"})
        )
        
        checklist = await client.rename_checklist(1, "Renamed List")
    
        assert checklist.id == 1
        assert checklist.name == "Renamed List"

@pytest.mark.asyncio
async def test_get_task_breadcrumbs():
    client = CheckvistClient(username="test", api_key="key")
    client.token = "token"
    # Parent -> Child
    tasks = [
        {"id": 1, "content": "Parent", "parent_id": None},
        {"id": 2, "content": "Child", "parent_id": 1},
    ]
    with respx.mock:
        respx.get("https://checkvist.com/checklists/100/tasks.json").mock(
            return_value=Response(200, json=tasks)
        )
        breadcrumbs = await client.get_task_breadcrumbs(100, 2)
        assert breadcrumbs == "Parent > Child"

@pytest.mark.asyncio
async def test_move_task_hierarchy_success():
    client = CheckvistClient(username="test", api_key="key")
    client.token = "token"
    with respx.mock:
        # Checkvist uses /paste endpoint for hierarchy moves
        respx.post(url__regex=r"https://checkvist.com/checklists/100/tasks/2/paste.*").mock(
            return_value=Response(200, json={"status": "ok"})
        )
        res = await client.move_task_hierarchy(100, 2, 200)
        assert res["status"] == "ok"

@pytest.mark.asyncio
async def test_search_global_success():
    client = CheckvistClient(username="test", api_key="key")
    client.token = "token"
    with respx.mock:
        respx.get(url__regex=r"https://checkvist.com/search/everywhere.json.*").mock(
            return_value=Response(200, json=[{"id": 101, "content": "Global Result"}])
        )
        
        results = await client.search_global("Global")
        assert len(results) == 1
        assert results[0].content == "Global Result"

@pytest.mark.asyncio
async def test_bulk_tag_tasks_success():
    client = CheckvistClient(username="test", api_key="key")
    client.token = "token"
    with respx.mock:
        # Checkvist bulk tagging uses the first task_id in the URL
        respx.post(url__regex=r"https://checkvist.com/checklists/100/tasks/101/tags.js.*").mock(
            return_value=Response(200, text="ok")
        )
        res = await client.bulk_tag_tasks(100, [101, 102], "tag1,tag2")
        assert res["status"] == "ok"

@pytest.mark.asyncio
async def test_bulk_move_tasks_success():
    client = CheckvistClient(username="test", api_key="key")
    client.token = "token"
    with respx.mock:
        respx.post("https://checkvist.com/checklists/100/tasks/move.json").mock(
            return_value=Response(200, json={"status": "ok"})
        )
        res = await client.bulk_move_tasks(100, [101, 102], 200)
        assert res["status"] == "ok"

@pytest.mark.asyncio
async def test_set_task_styling_success():
    client = CheckvistClient(username="test", api_key="key")
    client.token = "token"
    with respx.mock:
        respx.post("https://checkvist.com/details").mock(
            return_value=Response(200, json={"status": "ok"})
        )
        res = await client.set_task_styling(100, 101, mark="fg1")
        assert res["status"] == "ok"
