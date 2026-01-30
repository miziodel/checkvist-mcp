---
version: 1.1.0
last_modified: 2026-01-28
status: active
---

# 🧠 Checkvist MCP: The "Productivity OS" for Agents

> **Transform Checkvist from a simple outliner into an Agentic Neural Network.**

This MCP server acts as the bridge between your LLM (Claude, Gemini, etc.) and your Checkvist life. It doesn't just "read lists"; it understands **context**, manages **triage**, and finds **connections**.

## 🚀 The Vision

We are building a server that emulates the best "Pro" workflows from top productivity tools:

*   **Linear-Style Triage**: Inbox Zero via AI-assisted sorting.
*   **GitHub-Style Deps**: "Blocker" awareness and dependency management.
*   **Readwise-Style Recall**: Serendipitous resurfacing of old ideas.
*   **Superhuman-Style Focus**: Smart snoozing and context hiding.

[Read the Full Vision](docs/vision.md)

## 📚 Documentation

The project is structured to be "Documentation First". Start here:

-   **[Vision & Roadmap](docs/vision.md)**: The "Why" and "What".
-   **[Use Cases](docs/use-cases.md)**: 10 Core scenarios and 10 "Pro" agentic flows.
-   **[Risks & Mitigation](docs/risks.md)**: Critical analysis of API limits, privacy, and token costs.
-   **[Architecture](docs/architecture.md)**: The technical design (FastMCP + Python).
-   **[The Squad (AGENTS.md)](AGENTS.md)**: Who is building this?
-   **[Functional Scenarios](tests/SCENARIOS.md)**: Gherkin-style walkthrough of every feature.
-   **[Human Testing Playbook](tests/PLAYBOOK.md)**: Manual scenarios for "Vibe Checking".
-   **[Verification Guide](tests/VERIFICATION_GUIDE.md)**: How we test (TDD + Stateful Mocks).
-   **[Client Setup Guide](docs/client_setup.md)**: How to configure the server in your LLM client.

## 🛠️ Quick Start

### Prerequisites
-   Python 3.10+
-   A Checkvist Account (and API Key)
-   `uv` or `pip`

### Installation

```bash
# 1. Clone & Setup
git clone git@github.com:miziodel/checkvist-mcp.git
cd checkvist-mcp
python3.11 -m venv .venv
source .venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Configure Environment
cp .env.example .env
# Edit .env and add your CHECKVIST_USERNAME and CHECKVIST_API_KEY
```

> [!IMPORTANT]
> **Mandatory Virtual Environment**: All commands MUST be run with the virtual environment activated. 
> The Antigravity agent is configured to always use `source .venv/bin/activate && <command>` to ensure consistency and avoid "command not found" errors.

### Running the Server

```bash
# Development Mode (Active venv required)
source .venv/bin/activate && fastmcp dev src/server.py
```

### 🔌 Client Integration

To use this server in **Antigravity**, you can add it directly via the **Settings > MCP** menu.

See the **[Client Setup Guide](docs/client_setup.md)** for a ready-to-use JSON snippet and detailed instructions.

## 🧩 Features (WIP)

| Feature | Status | Description |
| :--- | :--- | :--- |
| **Auth** | ✅ Ready | Basic Auth via API Key. |
| **Read Lists** | ✅ Ready | Fetch list content (Flat). |
| **Add Task** | ✅ Ready | Simple append to bottom. |
| **Smart Triage** | 🚧 Planned | Inbox management & moves. |
| **Context** | 🚧 Planned | Deep search & Breadcrumbs. |
| **Tree View** | 🚧 Planned | Hierarchy-aware fetching. |

## 🛡️ "Choice Architecture" & Safety

This server follows strict **Agentic Protocols**:
1.  **Rate Limiting**: Prevents API bans by throttling "eager" agents.
2.  **Breadcrumbs**: Always provides full context ("Home > Kitchen > Milk") to prevent ambiguity.
3.  **Human-in-the-Loop**: Destructive actions (Delete/Archive) always require confirmation.

---
*Built with [FastMCP](https://github.com/jlowin/fastmcp) for the Anthropics MCP Standard.*
