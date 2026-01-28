---
version: 1.0.0
last_modified: 2026-01-28
status: active
---

# 🎯 Checkvist MCP: The "Productivity OS" Vision

## Slide 1: I 4 Pilastri dell'Ispirazione

Non stiamo inventando da zero. Stiamo assemblando i "Superpoteri" dei migliori tool.

| Tool | Concetto Key | In Checkvist MCP |
| :--- | :--- | :--- |
| **Linear** 🟢 | Triage & Cycles | L'IA scansiona la Inbox e propone dove smistare i task. |
| **GitHub** 🐙 | Issues & Deps | L'IA crea link di dipendenza: "Non puoi fare B se non finisci A". |
| **Readwise** 🧠 | Spaced Repetition | L'IA ripesca vecchie idee dimenticate per darti nuovi spunti. |
| **Superhuman** ⚡ | Zero Inbox | Comandi rapidi per nascondere/snoozare task non urgenti. |

---

## Slide 2: L'Architettura "Agentica"

Il server non è un passacarte. È un Agente Operativo.

### 🔄 Il Ciclo di Vita di un Task con MCP

1. **Input:** "Ho un'idea per il progetto Alpha..."
2. **Smart Parse (Todoist Style):** L'IA rileva `^prossimo martedì` e `#idea`.
3. **Context Check (Notion Style):** L'IA controlla se esiste già un ramo "Progetto Alpha".
4. **Linking (Roam Style):** "Ehi, questo è simile a una nota di 3 mesi fa. Li collego?"
5. **Action:** Il task viene creato nel posto giusto, con i tag giusti e i link al contesto.

---

## Slide 3: La "Tech Stack" del Server

Semplice, Veloce, Stateless.

- **Core:** Python 3.13 + [FastMCP](https://github.com/jlowin/fastmcp).
- **Auth:** Checkvist Open API (Basic Auth / API Key).
- **Speed:** Caching locale leggero dei nomi delle liste.
- **Format:** Markdown nativo per input/output.

---

## Documentazione Correlata
- [Architecture](architecture.md)
- [Risks & Mitigation](risks.md)
- [Use Cases](use-cases.md)
- [Market Analysis](analysis/notion.md)