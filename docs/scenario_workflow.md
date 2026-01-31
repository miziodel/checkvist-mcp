---
version: 1.0.1
last_modified: 2026-01-31
status: active
---

# scenario workflow guide

To ensure the Checkvist MCP maintains its 100% test coverage and alignment with the project vision, follow this workflow for any new feature or bug fix.

## 1. Scenario First
Before writing code, update `tests/SCENARIOS.md`.
- Assign a new Scenario ID (e.g., `TASK-006`).
- Write the expected behavior in Gherkin format.

## 2. Coverage Audit (The Gap)
Check if the scenario is covered.
- Update `tests/COVERAGE_REPORT.md` noting the new ID as "Planned".
- Identify if a new MCP tool is needed in `src/server.py`.

## 3. TDD Cycle
- Create a failing test in `tests/test_scenarios.py` referencing the Scenario ID.
- If it's a specific bug fix, use `tests/test_bug_report_verified.py` instead.
- Implement the code until the test passes.

## 4. Robustness Checklist
Check for common MCP pitfalls (from `mcp-api-forensics`):
- [ ] **Type Casting**: Are IDs cast to `int`?
- [ ] **Polymorphism**: Does it handle both `list` and `dict` responses?
- [ ] **204 Handling**: Does it use `_safe_json()`?
- [ ] **Confirmation**: Does destructive logic require a `confirmed` flag?

## 5. Verification
Run the full suite to ensure no regressions:
```bash
pytest tests/
```
Target: All tests (currently 58+) must pass.
