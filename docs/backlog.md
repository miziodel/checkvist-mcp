---
version: 1.0.1
last_modified: 2026-01-31
status: active
---

# Checkvist MCP Backlog

This document tracks features and improvements that are deferred due to risk, complexity, or pending clarification.

## Deferred Features

### 1. Permanent Delete Task (`delete_task`)
- **Reason**: High risk of data loss. Decision made to prioritize **Recursive Logical Deletion** (Archiving) first.
- **Priority**: Low

### 2. Hard Deletion Cleanup
- **Goal**: Implement a manual or semi-automated routine to permanently delete tasks tagged `#deleted` older than X days.
- **Priority**: Low


### 3. Code Quality Review (Python)
- **Status**: New request.
- **Goal**: Evaluate the quality of produced Python code.
- **Questions**: Do we need one or more specialized skills for this?

### 4. Enhanced Authentication Security
- **Status**: New request.
- **Goal**: Investigate if we can create a connection with something more secure than basic auth with an API key (e.g., OAuth2, session tokens, etc.).
- **Concerns**: Balancing security with the "Developer Ergonomics" of an MCP server.
