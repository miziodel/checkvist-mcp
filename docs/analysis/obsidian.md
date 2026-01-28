# Ispirazione dal Server MCP di Obsidian per Checkvist

Obsidian è l'unione tra un file system e una rete di pensieri. Per Checkvist, questo si traduce nel trattare le liste non solo come "compiti", ma come una vera base di conoscenza.

## 1. Il concetto di "Daily Note" (Note Giornaliere)

Quasi tutti i server MCP di Obsidian hanno un tool specifico `get_daily_note`.

- **Checkvist Adaptation:** Implementare un tool `get_today_focus`. Invece di cercare tra tutte le liste, questo tool interroga l'API di Checkvist per tutti i task con `due_date: oggi` o tag `#focus`.
- **Utilità:** Permette all'IA di dare un "buongiorno" operativo all'utente appena apre la chat.

## 2. Scrittura Atomica (Append vs Overwrite)

Gli MCP di Obsidian evitano di riscrivere interi file. Usano tool come `append_to_note` o `insert_before_heading`.

- **Checkvist Adaptation:** Invece di caricare e scaricare intere liste, il server dovrebbe specializzarsi in `append_subtask(parent_id, text)`.
- **Ispirazione:** Come Obsidian usa i "Headings" (titoli) come ancora, Checkvist può usare i task di primo livello come "sezioni" in cui l'IA può iniettare dati.

## 3. Backlinks e Riferimenti

Obsidian eccelle nel mostrare cosa punta a cosa.

- **Checkvist Adaptation:** Checkvist permette di ottenere link permanenti ai task. Il server MCP potrebbe implementare un tool `get_task_link(task_id)` che l'IA può usare per citare un task specifico in un'altra lista, creando una rete di progetti interconnessi.

## 4. Il Tool "Patch" (Modifica Intelligente)

Dato che i file di Obsidian sono lunghi, l'IA spesso usa un tool per cercare una stringa e sostituirla.

- **Checkvist Adaptation:** Implementare `rename_or_move_task`. Se l'utente dice "Sposta il progetto X sotto Archivio", l'IA non deve cancellare e ricreare, ma usare l'id del task per fare una PUT di spostamento, preservando tutti i sotto-task e i metadati.

---

## Mappatura dei Concetti: Da Obsidian a Checkvist

| Concetto Obsidian | Equivalente Checkvist | Funzione MCP Suggerita |
| :--- | :--- | :--- |
| **Vault** | Account / Insieme di Liste | `list_all_checklists` |
| **Folder** | Checklist (Lista principale) | `get_checklist_metadata` |
| **Markdown File** | Ramo di task (Nodo genitore) | `get_task_hierarchy` |
| **Frontmatter (YAML)** | Smart Syntax (`#tag`, `^data`) | `parse_smart_syntax` |
| **Search (Grep)** | API Global Search | `search_across_all_lists` |

### La lezione più importante: "Context over Content"

I server Obsidian MCP hanno successo perché non provano a leggere tutti i file contemporaneamente (saturerebbero la memoria dell'IA). Leggono solo i file necessari.

**Per il server Checkvist:** Non dobbiamo mai inviare 10 liste piene. Dobbiamo implementare un sistema di "Preview" (es. primi 2 livelli di profondità) e permettere all'IA di "Scavare più a fondo" (`expand_node`) solo se necessario.