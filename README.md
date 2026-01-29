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

## 🛠️ Quick Start

### Prerequisites
-   Python 3.10+
-   A Checkvist Account (and API Key)
-   `uv` or `pip`

### Installation

```bash
# 1. Clone & Setup
git clone <repo_url>
cd checkvist-mcp
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Configure Environment
cp .env.example .env
# Edit .env and add your CHECKVIST_USERNAME and CHECKVIST_API_KEY
```

### Running the Server

```bash
# Development Mode
mcp dev src/server.py
```

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
