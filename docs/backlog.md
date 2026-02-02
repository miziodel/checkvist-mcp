---
version: 1.3.0
last_modified: 2026-02-01
status: active
---

# Checkvist MCP Server - Centralized Backlog

This document is the single source of truth for all planned improvements, architectural refinements, and vision-driven features.

## 🌟 Product Vision Features (The "Superpowers")
*Inspired by Linear, GitHub, and Superhuman.*

### Triage & Organization
- [ ] **Autonomous Inbox Smarts**: Auto-suggest categorization for items in "Inbox" based on historical project patterns.
- [ ] **Smart Snoozing (`Superhuman Style`)**: Tool to hide task branches until a specified date (via tagging or snoozing node).
- [ ] **WBS Expansion**: Tool to decompose a high-level goal into a hierarchical Work Breakdown Structure (5+ levels).
- [ ] **Hard Deletion Cleanup (Manual)**: Implement a way to physically delete tasks (bypassing logical `#deleted` archive) for space management or privacy.

### Context & Knowledge
- [ ] **Semantic Search (`Logseq/Roam Style`)**: Implement local vector embeddings for tasks to support "meaning-based" search (e.g., finding "sustainability" in "green energy" tasks).
- [ ] **Dependency Linking (`GitHub Style`)**: Implement `link_dependency(task_a, task_b)` to visually/logically mark blockers (e.g., "Blocks #123").
- [ ] **Meeting Synthesis**: Automated tool to parse transcripts and inject tasks directly into meeting nodes.

### Productivity Workflows
- [ ] **Variable Injection for Templates**: Enhance `apply_template` to support dynamic variables (e.g., `{{CLIENT_NAME}}`).
- [ ] **Progressive Distillation (`BASB Style`)**: Automated weekly cleanup to move stale items to "Archive/Stale" and generate progress summaries.

---

## 🛠 Stability & Architecture
- [ ] **Custom Exception Hierarchy**: Refactor `src/client.py` to raise typed exceptions instead of returning empty fallback values.
- [ ] **Strict Type Safety (Mypy)**: Reach 100% type hint coverage in `client.py` and enforce in CI.
- [ ] **Enhanced API Authentication**: Upgrade the authentication mechanism to be more robust (e.g., token rotation, OAuth support if applicable, or better secret management).
- [ ] **Centralized ID Coercion**: Move `int()` casting from `server.py` to `CheckvistService` for cleaner tool handlers.
- [ ] **Lazy Tree Fetching**: Optimize `get_tree` for extremely large checklists by fetching sub-branches on-demand.
- [ ] **Recursive Code Quality Review**: Establish a periodic automated or semi-automated pipeline/checklist to audit code sanity, performance, and best practices.

---

## 🧪 QA & Security
- [x] **Resilience Testing**: Implement `tests/test_regressions.py` (API 500s, 403s, Timeouts). -> *Consolidated in v1.3.0*.
- [ ] **Input Sanitization**: Implement `tests/test_input_validation.py` to verify resilience against Type Poisoning.
- [ ] **Test Hierarchy**: Reorganize `tests/` into `unit/`, `integration/`, and `orchestration/` directories.
- [ ] **Secret Masking Audit**: Verify that `CHECKVIST_API_KEY` is never leaked in tool error outputs or logs.
- [ ] **Cross-List Permission Check**: Verify that `task_id` belongs to the provided `list_id` during operations.

---

## 📊 User Research & Metrics
*Emerged from 2026-02-01 Strategic Debate*

### User Behavior Research
- [ ] **Checkvist Forum Analysis**: Research Checkvist forum to understand:
  - How users actually use Checkvist (workflows, patterns)
  - What methodologies they apply (GTD, PARA, Zettelkasten, etc.)
  - Common pain points and feature requests
  - Power user tips and undocumented features
- [ ] **User Persona Validation**: Validate "Final User" persona with real user feedback
- [ ] **Usage Pattern Analysis**: Identify common task organization patterns to inform AI triage logic

### Metrics & Observability
- [ ] **Tool Success Rate Tracking**: Implement telemetry to measure success rate per tool (target: 95%+ for Stable tools)
- [ ] **API Call Efficiency Metrics**: Track API calls per workflow to validate optimization efforts
- [ ] **User Trust Score**: Implement periodic user feedback mechanism (1-10 scale)
- [ ] **Error Message Clarity Rating**: Collect user feedback on error message usefulness

---

## 🎯 Debate-Driven Priorities (2026-02-01)
*Immediate actions from multi-persona strategic debate*

### Critical (Week 1)
- [x] **API Refactor**: Use `with_notes=true&with_tags=true` to reduce API calls by 60%
- [x] **Fix `archive_task` Regression**: Achieve 100% success rate with notes, tags, hierarchies
- [x] **Fix `apply_template` Regression**: Preserve hierarchy in all cases
- [x] **User Trust Audit**: Implement standardized error response format for all tools
- [ ] **Resource Leak Audit**: Ensure all `httpx.AsyncClient()` instances have proper `aclose()` calls
- [ ] **Smart Syntax Import Polyfill**: Implement manual parsing of `^date` and `@user` in `import_tasks` tool (Client-side workaround for API limitation).
- [ ] **Regression Monitoring**: Monitor Bug #0 (ID Mismatch) and Bug #1 (Add Note 403) via `live_verify.py` (could not reproduce locally).

### High (Week 2)
- [ ] **Scenario-to-Test Mapping**: Create `tests/scenario_mapping.md` linking SCENARIOS.md to test files
- [ ] **API Compatibility Matrix**: Document all endpoints in `docs/checkvist_api_compatibility.md`
- [ ] **Test Coverage Gap Fill**: Write missing tests for BUG-006, BUG-007, BUG-008, SAFE-006
- [ ] **Resource Lifecycle Tests**: Add automated tests for client shutdown and timeout enforcement

### Medium (Week 3)
- [ ] **Tool Maturity Classification**: Label all tools as Alpha/Beta/Stable
- [ ] **Smart Templating with Variables**: Implement `{{VARIABLE}}` injection for templates
- [ ] **Tool Sunset Policy**: Define criteria for deprecating unused/unreliable tools

---

## 🧠 Knowledge Capture & Reusability
*Patterns to extract for cross-workspace use*

- [ ] **Multi-Persona Debate Pattern**: Convert debate methodology into reusable workflow/skill
- [ ] **Extreme Consequence Analysis**: Formalize risk exploration technique
- [ ] **Tool Maturity Framework**: Extract as reusable pattern for any tool-based project
- [ ] **User Trust Metrics**: Generalize trust measurement approach

---
*Generated by consolidating SCENARIOS.md, Vision.md, Use-Cases.md, and Audit findings.*
*Updated 2026-02-01: Added insights from Multi-Persona Strategic Debate.*

---

## 🏁 Recently Completed
- [x] **Investigation**: Access "due date" view from API (Found undocumented `/checklists/due.json`). <!-- id: task-due-api -->
- [x] **New Capability**: Implemented `get_upcoming_tasks` tool and `checkvist://due` resource.
