"""AI SQL assistant: plain English question -> SQL -> result, fully local.

Uses a read-only SQLite connection so a bad generation can never mutate data.

Inspired by Aman Kharwal's tutorial:
https://amanxai.com/2026/05/13/create-an-ai-sql-assistant-with-langchain/
"""

from __future__ import annotations

import os

# Read-only SQLite URI: even if the model writes DELETE/DROP, it cannot run.
READONLY_URI = os.environ.get(
    "SQL_ASSISTANT_DB", "sqlite:///file:sales.db?mode=ro&uri=true"
)
MODEL = os.environ.get("OLLAMA_MODEL", "codellama")


def build_chain():
    """Build the SQLDatabaseChain. Imports happen here so tests can skip them."""
    from langchain_community.utilities import SQLDatabase
    from langchain_experimental.sql import SQLDatabaseChain
    from langchain_ollama import OllamaLLM

    db = SQLDatabase.from_uri(READONLY_URI)
    # temperature=0: we want deterministic, precise SQL, not creative writing.
    llm = OllamaLLM(model=MODEL, temperature=0)
    return SQLDatabaseChain.from_llm(llm=llm, db=db, verbose=False, return_direct=True)


def ask(question: str) -> str:
    """Answer a natural-language question against the database."""
    chain = build_chain()
    return chain.invoke({"query": question})


if __name__ == "__main__":
    print(ask("Which product generated the highest revenue?"))
