# Verification Guide: High-Level Agentic Workflows

To verify that the MCP server solves high-level cases (the "Vision Pillars"), we use three levels of testing:

## 1. Tool-Level Functional Tests
**File**: `tests/test_functional_mock.py`
**Goal**: Verify individual tool execution with mocked API responses.
**Mapping**: `TASK-*`, `DISC-*`.

## 2. Scenario-Level Orchestration Tests (New)
**File**: `tests/test_scenarios.py`
**Goal**: Verify that *complex* scenarios (`PROC-*`, `BULK-*`) correctly coordinate multiple actions. 
**Method**: We use a `StatefulMockClient` that remembers created tasks in memory during the test execution.

### Example: Verifying `PROC-001 (Inbox Zero)`
1.  **Setup**: Pre-populate a mock "Inbox" list with 5 tasks.
2.  **Act**: Call `triage_inbox()`.
3.  **Assert**: Check if the returned result suggests the correct task IDs for movement.
4.  **Act**: Call `move_task_tool()` for one of the IDs.
5.  **Assert**: Verify the mock state shows the task has changed its `list_id`.

## 3. End-to-End "Agent Interaction" (Client Simulation)
**File**: `tests/test_agent_smoke.py`
**Goal**: Verify how an LLM "sees" the tools.
**Method**: Use the `mcp` library client to connect to the server and inspect the JSON-RPC schema.
- Does `get_tree` provide enough indentation for the LLM to understand hierarchy?
- Does `resurface_ideas` provide enough context (list names, task content)?

---

## 🚀 How to implement these tests?

We will implement a `conftest.py` with a `StatefulMock` fixture:
```python
class CheckvistStatefulMock:
    def __init__(self):
        self.lists = [...]
        self.tasks = [...]
    
    async def add_task(self, list_id, content, ...):
        new_task = {"id": next_id(), "content": content, "list_id": list_id, ...}
        self.tasks.append(new_task)
        return new_task
```
This allows us to write tests like:
```python
async def test_scenario_bulk_import_then_search(stateful_client):
    await import_tasks(list_id=1, content="A\n  B")
    result = await search_tasks(query="B")
    assert "B" in result
```
