---
version: 1.1.0
last_modified: 2026-02-03
status: ACTIVE (Executing Phase 2.1)
source: Multi-Persona Strategic Debate (2026-02-01)
---

# 3-Week Sprint Roadmap: Stabilization & Strategic Feature

**Context**: Consensus plan from multi-persona debate to balance stability, testing, and innovation.

**Source**: [`docs/strategy/260201/strategic_synthesis.md`](strategy/260201/strategic_synthesis.md)

**User Research Validation**: The "Smart Templating" feature (Week 3) and triage logic align with the [Productivity Architect persona](persona.md) discovered through [Checkvist forum research](research/user_research_2026_02.md).

---

## 🎯 Sprint Goals

1. **Week 1**: Restore user trust through surgical fixes and API optimization [COMPLETED ✅]
2. **Week 2**: Build safety net through test consolidation and documentation [ACTIVE 🏗️]
3. **Week 3**: Demonstrate safe feature delivery with tool maturity model [PLANNED 🚀]

---

## 📅 Week 1: Surgical Fixes & API Optimization

**Owner**: Checkvist Expert + MCP Developer  
**Goal**: Fix critical regressions and optimize API usage

### Day 1-2: API Forensics Sprint

**Priority**: 🔴 CRITICAL

- [x] Audit all `client.py` methods for missing `with_notes`, `with_tags` parameters
- [x] Refactor `get_task()` to use `?with_notes=true&with_tags=true`
- [x] Measure API call reduction (target: 60% fewer calls)
- [x] Fix `archive_task` using consolidated API response
- [x] Fix `apply_template` hierarchy preservation

**Success Criteria**:
- `archive_task` passes test with notes, tags, and 3-level hierarchy
- `apply_template` preserves hierarchy in automated test
- API call count for typical workflow reduced by 50%+

**Fallback**: If not fixed in 2 days, escalate to pair programming session

---

### Day 3-5: User Trust Audit + Operative Intelligence (High Resolution)

**Owner**: Final User + QA Analyst  
**Priority**: 🔴 CRITICAL

- [x] Audit all 20+ tools for error message quality
- [x] Implement standardized response format
- [x] Add validation layer in `server.py` to catch common errors before API call
- [x] Update tool docstrings with failure scenarios

**Success Criteria**:
- Every tool returns actionable error message on failure
- User can understand what happened without reading logs
- LLM receives clear guidance on retry strategy


**Owner**: MCP Developer + Final User
**Priority**: 🔴 CRITICAL (URGENT)

- [x] Implement `search_tasks_enriched`: Return search results with full Breadcrumbs (Parent hierarchy)
- [x] Refactor `get_task()`: Ensure 100% visibility of notes and comments by default
- [x] Audit all tool error messages for "Actionable Feedback" (Standardized Response)

**Success Criteria**:
- [x] Agent can identify the project/context of a search result without extra calls
- [x] All technical specifications in notes are readable by the agent
- [x] Zero "Context Blindness" incidents in verification sessions

---

## 📅 Week 2: Test Consolidation & Safety Net

**Owner**: QA Analyst + Architect  
**Goal**: Eliminate test coverage gaps and document API knowledge

### Day 6-8: Scenario-to-Test Mapping & Token Optimization

**Priority**: 🟠 HIGH

- [x] Create `tests/scenario_mapping.md` linking each SCENARIOS.md item to test file
- [x] Identify gaps (scenarios without tests)
- [ ] **Lazy Tree Fetching**: Optimize `get_tree` to fetch sub-branches on-demand (Token Efficiency)
- [x] Write missing tests for BUG-006, BUG-007, BUG-008, SAFE-006
- [x] Update `COVERAGE_REPORT.md` with completion percentage

**Success Criteria**:
- 90%+ of scenarios have corresponding automated tests
- All BUG-* scenarios have regression tests
- `get_tree` can handle lists with 1000+ tasks without hitting context limits
- Coverage report shows green status

---

### Day 9-10: Checkvist API Compatibility Matrix

**Owner**: Checkvist Expert + MCP Developer  
**Priority**: 🟡 MEDIUM

- [ ] Create `docs/checkvist_api_compatibility.md`
- [ ] Document all 15+ endpoints we use:
  - Endpoint URL
  - HTTP method
  - Required/optional parameters
  - Response format (with examples)
  - Known quirks
  - Workarounds implemented
- [ ] Add "Last Verified" date for each endpoint
- [ ] Create script to validate endpoint availability

**Success Criteria**:
- Complete documentation of all API interactions
- New developers can understand API quirks in 10 minutes
- Debugging time for API issues reduced by 70%

---

## 📅 Week 3: Tool Maturity & Strategic Feature

**Owner**: PM + MCP Developer  
**Goal**: Establish quality framework and ship one feature safely

### Day 11-12: Tool Maturity Classification

**Priority**: 🟡 MEDIUM

- [ ] Classify all tools into Alpha/Beta/Stable:
  - **Alpha**: Experimental, requires `confirmed=True`, can fail
  - **Beta**: Has tests, clear errors, 80%+ success rate
  - **Stable**: Battle-tested, 95%+ success rate, production-ready
