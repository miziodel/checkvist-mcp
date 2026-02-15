---
version: 1.0.0
last_modified: 2026-02-15
status: active
category: mcp-client-documentation
---

# Documentation for MCP Clients

This directory contains documentation specifically designed to help AI agents (MCP clients) use the Checkvist MCP server effectively.

## Available Resources

All documents in this directory are exposed as MCP resources with the URI pattern: `checkvist://docs/{name}`

### Core Guides

- **[workflow_guide.md](workflow_guide.md)** (`checkvist://docs/workflow-guide`)
  - Practical guide for agentic workflows
  - Covers OST (Opportunity Solution Tree), Transformation Engine, and other advanced patterns
  - **Use when**: Agent needs to understand how to orchestrate complex workflows

- **[use_cases.md](use_cases.md)** (`checkvist://docs/use-cases`)
  - Concrete scenarios and examples
  - Linear-style triage, GitHub-style dependencies, Readwise-style recall
  - **Use when**: Agent needs to understand WHEN to use specific tools

- **[persona.md](persona.md)** (`checkvist://docs/persona`)
  - The "Productivity Architect" mindset
  - Tone, approach, and philosophy for interacting with users
  - **Use when**: Agent needs guidance on communication style

### Technical Reference

- **[api_compatibility.md](api_compatibility.md)** (`checkvist://docs/api-compatibility`)
  - Known limitations of the Checkvist API
  - Common pitfalls and workarounds
  - **Use when**: Agent encounters unexpected API behavior

## How to Access

MCP clients can access these resources using the `read_resource` tool:

```python
# Example: Reading the workflow guide
resource = await mcp.read_resource("checkvist://docs/workflow-guide")
```

## For Developers

If you're a human developer looking for setup instructions, testing guides, or internal documentation, see:
- [../for-developers/](../for-developers/) - Development guides
- [../api-reference/](../api-reference/) - Checkvist API documentation
- [../project-management/](../project-management/) - Project strategy and planning
