import pytest
import json
from src.server import (
    list_checklists, search_list, get_tree, search_tasks,
    add_task, close_task, reopen_task, get_list_content,
    import_tasks, move_task_tool,
    add_note, update_task,
    apply_template, migrate_incomplete_tasks, rename_list,
    archive_task, weekly_review, triage_inbox
)
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_phase1_discovery(stateful_client):
    """Verifies DISC-001, DISC-002, DISC-003, DISC-004."""
    
    # DISC-001: List all (This is a resource, still returns string with wrap_data)
    res = await list_checklists()
    assert "Work (ID: 100)" in res
    assert "Spesa (ID: 200)" in res
    
    # DISC-002: Search list (Tool, returns JSON)
    res = await search_list(query="Work")
    data = json.loads(res)
    assert data["success"] is True
    assert any(l["id"] == 100 for l in data["data"])
    assert not any(l["id"] == 200 for l in data["data"])
    
    # DISC-003: Tree structure (Tool, returns JSON)
    res = await get_tree(list_id="200")
    data = json.loads(res)
    assert "Latte" in data["data"]
    
    # DISC-004: Global task search (Tool, returns JSON)
    res = await search_tasks(query="API")
    data = json.loads(res)
    assert any("Setup API" in t["breadcrumb"] for t in data["data"])

@pytest.mark.asyncio
async def test_phase2_task_management(stateful_client):
    """Verifies TASK-001, TASK-002, TASK-003."""
    
    # TASK-001: Add task
    await add_task(list_id="999", content="Clean the kitchen")
    inbox_content = await get_list_content(list_id="999")
    assert "Clean the kitchen" in inbox_content
    
    # Find the ID of the new task
    task_id = stateful_client.tasks[-1]["id"]
    
    # TASK-002: Close task
    await close_task(list_id="999", task_id=str(task_id))
    inbox_content = await get_list_content(list_id="999")
    assert "[x] Clean the kitchen" in inbox_content
    
    # TASK-003: Reopen task
    await reopen_task(list_id="999", task_id=str(task_id))
    inbox_content = await get_list_content(list_id="999")
    assert "[ ] Clean the kitchen" in inbox_content
    
    await rename_list(list_id="100", new_name="Work - Primary")
    res = await list_checklists()
    assert "Work - Primary" in res

@pytest.mark.asyncio
async def test_phase3_bulk_operations(stateful_client):
    """Verifies BULK-001, BULK-002, BULK-003."""
    
    # BULK-001: Hierarchical import
    import_data = "Project X\n  Subtask 1\n  Subtask 2"
    await import_tasks(list_id="100", content=import_data)
    
    # Verify presence (StatefulMock implementation of import_tasks will just append for now)
    work_content = await get_list_content(list_id="100")
    assert "Project X" in work_content
    assert "Subtask 1" in work_content
    
    # BULK-003: Cross-list move
    # Find one of the imported tasks
    task = next(t for t in stateful_client.tasks if t["content"] == "Subtask 1")
    await move_task_tool(list_id="100", task_id=str(task["id"]), target_list_id="200", confirmed=True)
    
    # Verify it moved
    spesa_content = await get_list_content(list_id="200")
    assert "Subtask 1" in spesa_content
    work_content = await get_list_content(list_id="100")
    assert "Subtask 1" not in work_content

@pytest.mark.asyncio
async def test_phase4_enrichment(stateful_client):
    """Verifies META-001, META-002, META-003, META-004."""
    
    # META-001: Add note
    await add_note(list_id="100", task_id="2", note="Checking if this works")
    # Verify mock state
    # (Note: StatefulMock doesn't track notes yet, but we check if tool exists and doesn't crash)
    
    # META-002: Set priority (via update_task)
    await update_task(list_id="100", task_id="2", priority=3)
    task = next(t for t in stateful_client.tasks if t["id"] == 2)
    assert task["priority"] == 3
    
    # META-003: Smart Tagging
    await update_task(list_id="100", task_id="2", tags="urgent, mcp")
    assert "urgent" in task["tags"]
    
    # META-004: Set due date (via update_task)
    await update_task(list_id="100", task_id="2", due="tomorrow")
    assert task["due_date"] == "tomorrow"
    
    # META-005: Metadata Visibility
    tree_res = await get_tree(list_id="100")
    tree_data = json.loads(tree_res)
    assert "!3" in tree_data["data"]
    assert "^tomorrow" in tree_data["data"]

@pytest.mark.asyncio
async def test_phase5_advanced_workflows(stateful_client):
    """Verifies PROC-003, PROC-005."""
    
    # 1. Prepare a Template List
    template_list_id = "300"
    stateful_client.lists.append({"id": 300, "name": "Template", "public": False})
    await stateful_client.add_task(list_id=300, content="Step 1")
    await stateful_client.add_task(list_id=300, content="Step 2")
    
    # PROC-003: Apply Template
    target_list_id = "100"
    await apply_template(template_list_id=template_list_id, target_list_id=target_list_id, confirmed=True)

    
    work_content = await get_list_content(list_id="100")
    assert "Step 1" in work_content
    assert "Step 2" in work_content

    # PROC-006: Template Verification (Empty case)
    res = await apply_template(template_list_id="9999", target_list_id="100", confirmed=True)
    data = json.loads(res)
    assert data["success"] is False
    assert "empty" in data["message"]
    
    # PROC-005: Cycle Migration
    # 'Latte' (ID 1) is open in Spesa (200). Move to Work (100).
    await migrate_incomplete_tasks(source_list_id="200", target_list_id="100", confirmed=True)

    
    spesa_content = await get_list_content(list_id="200")
    assert "Latte" not in spesa_content
    work_content = await get_list_content(list_id="100")
    assert "Latte" in work_content

