---
version: 1.0.0
last_modified: 2026-01-30
status: active
---

# Checkvist Open API Documentation

Reference documentation for Checkvist API, retrieved from https://checkvist.com/auth/api.

## General Principles
- **Base URL**: `https://checkvist.com`
- **Formats**: Supports `.json` and `.xml` suffixes.
- **HTTP Methods**: Supports GET, POST, PUT, DELETE. To emulate PUT/DELETE via POST, use `_method` parameter.

## Authentication
- **Token-based**: Recommended.
- **Header**: `X-Client-Token` or parameter `token`.
- **Obtaining Token**: `POST /auth/login.json?version=2` with `username` and `remote_key`.

## Working with Checklists
### Get list of user checklists
`GET /checklists.json`
- Parameters: `archived`, `order`, `skip_stats`.

### Create a checklist
`POST /checklists.json`
- Parameters: `checklist[name]`, `checklist[public]`.

## Working with List Items (Tasks)
### Get list items
`GET /checklists/{list_id}/tasks.json`
- Parameters: `with_notes`, `order`.

### Create list items (Single or Bulk)
`POST /checklists/{list_id}/tasks.json`
- **Single**: `task[content]`, `task[parent_id]`, `task[tags]`, `task[due_date]`, `task[position]`, `task[priority]`.
- **Bulk (Import)**:
    - **Endpoint**: `POST /checklists/{list_id}/import.json`
    - **Parameters**:
        - `import_content`: Hierarchical text.
        - `import_content_note`: Note for the first item.
        - `parent_id`: ID of the parent item.
        - `parse_tasks`: Boolean to parse smart syntax (^due, #tags, !priority).
        - `position`: 1-based position.

### Update list item
`PUT /checklists/{list_id}/tasks/{task_id}.json`
- Parameters: `task[content]`, `task[parent_id]`, `task[tags]`, `task[due_date]`, `task[position]`, `task[priority]`.

### Status Changes (Close/Open/Invalidate)
`POST /checklists/{list_id}/tasks/{task_id}/{action}.json`
- Actions: `close`, `reopen`, `invalidate`.
- **Note**: The API may return a list (e.g. `[{"id": ...}]`) instead of a single object for `close`. The client must handle both cases.

## Smart Syntax Parsing (Discovery Findings - Jan 2026)

Based on live probes, the following behaviors were confirmed:

### 1. `tasks.json` (POST) vs `import.json` (POST)
- **`tasks.json?parse=true`**: Extremely unreliable for v2 API. It often fails to strip symbols like `!1` or `#tag` from the content, even if it sets the metadata correctly.
- **`import.json?parse_tasks=1`**: Highly reliable for core symbols (`!`, `#`, `^`). It correctly strips the metadata from the `content` field.

### 2. Symbol Support Table

| Symbol                  | Example                | Stripped? | Metadata Set? | Notes                                         |
| :---------------------- | :--------------------- | :-------- | :------------ | :-------------------------------------------- |
| **Priority**            | `!1`                   | ✅ Yes    | ✅ Yes        | Use `!1` for high/red.                        |
| **Priority (Internal)** | `!!1`                  | ❌ No     | ❌ No         | Server now pre-processes to `!1`.             |
| **Tags**                | `#urgent`              | ✅ Yes    | ✅ Yes        |                                               |
| **Due Date**            | `^tomorrow`            | ✅ Yes    | 🟡 Partial   | Stripped from content, but verify `due_date`. |
| **Links**               | `[](/cvt/ID)`          | ❌ No     | ❌ No         | Internal task link.                           |
| **Links**               | `[QA](/checklists/ID)` | ❌ No     | ❌ No         | Internal checklist link.                      |

### 3. Implementation Strategy
- Route all single-line tasks with symbols through `import.json`.
- Pre-process `!!` to `!` to normalize high priority.

## Working with Notes (Comments)
### Get task notes
`GET /checklists/{list_id}/tasks/{task_id}/comments.json`

### Create a note for a task
`POST /checklists/{list_id}/tasks/{task_id}/comments.json`
- Parameters: `comment[comment]`.

### Update/Delete note
`PUT/DELETE /checklists/{list_id}/tasks/{task_id}/comments/{comment_id}.json`
