---
version: 1.1.0
last_modified: 2026-01-31
status: active
---

# AI-Integrated PKM: Authors and Workflows

Comparative analysis of thinkers who integrate AI agents with Personal Knowledge Management (PKM) tools.

## 1. Comparative Analysis

| Author            | Approach Name             | Workflow / Process                                                                                                                      | Key Tools                   |
| :---------------- | :------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------- |
| **Dan Shipper**   | **AI-First / The Spiral** | Automates repetitive creative tasks (e.g., transcript to essay). Minimizes manual organization in favor of AI-driven synthesis.         | Spiral, Notion, Claude      |
| **Tiago Forte**   | **AI-Augmented CODE**     | AI acts as a co-pilot within the CODE (Capture, Organize, Distill, Express) framework for summarization and drafting.                   | Notion, ChatGPT, Readwise   |
| **Ethan Mollick** | **Co-Intelligence**       | Differentiates between **Centaurs** (dividing work) and **Cyborgs** (integrating work). High-frequency experimentation with multi-LLMs. | ChatGPT, Claude, Gemini     |
| **Nick Milo**     | **Generative Thinking**   | Uses AI to discover non-obvious links within a local graph (Obsidian). "Sense-making" over automation.                                  | Obsidian, Smart Connections |

## 2. Key Workflow Concepts

### The "Spiral" (Dan Shipper)
Dan Shipper focuses on identifying the "bottleneck" in a creative process and building an AI "skill" to solve it. 
- *Checkvist Tie-in:* We can create "Transformation Nodes" that take raw notes and output a specific structured format (WBS, Outline, etc.).

### Cyborgs vs. Centaurs (Ethan Mollick)
- **Centaur:** You do the outlining, AI does the writing.
- **Cyborg:** You and the AI outline and write line-by-line in a loop.
- *Checkvist Tie-in:* The MCP can operate in both modes—either taking a command to "generate a sub-tree" or "critiquing a node as you type."

### AI-Augmented Distillation (Tiago Forte)
Uses AI to perform "Progressive Summarization" automatically.
- *Checkvist Tie-in:* A tool that adds a simplified "TL;DR" note to any parent node based on its children.

### Discovery MOCs (Nick Milo)
Using AI to suggest where a new item fits in existing "Maps of Content" (MOCs).
- *Checkvist Tie-in:* A search tool that suggests parent nodes based on semantic similarity.

## 3. Practical Example Flows

### Example Flow C: The "Spiral" (Dan Shipper)
*Goal: Automated synthesis of a thematic newsletter from multiple raw sources.*

1.  **Input (Checkvist Node: `#inbox`):** User collects 5-10 links and snippets about "The future of remote work".
2.  **Trigger MCP Skill (`spiral_synthesize`):**
    *   **Agent Logic:** Fetches the content of all links, cross-references them, and identifies a central "thesis".
    *   **Transformation:** Drafts a structured outline with quotes.
3.  **Output (Checkvist Branch):**
    *   `[ ] Newsletter Draft: The Remote Revolution`
        *   `[ ] #section: The Social Cost`
        *   `[ ] #section: The Tooling Stack`
        *   `[ ] #section: Curated Links (with AI summaries)`

### Example Flow D: The "Cyborg Outlining" (Ethan Mollick)
*Goal: Interactive brainstorming and structure verification.*

1.  **Context (Checkvist Tree):** User starts a project "New Product Launch" and adds 3-4 initial nodes.
2.  **Interactive Loop (Cyborg Mode):** 
    *   **User:** "Expand the 'Marketing' node."
    *   **Agent:** Generates 5 sub-nodes.
    *   **User:** "Delete nodes 3 and 4, they are too expensive. Suggest 2 low-cost alternatives."
    *   **Agent:** Replaces them with "Viral social hook" and "Partner outreach".
3.  **Outcome:** A refined WBS that is a direct 50/50 blend of human constraint and AI creativity.

### Example Flow E: AI-Augmented Distillation (Tiago Forte)
*Goal: Summarizing a project's evolution for a weekly review.*

1.  **Input (Checkvist Branch):** A complex project branch with dozens of finished nodes and internal notes.
2.  **Trigger MCP Skill (`distill_to_tldr`):**
    *   **Agent Logic:** Reads all nodes (Capture/Organize), identifies key achievements (Distill), and writes a brief summary.
3.  **Output:** A new child node `[ ] #tldr: Progress Report Week 04` containing the distilled essence, placed at the top of the branch.

### Example Flow F: The "Semantic Explorer" (Nick Milo)
*Goal: Finding "Sense-making" connections across unrelated lists.*

1.  **Input (New Item):** User adds a task "Research bio-plastic manufacturing".
2.  **Trigger MCP Skill (`find_semantic_links`):**
    *   **Agent Logic:** Performs a semantic search across all archived and active Checkvist lists.
    *   **Discovery:** "You have a node under 'Gardening 2023' about 'compostable pots'. Would you like to link them?"
3.  **Outcome:** Creation of a cross-reference link (`checkvist://...`) between the two nodes, preventing knowledge silos.

## 4. Comparison with Teresa Torres
While Teresa aligns with the **"Agentic Transformation"** (similar to Dan Shipper), her unique angle is the **Opportunity Solution Tree (OST)** logic. The OST provides the *structural grammar* that some of the others leave more "fluid."

- **Teresa:** "Structure first, then transform."
- **Dan Shipper:** "Transform first, structure is secondary."
- **Nick Milo:** "Link first, then discover."