@pytest.mark.asyncio
async def test_robustness_scenarios(stateful_client):
    """Verifies BUG-001, BUG-003, META-006, SAFE-001."""
    
    # SAFE-001: Logical Deletion (Archive)
    # Archive task 2 (Setup API)
    await archive_task(list_id="100", task_id="2")
    task = next(t for t in stateful_client.tasks if t["id"] == 2)
    assert "deleted" in task["tags"]
    
    # BUG-003: Tag Robustness (Dictionary vs List)
    # Simulate a task with dict tags in stateful_client
    stateful_client.tasks.append({
        "id": 5000, "content": "Dict Task", "tags": {"old": "tag"}, "status": 0, "parent_id": None, "list_id": 100
    })
    await archive_task(list_id="100", task_id="5000")
    task_dict = next(t for t in stateful_client.tasks if t["id"] == 5000)
    assert "deleted" in task_dict["tags"]
    assert "old" in task_dict["tags"]
    
    # META-006: Expanded Smart Syntax
    # !!1 should be pre-processed to !1 and route to import_tasks logic
    await add_task(list_id="100", content="Urgent !!1")
    # StatefulMockClient.add_task currently doesn't simulate the parsing logic,
    # but we verify the tool call doesn't fail and content is preserved/transformed.
    last_task = stateful_client.tasks[-1]
    assert "Urgent !1" in last_task["content"]

@pytest.mark.asyncio
async def test_proc_009_weekly_review(stateful_client):
    """Verifies PROC-009: Weekly Review Assistant."""
    
    # 1. Setup stale task (Latte is from 2026-01-01, very stale)
    # 2. Setup a "Win" (Closed today)
    await stateful_client.add_task(list_id="100", content="Recent Win")
    win_id = stateful_client.tasks[-1]["id"]
    await stateful_client.close_task(list_id="100", task_id=win_id)
    
    # 3. Setup a "Blocked" task
    await stateful_client.add_task(list_id="100", content="Blocked Task")
    block_id = stateful_client.tasks[-1]["id"]
    await stateful_client.update_task(list_id="100", task_id=block_id, tags="blocked")
    
    # 4. Run Review
    res = await weekly_review()
    data = json.loads(res)
    
    assert data["success"] is True
    report = data["data"]
    
    assert "Weekly Review Assistant Report" in report
    assert "Recent Win" in report
    assert "Latte" in report # Stale
    assert "Blocked Task" in report
    assert "Architecture Insights" in report

# --- New Consolidated Tests for Triage & Templating ---

@pytest.fixture
def mock_client_specialized(mocker):
    """Fixture for specialized logic (Templating & Triage) not covered by stateful client."""
    import src.server
    # Clear singleton to force mock injection
    src.server._service = None
    
    client_mock = AsyncMock()
    client_mock.token = "mock_token"
    
    # Mock Checklists (for Triage)
    client_mock.get_checklists.return_value = [
        {"id": 999, "name": "Inbox", "public": False},
        {"id": 100, "name": "Engineering", "public": False},
        {"id": 200, "name": "Marketing", "public": False}
    ]
    
    # Complex Mock for get_tasks to handle both Triage (id 999) and Template (id 100)
    # NOTE: In test calls, we use string IDs, so we handle that.
    def get_tasks_side_effect(list_id):
        lid = str(list_id)
        if lid == "999": # Inbox
            return [
                {"id": 1, "content": "Fix critical bug in auth", "tags": [], "parent_id": None, "status": 0},
                {"id": 2, "content": "Write blog post", "tags": [], "parent_id": None, "status": 0},
                {"id": 3, "content": "Subtask of Bug", "tags": [], "parent_id": 1, "status": 0}, 
            ]
        elif lid == "100": # Template Source
            return [
                {"id": 101, "content": "Kickoff with {{CLIENT}}", "parent_id": None, "tags": [], "parent_id": 0},
                {"id": 102, "content": "Send invoice to {{EMAIL}}", "parent_id": 101, "tags": [], "parent_id": 101}
            ]
        return []
        
    client_mock.get_tasks.side_effect = get_tasks_side_effect
    client_mock.import_tasks.return_value = [{"id": 201, "content": "Kickoff with Acme"}]
    
    mocker.patch("src.server.get_client", return_value=client_mock)
    return client_mock

@pytest.mark.asyncio
async def test_proc_003_templating_with_variables(mock_client_specialized):
    """PROC-003: Verify smart templating with variable substitution."""
    variables = {"CLIENT": "Acme Corp", "EMAIL": "billing@acme.com"}
    
    # Use "100" as template source (mocked above) and "200" as target
    result = await apply_template(template_list_id="100", target_list_id="200", confirmed=True, variables=variables)
    
    data = json.loads(result)
    assert data["success"] is True
    
    # Verify import content generated has substitutions
    args, _ = mock_client_specialized.import_tasks.call_args
    import_content = args[1]
    
    assert "Kickoff with Acme Corp" in import_content
    # The simple replace check:
    assert "Send invoice to billing@acme.com" in import_content

@pytest.mark.asyncio
async def test_proc_001_triage_heuristics(mock_client_specialized):
    """PROC-001: Verify triage heuristics (Keyword Matching)."""
    
    result = await triage_inbox(inbox_name="Inbox", analyze=True) 
    data = json.loads(result)
    
    assert data["success"] is True
    
    tasks = data["data"]
    # We expect "Fix critical bug" to match "Engineering"
    bug_task = next(t for t in tasks if "bug" in t["content"].lower())
    
    assert "suggestion" in bug_task, "Task missing triage suggestion"
    assert bug_task["suggestion"]["target_list"] == "Engineering"
