# Checkvist MCP Comprehensive Test Plan

Piano di test esaustivo per il server MCP Checkvist, basato sulla traccia fornita e arricchito con casi limite aggiuntivi identificati dall'analisi del server.

## User Review Required

> [!IMPORTANT]
> **Approccio Metodico Richiesto**
> 
> Questo test seguirà il principio "Quality First": ogni ciclo sarà eseguito completamente, verificato e documentato prima di procedere al successivo. Non ci saranno scorciatoie.

> [!WARNING]
> **Test Distruttivi**
> 
> Alcuni test (Cycle v6) includono operazioni potenzialmente distruttive:
> - Eliminazione di liste con link interni attivi
> - Operazioni rapide che potrebbero stressare l'API
> - Payload Unicode estremi
> 
> Tutti i test verranno eseguiti su liste dedicate create appositamente per questo scopo.

---

## Proposed Changes

Questo piano **non modifica codice**, ma esegue una campagna di test completa per verificare la robustezza del server MCP Checkvist esistente.

### Test Environment Setup

#### Preparazione Workspace
- Creazione di liste di test dedicate con naming convention: `[TEST-v{N}] {Description}`
- Documentazione dello stato iniziale del server
- Configurazione di costanti e IDs per facilitare il tracciamento

---

### Cycle v1: Hierarchy & CRUD Basics

**Obiettivo**: Verificare le operazioni fondamentali di creazione, lettura e gestione gerarchica.

#### Test 1.1: Bulk Import (5-Level Deep Structure)
```text
Parent L1 #test-v1
  Child L2 !2
    Child L3 ^tomorrow
      Child L4 @tester
        Child L5 #deep
```

**Verifica**:
- Tutti i livelli sono creati correttamente
- Tag, priorità e date sono parsati
- La gerarchia è preservata

#### Test 1.2: Hierarchy Move (Parent + Children)
- Spostare il nodo L2 sotto un nuovo parent
- Verificare che L3, L4, L5 seguano il parent

#### Test 1.3: Single Task CRUD
- `add_task` → `get_tree` → `update_task` → `close_task` → `reopen_task` → `archive_task`
- Verificare la consistenza dei dati in ogni fase

---

### Cycle v2: Stability & Regression Identification

**Obiettivo**: Identificare comportamenti anomali e limiti di sistema.

#### Test 2.1: Search Indexing Performance
- Creare 50 task con content univoco
- Eseguire `search_tasks` immediatamente dopo la creazione
- Verificare se tutti i task sono trovati (test di eventual consistency)

#### Test 2.2: Metadata Boundaries
- **Priority**: Testare !1, !2, !3, !6, !7 (e tentare !8, !0 per vedere il fallback)
- **Date**: `^today`, `^tomorrow`, `^2026-12-31`, `^next monday`, `^2026-02-01T14:30:00`

#### Test 2.3: Regression Hunt
- Eseguire `archive_task` su task con note e verificare persistenza
- Eseguire `apply_template` da lista con sotto-gerarchie complesse

---

### Cycle v3: Stability Recovery

**Obiettivo**: Testare scenari complessi di migrazione e linking.

#### Test 3.1: Deep Hierarchy Move (7 Levels)
- Creare struttura a 7 livelli
- Spostare il nodo L3 in un'altra lista
- Verificare che L4-L7 siano migrati intatti

#### Test 3.2: Internal Linking
```text
Task A (id: X)
Task B con link: [Vedi Task A](/cvt/X)
```
- Verificare che il link sia preservato dopo move
- Verificare link a liste: `[Lista Ref](/checklists/ID)`

#### Test 3.3: Mass Migration
- Creare lista "Sprint 1" con 30 task (10 chiusi, 20 aperti)
- Eseguire `migrate_incomplete_tasks` verso "Sprint 2"
- Verificare che solo i 20 aperti siano migrati

---

### Cycle v4: Extreme Stress I

**Obiettivo**: Stress test su densità di metadata e persistenza dello stato.

#### Test 4.1: Chaos Import
```text
Task Ultra !1 #urgent #client #backend ^tomorrow @dev1 @dev2
  Subtask A !3 #research #spike
  Subtask B !1 #blocker
```
- Verificare parsing completo di multi-tag e multi-assignment

#### Test 4.2: State Persistence
- Chiudere 5 task in lista A
- Spostare tutti i task in lista B (con `move_task_tool`)
- Verificare che i 5 task siano ancora chiusi

#### Test 4.3: Note Persistence
- Creare task con 3 livelli di note (task → nota → risposta)
- Migrare il task con `migrate_incomplete_tasks`
- Verificare che tutte le note siano preservate

---

### Cycle v5: Metadata & Linking Matrix

**Obiettivo**: Test esaustivo di tutte le combinazioni metadata + linking.

#### Test 5.1: Priority Matrix
- Creare 7 task, uno per ogni livello di priorità (1-7)
- Eseguire `search_tasks` con filtro per priorità (se supportato)
- Verificare rendering corretto in `get_tree`

#### Test 5.2: Date Matrix
| Formato | Esempio | Expected Behavior |
|---------|---------|-------------------|
| ISO Full | `^2026-12-31` | Exact date |
| Relative | `^tomorrow` | Current + 1 day |
| Named | `^next friday` | Next occurrence |
| Time-based | `^2026-02-15T10:30` | Date + time |

#### Test 5.3: Link Stress
- Creare task con 5 link interni e 3 link esterni
- Verificare che tutti i link siano preservati dopo `update_task`

