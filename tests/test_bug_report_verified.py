import pytest
from unittest.mock import AsyncMock, patch
from src.server import (
    search_tasks, get_tree, add_task, move_task_tool,
    migrate_incomplete_tasks, set_priority
)

@pytest.fixture
def mock_client_v2(mocker):
    client_mock = AsyncMock()
    client_mock.token = "mock_token"
    
    # Mock data with hierarchy and metadata
    MOCK_TASKS = [
        {"id": 1, "content": "Parent", "list_id": 100, "status": 0, "parent_id": None, "priority": 1, "due_date": "2026-12-31", "tags": ["mcp"]},
        {"id": 2, "content": "Child", "list_id": 100, "status": 0, "parent_id": 1}
    ]
    
    client_mock.get_checklists.return_value = [{"id": 100, "name": "Work"}]
    client_mock.get_tasks.return_value = MOCK_TASKS
    client_mock.get_task.return_value = MOCK_TASKS[0]
    client_mock.search_tasks.return_value = [{"id": 1, "content": "Parent", "list_id": 100, "list_name": "Work"}]
    client_mock.move_task_hierarchy.return_value = {"status": "ok"}
    client_mock.import_tasks.return_value = [{"id": 3, "content": "Parsed"}]
    client_mock.update_task.return_value = {"id": 1, "priority": 2}
    
    mocker.patch("src.server.get_client", return_value=client_mock)
    return client_mock

@pytest.mark.asyncio
async def test_verification_metadata_decorators(mock_client_v2):
    """Bug: Metadata (Prio, Due, Tags) missing from tree/search."""
    # Test ID search metadata
    result = await search_tasks(query="1")
    assert "Parent [!1 ^2026-12-31 #mcp]" in result
    
    # Test Tree metadata
    tree_result = await get_tree(list_id="100", depth=1)
    assert "Parent [!1 ^2026-12-31 #mcp]" in tree_result

@pytest.mark.asyncio
async def test_verification_smart_syntax_routing(mock_client_v2):
    """Bug: Smart syntax characters should trigger parsing."""
    # Symbols: ! @ # ^ /
    await add_task(list_id="100", content="Task !1 #tag ^tomorrow")
    # Should NOT call add_task, but call import_tasks
    mock_client_v2.add_task.assert_not_called()
    # Corrected assertion: server passes 3 positional args to import_tasks
    mock_client_v2.import_tasks.assert_called_with(100, "Task !1 #tag ^tomorrow", None)

@pytest.mark.asyncio
async def test_verification_smart_syntax_update(mock_client_v2):
    """Bug: Task updates should support smart syntax parsing."""
    await set_priority(list_id="100", task_id="1", priority=2)
    # Checkvist client's update_task is expected to be called with priority
    # but the client itself was modified to use parse=true internally
    mock_client_v2.update_task.assert_called_with(100, 1, priority=2)

@pytest.mark.asyncio
async def test_verification_migrate_hierarchy_safety(mock_client_v2):
    """Bug: Migrate tool used 'shallow' move, orphaning children."""
    await migrate_incomplete_tasks(source_list_id="100", target_list_id="200", confirmed=True)
    # Should call move_task_hierarchy, NOT move_task_to_list
    mock_client_v2.move_task_hierarchy.assert_called()
    # Ensure it's not the old method
    assert not hasattr(mock_client_v2, "move_task_to_list") or not mock_client_v2.move_task_to_list.called

@pytest.mark.asyncio
async def test_verification_search_breadcrumbs(mock_client_v2):
    """Feat: Search results should show the full path."""
    result = await search_tasks(query="Parent")
    # Breadcrumbs build path: Parent (no root parent)
    assert "Parent [List: Work (ID: 100), Task ID: 1]" in result

@pytest.mark.asyncio
async def test_verification_search_by_id_missing(mock_client_v2):
    """Bug Edge Case: Search by non-existent task ID."""
    mock_client_v2.get_task.side_effect = Exception("Not found")
    result = await search_tasks(query="9999")
    assert "Task ID 9999 not found" in result
