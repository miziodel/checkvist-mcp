import pytest
import os
import time
import json
from unittest.mock import MagicMock, patch, AsyncMock
from src.server import mcp, ARCHIVE_TAG
from src.client import CheckvistClient
from src.response import StandardResponse
import asyncio
from src.syntax import SyntaxParser
from src.models import Task, Checklist

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
        error_code="E004",
        action="test_action",
        strategy="Try again",
        error_details="Detailed error"
    )
    resp = json.loads(resp_str)
    assert resp["success"] is False
    assert resp["error_code"] == "E004"
    assert resp["message"] == "Failed"
    assert resp["action"] == "test_action"
    assert resp["suggestion"] == "Try again"
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
    mock_client.get_checklists.return_value = [Checklist(id=1, name="List 1")]
    
    with patch("src.server.get_client", return_value=mock_client):
        from src.server import list_checklists
        result = await list_checklists()
        assert "- List 1 (ID: 1)" in result

@pytest.mark.asyncio
async def test_get_list_content_resource():
    mock_client = AsyncMock(spec=CheckvistClient)
    mock_client.token = "mock_token"
    task = Task(id=10, content="Task 1", status=0, parent_id=None)
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

# --- SYNTAX PARSER TESTS ---

def test_syntax_extract_tags():
    parser = SyntaxParser()
    text = "Task with #tag1 and #tag2"
    clean, tags = parser.extract_tags(text)
    assert clean == "Task with and"
    assert "tag1" in tags
    assert "tag2" in tags

def test_syntax_extract_priority():
    parser = SyntaxParser()
    assert parser.extract_priority("Urgent !1") == ("Urgent", 1)
    assert parser.extract_priority("Normal !2") == ("Normal", 2)
    assert parser.extract_priority("Low !3") == ("Low", 3)
    assert parser.extract_priority("None") == ("None", 0)

def test_syntax_extract_due_date():
    parser = SyntaxParser()
    assert parser.extract_due_date("Do it ^tomorrow") == ("Do it", "tomorrow")
    assert parser.extract_due_date("Fixed ^2024-12-31") == ("Fixed", "2024-12-31")

def test_syntax_extract_user():
    parser = SyntaxParser()
    assert parser.extract_user("Ask @mizio") == ("Ask", "mizio")

def test_syntax_full_parse():
    parser = SyntaxParser()
    content = "Meeting @boss #work !1 ^today"
    result = parser.parse(content)
    assert result.content == "Meeting"
    assert result.priority == 1
    assert "work" in result.tags
    assert result.user == "boss"
    assert result.due == "today"

def test_syntax_has_symbols():
    parser = SyntaxParser()
    assert parser.has_symbols("Simple task") is False
    assert parser.has_symbols("Task #tag") is True
    assert parser.has_symbols("Task !1") is True
    assert parser.has_symbols("Task @user") is True
    assert parser.has_symbols("Task ^date") is True
    assert parser.has_symbols("Task !!1") is True

def test_context_guard_list_truncation():
    """Verify that CheckvistService._truncate_list truncates flat lists."""
    from src.service import CheckvistService
    service = CheckvistService(None)
    large_list = [{"id": i} for i in range(150)]
    truncated = service._truncate_list(large_list, limit=100)
    assert len(truncated) == 100
    assert truncated[0]["id"] == 0
    assert truncated[99]["id"] == 99

def test_context_guard_tree_truncation():
    """Verify that CheckvistService._truncate_list truncates deep structures (roots)."""
    from src.service import CheckvistService
    service = CheckvistService(None)
    large_tree = [{"data": {"id": i}, "children": []} for i in range(70)]
    truncated = service._truncate_list(large_tree, limit=50)
    assert len(truncated) == 50
    assert truncated[0]["data"]["id"] == 0
    assert truncated[49]["data"]["id"] == 49

def test_secret_masker_filter():
    """Verify that sensitive keys are masked in log records."""
    from src.logging_util import SecretMasker
    import logging
    
    masker = SecretMasker()
    
    # Test remote_key masking
    msg1 = "Authenticating with remote_key=SECRET_KEY&version=2"
    record1 = logging.LogRecord("test", logging.INFO, "path", 10, msg1, None, None)
    masker.filter(record1)
    assert "remote_key=[MASKED]" in record1.msg
    assert "SECRET_KEY" not in record1.msg
    
    # Test X-Client-Token masking (JSON-like)
    msg2 = "Headers: {'X-Client-Token': 'TOKEN_123'}"
    record2 = logging.LogRecord("test", logging.INFO, "path", 10, msg2, None, None)
    masker.filter(record2)
    assert "[MASKED]" in record2.msg
    assert "TOKEN_123" not in record2.msg
    assert "X-Client-Token" in record2.msg