- [ ] Update `server.py` to tag tools with maturity level
- [ ] Configure LLM to prefer Stable > Beta > Alpha
- [ ] Add `--experimental` flag to expose Alpha tools

**Success Criteria**:
- All tools labeled with maturity level
- LLM only sees Beta+ tools by default
- Documentation explains maturity model

---

### Day 13-17: Strategic Feature (Smart Templating)

**Owner**: MCP Developer + Final User  
**Priority**: 🟢 LOW (after stabilization)

- [ ] Implement variable injection for templates:
  ```
  Template: "Meeting with {{CLIENT_NAME}} on {{DATE}}"
  Usage: apply_template(template_id, variables={"CLIENT_NAME": "Acme Corp", "DATE": "2026-02-15"})
  ```
- [ ] Follow full TDD cycle:
  1. Write scenario in SCENARIOS.md
  2. Write failing test
  3. Implement feature
  4. Verify test passes
- [ ] Document in `walkthrough.md` with examples
- [ ] Update `lessons_learned.md` with insights

**Success Criteria**:
- Feature works with 3+ variable types (string, date, list)
- Has automated tests covering edge cases
- User can create dynamic templates for recurring workflows

---

### Day 18-21: Strategic Feature (Triage Inbox Automation)

**Owner**: MCP Developer + Final User  
**Priority**: 🟠 HIGH (validated by user research)

- [ ] Implement `triage_inbox` tool using [smart_triage_heuristics.md](research/smart_triage_heuristics.md):
  - H1.1: Tag Inheritance (children inherit parent context)
  - H2.1: Project Promotion (large task clusters → dedicated projects)
  - H3.1: Similarity Routing (match inbox items to existing projects)
- [ ] Follow full TDD cycle:
  1. Write scenario in SCENARIOS.md (PROC-001 extension)
  2. Write failing test
  3. Implement feature
  4. Verify test passes
- [ ] Return triage suggestions in keyboard-friendly format:
  ```
  Inbox Triage Suggestions:
  1. "Buy milk" → Move to "Home" (#errands)
  2. "Fix login bug" → Move to "Website Security" (#urgent)
  3. "Read article" → Move to "Resources" (#read)
  
  Confirm all? (y/n)
  ```
- [ ] Document in `walkthrough.md` with examples
- [ ] Update `lessons_learned.md` with insights

**Success Criteria**:
- Tool suggests correct destination for 80%+ of inbox items
- Respects keyboard-first workflow (no mouse required)
- User can batch-confirm or reject suggestions
- Validated against "Productivity Architect" persona needs

---

## 📊 Success Metrics

### Week 1 Metrics
- [x] `archive_task` success rate: 60% → **100%**
- [x] `apply_template` hierarchy preservation: 0% → **100%**
- [x] API calls per workflow: **-50%** reduction
- [x] User error clarity rating: **9/10** (Standardized responses implemented)
- [x] Context Blindness: **0 reported cases** (Operative Intelligence implemented)

### Week 2 Metrics
- [ ] Scenario test coverage: 70% → **90%+**
- [ ] API compatibility matrix: **100%** endpoint coverage
- [ ] Regression test suite: 9 → **15+** tests
- [ ] Resource leak incidents: 3 → **0**

### Week 3 Metrics
- [ ] Tool maturity classification: **100%** tools labeled
- [ ] Strategic features shipped: **Smart templating + Triage inbox automation**
- [ ] Triage accuracy: **80%+** correct suggestions
- [ ] User trust score: 6/10 → **9/10**
- [ ] Development velocity: **2x** faster debugging

---

## 🚨 Red Lines (Stop and Reassess)

If any of these occur, **STOP** the sprint and reconvene stakeholders:

1. **Data Loss Incident**: Any user reports losing tasks due to our tools
2. **API Ban**: Checkvist blocks our account due to rate limiting
3. **Security Breach**: Prompt injection causes unauthorized data access
4. **Resource Exhaustion**: Server/client hangs requiring manual restart
5. **User Churn**: 3+ users abandon system citing reliability issues

---

## 🔄 Feedback Loops

### Daily Standups (5 minutes)
- What did you ship yesterday?
- What are you shipping today?
- Any blockers?

### Weekly Retrospectives (30 minutes)
- What went well?
- What needs improvement?
- Update `lessons_learned.md`

### User Feedback Sessions (bi-weekly)
- Demo new features to Final User persona
- Collect trust score (1-10)
- Prioritize pain points

---

## 📚 Related Documentation

- [User Persona](persona.md) - The "Productivity Architect" target user
- [User Research (Feb 2026)](research/user_research_2026_02.md) - Forum analysis and behavior patterns
- [Smart Triage Heuristics](research/smart_triage_heuristics.md) - AI logic rules for automation
- [Multi-Persona Debate](strategy/260201/project_debate.md) - Full debate transcript
- [Strategic Synthesis](strategy/260201/strategic_synthesis.md) - Detailed implementation plan
- [Critical Insights](strategy/260201/critical_insights.md) - Breakthrough discoveries
- [Backlog](backlog.md) - Long-term feature backlog
- [Scenarios](../tests/SCENARIOS.md) - Test scenarios and vision mapping
