# Specification: Context & Search Engine (Operative Intelligence)

**Status**: ACTIVE
**Priority**: CRITICAL
**Driver**: User Feedback (Contextual/Hierarchical Blindness)

## 1. Problem Statement

Previously, the agent suffered from:
- **Blindness**: Inability to see Notes/Comments without full-tree fetches.
- **Lost Context**: Search results lacked parent hierarchy (Breadcrumbs).
- **High Cognitive Load**: Processing 50+ blind results was expensive.

## 2. Solution: Operative Intelligence Framework

We implemented a "Map & Zoom" architecture.

### Tool 1: `search_tasks(query)` (The Map)

**Goal**: "High-Resolution Triage".
**Behavior**:
- **Metadata Indicators**: Uses compact codes to signal task volume:
    - `[N]`: Task has Notes.
    - `[C]`: Task has Comments.
    - `[F: n]`: Task has `n` subtasks.
- **Breadcrumbs**: Returns the full parent chain (e.g., `Top Level > Middle > Leaf`).
- **Precision**: Limited to **10 results** for maximum token focus.

**Indicators Usage**: The agent should look for `[N]` or `[C]` to decide if a deep-dive via `get_task` is required.

### Tool 2: `get_task(list_id, task_id)` (The Zoom)

**Goal**: "Surgical Depth".
**Behavior**:
- Fetches **full metadata**: Content, Notes, Comments, and Breadcrumbs.
- **Branch Exploration**: Supports `include_children=True` with a recursion `depth` (default 2).
- **Success Case**: Used after a search to read the "technical specs" contained in task notes.

## 3. Implementation Details

- **Efficient Fetching**: Uses a single API call per list to build the local hierarchy map, preventing N+1 overhead.
- **TTL Caching**: Caches list metadata for 15s to speed up breadcrumb resolution across multiple searches.
- **Standardized formatting**: Breadcrumbs use the format `Grandparent > Parent > Task`.

## 4. Agentic Protocol

1.  **Search First**: Use `search_tasks` to get a high-level map.
2.  **Evaluate Indicators**: Observe `[N]`, `[C]`, and `[F: n]`.
3.  **Drill Down**: If `[N]` is present and you need the specs, call `get_task`.
4.  **Explore Branch**: If `[F: n]` indicates subtasks, use `get_task(include_children=True)` to understand the breakdown.
