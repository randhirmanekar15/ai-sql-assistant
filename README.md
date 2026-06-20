# AI SQL Assistant

Ask questions in plain English; a local LLM writes the SQL, runs it against a database, and returns the answer — behind a Streamlit UI. Fully local on [Ollama](https://ollama.com), no API keys.

The database connection is **read-only**: even if the model generates a `DELETE` or `DROP`, it cannot run.

## Stack

| Piece | Choice |
|-------|--------|
| LLM runtime | Ollama (local) |
| Model | `codellama` (`temperature=0`) |
| Orchestration | LangChain + `langchain-experimental` |
| Database | SQLite (read-only URI) |
| UI | Streamlit |

## Setup

```bash
ollama pull codellama
pip install -r requirements.txt
python db_setup.py          # creates demo sales.db
```

## Usage

```bash
streamlit run app.py        # UI
# or
python sql_assistant.py     # one-shot CLI
```

Configure via env vars: `OLLAMA_MODEL`, `SQL_ASSISTANT_DB`.

## Test

```bash
pip install pytest
pytest                      # DB builder test, no model needed
```

## Security

`SQLDatabaseChain` executes generated SQL. Always connect as a **read-only** user (the default URI here uses SQLite `mode=ro`). Never grant write/delete.

## Limitations

- Hallucinates on ambiguous questions — needs a clear metric and filter.
- Only as good as your schema: cryptic column names produce bad SQL.

---

Inspired by Aman Kharwal's tutorial, [Create an AI SQL Assistant with LangChain](https://amanxai.com/2026/05/13/create-an-ai-sql-assistant-with-langchain/). Rebuilt and extended (read-only enforcement, friendly error UX, demo DB builder, env config).

MIT licensed.
