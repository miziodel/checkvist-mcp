# 🐛 Bug Report: `move_task` Tool

**Status:** FIXED (2026-02-04)
**Tool:** `mcp_checkvist-move_task`

### ❌ The Issue: `target_parent_id` Ignored across Lists

When using `move_task` to move a task **from List A to List B** while specifying a `target_parent_id` in List B, the tool **ignores the parent ID**.

*   **Expected Behavior:** The task moves to List B and becomes a child of `target_parent_id`.
*   **Actual Behavior:** The task moves to List B but lands at the **Root Level**, completely ignoring the requested parent.

### 🧪 Reproduction Steps (Verified 2026-02-04)

1.  Created Source List `[TEST] Source Complex` (ID: 946622).
2.  Created Target List `[TEST] Target Complex` (ID: 946623).
3.  Created a Container Task `Archive Box` in Target List (ID: 72308548).
4.  Created a Task Tree in Source List:
    ```
    Root Task Complex (ID: 72308543)
      └── Child with Note
          └── Grandchild #urgent
    ```
5.  **Executed Action:**
    ```python
    move_task(
        list_id=946622, 
        task_id=72308543, 
        target_list_id=946623, 
        target_parent_id=72308548  <-- THE CONTAINER
    )
    ```
6.  **Result:**
    ```
    [TEST] Target Complex
    ├── Root Task Complex (ID: 72308543)  <-- FAIL: Landed at Root
    └── Archive Box (ID: 72308548)        <-- FAIL: Empty Container
    ```

### 📋 Technical Diagnosis

Checkvist API likely handles "Move to List" and "Set Parent" as distinct operations or requires a specific order/payload structure that the current MCP implementation flattens or misinterprets. 

**Workaround Found:**
It requires **two** separate calls to achieve the desired result:
1.  `move_task(target_list_id=...)` -> Moves to root of new list.
2.  `move_task(target_parent_id=...)` -> Moves inside the parent (within the same list).

### ✅ Fix Implemented (2026-02-04)

The fix involved splitting the cross-list move into two sequential API calls:
1.  **POST `/paste`**: Moves the task (and its children) to the target list (lands at root).
2.  **PUT `/tasks/{id}.json`**: Sets the correct `parent_id` within the target list.

Verified via integrated tests and browser forensics.
