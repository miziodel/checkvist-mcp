# Checkvist MCP Backlog

This document tracks features and improvements that are deferred due to risk, complexity, or pending clarification.

## Deferred Features

### 1. Delete Task (`delete_task`)
- **Reason**: High risk of data loss. Need to evaluate if a "Trash" or "Archive" approach is safer or if users need a confirmation flow.
- **Priority**: Low

## Under Review

### 1. Rename List (`rename_list`)
- **Status**: Assessing implications for cross-links (`[[list_name]]`).
- **Concern**: If links are literal strings, renaming the list might break existing references across the PKM system.

## Strategic & Operational Concerns

### 1. Risk Coverage Verification
- **Status**: Evaluating if current "Safety First" rules efficiently block destructive patterns without hampering agent autonomy.
- **Goal**: Create a "Safety Mesh" that audits agent actions against data loss risks.

### 2. Performance & Resource Efficiency
- **Status**: Assessing MCP server performance.
- **Concerns**:
    - Tool count: Are there too many fine-grained tools? (Cognitive load for LLM).
    - Token consumption: Are list/tree fetches consuming excessive context?
    - Latency: Impact of rate-limiting on complex workflow speed.
