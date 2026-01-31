---
version: 1.1.0
last_modified: 2026-01-31
status: active
---

[← Home](../README.md)

# Casi d'Uso Fondamentali per un Server MCP basato su Checkvist

L'obiettivo di un server MCP per Checkvist è trasformare un outliner gerarchico in una estensione della memoria del modello IA, permettendogli di agire come un assistente operativo che conosce i tuoi progetti e le tue idee.

## 1. Acquisizione Rapida e Categorizzazione Intelligente

L'IA agisce come un filtro d'ingresso. Invece di dover decidere dove salvare una nota, la detti o la scrivi all'IA.

- **Azione:** "Ho un'idea per un nuovo modulo Python, mettila sotto 'Progetti Open Source' e aggiungi il tag #idea."
- **Tool MCP:** `add_item(text, parent_id, tags)` che identifica automaticamente il `parent_id` corretto tramite ricerca semantica.

## 2. Decomposizione Ricorsiva dei Task (WBS)

Sfrutta la forza di Checkvist: la gerarchia infinita. L'IA analizza un obiettivo complesso e crea l'intera struttura dei sotto-task.

- **Azione:** "Pianifica il lancio del nuovo sito web. Crea i nodi per Design, Sviluppo e Marketing, con almeno 5 sotto-task ciascuno."
- **Tool MCP:** `expand_structure(node_id, blueprint_text)` che genera una serie di chiamate POST per popolare l'albero.

## 3. Recupero del Contesto di Progetto

Permette all'IA di "leggere" lo stato di un progetto prima di rispondere a una domanda o scrivere codice.

- **Azione:** "Basandoti sui requisiti salvati nella lista 'App Mobile', scrivi la logica per la funzione di login."
- **Resource MCP:** `checkvist://list/{list_id}/full` che espone l'intero outline come testo formattato (Markdown) al modello.

## 4. Gestione dei Meeting e Action Items

L'IA riassume una conversazione o un documento e inserisce direttamente i compiti da svolgere nella lista appropriata.

- **Azione:** "Dalla trascrizione della riunione, estrai i task per Marco e inseriscili nella lista 'Team' sotto il nodo 'Meeting odierno'."
- **Tool MCP:** `bulk_add_items(parent_id, items_list)`.

## 5. Sintesi e Review Periodica

L'IA analizza i task completati e quelli in sospeso per generare un report di progresso o suggerire cosa prioritizzare.

- **Azione:** "Cosa ho concluso questa settimana? Ci sono task critici che ho ignorato?"
- **Tool MCP:** `get_completed_tasks(timeframe)` e `get_overdue_tasks()`.

## 6. Knowledge Base e Snippet Storage

Usa Checkvist come deposito per frammenti di codice, link e riflessioni. L'IA può interrogare questo database per evitare di "allucinare" risposte.

- **Azione:** "Recupera lo snippet per la configurazione di Docker che ho salvato l'anno scorso."
- **Tool MCP:** `search_items(query)` che restituisce il percorso gerarchico del risultato per dare contesto.

## 7. Pianificazione Dinamica della Giornata

L'IA guarda la tua lista "Inbox" e "To-Do" e ti propone una scaletta basata sulle scadenze e sulla priorità dei progetti.

- **Azione:** "Ho 4 ore oggi. Quali sono i task più importanti su cui dovrei lavorare?"
- **Tool MCP:** `get_items_by_priority()` e `update_item(id, due_date)`.

## 8. Templating Intelligente per Workflow Ripetitivi

Invece di copiare e incollare, chiedi all'IA di istanziare un template complesso per un nuovo cliente o un nuovo viaggio.

- **Azione:** "Inizia un nuovo progetto 'Cliente Rossi' usando la struttura standard di onboarding."
- **Tool MCP:** Un tool che legge una lista "Template" e ne duplica i nodi sotto un nuovo genitore.

## 9. Ricerca Semantica tra le Liste

