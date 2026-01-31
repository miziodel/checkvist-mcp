# Lessons Learned: Checkvist MCP Development

## ⚙️ Technical Insights

### 1. Checkvist API Quirks
- **Unpredictable Response Types**: The `close_task` endpoint (and potentially others) can return a list `[{"id": ...}]` instead of a dictionary even for single actions. Always use robust type checking (`isinstance()`) before accessing keys.
- **Type Coercion**: LLM clients may send IDs as strings. Explicitly casting input parameters to `int` in the tool layer prevents `TypeError` and `AttributeError` during API calls.

### 2. Robust Error Handling
- **Passthrough vs. Friendly Errors**: Avoid passing raw Python exceptions to the MCP client. Use `try...except` in tools to return a formatted string that help the LLM understand what went wrong and how to fix it (e.g., "Invalid ID format" vs. `ValueError`).

## 🛠 Workflow Lessons

### 1. Strict TDD (Scenarios -> Tests -> Code)
- Following the **Scenarios -> Tests -> Implementation** loop ensures that:
    - Root causes are understood before fixing (Reproduction).
    - Success criteria are clearly defined in `SCENARIOS.md`.
    - Regressions are prevented by integrating new tests into the main suite.

### 2. Risk Management
- **Delayed Implementation of Destructive Tools**: Postponing `delete_task` was a deliberate choice to evaluate the risk of accidental data loss by the agent. High-risk operations should require more stringent validation or user confirmation cycles.

### 3. Safety Patterns (Defense in Depth)
- **Breadcrumbs Context**: Tools returning nested data must provide the full path (breadcrumbs) to avoid "Parent-Trap" ambiguity where similar task names are indistinguishable.
- **HIL (Human-in-the-loop)**: Structural or bulk operations (move, migrate) should implement mandatory confirmation via a `confirmed` parameter to prevent accidental triage chaos.
- **XML Encapsulation**: Wrapping user-generated data in XML tags (`<user_data>`) effectively builds a trust boundary that mitigates prompt injection risks.

## 🤖 Agentic Best Practices


- **Autonomous Flux**: Tools like `create_list` empower the agent to manage its own organization without pre-existing structures, increasing its value in greenfield projects.
- **Documentation as Memory**: Keeping `risks.md`, `architecture.md`, and `checkvist_api.md` updated ensures that future agents (or the same agent in future sessions) don't repeat the same mistakes.
