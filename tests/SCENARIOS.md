## 🗺️ Roadmap & Vision Mapping

| Phase             | Scenario IDs | Vision Pillar           | Concept                                    |
| ----------------- | ------------ | ----------------------- | ------------------------------------------ |
| **1: Discovery**  | `DISC-*`     | **Foundation**          | Basis for any context-aware action.        |
| **2: Tasks**      | `TASK-*`     | **Foundation**          | Core CRUD operations.                      |
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
