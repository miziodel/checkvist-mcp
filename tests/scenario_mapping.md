# Scenario to Test Mapping

This document links each scenario defined in `tests/SCENARIOS.md` to its corresponding automated test file and function.

| ID           | Scenario Name               | Test File                   | Test Function                                     | Status |
| :----------- | :-------------------------- | :-------------------------- | :------------------------------------------------ | :----- |
| **DISC-001** | List All Checklists         | `tests/test_scenarios.py`   | `test_phase1_discovery`                           | ✅     |
| **DISC-002** | Fuzzy Search for Checklists | `tests/test_scenarios.py`   | `test_phase1_discovery`                           | ✅     |
| **DISC-003** | Deep Dive Tree Analysis     | `tests/test_scenarios.py`   | `test_phase1_discovery`                           | ✅     |
| **DISC-004** | Global Task Search          | `tests/test_scenarios.py`   | `test_phase1_discovery`                           | ✅     |
| **TASK-001** | Add Single Task             | `tests/test_scenarios.py`   | `test_phase2_task_management`                     | ✅     |
| **TASK-002** | Close Task                  | `tests/test_scenarios.py`   | `test_phase2_task_management`                     | ✅     |
| **TASK-003** | Reopen Task                 | `tests/test_scenarios.py`   | `test_phase2_task_management`                     | ✅     |
| **TASK-004** | Create Checklist            | `tests/test_tools.py`       | `test_create_list_tool`                           | ✅     |
| **TASK-005** | Rename Checklist            | `tests/test_scenarios.py`   | `test_phase2_task_management`                     | ✅     |
| **BUG-001**  | Robust Task Operations      | `tests/test_regressions.py` | `test_bug_001_robust_task_operations`             | ✅     |
| **BUG-002**  | Handle 204 No Content       | `tests/test_regressions.py` | `test_bug_002_handle_204_no_content`              | ✅     |
| **BUG-003**  | Tag Robustness              | `tests/test_regressions.py` | `test_bug_003_tag_robustness_dict_format`         | ✅     |
| **BUG-004**  | Hierarchy Loss Move         | `tests/test_regressions.py` | `test_bug_004_hierarchy_loss_on_move`             | ✅     |
| **BUG-005**  | Search Scope Includes Tags  | `tests/test_regressions.py` | `test_bug_005_search_scope_includes_tags`         | ✅     |
| **BUG-006**  | Archive List Wrapping       | `tests/test_regressions.py` | `test_bug_006_archive_task_list_wrapped_response` | ✅     |
| **BUG-007**  | Template Hierarchy Loss     | `tests/test_regressions.py` | `test_bug_007_template_hierarchy_preservation`    | ✅     |
| **BUG-008**  | Reopen List Wrapping        | `tests/test_regressions.py` | `test_bug_008_reopen_task_list_response`          | ✅     |
| **BUG-009** | Import Tasks Payload Hang   | `tests/test_regressions.py` | `test_bug_009_import_tasks_payload_hygiene`       | ✅     |
| **BUG-010** | Cross-List Parent ID Fix    | `tests/test_regressions.py` | `test_bug_010_move_task_cross_list_parent_id`     | ✅     |
| **BULK-001** | Hierarchical Bulk Import    | `tests/test_scenarios.py`   | `test_phase3_bulk_operations`                     | ✅     |
| **BULK-002** | Internal Reparenting        | `tests/test_tools.py`       | `test_move_task_same_list`                        | ✅     |
| **BULK-003** | Cross-List Migration        | `tests/test_scenarios.py`   | `test_phase3_bulk_operations`                     | ✅     |
| **META-001** | Add Note                    | `tests/test_scenarios.py`   | `test_phase4_enrichment`                          | ✅     |
| **META-002** | Set Priority                | `tests/test_scenarios.py`   | `test_phase4_enrichment`                          | ✅     |
| **META-003** | Smart Tagging               | `tests/test_scenarios.py`   | `test_phase4_enrichment`                          | ✅     |
| **META-004** | Manage Due Dates            | `tests/test_scenarios.py`   | `test_phase4_enrichment`                          | ✅     |
| **META-005** | Metadata Visibility         | `tests/test_scenarios.py`   | `test_phase4_enrichment`                          | ✅     |
| **META-006** | Expanded Smart Syntax       | `tests/test_scenarios.py`   | `test_robustness_scenarios`                       | ✅     |
| **PROC-001** | Inbox Zero Triage           | `tests/test_tools.py`       | `test_triage_inbox_tool`                          | ✅     |
| **PROC-002** | Brainstorming Resurfacing   | `tests/test_tools.py`       | `test_resurface_ideas_tool`                       | ✅     |
| **PROC-003** | Smart Templating            | `tests/test_scenarios.py`   | `test_phase5_advanced_workflows`                  | ✅     |
| **PROC-004** | Periodic Review             | `tests/test_server.py`      | `test_review_data_wrapping`                       | ✅     |
| **PROC-005** | Cycle Migration             | `tests/test_scenarios.py`   | `test_phase5_advanced_workflows`                  | ✅     |
| **PROC-006** | Template Verification       | `tests/test_regressions.py` | `test_proc_006_template_verification_error`       | ✅     |
| **PROC-009** | Weekly Review Assistant     | `tests/test_scenarios.py`   | `test_proc_009_weekly_review`                     | ✅     |
| **SAFE-001** | Logical Deletion            | `tests/test_regressions.py` | `test_safe_001_recursive_logical_deletion`        | ✅     |
| **SAFE-002** | Injection Delimiters        | `tests/test_server.py`      | `test_safe_002_user_data_wrapping`                | ✅     |
| **SAFE-003** | API Rate Limit Warning      | `tests/test_regressions.py` | `test_safe_003_api_rate_limit_warning`            | ✅     |
| **SAFE-004** | Breadcrumbs Context         | `tests/test_regressions.py` | `test_safe_004_breadcrumbs_visibility`            | ✅     |
| **SAFE-005** | Triage Confirmation         | `tests/test_regressions.py` | `test_safe_005_triage_safeguards`                 | ✅     |
| **SAFE-006** | Resource Shutdown           | `tests/test_regressions.py` | `test_safe_006_resource_shutdown`                 | ✅     |
| **SAFE-007** | ID Poisoning Defense        | `tests/test_regressions.py` | `test_safe_id_validation`                         | ✅     |
| **PERF-001** | Rapid Triage Benchmark      | `tests/test_scenarios.py`   | `test_phase2_task_management` (Simulated)         | ✅     |

**Legend:**
- ✅: Fully covered by automated test.
- 🟠: Partially covered or relies on live verification.
- ❌: Not yet covered.
