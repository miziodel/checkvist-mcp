# Checkvist MCP Server: Architettura Visionaria

Questo documento è il punto di riferimento per lo sviluppo del server MCP. Unisce la struttura degli outliner, la flessibilità dei knowledge graph e l'efficienza dei tool di sviluppo.

## 1. Fondamenta della Struttura (The "Big Three")

| Fonte | Concetto | Applicazione Checkvist |
| :--- | :--- | :--- |
| **Notion** | Search-First | L'IA cerca sempre l'ID della lista/task per nome prima di operare. |
| **Obsidian** | Scrittura Atomica | Append veloce e gestione in Markdown per mantenere la leggibilità. |
| **ClickUp** | Metadati Ricchi | Uso intensivo di note e priorità per contestualizzare ogni task. |

## 2. Flusso di Lavoro Avanzato (Efficiency & NLP)

| Fonte | Concetto | Applicazione Checkvist |
| :--- | :--- | :--- |
| **Linear** | Triage Proattivo | Funzione di smistamento automatico dei nuovi task (Inbox Management). |
| **Todoist** | Smart Syntax | Inserimento tramite linguaggio naturale (`^domani #focus`). |
| **Logseq** | Proprietà Custom | Interpretazione di `chiave:: valore` all'interno del testo del task. |
| **Roam** | Serendipity | Ricerca di connessioni e riferimenti incrociati tra rami diversi. |

## 3. Livello Professionale (Advanced Automation)

| Fonte | Concetto | Applicazione Checkvist |
| :--- | :--- | :--- |
| **GitHub** | Cross-Referencing | Uso di ID e link per gestire le dipendenze ("Questo task blocca #123"). |
| **Readwise** | Resurfacing | L'IA ripropone vecchie idee o note per evitare che cadano nell'oblio. |
| **Superhuman** | Smart Snooze | Spostamento temporaneo di task non urgenti per pulire la vista attuale. |
| **Raycast** | Smart Macros | Template dinamici che iniettano variabili in strutture predefinite. |

---

## 4. Specifiche Tecniche dei Tool MCP

### Gruppo: Navigazione (Core)

- `search(query)`: Ricerca globale testuale e semantica.
- `get_tree(id, depth)`: Esplora la gerarchia in modo controllato.
- `get_breadcrumbs(id)`: Ricostruisce il percorso (es. Progetti > AI > Server).

### Gruppo: Azione (Agentic)

- `smart_add(text, parent_id)`: Aggiunge task interpretando date e tag.
- `triage_inbox()`: Analizza la inbox e propone destinazioni.
- `apply_template(template_id, variables)`: Clona strutture predefinite.

### Gruppo: Manutenzione (Proactive)

- `resurface_ideas()`: Recupera task "stagnanti" per revisione.
- `link_dependency(task_a, task_b)`: Crea un legame logico e visivo tra due compiti.
- `snooze(id, until)`: Nasconde o riprogramma task per ridurre il rumore.