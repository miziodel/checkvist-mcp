---
description: Workflow to safely close a session by ensuring work from ONLY this session is preserved and documented.
---

# Session Cleanup & Close Workflow

This workflow ensures that a coding session ends cleanly, with all work committed, tested, and documented, ready for the next session.

1.  **Verify Tests**: Ensure all tests (especially regressions) are passing.
    `pytest tests/test_scenarios.py` (or relevant test suite)

2.  **Audit Workspace**: Check for temporary files or directories that need cleanup.
    `ls -R src/` (Check for __pycache__ or temp files to ignore)

3.  **Update Strategic Docs** (CRITICAL):
    -   Mark completed items in `docs/roadmap*.md`.
    -   Update `docs/backlog.md`.
    -   Ensure `task.md` is up to date.

4.  **Finalize Artifacts**:
    -   Embed final screenshots or outputs in `walkthrough.md`.
    -   Ensure `implementation_plan.md` reflects what was actually built.

5.  **Notify User**:
    -   Send a final `notify_user` summary confirming the session is closed and docs are synced.
