import pytest
from unittest.mock import MagicMock, AsyncMock
import httpx
from src.client import CheckvistClient
from src.exceptions import (
    CheckvistAuthError,
    CheckvistAPIError,
    CheckvistRateLimitError,
    CheckvistResourceNotFoundError,
    CheckvistConnectionError
)

@pytest.fixture
def client():
    # We won't actually connect
    return CheckvistClient("dummy_user", "dummy_key")

@pytest.mark.asyncio
async def test_auth_failure_raises_custom_exception(client):
    """Verify 401/403 during auth raises CheckvistAuthError"""
    # Setup mock
    mock_post = AsyncMock()
    mock_post.return_value = MagicMock(status_code=401)
    client.client.post = mock_post

    # Expectation: CheckvistAuthError
    # Note: Requires src.exceptions to exist to pass this `raises` check
    with pytest.raises(CheckvistAuthError):
        await client.authenticate()

@pytest.mark.asyncio
async def test_resource_not_found_raises_exception(client):
    """Verify 404 raises CheckvistResourceNotFoundError"""
    # Mock a request that fails
    mock_request = AsyncMock()
    mock_resp = MagicMock(status_code=404)
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("404 Not Found", request=None, response=mock_resp)
    mock_request.return_value = mock_resp
    client.client.request = mock_request

    # We test on get_tasks as an example tool method
    with pytest.raises(CheckvistResourceNotFoundError):
        await client.get_tasks(123)

@pytest.mark.asyncio
async def test_rate_limit_raises_exception(client):
    """Verify 429 raises CheckvistRateLimitError"""
    mock_request = AsyncMock()
    mock_resp = MagicMock(status_code=429)
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("429 Too Many Requests", request=None, response=mock_resp)
    mock_request.return_value = mock_resp
    client.client.request = mock_request

    with pytest.raises(CheckvistRateLimitError):
        await client.get_tasks(123)

@pytest.mark.asyncio
async def test_server_error_raises_api_exception(client):
    """Verify 500 raises CheckvistAPIError"""
    mock_request = AsyncMock()
    mock_resp = MagicMock(status_code=500)
    mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError("500 Server Error", request=None, response=mock_resp)
    mock_request.return_value = mock_resp
    client.client.request = mock_request

    with pytest.raises(CheckvistAPIError) as exc_info:
        await client.get_tasks(123)
    
    assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_connection_error_handling(client):
    """Verify httpx.ConnectError is wrapped in CheckvistConnectionError"""
    client.client.request = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
    
    with pytest.raises(CheckvistConnectionError):
        await client.get_tasks(123)
@pytest.mark.asyncio
async def test_soft_error_200_raises_exception(client):
    """Verify that 200 OK with {"error": "..."} raises CheckvistAPIError"""
    mock_request = AsyncMock()
    mock_resp = MagicMock(status_code=200)
    # Simulate the "Soft Error" payload
    mock_resp.json.return_value = {"error": "Forbidden", "message": "You don't have access"}
    mock_resp.content = b'{"error": "Forbidden", "message": "You don\'t have access"}'
    mock_request.return_value = mock_resp
    client.client.request = mock_request

    # Currently _handle_request detects "Forbidden" in 200 OK and raises CheckvistAuthError
    with pytest.raises(CheckvistAuthError) as excinfo:
        await client.get_tasks(123)
    
    assert "Forbidden" in str(excinfo.value)
