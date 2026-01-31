# Checkvist MCP: Risk Mitigation Status

This document tracks the implementation status of risks identified in [risks.md](file:///Users/NOBKP/checkvist-mcp/docs/risks.md).

| Risk                        | Status         | Mitigation Strategy                                                           |
| :-------------------------- | :------------- | :---------------------------------------------------------------------------- |
| **API Rate Limiting**       | ✅ Implemented | Proactive notifications to LLM. **Next**: Async sleep.                        |
| **Token Overload**          | ✅ Implemented | `get_tree` supports `depth` parameter (default: 1).                           |
| **Parent-Trap (Ambiguity)** | ✅ Implemented | Full path breadcrumbs in search and reading tools. |

| **Smart Syntax Errors**     | 🚧 Planned     | Content validation before POST calls.                                         |
| **Privacy (Leaks)**         | 🚧 Planned     | System prompt instructions to avoid `#private` tags.                          |
| **Race Conditions**         | 🚧 Planned     | Graceful error handling for API 409/429.                                      |
| **Triage Chaos**            | ✅ Implemented | Mandatory human-in-the-loop (`confirmed` param) for bulk moves/renames. |
| **Prompt Injection**        | ✅ Implemented | XML-style data encapsulation (`<data>...</data>`).                            |
| **Logical Deletion**        | ✅ Implemented | `#deleted` tag-based filtering.                                               |


## Detailed Coverage

### 1. Token Overload (Lazy Loading)
- **Implemented in**: `get_tree(list_id, depth=1)`.
- **Status**: The server defaults to top-level tasks only. Docstrings updated to inform LLM.

### 2. API Rate Limiting
- **Implemented in**: `server.py` (`check_rate_limit` counter).
- **Status**: Triggers a `[!WARNING]` to the LLM if usage exceeds 10 calls/min. Proactive notification vs silent failure.

### 3. Logical Deletion
- **Implemented in**: `archive_task` tool and fetcher filters.
- **Status**: Tasks with `#deleted` tag are excluded from all read tools by default.

