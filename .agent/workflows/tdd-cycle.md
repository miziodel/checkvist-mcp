---
description: 
---

# 🔄 Workflow: TDD Cycle (Bug Fix & Feature)

This workflow is mandatory for all core implementation changes in the Checkvist MCP project.

1. **Scenario Definition**: Add the expected behavior to `tests/SCENARIOS.md` using Gherkin-style syntax.
2. **Reproduction**: Create a temporary test file (e.g., `tests/test_repro.py`) that demonstrates the failure or missing feature.
3. **Implementation**: 
    - First, update the `CheckvistClient` in `src/client.py` if needed.
    - Then, implement/update the tool in `src/server.py`.
    - Apply **Defensive Tooling** patterns (type casting and response type checking).
4. **Integration**: Move the tests into the main test suite (`tests/test_client.py`, `tests/test_server.py`, or `tests/test_functional_mock.py`).
5. **Full Verification**: Run the entire test suite:
   ```bash
   python -m pytest tests
   ```
6. **Audit**: Run the `meta-audit` to ensure compliance:
   ```bash
   python ~/.gemini/antigravity/skills/meta-audit/scripts/audit_engine.py /Users/NOBKP/checkvist-mcp
   ```
