# QA Instructions: Checkvist MCP Comprehensive Manual Testing

## 📋 Overview
This document provides detailed instructions for a manual tester to verify the Checkvist MCP server. The goal is to ensure 100% reliability of core operations and document behavior in edge cases.

---

## 🛑 Critical Rules for Testers
1. **Methodology**: Follow each cycle strictly. Verify and document results before moving to the next.
2. **Environment**: Use dedicated lists for testing. Use naming convention: `[QA-v{N}] {Description}`.
3. **Observation**: After each MCP operation, refresh the Checkvist UI (https://checkvist.com) to verify the result visually.
4. **Data Capture**: If a tool fails, copy the exact input parameters and the error message.

---

## 🛠 Cycle v1: Hierarchy & CRUD Basics
**Objective**: Verify fundamental creation, reading, and hierarchical management.

### Test 1.1: Bulk Import (5-Level Deep Structure)
- **Input**: Use `import_tasks` with:
  ```text
  Parent L1 #test-v1
    Child L2 !2
      Child L3 ^tomorrow
        Child L4 @tester
        Child L5 #deep
  ```
- **Verification**: 
  - [ ] Refresh UI: Are all 5 levels indented correctly?
  - [ ] Does L2 have priority "2" (orange)?
  - [ ] Is "#test-v1" and "#deep" parsed as tags?
  - [ ] *Note*: Due date (`^tomorrow`) and assignment (`@tester`) might remain as text (expected limitation).

### Test 1.2: Hierarchy Move
- **Input**: Use `move_task_tool` to move Child L2 under a new Root task.
- **Verification**: 
  - [ ] Do L3, L4, and L5 move along with L2?
  - [ ] Is the hierarchy under L2 preserved exactly?

### Test 1.3: Single Task Lifecycle
- **Steps**:
  1. `add_task` -> "QA Lifecycle Task"
  2. `get_tree` -> Verify the task is present in the tree.
  3. `update_task` -> Add tag `#updated`
  4. `close_task` -> Verify it strikes through in UI.
  5. `reopen_task` -> Verify it's active again.
  6. `archive_task` -> Verify it disappears from default view (becomes `#deleted`).

---

## ⚖️ Cycle v2: Stability & Regression Hunt
**Objective**: Identify anomalies and system limits.

### Test 2.1: Search Indexing
- **Action**: Create 20 tasks with unique random strings (e.g., "Alpha-99", "Beta-42").
- **Action**: Immediately run `search_tasks` for one of the strings.
- **Verification**: 
  - [ ] Does search find the task within 2 seconds of creation?

### Test 2.2: Metadata Boundaries
- **Action**: Test priority levels: `!1`, `!6`, `!7`.
- **Action**: Test date formats in `update_task`: `^today`, `^tomorrow`, `^2026-12-31`, `^next monday`.
- **Verification**: 
  - [ ] Do all valid formats apply correctly in the UI?

### Test 2.3: Regression Hunt
- **Action**: Eseguire `archive_task` su task con note e verificare persistenza
- **Action**: Eseguire `apply_template` da lista con sotto-gerarchie complesse
- **Verification**: 
  - [ ] Do actions update tasks correctly?

---

## 🚀 Cycle v3: Stability Recovery & Migrations
**Objective**: Scenari complessi di migrazioni e linking.

### Test 3.1: 7-Level Deep Migration
- **Action**: Create a 7-level structure. Move the 3rd level to a *different* list using `move_task_tool`.
- **Verification**: 
  - [ ] Are levels 4, 5, 6, and 7 present in the destination list?

### Test 3.2: Internal Linking
- **Action**: Create Task A. Copy its ID. Create Task B with content: `See [Task A](/cvt/TASK_ID)`.
- **Action**: Move Task A to another list.
- **Verification**: 
  - [ ] Does the link in Task B still point to Task A correctly in the UI?

### Test 3.3: Mass Migration (`migrate_incomplete_tasks`)
- **Action**: Create 10 tasks. Close 5. Run `migrate_incomplete_tasks` to a new list.
- **Verification**: 
  - [ ] Are exactly 5 (the open ones) moved?

---

## 🌪 Cycle v4: Extreme Stress I
**Objective**: Metadata density and state persistence.

### Test 4.1: Chaos Import
- **Input**:
  ```text
  Task Ultra !1 #urgent #client #backend ^tomorrow @dev1 @dev2
    Subtask A !3 #research #spike
    Subtask B !1 #blocker
  ```
- **Verification**: 
  - [ ] Verify multi-tag parsing. Verify hierarchy remains stable despite high density.

### Test 4.2: State Persistence
- **Action**: Chiudere 5 task in lista A
- **Action**: Spostare tutti i task in lista B (con `move_task_tool`)
- **Verification**: 
  - [ ] Verificare che i 5 task siano ancora chiusi

### Test 4.3: Note Persistence
- **Action**: Creare task con 3 livelli di note (task → nota → risposta)
- **Action**: Migrare il task con `migrate_incomplete_tasks`
- **Verification**: 
  - [ ] Verificare che tutte le note siano preservate

---

## 🧩 Cycle v5: Metadata Matrix
**Objective**: Exhaustive combination verification.

### Test 5.1: Priority Matrix
- **Action**: Creare 7 task, uno per ogni livello di priorità (1-7)
- **Action**: Eseguire `search_tasks` con filtro per priorità (se supportato)
- **Verification**: 
  - [ ] Verificare rendering corretto in `get_tree`

### Test 5.2: Date Matrix
| Formato    | Esempio             | Expected Behavior |
| ---------- | ------------------- | ----------------- |
| ISO Full   | `^2026-12-31`       | Exact date        |
| Relative   | `^tomorrow`         | Current + 1 day   |
| Named      | `^next friday`      | Next occurrence   |
| Time-based | `^2026-02-15T10:30` | Date + time       |

### Test 5.3: Link Stress
- **Action**: Creare task con 5 link interni e 3 link esterni
- **Verification**: 
  - [ ] Verificare che tutti i link siano preservati dopo `update_task`

### Test 5.4: Bug Re-verification
- **Action**: Re-eseguire i casi problematici di Cycle v2.3
- **Verification**: 
  - [ ] Documentare se i bug sono ancora presenti

---

## 🔥 Cycle v6: Edge of Chaos (Boundary Check)
**Objective**: Stress test resilience and "Torture" inputs.

### Test 6.1: Unicode & Content Stress ("Torture Node")
- **Action**: Inserire la nota seguente
```text
Task Title: مرا االم 🎉🚀✨💡🔥⚡🌟💫🎯🎨 שלם
Note: [1500 caratteri di Lorem Ipsum in arabo/ebraico/emoji misti]
```
- **Verification**:
  - [ ] Verificare che il server accetti e preservi il contenuto
- **Action**: Testare `search_tasks` su caratteri non-ASCII
- **Verification**: Verificare che `search_tasks` trovi il task

### Test 6.2: Referential Chaos (Broken Links)
1. **Action**: Creare Lista A con Task X
2. **Action**: Creare Lista B con Task Y contenente `[Link a X](/cvt/{id_X})`
3. **Action**: Eliminare/archiviare Lista A
- **Verification**: Verificare comportamento di Task Y (graceful degradation?)

### Test 6.3: Rapid Operational Convergence (Race Conditions)
- **Action**: Inserire la nota seguente
```python
# Pseudo-code
import_tasks(list_id, "Task 1\n  Task 1.1\n  Task 1.2\n...")  # 10 items
# Immediatamente dopo (senza attendere):
move_task_tool(list_id, root_task_id, target_list_id)
```
- **Verification**
  - [ ] Verificare che non ci siano errori di "task not found"
  - [ ] Verificare integrità della gerarchia finale

### Test 6.4: Empty State Stability (Template Logic)
- **Action**: Creare lista vuota "Target Empty"
- **Action**: Eseguire `apply_template` da una lista template popolata
- **Verification**:
  - [ ] Verificare che tutte le task siano clonate correttamente

### Test 6.5: Invisible Constraints (Whitespace-Only Content)
- **Action**: Tentare di creare task con content: `"   "` (solo spazi)
- **Action**: Tentare di creare task con content: `""` (stringa vuota)
- **Verification**: 
  - [ ] Verificare il comportamento del server (rifiuto? sanitization?)

---

## 🏁 Final Verification
- [ ] Run `get_review_data(timeframe="weekly")`. Compare numbers with UI.
- [ ] Clean up: Delete all `[QA-v*]` lists created during testing.
