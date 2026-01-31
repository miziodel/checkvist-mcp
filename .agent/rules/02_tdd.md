---
trigger: always_on
---

# 02 - TEST-DRIVEN DEVELOPMENT

1. **Automatic Tests Before Code (TDD)**: Every feature must have a failing test before implementation begins.
2. **Internalized TDD Workflow**: You MUST follow the standardized TDD procedure defined in `.agent/workflows/tdd-cycle.md` for any bug fix or new tool implementation.
3. **Scenario-Driven Coverage Audit**:
    - Periodically (or upon major tool changes), the Agent MUST audit the test suite against `tests/SCENARIOS.md`.
    - Every Scenario ID (e.g., `TASK-001`) MUST be mapped to a specific test or assertion.
    - If a gap is identified, it MUST be documented in `tests/COVERAGE_REPORT.md` before implementation begins.
