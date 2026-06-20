# I built an AI that turns plain English into SQL — and runs it locally for free

*A natural-language database assistant on top of LangChain, Ollama, and codellama. No API keys, no data leaving my machine, no SQL knowledge required to use it.*

## Why this, why now

Every company is sitting on a database that only three people know how to query. The marketing lead wants last quarter's top product. The founder wants churn by cohort. Both end up in a Slack queue waiting on an analyst who's already underwater.

That bottleneck is what "data democratization" actually means in practice — not a dashboard nobody opens, but letting a non-technical person ask a question in English and get a real answer from real data.

Natural-language-to-SQL is the unlock. And in 2026 it finally got cheap. You no longer need a metered API call to a frontier model every time someone asks "how many orders shipped late?" Local open-weight models — DeepSeek V4, Qwen 3.6, codellama — run on your own hardware. Private querying, zero per-query cost, and your customer data never touches someone else's server.

So I built one. Here's the project.

## What it does

You type a question: *"Which product generated the highest revenue?"*

The app sends it to a local LLM, which writes the SQL, runs it against a SQLite database, and hands back the answer. No SQL editor. No table names to memorize. A Streamlit text box and an answer.

It's the kind of internal tool you could drop in front of a sales ops person and they'd never know there was a `GROUP BY` happening behind the scenes.

## The stack

| Layer | Tool | Why |
|---|---|---|
| LLM runtime | Ollama | Runs open models locally, one command |
| Model | codellama (`temperature=0`) | Tuned for code/SQL, deterministic output |
| Orchestration | LangChain + `langchain-experimental` | `SQLDatabaseChain` wires LLM to DB |
| Database | SQLite (`sales.db`) | Zero-config, file-based, easy to demo |
| UI | Streamlit | Turns a script into a usable app in ~15 lines |

## How it works

The core is one chain. It introspects the database schema, asks the model to write SQL for your question, executes it, and returns the result.

```python
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_ollama import OllamaLLM

db = SQLDatabase.from_uri("sqlite:///sales.db")
llm = OllamaLLM(model="codellama", temperature=0)

db_chain = SQLDatabaseChain.from_llm(
    llm=llm, db=db, verbose=True, return_direct=True
)

result = db_chain.invoke({"query": "Which product generated the highest revenue?"})
```

The one setting that matters most here is `temperature=0`. This isn't a chatbot writing a poem — you want the *same* SQL for the *same* question, every time. Any creativity in SQL generation is a bug, not a feature. Crank the temperature up and you'll get a model that invents column names that "feel right."

`return_direct=True` means the chain hands back the raw query result instead of having the model summarize it again — fewer hops, fewer places to hallucinate.

Then the UI. Streamlit makes the whole thing a real product instead of a terminal demo:

```python
import streamlit as st

st.title("AI SQL Assistant")
question = st.text_input("Ask a question about your data:")

if question:
    with st.spinner("Thinking..."):
        try:
            result = db_chain.invoke({"query": question})
            st.success(result["result"])
        except Exception:
            st.error("Couldn't answer that one.")
            st.info("Tip: try naming the metric and timeframe, e.g. 'total revenue in 2025'.")
```

That's it. Input box, spinner, answer.

## What I changed

The tutorial gets you a working chain. I made four changes to get something I'd actually put in front of a colleague:

1. **Enforced a read-only DB user.** This is non-negotiable, and I'll explain why below. The connection string points at a user with `SELECT`-only grants. No `DROP`, no `DELETE`, no exceptions.
2. **Rewrote the error UX.** A raw stack trace is useless to a non-technical user. Instead of dumping the exception, I catch it and show a plain-English tip on how to rephrase — naming the metric and the timeframe fixes most failed queries.
3. **Swapped the model deliberately.** codellama is the default, but the architecture is model-agnostic. Point Ollama at Qwen 3.6 or DeepSeek V4 and the same chain runs — handy for benchmarking which local model writes the cleanest SQL on your schema.
4. **Made the Streamlit UI the real deliverable.** The chain is the engine; the app is the product. The whole point was something a person clicks, not a script a developer runs.

## Where it breaks

I'm not going to pretend this is production-grade out of the box.

**It hallucinates on ambiguous questions.** Ask "how are we doing?" and the model has nothing to anchor to. It needs a clear metric and a clear filter, or it guesses.

**It runs the SQL it writes.** `SQLDatabaseChain` executes generated queries directly. If your model decides to write a `DELETE` and you connected as an admin, it'll run. This is exactly why the read-only user isn't optional — it's the only thing standing between a bad generation and a wiped table.

**It's only as good as your schema.** Cryptic column names like `col_7` and `flg2` produce garbage SQL. Clean, descriptive table and column names are doing half the work for the model.

## Takeaway

The interesting part isn't that an LLM can write SQL — it's that it can now do it locally, for free, against your private data, behind a UI a non-engineer can use. That combination is what makes natural-language querying a real internal tool in 2026 instead of a demo.

Build it in an afternoon. Just connect as a read-only user before you let anyone near it.

*Built on top of Aman Kharwal's walkthrough — [Create an AI SQL Assistant with LangChain](https://amanxai.com/2026/05/13/create-an-ai-sql-assistant-with-langchain/). My changes are the read-only enforcement, the error UX, and the Streamlit deliverable.*

### Sources
- [Create an AI SQL Assistant with LangChain — Aman Kharwal](https://amanxai.com/2026/05/13/create-an-ai-sql-assistant-with-langchain/)
- [AI Agent Frameworks — LangChain](https://www.langchain.com/resources/ai-agent-frameworks)
- [The Open-Source LLM Landscape in 2026 — Codersera](https://codersera.com/blog/open-source-llms-landscape-2026/)
