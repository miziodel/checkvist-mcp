---
version: 1.1.0
last_modified: 2026-01-30
status: active
---

## 🗺️ Roadmap & Vision Mapping

| Phase             | Scenario IDs | Vision Pillar           | Concept                                    |
| ----------------- | ------------ | ----------------------- | ------------------------------------------ |
| **1: Discovery**  | `DISC-*`     | **Foundation**          | Basis for any context-aware action.        |
| **2: Tasks**      | `TASK-*`, `BUG-*` | **Foundation**          | Core CRUD operations & Robustness.         |
| **3: Bulk Ops**   | `BULK-*`     | **Linear / Superhuman** | High-speed triage and project scaffolding. |
| **4: Enrichment** | `META-*`     | **GitHub / Todoist**    | Dependencies, priorities, and smart tags.  |
| **5: Processes**  | `PROC-*`     | **Readwise / Linear**   | Autonomous triage and idea resurfacing.    |

---

## 🔍 Phase 1: Discovery & Navigation (DISC)
*Goal: Allow the Agent to find where things are and understand project structure.*

### DISC-001: List All Checklists
*Vision Match: Foundation / Context Recovery*
```gherkin
When the Agent calls `list_checklists`
Then the tool returns a list of all available checklists with their IDs.
```

### DISC-002: Fuzzy Search for Checklists
*Vision Match: Foundation / Context Recovery*
```gherkin
When the Agent calls `search_list(query="Server")`
Then the tool returns checklists whose name contains "Server".
```

### DISC-003: Deep Dive Tree Analysis
*Vision Match: Foundation / Deep Work Setup*
```gherkin
Given a checklist ID
When the Agent calls `get_tree(id, depth=2)`
Then it returns a Markdown representation of tasks up to level 2.
```

### DISC-004: Global Task Search
*Vision Match: Context Recovery / Roam Style*
```gherkin
When the Agent calls `search_tasks(query="Docker config")`
Then it searches across all checklists and returns matching tasks with their list names.
```

### DISC-005: Global Upcoming Tasks
*Vision Match: Todoist Style / Dynamic Planning*
```gherkin
When the Agent calls `get_upcoming_tasks(filter="today")`
Then it returns all tasks across all checklists that are due today.
```

