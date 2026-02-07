# 04 - TEST MODULE REUSE

1. **Reuse Existing Test Modules**: DO NOT create new test files if the logic can fit into existing ones (e.g., `tests/test_client.py`, `tests/test_service.py`, `tests/test_server.py`). Only create new files for entirely new architectural layers or isolated scenarios.
2. **Standardized Regression Testing**: Always add reproduction tests for bugs to `tests/test_regressions.py` as per `02_tdd.md`.