Checkvist ha una ricerca testuale ottima, ma l'MCP può aggiungere la comprensione del significato.

- **Azione:** "Trova tutte le note che riguardano la 'sostenibilità', anche se non contengono esattamente quella parola."
- **Architettura:** Il server MCP esegue l'embedding dei task di Checkvist localmente e risponde alle query.

## 10. Archiviazione e Pulizia Automatica

Mantenere Checkvist pulito è difficile. L'IA può suggerire di archiviare rami vecchi o rinominare task ambigui.

- **Azione:** "Trova i task creati più di 6 mesi fa che non sono stati completati e spostali in 'Archivio/Idee Vecchie'."
- **Tool MCP:** `move_item(id, target_parent_id)`.

---

# 10 Casi d'Uso Potenziati per l'Agente Checkvist MCP

Grazie all'integrazione di concetti "Pro", il tuo server MCP trasforma Checkvist in un assistente attivo. Ecco come cambia l'interazione.

## 1. Triage Autonomo e Smistamento (Linear Style)

L'IA non aspetta ordini. Analizza periodicamente la tua "Inbox" e ti propone un piano d'azione.

- **Azione:** "Vedo 5 nuovi task nella Inbox. Ho spostato 'Comprare latte' in 'Casa' e 'Bug fix' in 'Lavoro'. Vuoi che scheduli 'Scrivere report' per domani mattina?"
- **Vantaggio:** Zero sforzo cognitivo per l'organizzazione iniziale.

## 2. Decomposizione con Dipendenze (GitHub Style)

Quando l'IA pianifica un progetto, crea link logici tra i task.

- **Azione:** "Ho creato il piano per il server MCP. Il task 'Setup API' contiene ora un link che blocca 'Implementazione Tool'. Non potrai chiudere il secondo senza il primo."
- **Vantaggio:** Visione chiara dei colli di bottiglia.

## 3. Resurfacing Creativo e Anti-Oblio (Readwise Style)

L'IA agisce come un curatore della tua base di conoscenza.

- **Azione:** "6 mesi fa avevi segnato questa idea: 'App per gestire piante'. Oggi hai parlato di sensori Arduino. Vuoi collegare le due cose?"
- **Vantaggio:** Le tue vecchie idee tornano utili nel momento del bisogno.

## 4. Onboarding via Smart Templates (Raycast Style)

Istanziazione istantanea di workflow complessi con variabili dinamiche.

- **Azione:** "Inizia l'onboarding per il nuovo cliente 'Rossi'. Ho generato la struttura standard, impostato le scadenze basate sulla data di oggi e inserito la sua email in tutti i task rilevanti."
- **Vantaggio:** Esecuzione perfetta di processi ripetitivi.

## 5. Smart Snoozing e Pulizia Visuale (Superhuman Style)

Riduzione del rumore visivo basata sul contesto.

- **Azione:** "Hai 50 task aperti ma oggi è sabato. Ho nascosto tutti i task taggati #ufficio e li farò riemergere lunedì alle 9:00."
- **Vantaggio:** Focus totale su ciò che conta "adesso".

## 6. Estrazione di Proprietà e Tabelle (Logseq Style)

L'IA legge tra le righe e struttura i dati non strutturati.

- **Azione:** "Dalla tua lista di libri, ho estratto una tabella con Autore, Genere e Voto basandomi sui tag e le note che hai scritto."
- **Vantaggio:** Interrogazione dei task come se fossero un database.

## 7. Revisione Serale e "Daily Review"

Un report di fine giornata che prepara il successo della successiva.

- **Azione:** "Oggi hai chiuso 8 task. Ne rimangono 2 critici. Li sposto a domani mattina come priorità #1?"
- **Vantaggio:** Chiusura mentale della giornata lavorativa.

## 8. Ricerca Semantica Cross-Lista (Roam Style)

