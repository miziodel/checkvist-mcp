version: 1.3.1
last_modified: 2026-02-07
status: active

# Lessons Learned: Checkvist MCP Development

## ⚙️ Technical Insights

### 1. Checkvist API Quirks
- **Unpredictable Response Types**: The `close_task` endpoint (and potentially others) can return a list `[{"id": ...}]` instead of a dictionary even for single actions. Always use robust type checking (`isinstance()`) before accessing keys.
- **Undocumented/Non-functional Endpoints**: The `move.json` POST endpoint (often guessed for moves) exists but returns an empty body and performs no action for cross-list moves. 
- **Hidden Signatures**: Cross-list moves are correctly achieved via a **PUT request to the task endpoint with `task[checklist_id]`**.
- **Type Coercion**: LLM clients may send IDs as strings. Explicitly casting input parameters to `int` in the tool layer prevents `TypeError` and `AttributeError` during API calls.
- **Payload Location Hygiene**: For `POST` operations involving large text (imports), avoid query parameters (`params`). Some servers hang or return 414. Always use the request body (`data` or `json`).
- **API Call Efficiency Opportunity** (2026-02-01): The Checkvist API supports `?with_notes=true&with_tags=true` parameters to fetch task metadata in a single call. Using these parameters can reduce API calls by 60% and simplify error handling.
- **Soft Error Detection (2026-02-07)**: Many API endpoints return HTTP 200 OK even when a logical failure occurs (e.g. "task not found" error message in a JSON field). Robust clients MUST parse 200 OK payloads for known error indicators and raise appropriate exceptions.
- **Partial Failure Atomicity (2026-02-07)**: For multi-step operations (like cross-list move + re-parent), implement "Verify-Before-Success". If a step fails, raise a typed `CheckvistPartialSuccessError` containing the state of the first successful step to prevent "Ghost Tasks" orphans.
- **Smart Syntax Limits in Import**: The `/import.json` endpoint supports priority (`!N`) and tags (`#tag`), but **NOT** due dates (`^date`) or assignments (`@user`). These must be set via `update_task` after import. Attempting to use them in import results in raw text.
- **Hidden "Due View" Endpoint** (2026-02-02): While the official API documentation lacks a global "due tasks" filter, a hidden endpoint `/checklists/due.json` exists (discovered via browser network traffic inspection). It returns all tasks with a due date across all lists, which is much more efficient than client-side scanning.

### 2. Resource Lifecycle Management
- **Persistent Clients & Timeouts**: Asynchronous clients like `httpx` must have explicit timeouts (e.g., 10s) and a forced shutdown hook (`aclose()`) to prevent resource leaks and "hanging" processes during testing or production.
- **ASGI Lifespan Integration (2026-02-07)**: For long-running MCP servers, leveraging the ASGI lifespan protocol ensures that dependencies (like API clients) are gracefully closed even during unexpected server terminations.
- **Verification Script Hygiene** (2026-02-01): Long-running verification scripts (1h+) indicate resource leaks. All async clients must be properly closed in `finally` blocks, and scripts should have maximum runtime enforcement.

### 3. Robust Error Handling
- **Passthrough vs. Friendly Errors**: Avoid passing raw Python exceptions to the MCP client. Use `try...except` in tools to return a formatted string that help the LLM understand what went wrong and how to fix it (e.g., "Invalid ID format" vs. `ValueError`).
- **Standardized Error Format** (2026-02-01): All tools should return errors in a consistent format: `{"success": bool, "message": str, "action": str, "next_steps": str}` to improve LLM comprehension and user trust.
- **Recursive Archiving Resilience (2026-02-07)**: High-latency operations like large branch archiving should use a "Collect and Report" pattern. Instead of failing on the first error, collect all failures and return a summary report to the user, ensuring maximum progress is made.

## 🛠 Workflow Lessons

### 1. Strict TDD (Scenarios -> Tests -> Code)
- Following the **Scenarios -> Tests -> Implementation** loop ensures that:
    - Root causes are understood before fixing (Reproduction).
    - Success criteria are clearly defined in `SCENARIOS.md`.
    - Regressions are prevented by integrating new tests into the main suite.
- **Test Coverage as Insurance** (2026-02-01): Every untested scenario is a future regression waiting to happen. Aim for 90%+ scenario-to-test mapping.

