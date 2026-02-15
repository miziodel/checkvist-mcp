# Checkvist API Compatibility Matrix

**Last Verified**: 2026-02-04
**Status**: Active

This document tracks all Checkvist API endpoints used by the MCP server, their status, and known quirks. It serves as a reference for developers and a source of truth for the `validate_api_endpoints.py` script.

## 🟢 Core Task Management

| Endpoint                                       | Method   | Params (Key)                       | Status      | Quirks / Notes                                                                            |
| :--------------------------------------------- | :------- | :--------------------------------- | :---------- | :---------------------------------------------------------------------------------------- |
| `/checklists/{id}/tasks.json`                  | `GET`    | `with_notes`, `with_tags`          | ✅ Verified | Returns list of dicts. Note: Tags can sometimes be returned as dict keys instead of list. |
| `/checklists/{id}/tasks.json`                  | `POST`   | `task[content]`, `task[parent_id]` | ✅ Verified | Returns created task dict.                                                                |
| `/checklists/{id}/tasks/{task_id}.json`        | `GET`    | `with_notes`, `with_tags`          | ✅ Verified | **Polymorphic**: Can return `[task]` (list) or `task` (dict). Must handle both.           |
| `/checklists/{id}/tasks/{task_id}.json`        | `PUT`    | `task[content]`, `parse`           | ✅ Verified | Use `parse=true` for smart syntax processing.                                             |
| `/checklists/{id}/tasks/{task_id}.json`        | `DELETE` | -                                  | ✅ Verified | Returns 200 OK on success.                                                                |
| `/checklists/{id}/tasks/{task_id}/close.json`  | `POST`   | -                                  | ✅ Verified | Returns updated task.                                                                     |
| `/checklists/{id}/tasks/{task_id}/reopen.json` | `POST`   | -                                  | ✅ Verified | Can return list-wrapped response.                                                         |

## 🟢 Lists & Checklists

| Endpoint                | Method   | Params (Key)                           | Status      | Quirks / Notes                                               |
| :---------------------- | :------- | :------------------------------------- | :---------- | :----------------------------------------------------------- |
| `/checklists.json`      | `GET`    | -                                      | ✅ Verified | Returns list of user's checklists.                           |
| `/checklists.json`      | `POST`   | `checklist[name]`, `checklist[public]` | ✅ Verified | Creates a new list.                                          |
| `/checklists/{id}.json` | `PUT`    | `checklist[name]`                      | ✅ Verified | Renames checklist.                                           |
| `/checklists/{id}.json` | `DELETE` | -                                      | ✅ Verified | Deletes checklist.                                           |
| `/checklists/due.json`  | `GET`    | -                                      | ✅ Verified | Undocumented. Returns tasks with due dates across all lists. |

## 🟠 Advanced & Undocumented

| Endpoint                                         | Method | Params (Key)                    | Status      | Quirks / Notes                                                                                     |
| :----------------------------------------------- | :----- | :------------------------------ | :---------- | :------------------------------------------------------------------------------------------------- |
| `/auth/login.json?version=2`                     | `POST` | `username`, `remote_key`        | ✅ Verified | Returns just the token string in JSON, not a dict.                                                 |
| `/checklists/{id}/import.json`                   | `POST` | `import_content`, `parse_tasks` | ✅ Verified | Send content in body to avoid URL length limits.                                                   |
| `/checklists/{id}/tasks/{task_id}/comments.json` | `POST` | `comment[comment]`              | ✅ Verified | Adds a note/comment.                                                                               |
| `/checklists/{id}/tasks/{task_id}/paste`         | `POST` | `move_to`, `task_ids`           | ⚠️ Beta   | **Undocumented**. Returns `text/javascript`. Used for cross-list moves. (Found via Forensics)      |
| `/checklists/{id}/tasks/{task_id}/tags.js`       | `POST` | `tags`, `task_ids`              | ⚠️ Beta   | **Undocumented**. Bulk tag operation. `task_ids` is comma-separated string.                        |
| `/checklists/{id}/tasks/move.json`               | `POST` | `task_ids[]`, `parent_id`       | ⚠️ Beta   | **Undocumented**. Bulk re-parenting across or within checklists.                                   |
| `/search/everywhere.json`                        | `GET`  | `what`                          | ⚠️ Beta   | **Undocumented**. Powerful global search for tasks and lists with unified suggestions.             |
| `/checklists/{id}/tasks/{task_id}/details`       | `POST` | `details[mark]`, `_method=put`  | ⚠️ Beta   | **Undocumented**. Sets Priority/Color (e.g. `fg1`=Red, `fg2`=Orange). Requires `_method=put`.      |

## 🧪 Validation Strategy

Run `python3 scripts/validate_api_endpoints.py` to ping all GET endpoints and verify minimal connectivity.
For state-changing endpoints (POST/PUT/DELETE), rely on `tests/test_regressions.py`.
