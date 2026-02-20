# changelog

## [v1.3.0] - 2026-02-20

### Added (Sprint B & C)
- **Standardized Error Format (`B3`)**: Unified error responses with `error_code` (e.g., E001, E002, E004) and `suggestion` fields for improved LLM handling. *(Backlog: "User Trust Audit")*
- **Context Guard (`B1`)**: Proactive list truncation in `service.py` to prevent context window overflow (Limit: 100 items for lists, 50 for trees). *(Roadmap: "MCP-002: Structural Sampling & Context Guard")*
- **Secret Masker (`SAFE-001`)**: Custom `SecretMasker` logging filter in `src/logging_util.py` that masks `X-Client-Token`, `remote_key`, and generic token patterns in all log output. *(Roadmap: "SAFE-001: Security Hardening & Secret Masking")*
- **Prompt Injection Mitigation (`SAFE-002`)**: Automated XML-style wrapping (`<user_data>`) applied to ALL tools returning user-originated content. *(Backlog: "Prompt Injection Mitigation Audit")*
- **Granular Input Validation (`C2`)**: 
  - Centralized `parse_id` helper ensuring all IDs are positive integers.
  - Non-empty string validation for `add_task`, `import_tasks`, `add_note`, and `rename_list`.
  - *(Backlog: "Input Sanitization")*
- **Integrated Security Verification (`C1`)**: Consolidated security-sensitive tests (Secret Masker, XML Wrapping) into the core suite (`test_server.py`, `test_tools.py`) for high-velocity CI. *(Backlog: "Resilience Testing")*

### Changed
- **Error Field Renaming**: Renamed `next_steps` to `suggestion` in `StandardResponse` (Breaking Change).
- **Test Organization**: Re-structured `tests/test_regressions.py` to contain only bug-specific reproductions.
- **Response Wrapping**: Enhanced XML-style wrapping (`<user_data>`) for all user-originated content to mitigate prompt injection.
- **Resource Lifecycle**: Audited all `httpx.AsyncClient()` instances for proper `aclose()` calls and ASGI lifespan compliance. *(Backlog: "Resource Leak Audit")*

### Fixed
- **Regression Fixes**: 
  - Restored test compatibility after error format changes.
  - Fixed exact match failures in tests caused by XML wrapping implementation.
  - Verified stability of BUG-010 (cross-list parenting) via complex live integration tests.
  - Monitored and verified Bug #0 (ID Mismatch) and Bug #1 (Add Note 403) via `live_verify.py`. *(Backlog: "Regression Monitoring")*


## [v0.3.1] - 2026-02-15

### Fixed
- **MCP Configuration (`DOC-002`)**: Resolved `ModuleNotFoundError: No module named 'httpcore'` by documenting correct MCP server configuration:
  - Updated `client_setup.md` with absolute paths to `.venv/bin/python`
  - Added troubleshooting section for dependency errors
  - Verified working configuration: direct `server.py` execution (not `fastmcp run`)

### Changed
- **Documentation Reorganization (`DOC-001`)**: Restructured `docs/` folder for clarity and reduced semantic overlap:
  - Created `for-mcp-clients/` for AI agent-facing documentation (workflow guides, use cases, persona, API compatibility)
  - Created `for-developers/` for internal development guides (setup, testing, QA instructions)
  - Created `engineering/` to consolidate specifications, proposals, and bug reports
  - Moved competitive analysis to `research/competitive/`
  - Moved strategic planning sessions to `project-management/strategy/`
  - Reduced folder count from 10 to 6 (-40% reduction in top-level directories)
  - Updated `server.py` to expose 3 new MCP resources: `use-cases`, `persona`, `api-compatibility`
  - Added comprehensive README for `for-mcp-clients/` directory

### Documentation
- Updated `maintain_living_documentation` skill with MCP-specific patterns:
  - Audience separation (AI agents vs. human developers)
  - Consolidation heuristics for growing documentation sets
  - Resource exposure strategy for MCP servers

## [v0.3.0] - 2026-02-14

### Added
- **Pydantic Integration (`ARCH-001`)**: Replaced raw dictionary usage with formal `Task`, `Checklist`, and `Comment` models for robust data validation.
- **Smart Syntax Engine (`REFACTOR-001`)**: Extracted task parsing logic into `src/syntax.py` with support for due dates (`^tomorrow`), priorities (`!1`, `!!1`), tags (`#tag`), and assignments (`@user`).
- **Import Polyfill**: Enhanced `import_tasks` with client-side polyfill to support smart syntax features not natively handled by Checkvist's bulk import API.
- **Recursive Archiving**: Implemented robust deep-tree archiving logic in `service.py`, ensuring all descendants are tagged correctly even if parent IDs are mixed types.

### Changed
- **Client Refactor**: Updated `CheckvistClient` to return Pydantic models instead of raw dictionaries.
- **Service Layer**: Introduced `CheckvistService` with caching and proper invalidation for state-changing operations.
- **Search (Global)**: Updated `search_global` to handle Checkvist's native polymorphic response format (`{"commands": [...]}` vs list).

### Fixed
- **Orphaned Tasks**: Resolved a bug where descendants of archived tasks would appear as roots due to missing parent nodes in the tree construction map.
- **API Response Handling**: Improved resilience against unexpected API response types (single-item lists vs dicts) using `_to_task` helper.

## [v0.2.0] - 2026-02-07

### Added
- **High-Performance Bulk Operations**:
    - **Atomic Bulk Tagging**: Native `/tags.js` implementation for O(1) multi-task tagging.
    - **Native Bulk Re-parenting**: Integrated `/move.json` for complex multi-task reorganization.
    - **Global Search 2.0**: Integrated Checkvist native `/search/everywhere.json` to replace iterative playlist search.
    - **Advanced Task Styling**: Support for manual Priority (marks) and Boldness via the native `details` endpoint.
- **Resilience Core**:
    - **Bulk Transactionality**: Added "Verify-Before-Success" logic for `move_task` and `apply_template`.
    - **Soft Error Detection**: Refactored `_parse_checkvist_response` to catch error fields hidden in HTTP 200 responses.
- **New Tools**:
    - `get_upcoming_tasks`: Unified view for Today, Tomorrow, and Overdue tasks.
    - `weekly_review`: Summary report generator for Wins, Stale tasks, and Blocked items.
    - `checkvist://due` resource provider.

### Fixed
- **Hierarchy Loss**: Fixed `move_task` regression that caused parent/child disconnection when moving across checklists.
- **Archive Reliablity**: Improved `archive_task` to handle complex hierarchies and preserve notes/tags.

## [v0.1.0] - 2026-02-01

### Added
- **Foundational Methodology**: Established GTD/PARA compatibility roadmap.
- **Infrastructure**: ASGI Lifespan hygiene for `FastMCP`, typed exceptions, and basic auth resilience.
- **User Research**: Completed deep dive into Checkvist user patterns and forum pain points.