### DISC-006: Due Date Agenda View
*Vision Match: Full Context / Daily Review*
```gherkin
When the Agent reads the resource `checkvist://due`
Then it returns a formatted Markdown agenda of all upcoming tasks grouped by date.
```

---

## ✍️ Phase 2: Core Task Management (TASK)
*Goal: Essential CRUD operations for single items.*

### TASK-001: Add Single Task
*Vision Match: Foundation / Smart Parse*
```gherkin
When the Agent calls `add_task(list_id, content="New Item")`
Then a new task is created at the end of the root level.
```

### TASK-002: Close Task
*Vision Match: Foundation / Linear Style*
```gherkin
When the Agent calls `close_task(list_id, task_id)`
Then the task status is set to 1 (completed).
```

### TASK-003: Reopen Task
*Vision Match: Foundation*
```gherkin
When the Agent calls `reopen_task(list_id, task_id)`
Then the task status is set back to 0 (open).
```

### TASK-004: Create Checklist
*Vision Match: Foundation / Autonomous Flux*
```gherkin
When the Agent calls `create_list(name="New Project")`
Then a new checklist is created with the given name.
```

### TASK-005: Rename Checklist
*Vision Match: Foundation / PARA Maintenance*
```gherkin
Given a checklist ID
When the Agent calls `rename_list(list_id, new_name="Archived: Projects")`
Then the checklist name is updated in Checkvist.
And internal cross-links (ID-based) remain functional.
```

---

## 🐞 Bug Fixes & Robustness (BUG)

### BUG-001: Robust Task Operations
*Issue: Systematic failure when closing or archiving tasks due to API response format variability.*
```gherkin
Given a list_id and task_id
When the Agent calls `close_task` or `archive_task`
Then the server handles the API response safely even if it's a list or dictionary.
```

### BUG-002: Handle 204 No Content
*Issue: JSON parsing error on empty bodies from move/migrate operations.*
```gherkin
Given a move or migration operation
When the API returns HTTP 204 (No Content)
Then the client should bypass JSON parsing and return success.
```

### BUG-003: Tag Robustness (Dictionary vs List)
*Issue: Crash in archive_task when tags are returned as a dictionary.*
```gherkin
Given a task where the API returns tags as a dictionary (key-indexed)
When the Agent calls `archive_task`
Then the server correctly converts the dictionary keys to a list before appending `#deleted`.
```

### BUG-004: Hierarchy Loss on Cross-List Move
*Issue: Children are detached (become roots) when migrating a parent task to a new list.*
```gherkin
Given a parent task with children
When the Agent calls `move_task_tool` to a different list
Then the children are also moved and remain nested under the original parent.
```

### BUG-005: Search Scope Includes Tags
*Issue: Search only checks content, missing tasks labeled with searchable tags.*
```gherkin
Given a task with tag "urgent" and content "Fix bug"
When the Agent calls `search_tasks(query="urgent")`
Then the task is found even if "urgent" is not in the content.
```

### BUG-006: Archive Task List-Wrapped Response
*Issue: API occasionally returns task object wrapped in a list, causing attribute errors.*
```gherkin
Given a task ID
When the API returns `[{...}]` instead of `{...}` for a task fetch/update during archive
Then the server correctly unwraps the list before accessing task attributes.
```

### BUG-007: Template Hierarchy Loss
*Issue: apply_template flattens nested tasks to root level or skips them.*
```gherkin
Given a template list with a 3-level hierarchy (Root > Child > Grandchild)
When the Agent calls `apply_template`
Then the target list contains the same 3-level hierarchy with correct indentation.
```

### BUG-008: Reopen Task List-Wrapped Response
*Issue: API returns `[{...}]` for reopen operations, causing AttributeError.*
```gherkin
Given a closed task ID
When the API returns a list-wrapped object upon reopening
Then the server correctly normalizes the response and completes the operation.
```

### BUG-009: Import Tasks Payload Hang
*Issue: Large text imports via query parameters cause server timeouts/hangs.*
```gherkin
Given a large amount of hierarchical text
When the Agent calls `import_tasks`
Then the content is sent in the POST body (not URL) to ensure stability.
```

---

## 📦 Phase 3: Bulk & Group Operations (BULK)
*Goal: High-speed organization and hierarchy management.*

### BULK-001: Hierarchical Bulk Import
*Vision Match: Linear Style / Triage*
```gherkin
Given a complex project structure in text
When the Agent calls `import_tasks(list_id, content="Root\n  Child 1\n  Child 2")`
Then Checkvist creates the tasks preserving the indentation hierarchy.
```

### BULK-002: Internal Reparenting
*Vision Match: Linear Style / Triage*
```gherkin
When the Agent calls `move_task_tool(list_id, task_id, target_parent_id=...)`
Then the task is moved under a new parent in the same list.
```

### BULK-003: Cross-List Migration
*Vision Match: Linear Style / Superhuman Zero Inbox*
```gherkin
When the Agent calls `move_task_tool(list_id, task_id, target_list_id=...)`
Then the task is relocated to a different checklist.
```

---

## 💎 Phase 4: Enrichment & Metadata (META)
*Goal: Adding detail, priority, and context to tasks.*

### META-001: Add Note (Comment)
*Vision Match: Roam Style / Context Building*
```gherkin
When the Agent calls `add_note(list_id, task_id, note="Ref context...")`
Then a comment is attached to the task.
```

### META-002: Set Priority
```gherkin
*Vision Match: GitHub Style / Triage*
When the Agent calls `set_priority(list_id, task_id, priority=3)`
Then the task is color-coded with priority 3.
```

### META-003: Smart Tagging
*Vision Match: Todoist Style / Smart Parse*
```gherkin
When the Agent calls `update_task(list_id, task_id, tags="urgent, mcp")`
Then the task is assigned the specified tags.
```

### META-004: Manage Due Dates
*Vision Match: Todoist Style / Dynamic Planning*
```gherkin
When the Agent calls `set_due_date(list_id, task_id, due="tomorrow")`
Then the task due date is updated using Checkvist's smart syntax.
```

### META-005: Metadata Visibility
*Vision Match: Full Context / Deep Work*
```gherkin
When the Agent calls `get_tree` or `search_tasks`
Then the output includes visual decorators for metadata:
- Priorities (e.g., `!1`)
- Due dates (e.g., `^2026-12-31`)
- Tags (e.g., `#deleted`, `#urgent`)
```

### META-006: Expanded Smart Syntax Support
*Vision Match: Superhuman Efficiency*
```gherkin
When the Agent calls `add_task` with content containing:
- High priority markers (e.g., `!!1`)
- Internal links or ID references (e.g., `[id:123]`)
Then the tool triggers `parse=True` to ensure Checkvist processes these symbols.
```

---

## 🤖 Phase 5: Advanced Workflows (PROC)
*Goal: Autonomous agentic processes for productivity.*

### PROC-001: Inbox Zero Triage
*Vision Match: Superhuman Style / Linear Triage*
```gherkin
When the Agent finds a list named "Inbox"
Then it lists all open tasks to prepare for a "move to project" loop.
```

### PROC-002: Brainstorming Resurfacing
*Vision Match: Readwise Style / Anti-Oblio*
```gherkin
When the Agent calls `resurface_ideas()`
Then it picks 3 random open tasks from various lists to jog the user's memory.
```

### PROC-003: Smart Templating
*Vision Match: Raycast Style / Onboarding*
```gherkin
Given a "Template" list
When the Agent calls `apply_template(template_list_id, target_list_id)`
Then all tasks from the template are cloned into the target list.
```

### PROC-004: Periodic Review & Synthesis
*Vision Match: Daily Review / Synthesis*
```gherkin
When the Agent calls `get_review_data(timeframe="weekly")`
Then it returns completed vs pending stats to prepare a progress report.
```

### PROC-005: Cycle Migration
*Vision Match: Linear Style / Cycles*
```gherkin
Given a list of tasks in "Current Cycle"
When the Agent calls `migrate_incomplete_tasks(source_list_id, target_list_id)`
Then all tasks with status 0 are moved to the target list.
```

### PROC-006: Template Verification
*Vision Match: Safety / Robust Automation*
```gherkin
Given an empty or invalid template checklist
When the Agent calls `apply_template`
Then it returns a clear error message instead of reporting "Template applied".
```

---
## 🛡️ Phase 6: Risk Mitigation & Safety (SAFE)
*Goal: Ensure data integrity and system robustness.*

### SAFE-001: Logical Deletion (Archive)
*Vision Match: Safety / Data Integrity*
```gherkin
Given a list_id and task_id
When the Agent calls `archive_task(list_id, task_id)`
Then the task (and all its subtasks) are assigned the tag "#deleted"
And subsequent calls to `get_tree` or `get_list_content` exclude this entire branch.
```

### SAFE-002: Prompt Injection Delimiters
*Vision Match: Security / Trust Boundaries*
```gherkin
When any read tool (e.g., `get_list_content`) returns user-generated data
Then the content is wrapped in `<user_data>` XML-style delimiters.
```

### SAFE-003: API Rate Limit Warning
*Vision Match: Stability / Rate Limiting*
```gherkin
When the Agent makes more than 10 tool calls in 60 seconds
Then the tool output includes a `[!WARNING]` about high API usage.
```

### SAFE-004: Breadcrumbs Context
*Vision Match: Context awareness / Parent-Trap prevention*
```gherkin
When the Agent searches for a task or lists content
Then the output shows the full breadcrumb path (e.g. "Root > Category > Task").
```

### SAFE-005: Triage Confirmation (Human-in-the-loop)
*Vision Match: Safety / Triage Chaos prevention*
```gherkin
When the Agent tries to move a task or migrate tasks
Then the tool returns a summary of the action and a `[!IMPORTANT]` note requesting user confirmation before proceeding.
And the action is NOT performed until a "confirmed" parameter is set or the LLM explicitly acknowledges.
*Note: For this v1, we will implement the warning message first to allow the LLM to pause.*
```

### SAFE-006: Managed Resource Shutdown
*Vision Match: Stability / Lifecycle Management*
```gherkin
Given an active MCP server or verification script
When the process finishes or encounters an error
Then all HTTP client connections are explicitly closed via a shutdown hook
And no background hanging processes remain.
```

---
## 📚 Related Documentation
- [Vision & Roadmap](../docs/vision.md)
- [Verification Guide](VERIFICATION_GUIDE.md)
- [Human Playbook](PLAYBOOK.md)
