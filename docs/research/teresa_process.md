---
version: 1.1.0
last_modified: 2026-01-31
status: active
---

# Teresa Torres' "Agentic Discovery" Process

This document synthesizes Teresa Torres' recent methodology for using AI agents and hierarchical structures to manage complex work and personal discovery.

## 1. The Transformation Engine
Teresa's writing and discovery process has evolved from a manual "brain dump and outline" to an AI-assisted sequence:

| Phase          | Description                                                                   | Output               |
| :------------- | :---------------------------------------------------------------------------- | :------------------- |
| **Input**      | A "messy" brain dump of thoughts, notes, or interview transcripts.            | Raw Text / Notes     |
| **Process**    | A defined "Transformation Engine" (Agent/Prompt) that follows a set of rules. | Structured Data      |
| **Automation** | Identifying high-frequency/friction steps and creating "skills" for them.     | Reusable Workflows   |
| **Output**     | Multiple derivatives: outlines, social logs, and actionable tasks.            | Multi-format exports |

## 2. OST in Everyday Life (The Hierarchy)
Teresa applies the Opportunity Solution Tree (OST) to personal management, which maps perfectly to an outliner like Checkvist.

### The Structure:
1.  **Outcome (Node Level 1):** The high-level goal (e.g., "Improve physical wellbeing").
2.  **Root Opportunities (Node Level 2):** Based on **Maslow’s Hierarchy** (Wellness, Safety, Belonging, Esteem, Growth).
3.  **Opportunities (Node Level 3):** Specific pain points or desires (e.g., "I feel tired by 3 PM").
4.  **Solutions (Node Level 4):** Potential ideas to address opportunities (e.g., "Take a 15-min walk").
5.  **Experiments (Node Level 5 - Actions):** The actual tasks to perform.

### Visual Cues & Meta-data:
- **Tags:** Use `#outcome`, `#opp`, `#sol`, `#exp`.
- **Status/Color:** Use Checkvist colors or emoji status indicators to represent progress.

## 3. Core Principles of the Torres Workflow

Beyond the structure, these principles are what make the workflow "efficient":

1.  **Separation of Outcome and Solution**: The Outcome stays fixed for a period; Solutions are many and disposable. Never put a solution in a top-level node.
2.  **Depth is Search**: Every level of nesting in Checkvist represents a deeper "Why" or a more granular "How".
3.  **Everything is an Experiment**: Tasks are not just "to-dos"; they are tests (`#exp`). If an experiment fails, it's not a failure, but a "lesson learned" (`#lesson`).
4.  **Evidence-Based Branching**: You only expand a Solution node into task nodes if you have evidence that the Solution might solve the Opportunity.
5.  **Focus on Energy, not Time**: Using Maslow's roots (Wellness, etc.) ensures that you aren't just productive, but sustainable.

## 4. Practical Example Flows

### Example Flow A: The "Content Machine" (Transformation Engine)
*Goal: Turn 15 minutes of random voice notes into a structured content roadmap.*

1.  **Input (Checkvist Node: `#inbox`):** User dictates a messy brain dump about "Integrating MCP with Checkvist".
2.  **Trigger MCP Skill (`brain_dump_to_ost`):**
    *   **Agent Logic:** Analyzes raw text for *Needs* (Opportunities) and *Proposed Actions* (Solutions).
    *   **Mapping:** Creates a new branch under "MCP Project".
3.  **Output (Checkvist Branch):**
    *   `[ ] #opp: Users find it hard to configure API keys`
        *   `[ ] #sol: Create a step-by-step setup script`
            *   `[ ] #exp: Test script with a new user`
    *   `[ ] #opp: Confusion between 'Tasks' and 'Skills'`
        *   `[ ] #sol: Add a 'Definitions' section to the docs`

### Example Flow B: The "Strategic Pivot" (Living Roadmap)
*Goal: Adjust a career path based on recent feedback.*

1.  **Context (Checkvist Tree):** Career Roadmap node has several `#sol` (e.g., "Get AWS Certification").
2.  **Trigger MCP Skill (`critique_branch`):**
    *   **Agent Logic:** Checks recent `#lesson` tags in the branch.
    *   **Analysis:** "You failed 3 experiments related to AWS; perhaps the opportunity 'Technical Scaling' should be addressed via 'Serverless' instead?"
3.  **Outcome:** The Agent suggests a pivot, re-tagging the AWS node as `#archived` and creating a new `#sol` branch for "Google Cloud Functions".

## 5. The 2026 Vision: Expert AI Feedback
The next stage is the **AI Discovery Co-pilot**:
- Moving from just "managing lists" to "critiquing strategy".
- The AI acts as a "Coach", providing feedback on the tree structure itself (e.g., "Your experiments don't clearly address the opportunity 'low energy'").

## 6. Input/Output Loop with MCP
- **Skill 1:** `brain_dump_to_ost`: Takes raw text and populates a Checkvist branch with `#opp` and `#sol` nodes.
- **Skill 2:** `critique_ost_branch`: Analyzes a specific Checkvist branch and adds "Coach Feedback" comments/nodes.
