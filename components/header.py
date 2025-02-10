import streamlit as st


def set_page_header():
    st.header("📚 Local RAG System for Mathematical Question Answering ", anchor=False)
    st.caption(
        "Ingest your data for retrieval augmented generation (RAG) with open-source Large Language Models (LLMs), all without 3rd parties or sensitive information leaving your network."
    )
