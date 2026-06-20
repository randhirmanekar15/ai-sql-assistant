# AI SQL Assistant

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-green) ![Runs 100% Local](https://img.shields.io/badge/runs-100%25%20local-orange)

**Ask your database questions in plain English. A local LLM writes the SQL, runs it against a read-only connection, and hands you the answer — all behind a Streamlit UI.**

## Overview

Most people who need answers from a database can't write SQL. So they file a ticket, wait two days, and the analyst who finally runs the query has already lost the context of why anyone asked. Natural-language-to-SQL fixes that loop — type "what were our top 5 products by revenue?" and get a number back, not a meeting.

Until recently the catch was that good text-to-SQL meant shipping your schema (and sometimes your data) to a cloud API. For a lot of teams that's a non-starter. AI SQL Assistant runs the model **locally with Ollama**, so nothing leaves your machine: no API keys, no per-query bill, no compliance review. Private and free is a different product than private-and-expensive.

The interesting part isn't the demo — it's the guardrail. An LLM that can write SQL can also write `DROP TABLE`. This project connects to the database in **read-only mode** (SQLite `mode=ro`), so even a hallucinated destructive query simply fails to execute. The model runs at `temperature=0` for deterministic, repeatable SQL. The result is data democratization you can actually let non-technical people touch.

## Features

- **Plain-English queries** — ask questions the way you'd ask a colleague.
- **100% local** — powered by Ollama (`codellama`); no cloud, no API keys, no usage costs.
- **Read-only by design** — the DB connection is opened `mode=ro`; `DELETE`/`DROP`/`UPDATE` physically cannot run.
- **Deterministic SQL** — `temperature=0` means the same question yields the same query.
- **Two interfaces** — a Streamlit web UI and a CLI.
- **Friendly error UX** — ambiguous questions return a plain-English tip, not a Python stack trace.
- **Batteries-included demo** — `db_setup.py` builds a sample `sales.db` using only the standard library.
- **Env-configurable** — swap the model or database without touching code.

## How it works

You type a question. LangChain's `SQLDatabaseChain` feeds the question plus your schema to the local `codellama` model, which generates a SQL query. That query is executed against a **read-only** connection, and the result comes back as the answer.

```
   ┌──────────────┐
   │ Your Question│  "Top 5 products by revenue?"
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  Local LLM   │  Ollama · codellama · temperature=0
   │ (LangChain)  │
   └──────┬───────┘
          │  generates SQL
          ▼
   ┌──────────────────────┐
   │  Read-Only Database  │  SQLite (mode=ro) — writes rejected
   └──────┬───────────────┘
          │  result rows
          ▼
   ┌──────────────┐
   │   Answer     │  "Your top product was Widget X."
   └──────────────┘
```

## Tech stack

| Layer | Tool |
|-------|------|
| LLM runtime | [Ollama](https://ollama.com/) (`codellama`) |
| Orchestration | LangChain + `langchain-experimental` (`SQLDatabaseChain`) |
| Database | SQLite (opened `mode=ro`) |
| Web UI | Streamlit |
| Language | Python 3.10+ |

## Project structure

```
ai-sql-assistant/
├── db_setup.py          # builds the demo sales.db (stdlib only)
├── sql_assistant.py     # the LangChain chain (also runs as a CLI)
├── app.py               # Streamlit UI
├── test_db_setup.py     # tests for the DB builder
├── ARTICLE.md
├── requirements.txt
├── LICENSE
└── README.md
```

## Installation

**Prerequisites:** Python 3.10+ and [Ollama](https://ollama.com/) installed and running.

```bash
git clone https://github.com/randhirmanekar15/ai-sql-assistant.git
cd ai-sql-assistant
pip install -r requirements.txt
ollama pull codellama
```

## Usage

**Step 1 — build the demo database:**

```bash
python db_setup.py
```

**Step 2 — ask questions.** Web UI (recommended):

```bash
streamlit run app.py
```

Or from the command line:

```bash
python sql_assistant.py
```

Then ask things like *"What is our total revenue?"* or *"Which product sold the most units?"*

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `codellama` | The Ollama model used to generate SQL |
| `SQL_ASSISTANT_DB` | `sqlite:///file:sales.db?mode=ro&uri=true` | Read-only DB connection URI |

## Security

**The read-only connection is not optional — it is the security model.**

`SQLDatabaseChain` executes whatever SQL the model generates. That's the whole point, and also the whole risk: an LLM can hallucinate a `DELETE FROM orders` or a `DROP TABLE` as confidently as it writes a `SELECT`. There is no prompt that guarantees it never will.

So this project doesn't rely on the prompt. It opens the database with SQLite's `mode=ro` flag, so a destructive statement is **rejected by the database engine itself** before it can touch a row. If you point this at your own database, always connect with a read-only user, and keep the assistant pointed at a replica or restricted view for sensitive data.

## Testing

```bash
pip install pytest
pytest
```

`test_db_setup.py` verifies `db_setup.py` creates the expected tables and sample rows, so the demo works on a fresh clone — no model needed.

## Limitations

- **Ambiguous questions cause hallucinations.** Give it a clear metric and filter ("total revenue *in 2025*").
- **Generated SQL is executed** — which is exactly why read-only access is mandatory.
- **It's only as good as your schema.** Cryptic column names produce cryptic queries.
- **Local model quality varies.** Complex joins or window functions may need a larger model.

## Roadmap

- [ ] Support PostgreSQL and MySQL (with enforced read-only roles)
- [ ] Show the generated SQL alongside the answer for transparency
- [ ] Query history and one-click re-run in the Streamlit UI
- [ ] Optional human-in-the-loop confirmation before execution
- [ ] Model dropdown in the UI

## Credits

📖 Full write-up: [ARTICLE.md](ARTICLE.md).

Based on Aman Kharwal's tutorial, ["Create an AI SQL Assistant with LangChain"](https://amanxai.com/2026/05/13/create-an-ai-sql-assistant-with-langchain/).

**What I changed vs the source tutorial:**

- Added **read-only enforcement** (`SQLite mode=ro`) so generated SQL can't mutate or drop data.
- Built a **friendly error UX** — ambiguous questions return a plain-English tip instead of a stack trace.
- Added a **demo database builder** (`db_setup.py`, stdlib only) plus tests.
- Made the model and database path **configurable via environment variables**.

## Author

Built by **Randhir Manekar** — [randhirmanekar.com](https://randhirmanekar.com) · [github.com/randhirmanekar15](https://github.com/randhirmanekar15)

## License

MIT — see [LICENSE](LICENSE).