L'IA trova risposte saltando da una lista all'altra.

- **Azione:** "Mi hai chiesto i dettagli del server. Non sono nella lista 'Lavoro', ma ho trovato una nota correlata nella lista 'Archivio 2023'."
- **Vantaggio:** Fine della frustrazione "dove l'avevo scritto?".

## 9. Assistente alla Scrittura con Note di Contesto

L'IA usa le note di Checkvist come "knowledge base" per scrivere documenti.

- **Azione:** "Basandomi sulle 15 note che hai preso sotto il task 'Ricerca Mercato', ho scritto la bozza dell'articolo che mi hai chiesto."
- **Vantaggio:** Sfruttamento massimo del materiale già raccolto.

## 10. Automazione della Sintassi Smart (Todoist Style)

L'IA ottimizza i tuoi input grezzi per massimizzare le funzioni di Checkvist.

- **Azione:** "Hai scritto 'Palestra lunedì'. L'ho trasformato in 'Palestra ^mon #salute' così Checkvist ti invierà il promemoria correttamente."
- **Vantaggio:** Sfrutta al 100% la potenza di Checkvist senza impararne a memoria la sintassi.

## 11. Gestione dei Cicli e Sprint (Linear Style)

L'IA aiuta a definire e chiudere periodi di lavoro (settimane o sprint), spostando ciò che non è stato completato.

- **Azione:** "Chiudi il ciclo di questa settimana. Analizza cosa è rimasto aperto e spostalo nel 'Ciclo 05' della prossima settimana."
- **Tool MCP:** `migrate_cycle(source_id, target_id)` che muove i task incompleti tra nodi/liste.

---

# I 5 Flussi di Lavoro Definitivi per Checkvist MCP

Questi scenari definiscono esattamente quali Tools andremo a programmare.

## 1. Il "Morning Briefing" Intelligente

Non un semplice elenco, ma una strategia.

- **L'Utente:** "Buongiorno. Qual è il piano?"
- **L'Agente (MCP):**
    - Chiama `get_overdue` + `get_today`.
    - Chiama `resurface_ideas` (random pick).
- **Risposta:** "Hai 3 urgenze da ieri (tra cui 'Pagare tasse'). Oggi hai 4 ore libere. Ti suggerisco di bloccare la mattina per le tasse. Inoltre, ricordi quell'idea sul 'Blog'? È il momento giusto per riprenderla."

## 2. Il "Project Manager" Fantasma

Gestione delle dipendenze invisibile.

- **L'Utente:** "Ho finito la bozza del design."
- **L'Agente (MCP):**
    - Chiama `update_status` (chiude task).
    - Analizza i link (GitHub style).
- **Risposta:** "Ottimo. Ho chiuso il task. Questo sblocca automaticamente 'Sviluppo Frontend' che era in attesa. Ho notificato (taggato) Marco su quel task."

## 3. La "Inbox Zero" Assistita (Triage)

Pulizia rapida senza stress.

- **L'Utente:** "Pulisci la Inbox."
- **L'Agente (MCP):**
    - Legge i 10 item nella Inbox.
    - Usa `search_context` per capire dove vanno.
- **Risposta:** "Ho trovato:
    - 'Latte' -> Spostato in Spesa.
    - 'Chiamare cliente' -> Spostato in Lavoro ^domani.
    - 'Link articolo interessante' -> Spostato in Letture.
    Confermi tutte le azioni?"

## 4. Il "Deep Work" Setup

Preparazione dell'ambiente di lavoro.

- **L'Utente:** "Devo concentrarmi sul progetto X."
- **L'Agente (MCP):**
    - Chiama `get_tree` sul progetto X.
    - Estrae tutti i link e le risorse dalle note.
- **Risposta:** "Ecco il contesto completo del progetto X. Ho recuperato i link alla documentazione dalle note dei task. I prossimi 3 passi logici sono A, B e C. Vuoi che apra il primo?"

