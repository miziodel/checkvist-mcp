# Vision-Persona Alignment Matrix

**Purpose**: Validate that our Vision pillars align with the "Productivity Architect" persona discovered through user research.

**Source**: Cross-reference between [vision.md](../vision.md), [persona.md](../persona.md), and [user_research_2026_02.md](user_research_2026_02.md).

---

## 🎯 The Alignment Test

For each Vision pillar, we verify:
1. **Does the persona need this?** (User Research validation)
2. **Will they use it?** (Keyboard-first compatibility)
3. **What's the risk?** (Entropy vs. Control trade-off)

---

## 📊 Pillar-by-Pillar Analysis

### 1. Linear: Triage & Cycles ✅ VALIDATED

**Vision Promise**: "L'IA scansiona la Inbox e propone dove smistare i task."

**Persona Need**: 
- **Pain Point #4**: "Triage Overhead - Moving items from Inbox to projects (`mm`) is fast but requires constant manual decision-making."
- **Mental Model**: GTD "Inbox Zero" obsession.

**Research Evidence**: 
> "Users rely on a dedicated 'Inbox' list for rapid capture. The `mm` (move) command is used constantly for triage."

**Keyboard-First Check**: ✅ PASS
- The AI suggests moves, but the user confirms via keyboard (no mouse required).
- Faster than manual `mm` + typing list name.

**Implementation Status**: 
- Heuristics defined in [smart_triage_heuristics.md](smart_triage_heuristics.md) (H3.1: Similarity Routing).
- Tool: `triage_inbox` (planned for Week 3).

---

### 2. GitHub: Issues & Deps ⚠️ NEEDS VALIDATION

**Vision Promise**: "L'IA crea link di dipendenza: 'Non puoi fare B se non finisci A'."

**Persona Need**: 
- **Not explicitly mentioned** in forum research.
- Power users focus on hierarchy (parent-child) rather than cross-task dependencies.

**Research Evidence**: 
> "Projects are represented as parent items with nested sub-tasks."

**Keyboard-First Check**: ⚠️ UNCERTAIN
- Creating links might require additional UI steps.
- Risk of adding friction to the workflow.

**Recommendation**: 
- **Defer** until we validate if users actually need cross-task blocking.
- Alternative: Use parent-child nesting for dependencies (already native to Checkvist).

---

### 3. Readwise: Spaced Repetition ✅ VALIDATED

**Vision Promise**: "L'IA ripesca vecchie idee dimenticate per darti nuovi spunti."

**Persona Need**: 
- **Goal**: "Knowledge Synergy - Discover connections between old notes and current tasks."
- **Pain Point**: Context loss and forgetting why tasks were created.

**Research Evidence**: 
> "Some users build Zettelkastens by using inter-list linking and deep nesting."

**Keyboard-First Check**: ✅ PASS
- AI surfaces ideas passively (no user action required).
- User can ignore or act via keyboard.

**Implementation Status**: 
- Tool: `resurface_ideas` (already implemented).

---

### 4. Superhuman: Zero Inbox ✅ VALIDATED

**Vision Promise**: "Comandi rapidi per nascondere/snoozare task non urgenti."

**Persona Need**: 
- **Pain Point #1**: "Inbox Chaos - Rapidly capturing ideas leads to a messy inbox."
- **Mental Model**: GTD "Next Actions" and focus on what matters "now".

**Research Evidence**: 
> "Due dates are often used as 'focus' markers rather than hard deadlines."

**Keyboard-First Check**: ✅ PASS
- Snoozing can be triggered via command (e.g., `/snooze`).
- No mouse required.

**Implementation Status**: 
- Planned as `snooze_task` tool (backlog).

---

### 5. Obsidian: Keyboard-First ✅ CORE PRINCIPLE

**Vision Promise**: "Comandi mimici (`LL`, `MM`) per navigazione e triage senza mouse."

**Persona Need**: 
- **Core Identity**: "Mouse clicks are considered a failure of UI design."
- **Required Behavior**: "Respect Keyboard Flow - Never propose workflows slower than manual shortcuts."

**Research Evidence**: 
> "Success is measured by how few times the mouse is touched. Power users are obsessed with keyboard shortcuts, speed, and clean hierarchies."

**Keyboard-First Check**: ✅ MANDATORY
- This is not a feature, it's a **constraint** on all other features.

**Implementation Status**: 
- Now formalized as architectural principle in [architecture.md](../architecture.md).

---

## 🚨 Gaps & Misalignments

### Gap 1: Variable Templating (Week 3 Feature)
**Status**: ⚠️ NOT VALIDATED BY RESEARCH

**Issue**: The "Smart Templating with Variables" feature (Week 3) was proposed in the strategic debate but NOT mentioned in forum research.

**Risk**: Building a feature users don't need.

**Mitigation**: 
- Search forums specifically for "template" or "recurring" workflows.
- If no evidence found, downgrade to "nice-to-have" instead of sprint priority.

### Gap 2: Semantic Search
**Status**: ⚠️ UNCERTAIN VALUE

**Issue**: Vision mentions "Semantic Search (Logseq/Roam Style)" but forum users rely on exact keyword search and tags.

**Risk**: Over-engineering a solution for a non-problem.

**Mitigation**: 
- Validate if users complain about search limitations.
- Start with tag-aware search (already in heuristics) before adding embeddings.

---

## ✅ Validated Vision Pillars (Priority Order)

1. **Keyboard-First** (Obsidian) - MANDATORY constraint
2. **Triage & Cycles** (Linear) - #1 pain point
3. **Zero Inbox** (Superhuman) - Directly addresses chaos
4. **Spaced Repetition** (Readwise) - Validated by Zettelkasten users

## ⚠️ Needs Further Research

- **Issues & Deps** (GitHub) - No evidence of need
- **Variable Templating** - Not mentioned in forums
- **Semantic Search** - Users seem satisfied with tags

---

**Recommendation**: Focus Week 3 feature development on **Triage Automation** (validated) rather than **Variable Templating** (unvalidated).

**Next Steps**: 
1. Search forums for "template" and "recurring" to validate templating need.
2. Implement `triage_inbox` tool using [smart_triage_heuristics.md](smart_triage_heuristics.md).
3. Defer GitHub-style dependencies until user demand is proven.
