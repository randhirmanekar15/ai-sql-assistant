"""Streamlit UI for the AI SQL assistant.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from sql_assistant import build_chain

st.set_page_config(page_title="AI SQL Assistant", layout="centered")
st.title("AI SQL Assistant")
st.markdown("Ask questions about your sales data in plain English.")


@st.cache_resource
def _chain():
    return build_chain()


question = st.text_input(
    "Ask a database question",
    placeholder="e.g., How many units of 'Widget A' were sold?",
)

if question:
    with st.spinner("Analyzing database..."):
        try:
            result = _chain().invoke({"query": question})
            st.subheader("Answer")
            st.success(result)
        except Exception:  # noqa: BLE001  show a friendly tip, not a stack trace
            st.error("I couldn't answer that one.")
            st.info(
                "Tip: name the metric and timeframe, e.g. 'total revenue in 2025', "
                "and make sure it refers to tables/columns that exist."
            )
