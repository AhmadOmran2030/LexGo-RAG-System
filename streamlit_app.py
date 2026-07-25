from importlib import import_module

import streamlit as st

rag = import_module("07_prompting")

try:
    if not rag.OPENAI_API_KEY:
        rag.OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
    rag.OPENAI_MODEL = st.secrets.get("OPENAI_MODEL", rag.OPENAI_MODEL)
except Exception:
    pass
    
st.title("Legal RAG Assistant")
st.caption("Answers general internal policy questions on corporate governance, M&A, and IP. Not legal advice.")

question = st.text_area("Question")

if st.button("Answer") and question.strip():
    answer, sources = rag.answer_question(question)
    st.text_area("Answer", value=answer, height=220)

    with st.expander("Sources"):
        for source in sources:
            st.write(source["title"])
            st.write(source["chunk_text"])

