# Checkvist MCP Backlog

This document tracks features and improvements that are deferred due to risk, complexity, or pending clarification.

## Deferred Features

### 1. Delete Task (`delete_task`)
- **Reason**: High risk of data loss. Need to evaluate if a "Trash" or "Archive" approach is safer or if users need a confirmation flow.
- **Priority**: Low

## Under Review

### 1. Risk Coverage Verification
- **Status**: Evaluating if current "Safety First" rules efficiently block destructive patterns without hampering agent autonomy.
- **Goal**: Create a "Safety Mesh" that audits agent actions against data loss risks.

### 2. Performance & Resource Efficiency
- **Status**: Assessing MCP server performance.
- **Concerns**:
    - Tool count: Are there too many fine-grained tools? (Cognitive load for LLM).
    - Token consumption: Are list/tree fetches consuming excessive context?
    - Latency: Impact of rate-limiting on complex workflow speed.
- **Future Improvement**: Add `async sleep` mechanism for smarter rate limiting (currently using notifications).

### 3. Hard Deletion Cleanup
- **Goal**: Implement a manual or semi-automated routine to permanently delete tasks tagged `#deleted` older than X days.


### 4. Code Quality Review (Python)
- **Status**: New request.
- **Goal**: Evaluate the quality of produced Python code.
- **Questions**: Do we need one or more specialized skills for this?

### 5. Logical Deletion Mechanism
- **Status**: Proposed as safer alternative to `delete_task`.
- **Goal**: Implement a mechanism for logical deletion based on tags or similar markers, to prevent accidental data loss while allowing users to "cleanup" views.
