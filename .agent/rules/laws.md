---
trigger: always_on
---

# PROJECT LAWS

1. **Documentation First**: No implementation starts without a clear description in the docs or implementation plan.
2. **Automatic Tests Before Code (TDD)**: Every feature must have a failing test before implementation begins.
3. **MCP Ease of Use**: The server must be intuitive for LLM clients to consume.
4. **Organic Storage**: Checkvist must be treated as a fluid storage for notes and todos, not just a rigid database.
5. **No Blind Commits**: Final commits must ALWAYS be approved by the user before execution.
6. **Mandatory .venv**: All commands and development activities MUST be performed within the project's virtual environment (`.venv`), each command must activate the venv first.
7. **Relative Documentation Links**: All internal links between `.md` files must use relative paths. Absolute paths or `file://` URIs are prohibited to ensure portability.
8. **Secrets Sanctity**: NEVER attempt to read, print, or access the content of `.env` files or any other secret configuration files. Refer to secrets only by their environment variable names.
9. **Global Workflow Discovery**: If a requested workflow (e.g., via a slash command) is not found in the local `.agent/workflows/` directory, the agent MUST search in the global directory `/Users/mauriziowep/.gemini/antigravity/global_workflows/` before reporting it as missing.
