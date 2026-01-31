---
version: 1.1.0
last_modified: 2026-01-31
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
| **Command** | `/absolute/path/to/checkvist-mcp/.venv/bin/python` |
| **Arguments** | `/absolute/path/to/checkvist-mcp/src/server.py` |

### Metodo Consigliato: File `.env` (Più Sicuro)

Per evitare di scrivere le tue credenziali direttamente nella configurazione di Antigravity:

1.  Assicurati che esista un file `.env` nella cartella root del progetto (`/Users/NOBKP/checkvist-mcp/.env`).
2.  All'interno, inserisci le tue credenziali:
    ```env
    CHECKVIST_USERNAME=tua_email@esempio.com
    CHECKVIST_API_KEY=la_tua_api_key
    ```
3.  Nella configurazione di Antigravity, puoi ora **omettere** `CHECKVIST_USERNAME` e `CHECKVIST_API_KEY`, mantenendo solo `PYTHONPATH`.

### Esempio JSON (Metodo Sicuro)

```json
"checkvist-mcp": {
  "command": "/absolute/path/to/checkvist-mcp/.venv/bin/python",
  "args": [
    "/absolute/path/to/checkvist-mcp/src/server.py"
  ],
  "env": {
    "PYTHONPATH": "/absolute/path/to/checkvist-mcp"
  }
}
```

### Environment Variables

*   `PYTHONPATH`: `/absolute/path/to/checkvist-mcp` (**Obbligatorio**).
*   `CHECKVIST_USERNAME` e `CHECKVIST_API_KEY`: (Opzionali se presenti nel file `.env`).

## 🔍 Troubleshooting

*   **ModuleNotFoundError: No module named 'src'**: Questo accade se la variabile `PYTHONPATH` non è impostata nel client. Assicurati che punti alla cartella genitore di `src`.
