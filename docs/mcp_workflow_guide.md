---
version: 1.1.0
last_modified: 2026-01-31
status: active
---

# Guida Operativa: Workflow Agentico con Checkvist e MCP

Benvenuto nel futuro della "Continuous Discovery". Questa guida ti mostrerà come implementare la metodologia di **Teresa Torres** e il concetto di **"Agentic PKM"** utilizzando **Checkvist** come outliner e il server **MCP** come motore di trasformazione.

> [!NOTE]
> **Questo workflow è un "Flavor" (uno stile d'uso):**
> Il server MCP per Checkvist è uno strumento agnostico. Quello descritto qui è solo uno dei tanti modi (un "sapore") di utilizzarlo. La filosofia unica dell'integrazione è quella di dare potere all'utente tramite l'IA, indipendentemente dalla specifica metodologia scelta (che sia OST, GTD, PARA o un sistema personale).

## 1. Struttura Checkvist: L'Opportunity Solution Tree (OST)

In Checkvist, ogni lista o progetto dovrebbe seguire questa gerarchia logica:

1.  **Outcome (#outcome)**: Il tuo obiettivo strategico (es. "Migliorare la salute fisica").
2.  **Radici Maslow**: Wellness, Safety, Belonging, Esteem, Growth (per categorizzare l'origine del bisogno).
3.  **Opportunity (#opp)**: Un problema, bisogno o desiderio dell'utente (o tuo).
4.  **Solution (#sol)**: Un modo potenziale per risolvere l'opportunità.
5.  **Experiment (#exp)**: Un'azione pratica, piccola e misurabile per testare la soluzione.

### Esempio di Struttura:
```text
[ ] Migliorare il setup di lavoro #outcome
  [ ] Wellness
    [ ] #opp: La sedia attuale mi causa mal di schiena
      [ ] #sol: Comprare una nuova sedia ergonomica
        [ ] #exp: Provare 3 modelli nello showroom X
      [ ] #sol: Usare una standing desk
```

## 2. Il "Transformation Engine" con MCP

Uno dei colli di bottiglia maggiori è passare da un'idea confusa (Brain Dump) a una struttura ordinata. L'MCP risolve questo problema.

### Caricamento dell'Input
Crea un nodo chiamato `Inbox` o utilizza il tag `#dump`. Scrivi liberamente le tue idee o incolla la trascrizione di una riunione/intervista.

### Comando Assistente (The Hybrid Cyborg)
Chiedi al tuo Agente AI (es. Claude) di agire sul ramo:
> "Prendi il contenuto del nodo 'Brain Dump Progetto X', analizzalo secondo la metodologia OST e crea una struttura di Opportunities e Solutions sotto il nodo 'Roadmap 2026'."

### Risultato Atteso
L'MCP eseguirà una serie di chiamate `add_item` per popolare l'albero su Checkvist, applicando automaticamente i tag `#opp` e `#sol`.

## 3. Gestione del Ciclo di Vita (Status & Feedback)

Usa i tag e i colori di Checkvist per gestire lo stato degli esperimenti:

- `#exp` + `Closed`: L'esperimento è finito.
- `#lesson`: Aggiungi questo tag a un nodo per descrivere ciò che hai imparato.
- `#archived`: Per le soluzioni scartate dopo un esperimento fallito.

### Revisione Automatica (Co-pilot Feedback)
Chiedi all'Agente:
> "Analizza il ramo 'Setup Lavoro'. Basandoti sugli esperimenti chiusi e sui tag #lesson, suggerisci se dovremmo approfondire la soluzione 'Standing Desk' o se è il caso di scartarla."

## 4. Cheat Sheet per i Prompt MCP

Ecco alcuni prompt pronti all'uso per massimizzare l'efficienza:

| Obiettivo         | Prompt Suggerito                                                                                    |
| :---------------- | :-------------------------------------------------------------------------------------------------- |
| **Brainstorming** | "Genera 5 #sol alternative per l'opportunità 'Mal di schiena' basandoti sui principi di ergonomia." |
| **Triage**        | "Guarda la mia Inbox e suggerisci quale #outcome esistente potrebbe accogliere questi nuovi item."  |
| **Sintesi**       | "Crea un #tldr dei progressi fatti su questo ramo nelle ultime due settimane."                      |
| **Discovery**     | "Cerca nelle mie liste archiviate se abbiamo già testato soluzioni simili a questa."                |

## 5. Prossimi Passi
1.  **Configura i Tag**: Assicurati che `#outcome`, `#opp`, `#sol`, `#exp` siano tra i tuoi tag preferiti in Checkvist.
2.  **Crea la Radice**: Inizia un nuovo albero partendo da un Outcome chiaro.
3.  **Delega la Struttura**: Inizia con un brain dump e chiedi all'MCP di "ordinare il caos".

---

### Per Approfondire
- **[Research Hub](research/README.md)**: Scopri le teorie di Dan Shipper, Tiago Forte, Ethan Mollick e Nick Milo.
- **[Casi d'Uso Evoluti](use-cases.md)**: Esempi pratici di comandi per ogni stile di workflow.