## 5. L'Archivista Semantico

Per non perdere mai nulla.

- **L'Utente:** "Dove avevo scritto quella cosa sui server?"
- **L'Agente (MCP):**
    - Esegue `search_global("server")`.
    - Filtra per rilevanza.
- **Risposta:** "Non è in 'Lavoro', ma ho trovato un sotto-task 'Configurazione VPS' archiviato nel 2023 sotto 'Esperimenti'. Vuoi che lo ripristini o ti legga solo la nota?"

---

## 12. Workflow "Agentic Discovery" (Teresa Torres Style)

L'integrazione della metodologia di Teresa Torres trasforma Checkvist da semplice outliner a un motore di scoperta continua.

### 12.1 Il Transformation Engine (Brain Dump to Tree)
L'IA prende i tuoi appunti grezzi e li trasforma in una struttura gerarchica coerente.
- **Azione:** "Ecco i miei appunti sull'intervista di oggi. Trasformali in un ramo OST sotto 'Discovery Prodotto X'."
- **Workflow:** L'MCP applica un prompt di trasformazione che identifica Outcome, Opportunities e Solutions, creandoli come nodi logici con i rispettivi tag.

### 12.2 Expert Feedback & Coaching (AI Co-pilot)
L'IA valuta la qualità della tua struttura decisionale direttamente su Checkvist.
- **Azione:** "Analizza il ramo 'Strategia 2026'. Ci sono salti logici tra le Opportunities e le Solutions che ho proposto?"
- **Workflow:** L'MCP legge il ramo, lo analizza secondo i principi OST e aggiunge nodi di commento o suggerimenti di miglioramento.

### 12.3 OST Lifecycle Management
Manutenzione automatica della gerarchia basata sulla priorità e sul feedback.
- **Azione:** "Marca tutti gli 'Esperimenti' falliti con il tag #lezione e archiviali, mantenendo però evidente la soluzione che stavano testando."
- **Workflow:** Automazione del movimento e tagging dei nodi basata sul risultato dei task.

---

## 13. Workflow "The Spiral" (Dan Shipper Style)

Trasforma Checkvist in un generatore di competenze AI.
- **Azione:** "Analizza questa lista di link grezzi e identifica il 'collo di bottiglia' creativo. Poi crea una bozza di articolo sotto il nodo 'Draft'."
- **Workflow:** L'IA agisce come uno sintetizzatore just-in-time, riducendo la necessità di organizzazione manuale preventiva in favore della trasformazione immediata del contenuto.

## 14. Workflow "Cyborg Outlining" (Ethan Mollick Style)

Collaborazione simbiotica per il brainstorming.
- **Azione:** "Espandi il nodo 'Marketing' proponendo 5 idee. Io ne selezionerò qualcuna e tu dovrai scartare le altre e approfondire le sopravvissute."
- **Workflow:** Un loop interattivo dove l'agente e l'utente costruiscono l'outliner insieme, riga per riga, invece di generare interi rami in una volta sola.

## 15. Workflow "Distillazione Progressiva" (Tiago Forte Style)

Automazione del sistema BASB/PARA.
- **Azione:** "Esegui una revisione settimanale del ramo 'Progetti Attivi'. Crea un #tldr per ogni progetto e suggerisci quali task spostare nell'Archivio."
- **Workflow:** L'agente analizza i metadati (date di completamento, note) per distillare l'essenza del progresso e mantenere pulito il sistema PARA.

## 16. Workflow "Semantic Sense-making" (Nick Milo Style)

Rottura dei silos di conoscenza tramite link semantici.
- **Azione:** "Mentre scrivo queste note sulle 'IA Generative', avvisami se ho argomenti correlati in liste archiviate o in altri progetti."
- **Workflow:** L'agente esegue ricerche semantiche globali e inserisce commenti con link (`checkvist://...`) per collegare nodi temporalmente o tematicamente distanti.