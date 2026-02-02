# Smart Triage Heuristics for Checkvist MCP

Based on the February 2026 User Research, these heuristics define the logic that an autonomous agent or tool should follow when triaging items in Checkvist.

## 1. Contextual Classification (GTD Focus)

### H1.1: Tag Inheritance
- **Rule**: If a parent node has a context tag (e.g., `#work`, `#errands`), all children added to it by the AI should inherit this tag unless a more specific tag is detected.
- **Logic**: `IF parent.tags contains context_tag AND child.tags is empty THEN child.add_tag(context_tag)`

### H1.2: Keyword-to-Tag Mapping
- **Rule**: Map natural language keywords to common user tags.
- **Mapping**:
    - "Chiama", "Phone", "Call" -> `#phone`
    - "Compra", "Buy", "Supermarket" -> `#errands`
    - "Leggi", "Read", "Article" -> `#read`

## 2. Structural Organization (PARA Focus)

### H2.1: Project Promotion
- **Rule**: If a task has more than 5 sub-tasks or contains a breakdown (WBS), it should be suggested for "Promotion" to a parent node or a dedicated project list.
- **Trigger**: `child_count > 5` OR `contains_bullet_points`

### H2.2: Area Allocation
- **Rule**: Use the numerical prefix of top-level lists to identify the target Area.
- **Logic**: 
    - `1. Projects` -> High priority, active
    - `2. Areas` -> Long-term responsibility
    - `3. Resources` -> Information, no due dates
    - `4. Archives` -> Completed/Stale

## 3. Autonomous Inbox Processing

### H3.1: Similarity-Based Routing
- **Rule**: Compare new Inbox items against the content of existing lists.
- **Logic**: If an item in search terms or keywords matches an existing project name (e.g., "Fix login" -> Project "Website Security"), suggest moving it there (`mm`).

### H3.2: Entropy Guard (Cleanup)
- **Rule**: Identify items in the Inbox older than 7 days without tags or due dates.
- **Action**: Mark with `#stale` or suggest "Snooze" to a future date.

## 4. Implementation Guidelines for AI Agents

1. **Verify before Move**: Always ask for confirmation before moving an item across lists (`mm`), but provide the "Reason" based on these heuristics.
2. **Batch Processing**: Instead of one-by-one, present a "Triage Table" showing: `Item | Suggested List | Heuristic Used`.
3. **Respect Keyboard Workflow**: The triage process must be triggerable via a single command (e.g., `/triage-inbox`) and navigable via keyboard.

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-01  
**Status**: DRAFT - Pending User Approval
