---
trigger: always_on
---

# 01 - PROCESS & APPROVALS

1. **Documentation First**: No implementation starts without a clear description in the docs or implementation plan.
2. **No Blind Commits**: Final commits must ALWAYS be approved by the user before execution.
3. **Global Workflow Discovery**: If a requested workflow (e.g., via a slash command) is not found in the local `.agent/workflows/` directory, the agent MUST search in the global directory `~/.gemini/antigravity/global_workflows/` before reporting it as missing.
4. **Terminal Escalation for Permissions**: If any command fails with 'Operation not permitted' or 'Permission denied' due to environment restrictions (e.g., executing binaries from `.venv`), the Agent MUST stop and provide the full command for the USER to execute manually.
5. **Parallel Session Preservation**: NEVER modify, stage, or delete files that are not already staged in the git index. These files may belong to parallel work sessions. Only interact with files relevant to the current task's approved implementation plan.
6. **Mandatory Plan Sections**: Every Implementation Plan MUST include a "Documentation & Awareness Plan" section. This section must detail how the changes will be communicated to the USER (via README.md) and to other LLM clients (via docstrings or configuration updates).
