---
description: Conduct a multi-persona strategic debate to assess project state and build consensus
---

# Multi-Persona Strategic Debate Workflow

## Purpose
Use this workflow when facing critical project decisions that require multiple stakeholder perspectives. This technique surfaces hidden assumptions, explores extreme consequences, and builds actionable consensus.

## When to Use
- Major architectural decisions
- Strategic prioritization (features vs stability)
- Risk assessment and mitigation planning
- Post-mortem analysis of complex failures
- Quarterly/annual planning sessions

## Prerequisites
1. Define personas (roles/stakeholders) in a `AGENTS.md` or similar file
2. Gather relevant documentation (vision, risks, backlog, metrics)
3. Identify the core question or decision to debate

## Steps

### 1. Preparation (15-30 minutes)
- [ ] Review all relevant project documentation
- [ ] Identify 4-6 distinct personas (e.g., Architect, Developer, QA, User, Domain Expert, PM)
- [ ] Define the debate question clearly
- [ ] Set time budget (typically 1-2 hours for full debate)

### 2. Context Setting (5 minutes)
- [ ] Create opening statement summarizing:
  - Current project state
  - Key metrics/data points
  - The decision or question at hand
  - Why this matters now

### 3. Round-Robin Debate (30-60 minutes)
For each persona, simulate their perspective:

**Round 1: Initial Positions**
- [ ] Each persona states their primary concern
- [ ] Each persona proposes their preferred solution
- [ ] Each persona identifies what they fear most

**Round 2: Rebuttals & Counter-Proposals**
- [ ] Personas challenge each other's assumptions
- [ ] Explore edge cases and failure modes
- [ ] Propose alternative approaches

**Round 3: Extreme Consequence Analysis**
- [ ] For each major risk, trace the "cascade" to its logical extreme
- [ ] Ask: "What if this goes catastrophically wrong?"
- [ ] Identify "red lines" (non-negotiable outcomes to avoid)

**Round 4: Synthesis & Consensus**
- [ ] PM/Facilitator persona synthesizes all viewpoints
- [ ] Propose hybrid solution addressing all concerns
- [ ] Get explicit buy-in from each persona

### 4. Documentation (15-30 minutes)
Create three artifacts:

- [ ] **Debate Transcript** (`project_debate.md`):
  - Full dialogue with all rounds
  - Extreme consequence threads
  - Closing reflections from each persona

- [ ] **Strategic Synthesis** (`strategic_synthesis.md`):
  - Executive summary
  - Detailed action plan with owners and timelines
  - Success metrics and red lines
  - Risk dashboard

- [ ] **Critical Insights** (`critical_insights.md`):
  - Non-obvious discoveries
  - Breakthrough realizations
  - Strategic implications
  - The "one thing that changes everything"

### 5. Action Planning (10 minutes)
- [ ] Extract concrete action items from synthesis
- [ ] Update project backlog with new priorities
- [ ] Create roadmap if needed
- [ ] Schedule follow-up checkpoints

## Persona Guidelines

### Essential Personas
1. **Architect/Technical Lead**: Focus on long-term sustainability, technical debt, scalability
2. **Developer/Implementer**: Focus on feasibility, development velocity, tooling
3. **QA/Quality Expert**: Focus on testing, reliability, edge cases
4. **End User/Customer**: Focus on usability, trust, value delivery
5. **Domain Expert**: Focus on domain-specific constraints, best practices, hidden risks
6. **PM/Facilitator**: Focus on trade-offs, consensus, actionable outcomes

### Optional Personas
- Security Expert
- DevOps/SRE
- Designer/UX
- Business/Stakeholder
- Support/Community Manager

## Tips for Effective Debates

### Do:
✅ Use concrete examples and data when available
✅ Explore "what if" scenarios aggressively
✅ Challenge assumptions, especially your own
✅ Document dissenting opinions (they often reveal hidden risks)
✅ End with clear action items and owners

### Don't:
❌ Let one persona dominate (balance airtime)
❌ Avoid conflict (productive disagreement is the goal)
❌ Rush to consensus (explore thoroughly first)
❌ Ignore "soft" concerns (UX, trust, culture)
❌ Create artifacts without clear next steps

## Example Debate Questions
- "Should we freeze features to stabilize, or ship fast and iterate?"
- "Is our current architecture sustainable for 10x scale?"
- "Which of these 5 features should we prioritize?"
- "Should we rewrite this component or refactor incrementally?"
- "How do we balance security with developer velocity?"

## Success Indicators
- All personas feel heard and understood
- At least one "breakthrough insight" emerges
- Consensus plan addresses all major concerns
- Clear action items with owners and deadlines
- Documentation captures both decision and rationale

## Follow-Up
- Schedule retrospective after executing the plan
- Update `lessons_learned.md` with outcomes
- Refine persona definitions based on what worked
- Consider making this a quarterly practice

---

**Related Resources**:
- Example debate: `docs/strategy/260201/project_debate.md` (Checkvist MCP)
- Synthesis template: `docs/strategy/260201/strategic_synthesis.md`
