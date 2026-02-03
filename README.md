---
version: 1.3.1
last_modified: 2026-02-02
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
The project is "Documentation First". All reference materials are organized in our:

- **[📖 Documentation Hub (docs/README.md)](docs/README.md)**

Start there to explore **Vision, Architecture, Use Cases**, and the **Agentic PKM Research**.

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

## 🧩 Features (Pro Suite)

| Feature                   | Status   | Description                                                                                            |
| :------------------------ | :------- | :----------------------------------------------------------------------------------------------------- |
| **Operative Intelligence**| ✅ Ready | **High-Res Search**: Breadcrumbs + [N]otes, [C]omments, and [F]igli indicators for instant context.     |
| **Drill-Down Tool**       | ✅ Ready | `get_task`: Unified fetch for notes, comments, and deep branch exploration (`include_children`).      |
| **Auth**                  | ✅ Ready | Basic Auth via API Key.                                                                                |
| **Standardized Feedback** | ✅ Ready | All tools return structured JSON with clear failure reasons and next steps.                            |
| **Optimization**          | ✅ Ready | Smart Fetch (notes/tags in a single call) prevents N+1 latencies.                                      |
| **Read Lists**            | ✅ Ready | Fetch list content (Flat).                                                                             |
| **Add Task**              | ✅ Ready | Smart Parse & Tagging.                                                                                 |
| **Smart Triage**          | ✅ Ready | Hierarchy-aware movement and movement between checklists.                                              |
| **Tree View**             | ✅ Ready | Deep exploration & Metadata.                                                                           |
| **Agenda Tool**           | ✅ Ready | Unified view across all lists for tasks due Today, Tomorrow, or Overdue (`get_upcoming_tasks`).      |
| **Weekly Review**         | ✅ Ready | Strategic summary of wins, stale tasks, and blocked items for the "Productivity Architect".            |
| **Maintenance**           | ✅ Ready | Recursive Logical Archiving (#deleted tag), Smart Syntax normalization (!! -> !), Robust Tag Handling. |

## 🛡️ "Choice Architecture" & Safety

This server follows strict **Agentic Protocols**:
1.  **Rate Limiting**: Prevents API bans by throttling "eager" agents.
2.  **Breadcrumbs**: Always provides full context ("Home > Kitchen > Milk") to prevent ambiguity.
3.  **Human-in-the-Loop**: Destructive actions (Delete/Archive) always require confirmation.

---
*Built with [FastMCP](https://github.com/jlowin/fastmcp) for the Anthropics MCP Standard.*
