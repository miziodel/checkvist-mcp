---
version: 1.0.1
last_modified: 2026-01-30
status: active
---

# 🎭 Human Testing Playbook (The "Vibe Check")

While the automated tests verify the code, these manual scenarios verify if the Agent is actually *useful* and *intelligent*.

## 🧪 Persona: The Messy Brain (Triage & Capture)
**Goal**: Test how well the Agent handles unorganized input.

1.  **Scenario: The Brain Dump**
    - **Action**: Paste the following text:
      > "Ricordati di comprare il latte stasera ^oggi, poi ho pensato che per il progetto MCP dovremmo aggiungere la ricerca globale !2. Ah, per la spesa servono anche le uova. Devo anche chiamare l'assicurazione lunedì prossimo per il rinnovo della macchina. E magari taggare tutto come #admin."
    - **Prompt**: "Smista queste note in Checkvist. Metti le cose di casa in 'Spesa' e quelle di lavoro in 'Lavoro'. Usa la smart syntax di Checkvist per date e priorità."
    - **Vibe Check**: Does the agent correctly group them? Does it extract "latte" and "uova" into 'Spesa'? Is the insurance call scheduled for next Monday?
2.  **Scenario: Identity Crisis**
    - **Action**: Have two checklists with similar names (e.g., "Dev" and "Dev-Legacy").
    - **Prompt**: "Aggiungi un task a Dev."
    - **Vibe Check**: Does it pick the most relevant one or ask for help?

## 🧪 Persona: The Architect (WBS & Structure)
**Goal**: Test nested hierarchy and bulk operations.

1.  **Scenario: Project Scaffolding**
    - **Prompt**: "Crea la struttura di un progetto per lanciare un Podcast. Voglio nodi per Registrazione, Editing e Distribuzione, con almeno 3 sotto-task ciascuno."
    - **Vibe Check**: View the tree in Checkvist. Is the hierarchy clean? Are the sub-tasks logical?
2.  **Scenario: The Big Move**
    - **Prompt**: "Sposta tutto l'intero ramo 'Editing' sotto una nuova lista chiamata 'Produzione'."
    - **Vibe Check**: Check if all children moved correctly without breaking links.

## 🧪 Persona: The Curator (Review & Resurfacing)
**Goal**: Test intelligence and memory.

1.  **Scenario: The Morning Briefing**
    - **Prompt**: "Sei il mio Project Manager. Dimmi cosa devo fare oggi e ripesca un'idea vecchia che potrebbe aiutarmi."
    - **Vibe Check**: Does the summary sound professional? Is the "resurfaced" idea actually relevant?
2.  **Scenario: Snippet Hunt**
    - **Prompt**: "Dove ho salvato quel pezzo di codice Python per l'autenticazione?"
    - **Vibe Check**: Does it find it even if it's buried in a task note from 2 months ago?

---

## 🚦 Verification Checklist for Humans
- [ ] **Formatting**: I risultati in chat sono leggibili (Markdown)?
- [ ] **Speed**: L'Agent risponde in tempi ragionevoli?
- [ ] **Smartness**: L'Agent ha usato `^due` e `#tags` correttamente invece di scrivere testo piatto?
- [ ] **Safety**: L'Agent chiede conferma prima di cancellare o fare mosse "massive"?
