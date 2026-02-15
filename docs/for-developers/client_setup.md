---
version: 1.2.0
last_modified: 2026-02-01
status: active
---

# 🖥️ Client Setup: Connecting Checkvist MCP

This guide explains how to configure the Checkvist MCP server within the **Antigravity** agentic assistant.

## 1. Antigravity Configuration

Antigravity makes it easy to add custom MCP servers directly through its interface.

### Steps to Add the Server:

1.  Open **Antigravity**.
2.  Go to **Settings** (Gear icon) > **MCP**.
3.  Click on **Add Server**.
### Configurazione (UI di Antigravity)

In Antigravity, è fondamentale che gli argomenti siano separati correttamente. Se l'interfaccia permette l'inserimento riga per riga, usa una riga per ogni parola.

| Field | Value |
| :--- | :--- |
| **Server Name** | `checkvist` |
| **Command** | `path/to/.venv/bin/python` |
| **Arguments** | `path/to/src/server.py` |

### Metodo Consigliato: File `.env` (Più Sicuro)

Per evitare di scrivere le tue credenziali direttamente nella configurazione di Antigravity:

1.  Assicurati che esista un file `.env` nella cartella root del progetto.
2.  All'interno, inserisci le tue credenziali:
    ```env
    CHECKVIST_USERNAME=tua_email@esempio.com
    CHECKVIST_API_KEY=la_tua_api_key
    ```
3.  Nella configurazione di Antigravity, puoi ora **omettere** `CHECKVIST_USERNAME` e `CHECKVIST_API_KEY`, mantenendo solo `PYTHONPATH`.

### Esempio JSON (Metodo Sicuro)

```json
"checkvist-mcp": {
  "command": "path/to/.venv/bin/python",
  "args": [
    "path/to/src/server.py"
  ],
  "env": {
    "PYTHONPATH": "path/to/checkvist-mcp"
  }
}
```

### Environment Variables

*   `PYTHONPATH`: `path/to/checkvist-mcp` (**Obbligatorio**).
*   `CHECKVIST_USERNAME` e `CHECKVIST_API_KEY`: (Opzionali se presenti nel file `.env`).

## 🔍 Troubleshooting

*   **ModuleNotFoundError: No module named 'src'**: Questo accade se la variabile `PYTHONPATH` non è impostata nel client. Assicurati che punti alla cartella genitore di `src`.

## 🤖 Error Handling & Response Format

A partire dalla versione **1.2.0**, tutti i tool restituiscono risposte strutturate in formato JSON per migliorare la precisione degli agenti AI.

### Formato Risposta
```json
{
  "success": true,
  "message": "Human-readable summary",
  "data": { ... },       // Dati opzionali se success è true
  "action": "tool_name", // Presente in caso di errore
  "next_steps": "Guida", // Suggerimenti per l'AI in caso di errore
  "error_details": "..." // Dettagli tecnici (eccetto in caso di errore 401/403)
}
```

Questo formato permette a Antigravity (o altri client) di reagire correttamente ai fallimenti invece di ricevere messaggi di testo ambigui.

## 🧠 Protocollo "Operative Intelligence" (Novità v1.4)

Per sfruttare le nuove capacità di ricerca ad alta risoluzione, suggeriamo di fornire al tuo Agent il seguente **System Prompt** o istruzioni d'uso:

### Guida per l'Agente

1.  **Cerca Prima, Leggi Dopo**: Usa sempre `search_tasks(query)` come primo passo.
2.  **Interpreta gli Indicatori**:
    *   `[N]`: Significa che ci sono **Note**. È probabile che qui ci siano le specifiche tecniche o i dettagli. -> **Azione**: `get_task(task_id)`.
    *   `[C]`: Significa che ci sono **Commenti**. Utile per capire lo storico o le discussioni. -> **Azione**: `get_task(task_id)`.
    *   `[F: 5]`: Significa che ci sono **5 Figli**. È un task "contenitore". -> **Azione**: `get_task(task_id, include_children=True)` per esplorare la struttura.
3.  **Non Indovinare**: Se la ricerca restituisce un task come `Progetto Alpha > Backend > Auth`, non chiedere "Cos'è il progetto Alpha?". Hai già il contesto nel breadcrumb.

### Esempi di Prompt Utente

*   **Drill-Down**: "Cerca 'Auth' e dammi i dettagli tecnici del task che sembra contenere le specifiche." (L'agent cercherà 'Auth', vedrà `[N]` vicino a 'Specs', e chiamerà `get_task`).
*   **Esplorazione**: "Fammi vedere come è strutturato il lavoro sul 'Backend'." (L'agent cercherà 'Backend', vedrà `[F: 12]`, e chiamerà `get_task(..., include_children=True)`).
