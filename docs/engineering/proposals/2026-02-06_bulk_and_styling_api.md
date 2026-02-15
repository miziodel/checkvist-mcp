# Proposal: Bulk Operations, Advanced Styling & Global Search (v1.0)

**Date**: 2026-02-06
**Status**: PROPOSED
**Source**: API Forensics Session (UI/UX Exploration)

## 1. Context & Motivation

During the forensic exploration of the Checkvist UI, we discovered several high-performance, undocumented endpoints that power the web interface. These endpoints offer capabilities significantly superior to the current iterative approaches used by the MCP server, particularly for batch operations and search.

Implementing these would move the MCP server from "Basic Wrapper" to "Power User Tool", allowing for operations like "Move these 50 tasks to Archive" in a single API call rather than 50 sequential ones.

## 2. Discovered Capabilities

### 2.1 Native Bulk Operations
Currently, the MCP performs bulk actions by iterating through tasks one by one. The UI uses specific bulk endpoints:

*   **Bulk Tagging**: `/checklists/{id}/tasks/{task_id}/tags.js` accepts a comma-separated string of `task_ids`.
*   **Bulk Moving/Reparenting**: `/checklists/{id}/tasks/move.json` accepts an array `task_ids[]` and supports cross-list moves + re-parenting in one go.

### 2.2 Advanced Styling (Priority)
The "Color" of a task in Checkvist is actually its **Priority**.
*   **Endpoint**: `/details` with `details[mark]` parameter.
*   **Mapping**:
    *   `fg1`: Red (Highest)
    *   `fg2`: Orange
    *   `fg3`: Green
    *   ...
    *   `fg9`: Neutral/Grey

### 2.3 Global Search Strategy
The UI uses `/search/everywhere.json?what={query}`.
*   **Current MCP**: Iterates through ALL playlists (slow, heavy on tokens/requests).
*   **Proposed**: Use this single endpoint to get instant, prioritized results from the entire account.

## 3. Proposed Tool Implementations

### `bulk_tag_tasks`
```python
def bulk_tag_tasks(list_id: int, task_ids: List[int], tags: List[str]):
    """ 
    Apply tags to multiple tasks in a single atomic transaction.
    Performance: O(1) request vs O(N).
    """
```

### `bulk_move_tasks`
```python
def bulk_move_tasks(source_list_id: int, task_ids: List[int], target_list_id: int, target_parent_id: int = None):
    """
    Move multiple tasks to a new list/parent.
    Handles the complex logic of "Paste vs Reparent" internally.
    """
```

### `set_task_styling`
```python
def set_task_styling(list_id: int, task_id: int, color: str = None, bold: bool = None):
    """
    Set visual attributes.
    color: "red", "orange", "green", "neutral" (Mapped to fg1-fg9)
    bold: Toggle bold markdown (**text**)
    """
```

### `search_global` (Replacer for `search_tasks`)
```python
def search_global(query: str):
    """
    Instant global search using Chcekvist's native index.
    """
```

## 4. Integration Roadmap (Draft)

1.  **Phase 1 (Low Hanging Fruit)**: Implement `search_global` to replace the heavy iteration logic.
2.  **Phase 2 (Power Tools)**: Implement `bulk_*` operations when the "Triage Inbox" workflow is refined.
3.  **Phase 3 (Aesthetics)**: Add `set_task_styling` for the "Productivity Architect" persona to use in organizing dashboards.