### 2. Risk Management
- **Delayed Implementation of Destructive Tools**: Postponing `delete_task` was a deliberate choice to evaluate the risk of accidental data loss by the agent. High-risk operations should require more stringent validation or user confirmation cycles.

### 3. Safety Patterns (Defense in Depth)
- **Breadcrumbs Context**: Tools returning nested data must provide the full path (breadcrumbs) to avoid "Parent-Trap" ambiguity where similar task names are indistinguishable.
- **HIL (Human-in-the-loop)**: Structural or bulk operations (move, migrate) should implement mandatory confirmation via a `confirmed` parameter to prevent accidental triage chaos.
- **XML Encapsulation**: Wrapping user-generated data in XML tags (`<user_data>`) effectively builds a trust boundary that mitigates prompt injection risks.

## 🤖 Agentic Best Practices

- **Autonomous Flux**: Tools like `create_list` empower the agent to manage its own organization without pre-existing structures, increasing its value in greenfield projects.
- **Documentation as Memory**: Keeping `risks.md`, `architecture.md`, and `checkvist_api.md` updated ensures that future agents (or the same agent in future sessions) don't repeat the same mistakes.

## 🎯 Strategic Insights (2026-02-01 Multi-Persona Debate)

### 1. The Binary Trust Principle
**Discovery**: In productivity/reliability-critical systems, user trust is binary, not gradual.

**Formula**: `User Trust = min(reliability_of_all_tools)`

**Implication**: One broken tool destroys trust in the entire system. Aim for 100% reliability on core operations before adding features.

### 2. API Forensics > New Features
**Discovery**: Understanding existing tools deeply often yields more value than building new ones.

**Example**: Discovering `?with_notes=true&with_tags=true` parameter fixed 2 regressions and improved performance 60%.

**Implication**: "Use the tools correctly" before "build more tools". Invest in API compatibility documentation.

### 3. Tool Maturity Framework
**Discovery**: Not all features should be treated equally or exposed by default.

**Classification**:
- **Alpha**: Experimental, can fail, requires `confirmed=True`
- **Beta**: Tested, clear errors, 80%+ success rate
- **Stable**: Battle-tested, 95%+ success rate, production-ready

**Implication**: Expose only Beta+ tools to LLM by default. Alpha tools require explicit opt-in.

### 4. Stability Before Features
**Discovery**: Feature velocity without stability leads to user abandonment.

**Consensus**: All 6 personas in strategic debate agreed: freeze features when core reliability drops below 95%.

**Implication**: Implement "red lines" - if critical tools fail, stop feature development and stabilize.

### 5. Multi-Persona Decision Making
**Discovery**: Critical decisions benefit from simulating multiple stakeholder perspectives.

**Method**: Architect, Developer, QA, User, Domain Expert, PM personas debate with extreme consequence analysis.

**Implication**: Use strategic debate methodology (now captured as global skill) for major architectural decisions.

**Reference**: See `docs/strategy/260201/` for full debate transcript and synthesis.

### 6. User Research Validates Design Decisions (2026-02-01)
**Discovery**: Real user behavior research confirms architectural priorities.

**Method**: Analyzed [Checkvist forums](https://discuss.checkvist.com/) to understand how power users actually work.

**Key Findings**:
- **Keyboard-First Obsession**: Users measure success by "how few mouse clicks". Any automation must be faster than manual shortcuts (`LL`, `MM`).
- **PARA + GTD Dominance**: Users rely on numerical prefixes (`1. Projects`) and context tags (`#work`) for organization.
- **Triage Overhead**: Manual inbox processing is the #1 pain point - perfect target for AI automation.

**Implication**: The "Productivity Architect" persona demands that every tool respects speed and hierarchy. Features like `triage_inbox` are now validated by real user needs, not assumptions.

**Reference**: See [User Research (Feb 2026)](research/user_research_2026_02.md) and [Smart Triage Heuristics](research/smart_triage_heuristics.md).

---

**Related Documentation**:
- [User Persona](persona.md)
- [User Research (Feb 2026)](research/user_research_2026_02.md)
- [Strategic Debate (2026-02-01)](strategy/260201/project_debate.md)
- [Critical Insights](strategy/260201/critical_insights.md)
- [3-Week Sprint Roadmap](roadmap_3week_sprint.md)

