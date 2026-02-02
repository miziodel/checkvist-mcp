# Checkvist User Research (February 2026)

## Overview
This document captures insights from the Checkvist user community to inform the development of the Checkvist MCP server, specifically for autonomous triage logic and persona validation.

**Source**: [Checkvist Forums (discuss.checkvist.com)](https://discuss.checkvist.com/)

---

## 🏗 Methodologies Identified
*What frameworks or systems do users apply to Checkvist?*

- **GTD (Getting Things Done)**:
    - **Contexts**: Implemented via tags (e.g., `#home`, `#work`) or top-level lists named by context.
    - **Projects**: Represented as parent items with nested sub-tasks.
    - **Next Actions**: Defined by manual ordering (top item = next action). Due dates often used as "focus" markers.
    - **Inbox**: A dedicated "Inbox" list is common for rapid capture.
- **PARA Method (Projects, Areas, Resources, Archives)**:
    - **Structure**: Users create four main lists or folders.
    - **Ordering**: Numerical prefixes (e.g., `1. Projects`) are used to force a consistent sort order in the navigation menu.
    - **Navigation**: Bookmarks (`ab` command) are essential for jumping between PARA sections quickly.
- **Zettelkasten / Knowledge Management**:
    - **Implementation**: Deep hierarchies and inter-list linking. Parent nodes serve as "zettels" (notes).
- **FVP (Final Version Perfected)**:
    - Mentioned as a method for processing tasks sequentially within a list.

---

## 😫 Common Pain Points
*What challenges do users face that we can solve with AI?*

1. **Navigation Friction**: The `LL` menu is mostly recency-based, leading to difficulty finding lists without numerical prefixes.
2. **"Blind" Capture**: Hard to add an item to a specific list without leaving the current view.
3. **Hierarchy Maintenance**: Managing very deep hierarchies can become cumbersome manually.
4. **Triage Overhead**: Moving items from Inbox to projects (`mm`) is fast but requires constant manual decision-making.

---

## 💡 Power User Tips & "Hidden Gems"
*Undocumented or advanced features found in forum discussions.*

- **Numerical Prefixes**: Vital for keeping list order stable.
- **Unique Characters**: Using `@Inbox` or `.Projects` to make search completion faster.
- **Bookmark Mastery**: Using `b1`, `b2` for instant context switching.
- **Keyboard-First Everything**: Success is measured by how few times the mouse is touched.

---

## 📊 Feature Requests & Gaps
*What are users asking for that the MCP could provide?*

- **Alphabetical List Sorting**: A recurring request.
- **Cross-List Search/View**: Better ways to see tasks from multiple lists in one unified view.
- **Automated Reorganization**: AI-assisted moving of tasks to relevant sections.

---

## 🧩 Autonomous Triage Patterns
*Observations on how users organize tasks that can be automated.*

- **Pattern 1: Tag Inheritance**: If a parent is tagged `#work`, sub-items often belong to that context unless specified otherwise.
- **Pattern 2: Project Promotion**: A task with many complex sub-tasks should probably become its own dedicated project/parent node.
- **Pattern 3: Status Tracking**: Items with specific keyword patterns often represent internal status transitions (e.g., "Review [task]").

---

## 🧘 Persona Validation
*Testing the "Final User" assumptions against real-world feedback.*

- **Current Assumption**: The typical user is a developer/tech-savvy person looking for a "keyboard-first" productivity tool.
- **Market Reality**: Confirmed. Power users are obsessed with keyboard shortcuts, speed, and clean hierarchies. They value "lack of clutter" over "visual flashiness".
- **Insight**: Any tool we build MUST respect keyboard-first workflows and NOT introduce lag or unnecessary UI steps.
