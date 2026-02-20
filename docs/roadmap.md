# Product Roadmap: The Productivity Architect

**Status**: Active (Consensus 2026-02-02)
**Context**: Pivot from stabilization to methodology-driven features (GTD/PARA).

---

## 📅 Phase 1.1: Methodology Foundation (The "Agenda" Sprint)
**Status**: Completed (2026-02-01)
See [changelog.md](changelog.md) for details.

---

## 📅 Phase 1.2: Structural Intelligence (The "Context" Sprint)
**Goal**: Automate project organization and improve operational speed.
**Timeline**: 4 Weeks

- [ ] **PROC-007: PARA Structure Recognition (Pattern-Based)**
  - Automatically identify PARA folders (1. Projects, 2. Areas, etc.).
  - Suggest move targets based on folder name keywords.
- [ ] **META-007-Lite: Automatic Context Linking (Grep-Based)**
  - When viewing or creating a task, suggest related tasks based on keyword intersections.
  - Prevent duplicate research/tasks.

**Success Metric**: 70% accuracy in PARA identification; 80% reduction in bulk operation latency.

---

## 📅 Phase 1.3: Architectural Excellence (The "Model" Sprint)
**Status**: Completed (2026-02-20)
See [changelog.md](changelog.md) for details (v0.3.0: Pydantic Models, Smart Syntax; v1.3.0: Context Guard, Security Hardening).

---

## 🚀 Phase 2.0: Deep Intelligence (The "Neural" Sprint)
**Goal**: Full semantic understanding and proactive agentic assistance.
**Timeline**: 3-6 Months

- [ ] **PARA Recognition (Semantic)**
  - Use LLM/Embeddings to categorize items into PARA even without clear prefixes.
- [ ] **Smart Linking (Semantic)**
  - Cross-reference tasks and notes using vector resonance.
- [ ] **Global Search 2.0**
  - Replace iterated playlist search with native instant search (`/search/everywhere.json`).
- [ ] **GTD Full Contextualizer**
  - Support for `@context` tags even where native Checkvist support is limited.

---

## 📊 Evaluation & Validation
- **User Survey**: Launch survey on Checkvist forum to validate Phase 1.2 and 2.0 priorities.
- **Methodology Audit**: Deep dive into GTD/PARA compatibility in `docs/research/`.

---

## 📚 Related
- [User Persona](persona.md)
- [Multi-Persona Debate (2026-02-02)](strategy/260202/project_debate.md)
- [Discovery: Bulk Ops & Styling Proposal](proposals/2026-02-06_bulk_and_styling_api.md)
