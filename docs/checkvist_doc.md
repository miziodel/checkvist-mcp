---
version: 1.1.0
last_modified: 2026-01-31
status: active
---

# Checkvist Documentation: Tips & Pro Features

This document collects key notions about Checkvist functionality to aid in MCP server optimization and user guidance.

## Core Multi-line & Syntax Features

### 1. Estimates and Rollups
- **Syntax**: Use tags like `#30m`, `#1h`, `#2d` at the end of a task.
- **Rollup Automatico**: Checkvist automatically sums these durations on parent tasks.
- **MCP Opportunity**: The server should allow clean extraction of these tags for capacity calculations (e.g., "Total hours in parent X?").

### 2. Smart Syntax & Dates
- **Deadlines**: Support for native shortcuts: `^today`, `^tomorrow`, `^friday`.
- **Repeat (Ricorrenza)**: Syntax is complex and often a PRO feature.
- **MCP Opportunity**: A dedicated `set_repeat` tool could simplify sending recurrence strings (e.g., "every Monday").

### 3. Cross-Linking (Zettelkasten)
- **Syntax**: Use `[[task_id]]` or `[[checklist_name]]`.
- **Usage**: Critical for creating Maps of Content (MOC) linking organic summaries to archived notes.
- **MCP Opportunity**: Facilitate resolution of these links.

---

## Pro User Insights & Advanced Tips

### 1. Keyboard Shortcuts (The "Zen" of Checkvist)
Checkvist is keyboard-first. Key commands every Pro should know:
- **Master Search**: `Shift Shift` (Quickly find any list or item).
- **Navigation**: `Shift →` (Hoisting/Focusing on a branch), `Shift ←` (Unhoisting).
- **Actions Menu**: `aa` (Access all context actions).
- **Indentation**: `Tab` / `Shift+Tab`.
- **Reordering**: `Ctrl+↑` / `Ctrl+↓`.
- **Collapse/Expand**: `Ctrl-Shift ←` / `Ctrl-Shift →`.
- **Quick Attributes**: `tt` for tags, `dd` for due dates.
- **Undo**: `uu` or `Ctrl+Z`.

### 2. PARA Method Implementation
Checkvist's hierarchy is perfect for Tiago Forte's P.A.R.A:
- **Projects**: Use specific lists or top-level nodes for active projects. Use `#project` tag and `^due` dates.
- **Areas**: Long-term responsibilities (e.g., "Health", "Finances"). Use distinct lists.
- **Resources**: Knowledge base. Use `[[link]]` syntax to connect notes.
- **Archives**: Moved completed projects here. Use `hc` (hide completed) to keep it clean.

### 3. Smart Syntax (Type as you think)
- **Priorities**: Type `!1` (highest) to `!9` at the start/end of a line.
- **Deadlines**: Typing `tomorrow` or `next mon` at the end of a line is automatically recognized.
- **Styles**: Use `[ ]` for tasks, `[*]` for notes, `[1]` for numbered lists.

---

## Technical Optimization (MCP Context)

### Handling 204 No Content
Operations like `move_task_to_list` and `migrate_incomplete_tasks` return an HTTP 204. The client MUST NOT attempt to parse JSON on these responses.

### Batch Operations
Use `import_tasks` for hierarchy-preserving bulk imports. The string should use 2-space indentation for children.
