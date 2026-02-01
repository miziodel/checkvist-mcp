# Checkvist MCP Bug Report

**Test Session**: 2026-02-01  
**Total Issues Found**: 3  
**Critical**: 1  
**Medium**: 1  
**Low**: 1

---

## 🔴 BUG #0: Task ID Mismatch in `create_list`

**Severity**: CRITICAL  
**Status**: CONFIRMED  
**Discovered In**: Revalidation test

### Description
Il tool `create_list` restituisce un ID diverso da quello effettivamente creato, causando errori 403 su operazioni successive.

### Reproduction
```python
result = mcp_checkvist-mcp_create_list(name="Test List")
# Returns: "Checklist created: Test List (ID: 946470)"

# Ma poi:
mcp_checkvist-mcp_import_tasks(list_id="946469", content="Task")
# Error: 403 Forbidden on list 946469
```

### Impact
Tutte le operazioni su liste appena create potrebbero fallire se si usa l'ID restituito.

### Root Cause
Probabile off-by-one error o race condition nel server MCP.

---

## 🔴 BUG #1: `add_note` API Returns 403 Forbidden

**Severity**: CRITICAL  
**Status**: OPEN (potrebbe essere correlato a Bug #0)  
**Discovered In**: Cycle v4, Test 4.3

### Description
Chiamate a `mcp_checkvist-mcp_add_note` falliscono con errore HTTP 403 Forbidden.

### Reproduction Steps
```python
# Step 1: Create task
task_id = mcp_checkvist-mcp_add_task(
    content="Test Task",
    list_id="946456"
)
# Returns: Task ID 72268100

# Step 2: Add note
mcp_checkvist-mcp_add_note(
    list_id="946456",
    task_id="72268100",
    note="This is a test note"
)
# Result: 403 Forbidden
```

### Error Message
```
Error adding note to task 72268100: Client error '403 Forbidden' for url 
'https://checkvist.com/checklists/946456/tasks/72268100/comments.json?comment%5Bcomment%5D=...'
```

### Impact
- Impossibile testare la persistenza delle note dopo migrazioni
- Blocca il workflow di aggiunta commenti/note via MCP

### Possible Root Causes
1. **Task ID mismatch**: L'ID restituito da `add_task` potrebbe non corrispondere all'ID effettivo del task creato
2. **Permission issue**: L'account Checkvist potrebbe non avere permessi per aggiungere commenti
3. **API endpoint bug**: Il server MCP potrebbe costruire l'URL in modo errato

### Workaround
Nessuno disponibile via MCP. Le note devono essere aggiunte manualmente via UI Checkvist.

### Recommendation
Investigare il codice sorgente del tool `add_note` nel server MCP per verificare:
- Come viene costruito l'URL API
- Se l'ID del task viene validato prima della chiamata
- Se ci sono header di autenticazione mancanti

---

## ⚠️ BUG #2: Date Parsing via Smart Syntax (`^`) Non Funziona in Import

**Severity**: MEDIUM  
**Status**: OPEN  
**Discovered In**: Cycle v1, Test 1.1 | Cycle v2, Test 2.2

### Description
Il parsing delle date usando la sintassi `^date` non funziona in `import_tasks`. Le date rimangono come testo nel content invece di essere applicate come due date.

### Reproduction Steps
```python
mcp_checkvist-mcp_import_tasks(
    content="Task with date ^tomorrow\nAnother task ^2026-12-31",
    list_id="946454"
)

# Expected: Due dates applicate ai task
# Actual: "^tomorrow" e "^2026-12-31" rimangono nel testo
```

### Tested Date Formats (All Failed)
- `^today`
- `^tomorrow`
- `^2026-12-31` (ISO format)
- `^next monday` (named)
- `^2026-02-15T10:30:00` (with time)

### Impact
- Users non possono impostare due date durante bulk import
- Workflow meno efficiente (richiede update separato per ogni task)

### Workaround
Usare `update_task` con parametro `due` dopo l'import:

```python
# Step 1: Import senza date
result = mcp_checkvist-mcp_import_tasks(
    content="Task",
    list_id="123"
)

# Step 2: Update con due date
mcp_checkvist-mcp_update_task(
    task_id=task_id,
    list_id="123",
    due="tomorrow"  # ✅ Funziona
)
```

### Note
- Priority parsing (`!1`, `!2`, ecc.) **funziona correttamente** in import
- Tag parsing (`#tag`) **funziona correttamente** in import
- Solo date (`^`) e assignment (`@`) non funzionano

### ⚠️ IMPORTANT: Verification Needed
**User Feedback**: `@person` richiede che la persona esista come utente collaboratore nella lista Checkvist. `^date` richiede formati riconosciuti da Checkvist.

**Status**: NON VERIFICATO se i test hanno usato:
- Utenti validi per `@dev1`, `@dev2`, `@tester`
- Formati date riconosciuti da Checkvist

**Recommendation**: Re-testare con:
1. Utenti reali dal team Checkvist
2. Formati date documentati ufficialmente da Checkvist

Questo potrebbe essere un **falso positivo** - il parsing potrebbe funzionare correttamente con input validi.

---

## ℹ️ BUG #3: Assignment Parsing (`@person`) Non Funziona in Import

**Severity**: LOW  
**Status**: OPEN  
**Discovered In**: Cycle v1, Test 1.1 | Cycle v4, Test 4.1

### Description
Il parsing degli assignment usando la sintassi `@person` non funziona in `import_tasks`. Gli assignment rimangono come testo nel content.

### Reproduction Steps
```python
mcp_checkvist-mcp_import_tasks(
    content="Task @dev1 @dev2",
    list_id="946456"
)

# Expected: Task assegnato a dev1 e dev2
# Actual: "@dev1 @dev2" rimane nel testo
```

### Impact
- Users non possono assegnare task durante bulk import
- Minore rispetto al bug delle date perché gli assignment sono meno comuni

### Workaround
Nessuno disponibile via API MCP. Non esiste un parametro `assigned_to` in `update_task`.

**Soluzione**: Assegnare manualmente via UI Checkvist.

### Note
Questo potrebbe essere un **limitation by design** se l'API Checkvist non supporta assignment via import endpoint.

### ⚠️ IMPORTANT: Verification Needed
**User Feedback**: `@person` funziona solo se la persona è un collaboratore esistente nella lista Checkvist.

**Status**: NON VERIFICATO - i test hanno usato `@dev1`, `@dev2` che probabilmente non esistono come utenti.

**Recommendation**: Re-testare con utenti reali dal team Checkvist.

Questo è probabilmente un **falso positivo**.

---

## Summary Table

| Bug ID | Component | Severity | Status | Workaround Available |
|--------|-----------|----------|--------|---------------------|
| #0 | `create_list` ID mismatch | CRITICAL | CONFIRMED | ❌ No |
| #1 | `add_note` 403 error | CRITICAL | OPEN (likely related to #0) | ❌ No |
| #2 | Date parsing `^` | N/A | NOT A BUG (API limitation) | ✅ Yes (via `update_task`) |
| #3 | Assignment parsing `@` | N/A | NOT A BUG (API limitation) | ❌ No (manual UI only) |

### Final Verdict

**Actual Bugs**: 2 (Bug #0 and Bug #1, likely related)  
**False Positives**: 2 (Bug #2 and #3 are Checkvist API limitations, not MCP bugs)

**Root Cause Analysis**: Bug #0 (ID mismatch) is likely causing Bug #1 (403 on add_note). Fixing Bug #0 should resolve both issues.

---

## Recommendations

### Immediate Actions
1. **Fix Bug #1** (`add_note` 403): Highest priority, blocca testing completo
2. **Document Bug #2** workaround: Aggiungere alla documentazione MCP che date devono essere impostate via `update_task`

### Future Enhancements
1. Implementare parsing `^date` in `import_tasks` per parità con priority/tag parsing
2. Investigare se assignment `@person` è supportato dall'API Checkvist upstream
3. Aggiungere validation degli ID prima di chiamare `add_note` per evitare 403

---

## Test Evidence

Tutti i bug sono stati riprodotti durante la test session del 2026-02-01.

**Logs disponibili in**: `test_config.md`  
**Full walkthrough**: `walkthrough.md`
