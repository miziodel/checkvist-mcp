# Ispirazione dal Server MCP di Notion per Checkvist

Analizzando come il protocollo MCP interagisce con Notion, ecco le "best practice" e le funzionalità da importare nel design di un server per Checkvist.

## 1. Il Tool "Search" come Punto d'Ingresso

L'MCP di Notion non costringe l'IA a conoscere gli ID delle pagine. Offre un tool `search` che permette al modello di trovare il contesto prima di agire.

- **Checkvist Adaptation:** Implementare un tool `search_checkvist(query)` che restituisce una lista di ID di task o checklist.
- **Esempio:** Se chiedi "Aggiungi latte alla spesa", l'IA prima cerca "spesa", ottiene l'ID della lista e poi aggiunge il task.

## 2. Rappresentazione in Markdown della Gerarchia

Notion trasforma i blocchi annidati in Markdown per renderli leggibili all'LLM.

- **Checkvist Adaptation:** Quando una risorsa (es. una lista intera) viene caricata, il server deve convertirla in un formato indentato:
    - Task Genitore
        - Sotto-task A
        - Sotto-task B (completato)

Questo permette all'IA di "vedere" la struttura ad albero tipica degli outliner come Checkvist.

## 3. Strumenti Atomici vs. Strumenti Composti

Notion espone strumenti semplici come `append_block`. Per Checkvist, dovremmo seguire questo schema:

- `add_task`: Crea un singolo nodo.
- `update_task`: Cambia testo, stato o tag.
- `move_task`: Cruciale in un outliner per riorganizzare la gerarchia.

## 4. Gestione dei Metadati (Tags e Date)

L'MCP di Notion gestisce le proprietà dei database (date, select, multi-select).

- **Checkvist Adaptation:** Dobbiamo esporre i "Smart Syntax" di Checkvist tramite l'API. Se l'IA invia un task con `^domani` o `#priorità`, il server deve decidere se inviarlo come testo grezzo (lasciando che Checkvist lo processi) o mappare esplicitamente i campi `due_date` e `tags` dell'API.

---

## Struttura Suggerita per il Server Checkvist MCP

Ecco come definirei i "Tools" ispirandomi alla pulizia di Notion:

| Tool | Input | Descrizione |
| :--- | :--- | :--- |
| `list_checklists` | - | Elenca tutte le checklist (per dare una panoramica iniziale). |
| `get_list_content` | `list_id` | Recupera l'intero outline formattato in Markdown. |
| `search` | `query` | Cerca task o liste corrispondenti a una stringa. |
| `add_task` | `content, parent_id, position` | Aggiunge un task (anche in una posizione specifica). |
| `set_task_status` | `task_id, completed` | Marca come fatto/non fatto. |
| `add_note` | `task_id, note_text` | Aggiunge commenti o note a un task esistente. |

### Il "Tocco di Classe" di Notion: Caching degli ID

L'MCP di Notion è veloce perché "ricorda" brevemente le ultime pagine visitate. Per Checkvist, il server potrebbe tenere in cache la mappatura tra "Nome della Lista" e "ID" per evitare chiamate API ridondanti ogni volta che l'utente nomina un progetto.