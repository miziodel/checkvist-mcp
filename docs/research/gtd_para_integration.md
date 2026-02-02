# Research: GTD & PARA Integration in Checkvist

**Goal**: Analyze how to map the Productivity Architect's methodologies to Checkvist's hierarchical structure.

## 1. PARA Method (by Tiago Forte)
PARA stands for **Projects**, **Areas**, **Resources**, and **Archives**.

### Mapping to Checkvist:
- **Projects**: Checklists with a clear "outcome" and due date. 
  - *Structure*: `1. Projects` root list.
- **Areas**: Long-term responsibilities (e.g., "Health", "Finances"). No fixed deadline.
  - *Structure*: `2. Areas` root list.
- **Resources**: Reference material, notes, ideas.
  - *Structure*: `3. Resources` root list.
- **Archives**: Completed or inactive items from the other three categories.
  - *Structure*: `4. Archives` root list + use of `#deleted` or archived lists.

### Implementation Opportunities:
- **Heuristic**: If a list has 10+ completed tasks and hasn't been touched in 30 days, suggest archiving.
- **Triage**: Suggest moving items with "^date" to Projects, and items without dates to Areas or Resources.

---

## 2. GTD Method (by David Allen)
GTD focuses on **Contexts**, **Next Actions**, and **Weekly Reviews**.

### Mapping to Checkvist:
- **Inbox**: The primary capture list.
- **Next Actions**: In Checkvist, these are effectively tasks at the "bottom" of a hierarchy (leaves) that have no blockers.
- **Contexts (@tags)**: Checkvist supports tags, but they are flat. Many users use sub-lists as contexts (e.g. `Home > Errands`).
- **Weekly Review**: Checkvist lacks a built-in "Summarizer".

### Implementation Opportunities (The "Agenda"):
- **`get_upcoming_tasks`**: Addresses the "Next Actions" and "Due" visibility.
- **`weekly_review`**: Fills the gap for a summary-driven review.
- **Filtering**: Need to identify "Next Actions" by excluding tasks that are parents of uncompleted subtasks.

---

## 3. Potential Conflict Points
- **Hierarchy vs Flat Contexts**: GTD purists prefer contexts over deep nesting. Productivity Architects often blend both.
- **Speed**: Any automation must be faster than `MM` (Move) or `LL` (List Search) keyboard shortcuts.

---

## 4. Next Research Steps
- [ ] Document common Checkvist user workflows for PARA.
- [ ] Draft heuristics for identifying "Next Actions" in a tree.
