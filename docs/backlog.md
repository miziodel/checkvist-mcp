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
- [x] **Autonomous Inbox Smarts**: Auto-suggest categorization for items in "Inbox" based on historical project patterns. (Shipped Phase 1.3 - Triage Heuristics)
- [ ] **Hierarchical Search (`search_tasks_enriched`)**: Return task breadcrumbs to solve "Hierarchical Blindness". (Planned for **Phase 1.2**)
- [ ] **Smart Snoozing (`Superhuman Style`)**: Tool to hide task branches until a specified date (via tagging or snoozing node).
- [ ] **WBS Expansion**: Tool to decompose a high-level goal into a hierarchical Work Breakdown Structure (5+ levels).
- [ ] **Hard Deletion Cleanup (Manual)**: Implement a way to physically delete tasks (bypassing logical `#deleted` archive) for space management or privacy.

### Context & Knowledge
- [ ] **Semantic Search (`Logseq/Roam Style`)**: Implement local vector embeddings for tasks to support "meaning-based" search. (Planned for **Phase 2.0**)
- [ ] **Dependency Linking (`GitHub Style`)**: Implement `link_dependency(task_a, task_b)` to visually/logically mark blockers (e.g., "Blocks #123").
- [ ] **Meeting Synthesis**: Automated tool to parse transcripts and inject tasks directly into meeting nodes.

### Productivity Workflows
- [x] **Variable Injection for Templates**: Enhance `apply_template` to support dynamic variables (e.g., `{{CLIENT_NAME}}`). (Shipped Phase 1.3)
- [ ] **Progressive Distillation (`BASB Style`)**: Automated weekly cleanup to move stale items to "Archive/Stale" and generate progress summaries.

### High-Performance Bulk Operations (Forensics Phase 2.0)
- [ ] **Atomic Bulk Tagging**: Use native `/tags.js` for O(1) multi-tagging.
- [ ] **Native Bulk Re-parenting**: Use `/move.json` for complex reorganization without iterative calls.
- [ ] **Global Search 2.0**: Replace iterating playlist search with native `/search/everywhere.json`.
- [ ] **Task Styling API**: Implement tool for setting Priority (marks) and Boldness via native `details` endpoint.

---

## 🛠 Stability & Architecture
- [x] **Custom Exception Hierarchy**: Refactor `src/client.py` to raise typed exceptions (e.g., `CheckvistAPIError`). (Shipped 2026-02-06)
- [ ] **Strict Type Safety (Mypy)**: Reach 100% type hint coverage in `client.py` and enforce in CI.
- [ ] **Enhanced API Authentication**: Upgrade the authentication mechanism to be more robust (e.g., token rotation, OAuth support if applicable, or better secret management).
- [ ] **Centralized ID Coercion**: Move `int()` casting from `server.py` to `CheckvistService` for cleaner tool handlers.
- [x] **Lazy Tree Fetching**: Optimize `get_tree` for extremely large checklists by fetching sub-branches on-demand. (Shipped Phase 1.3)
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
- [x] **Checkvist Forum Analysis**: Research Checkvist forum to understand workflows, methodologies (GTD, PARA), and pain points. -> *Completed 2026-02-01 in `docs/research/user_research_2026_02.md`*.
- [ ] **User Persona Validation**: Validate "Final User" persona with real user feedback (Initial validation done in research doc).
- [ ] **Usage Pattern Analysis**: Identify common task organization patterns to inform AI triage logic. -> *Initial heuristics defined in `docs/research/smart_triage_heuristics.md`*.

### Metrics & Observability
- [ ] **Tool Success Rate Tracking**: Implement telemetry to measure success rate per tool (target: 95%+ for Stable tools)
- [ ] **API Call Efficiency Metrics**: Track API calls per workflow to validate optimization efforts
- [ ] **User Trust Score**: Implement periodic user feedback mechanism (1-10 scale)
- [ ] **Error Message Clarity Rating**: Collect user feedback on error message usefulness

### Phase 7: Performance & Velocity (PERF)
*New focus area from Productivity Architect validation*
- [ ] **Benchmark Suite**: Implement `tests/test_benchmark.py` for Triage (target < 30s) and Tree Fetch (target < 5s).
- [ ] **Latency Monitoring**: Add `X-Response-Time` tracking to all service calls.

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
- [x] **Scenario-to-Test Mapping**: Create `tests/scenario_mapping.md` linking SCENARIOS.md to test files
- [x] **API Compatibility Matrix**: Document all endpoints in `docs/checkvist_api_compatibility.md`
- [x] **Test Coverage Gap Fill**: Write missing tests for BUG-006, BUG-007, BUG-008, SAFE-006
- [ ] **Resource Lifecycle Tests**: Add automated tests for client shutdown and timeout enforcement

### Medium (Week 3)
- [x] **Tool Maturity Classification**: Label all tools as Alpha/Beta/Stable
- [x] **Smart Templating with Variables**: Implement `{{VARIABLE}}` injection for templates (Implemented as `apply_template` confirm/logic)
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

## 🎯 Debate-Driven Priorities (2026-02-06)
*Strategic alignment after Technical Stability implementation*

### Critical
- [ ] **Soft Error Audit**: Refactor `_safe_json` to `_parse_checkvist_response` to detect error fields in 200 OK payloads.
- [ ] **Connection Hygiene Research**: Find the hook for `FastMCP` teardown (ASGI lifespan) to ensure `aclose()` is guaranteed.
- [ ] **Bulk Transactionality**: Implement "Verify-Before-Success" for `move_task` and `apply_template`.

---

## 🏁 Recently Completed
- [x] **Technical Stability Foundation**: Implemented Typed Exception Hierarchy and Client Refactor (2026-02-06).
- [x] **Investigation**: Access "due date" view from API (Found undocumented `/checklists/due.json`). <!-- id: task-due-api -->
- [x] **New Capability**: Implemented `get_upcoming_tasks` tool and `checkvist://due` resource.
- [x] **Capability**: Implemented `weekly_review` tool for Productivity Architect (Wins/Stale/Blocked analysis).
- [x] **Documentation**: Added `PERF-001` benchmark to SCENARIOS.md and VERIFICATION_GUIDE.md.
- [x] **Bug Fix**: `move_task` hierarchy loss across lists (Fixed 2026-02-04).
- [x] **API Proposal**: [Bulk Operations & Advanced Styling](proposals/2026-02-06_bulk_and_styling_api.md) (Created 2026-02-06).

