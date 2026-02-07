version: 1.3.0
last_modified: 2026-02-07
status: active

# Test Coverage vs Scenarios Report
Date: 2026-02-07

## Summary
Execution of `pytest tests` passed (83/83 tests). The suite now includes `resilience` coverage, `lifespan` hygiene, and `BUG-010` verification across lists.

| Scenario ID | Name                  | Implemented? | Tested? | Status               |
| ----------- | --------------------- | ------------ | ------- | -------------------- |
| DISC-001    | List Checklists       | ✅           | ✅      | Covered              |
| DISC-002    | Search List           | ✅           | ✅      | Covered              |
| DISC-003    | Tree Analysis         | ✅           | ✅      | Covered              |
| DISC-004    | Global Task Search    | ✅           | ✅      | Covered              |
| TASK-001    | Add Task              | ✅           | ✅      | Covered              |
| TASK-002    | Close Task            | ✅           | ✅      | Covered              |
| TASK-003    | Reopen Task           | ✅           | ✅      | Covered              |
| TASK-004    | Create Checklist      | ✅           | ✅      | Covered              |
| TASK-005    | Rename Checklist      | ✅           | ✅      | Covered              |
| BUG-001     | Robust Task Closing   | ✅           | ✅      | Covered              |
| BUG-002     | Handle 204 No Content | ✅           | ✅      | Covered              |
| BUG-003     | Tag Robustness        | ✅           | ✅      | Covered              |
| BUG-004     | Hierarchy Loss Move   | ✅           | ✅      | Covered              |
| BUG-005     | Search Tags Scope     | ✅           | ✅      | Covered              |
| BUG-006     | Archive List Wrapping | ✅           | ✅      | Covered              |
| BUG-007     | Template Hierarchy    | ✅           | ✅      | Covered              |
| BUG-008     | Reopen List Wrapping  | ✅           | ✅      | Covered (repro_bugs) |
| BUG-009     | Import Body Hygiene   | ✅           | ✅      | Covered (live_verify)|
| BUG-010     | Cross-List Parent ID  | ✅           | ✅      | Covered (live_verify)        |
| BULK-001    | Bulk Import           | ✅           | ✅      | Covered              |
| BULK-002    | Internal Reparenting  | ✅           | ✅      | Covered              |
| BULK-003    | Cross-List Migration  | ✅           | ✅      | Covered              |
| META-001    | Add Note              | ✅           | ✅      | Covered              |
| META-002    | Set Priority          | ✅           | ✅      | Covered (via update) |
| META-003    | Smart Tagging         | ✅           | ✅      | Covered              |
| META-004    | Due Dates             | ✅           | ✅      | Covered              |
| META-005    | Metadata Visibility   | ✅           | ✅      | Covered              |
| META-006    | Smart Syntax Parsing  | ✅           | ✅      | Covered              |
| PROC-001    | Inbox Zero            | ✅           | ✅      | Covered              |
| PROC-002    | Idea Resurfacing      | ✅           | ✅      | Covered              |
| PROC-003    | Templates             | ✅           | ✅      | Covered              |
| PROC-004    | Periodic Review       | ✅           | ✅      | Covered              |
| PROC-005    | Cycle Migration       | ✅           | ✅      | Covered              |
| PROC-006    | Template Verification | ✅           | ✅      | Covered              |
| PROC-009    | Weekly Review         | ✅           | ✅      | Covered              |
| PERF-001    | Performance Benchmark | ✅           | ✅      | Covered              |
| SAFE-001    | Logical Deletion      | ✅           | ✅      | Covered              |
| SAFE-002    | Injection Delimiters  | ✅           | ✅      | Covered              |
| SAFE-003    | Rate Limit Warning    | ✅           | ✅      | Covered              |
| SAFE-004    | Breadcrumbs           | ✅           | ✅      | Covered              |
| SAFE-005    | Triage Confirmation   | ✅           | ✅      | Covered              |
| SAFE-006    | Resource Shutdown     | ✅           | ✅      | Covered (live_verify)|

## Recommendations
Maintain the `tests/test_bug_report_verified.py` file for all future regressions to keep the core scenario tests clean.
