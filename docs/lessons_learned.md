---
version: 1.2.0
last_modified: 2026-02-01
status: active
---

# Lessons Learned: Checkvist MCP Development

## ⚙️ Technical Insights

### 1. Checkvist API Quirks
- **Unpredictable Response Types**: The `close_task` endpoint (and potentially others) can return a list `[{"id": ...}]` instead of a dictionary even for single actions. Always use robust type checking (`isinstance()`) before accessing keys.
- **Undocumented/Non-functional Endpoints**: The `move.json` POST endpoint (often guessed for moves) exists but returns an empty body and performs no action for cross-list moves. 
- **Hidden Signatures**: Cross-list moves are correctly achieved via a **PUT request to the task endpoint with `task[checklist_id]`**.
- **Type Coercion**: LLM clients may send IDs as strings. Explicitly casting input parameters to `int` in the tool layer prevents `TypeError` and `AttributeError` during API calls.
- **Payload Location Hygiene**: For `POST` operations involving large text (imports), avoid query parameters (`params`). Some servers hang or return 414. Always use the request body (`data` or `json`).
- **API Efficiency Opportunity** (2026-02-01): The Checkvist API supports `?with_notes=true&with_tags=true` parameters to fetch task metadata in a single call. Using these parameters can reduce API calls by 60% and simplify error handling (1 call = 1 failure mode vs 3).
- **Smart Syntax Limits in Import**: The `/import.json` endpoint supports priority (`!N`) and tags (`#tag`), but **NOT** due dates (`^date`) or assignments (`@user`). These must be set via `update_task` after import. Attempting to use them in import results in raw text.

### 2. Resource Lifecycle Management
- **Persistent Clients & Timeouts**: Asynchronous clients like `httpx` must have explicit timeouts (e.g., 10s) and a forced shutdown hook (`aclose()`) to prevent resource leaks and "hanging" processes during testing or production.
- **Verification Script Hygiene** (2026-02-01): Long-running verification scripts (1h+) indicate resource leaks. All async clients must be properly closed in `finally` blocks, and scripts should have maximum runtime enforcement.

### 3. Robust Error Handling
- **Passthrough vs. Friendly Errors**: Avoid passing raw Python exceptions to the MCP client. Use `try...except` in tools to return a formatted string that help the LLM understand what went wrong and how to fix it (e.g., "Invalid ID format" vs. `ValueError`).
- **Standardized Error Format** (2026-02-01): All tools should return errors in a consistent format: `{"success": bool, "message": str, "action": str, "next_steps": str}` to improve LLM comprehension and user trust.

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

---

**Related Documentation**:
- [Strategic Debate (2026-02-01)](strategy/260201/project_debate.md)
- [Critical Insights](strategy/260201/critical_insights.md)
- [3-Week Sprint Roadmap](roadmap_3week_sprint.md)