#### Test 5.4: Bug Re-verification
- Re-eseguire i casi problematici di Cycle v2.3
- Documentare se i bug sono ancora presenti

---

### Cycle v6: Edge of Chaos (Final Boundary Check)

**Obiettivo**: Testare scenari estremi e improbabili per garantire resilienza al 100%.

#### Test 6.1: Unicode & Content Stress ("Torture Node")
```text
Task Title: مرحبا العالم 🎉🚀✨💡🔥⚡🌟💫🎯🎨 שלום עולם
Note: [1500 caratteri di Lorem Ipsum in arabo/ebraico/emoji misti]
```
- Verificare che il server accetti e preservi il contenuto
- Testare `search_tasks` su caratteri non-ASCII

#### Test 6.2: Referential Chaos (Broken Links)
1. Creare Lista A con Task X
2. Creare Lista B con Task Y contenente `[Link a X](/cvt/{id_X})`
3. Eliminare/archiviare Lista A
4. Verificare comportamento di Task Y (graceful degradation?)

#### Test 6.3: Rapid Operational Convergence (Race Conditions)
```python
# Pseudo-code
import_tasks(list_id, "Task 1\n  Task 1.1\n  Task 1.2\n...")  # 10 items
# Immediatamente dopo (senza attendere):
move_task_tool(list_id, root_task_id, target_list_id)
```
- Verificare che non ci siano errori di "task not found"
- Verificare integrità della gerarchia finale

#### Test 6.4: Empty State Stability (Template Logic)
- Creare lista vuota "Target Empty"
- Eseguire `apply_template` da una lista template popolata
- Verificare che tutte le task siano clonate correttamente

#### Test 6.5: Invisible Constraints (Whitespace-Only Content)
- Tentare di creare task con content: `"   "` (solo spazi)
- Tentare di creare task con content: `""` (stringa vuota)
- Verificare il comportamento del server (rifiuto? sanitization?)

---

### Additional Tests (Bonus - Casi Aggiuntivi Identificati)

#### Test 7.1: Triage Workflow
- Popolare lista "Inbox" con 20 task misti
- Eseguire `triage_inbox` e verificare la lista completa
- Spostare 10 task in altre liste
- Re-eseguire `triage_inbox` e verificare che rimangano solo 10

#### Test 7.2: Review Data Analysis
- Creare lista con mix di task aperte/chiuse con date distribuite
- Eseguire `get_review_data(timeframe="weekly")`
- Verificare che le statistiche siano corrette

#### Test 7.3: Template Cloning Deep Hierarchy
- Creare template con 5 livelli di gerarchia e 20+ task
- Eseguire `apply_template` su lista target
- Verificare che TUTTA la gerarchia sia clonata senza perdite

---

## Verification Plan

### Automated Test Framework

**Strumento**: Script Python con chiamate dirette agli MCP tools

**Pattern di Verifica**:
```python
def verify_test_case(test_name, setup, action, assertions):
    """
    - setup: Preparazione stato iniziale
    - action: Esecuzione dell'operazione MCP
    - assertions: Lista di condizioni da verificare
    """
    print(f"🧪 Running: {test_name}")
    setup()
    result = action()
    for assertion in assertions:
        assert assertion(result), f"Failed: {test_name}"
    print(f"✅ Passed: {test_name}")
```

**Esecuzione**:
```bash
# Da eseguire nella directory del workspace
python test_checkvist_mcp.py --cycle v1
python test_checkvist_mcp.py --cycle v2
# ... fino a v6
python test_checkvist_mcp.py --cycle all  # Full suite
```

### Manual Verification

**Checkpoint Visivi** (dopo ogni ciclo):
1. Aprire Checkvist UI (https://checkvist.com)
2. Verificare visivamente che le liste di test siano nello stato atteso
3. Confrontare con gli screenshot/dump JSON salvati dal test automatico

**Verifica Finale**:
- Eseguire `get_review_data` e confrontare con le aspettative
- Eseguire `search_tasks` globale per verificare che tutti i test task siano indicizzati
- Cleanup: Eliminare tutte le liste `[TEST-v*]`

### Test Artifacts

Ogni ciclo produrrà:
- **test_results_v{N}.json**: Output raw di ogni chiamata MCP
- **test_assertions_v{N}.md**: Lista di assertion passate/fallite
- **screenshots_v{N}/**: Screenshot della UI Checkvist per confronto visivo

### Success Criteria

- ✅ **100% dei test passati** nei cicli v1-v7
- ✅ **Resilienza documentata** per i casi limite del ciclo v6 (anche se falliscono, devono fallire gracefully)
- ✅ **Zero regressioni** sui bug già fixati
- ✅ **Walkthrough completo** con evidenze visive di ogni test

---

## Timeline Stimato

| Ciclo      | Complessità | Tempo Stimato |
| ---------- | ----------- | ------------- |
| Setup      | Bassa       | 15 min        |
| v1         | Bassa       | 30 min        |
| v2         | Media       | 45 min        |
| v3         | Alta        | 60 min        |
| v4         | Alta        | 60 min        |
| v5         | Molto Alta  | 90 min        |
| v6         | Estrema     | 120 min       |
| v7         | Estrema     | 120 min       |
| Reporting  | Media       | 30 min        |
| **TOTALE** | -           | **~7 ore**    |

> [!NOTE]
> Seguendo il principio "Slow is smooth, smooth is fast", è preferibile dedicare il tempo necessario piuttosto che affrettare e dover re-testare.
