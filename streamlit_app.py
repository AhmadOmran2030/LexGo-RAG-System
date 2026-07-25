from importlib import import_module
import streamlit as st

# Config Page
st.set_page_config(page_title="Legal RAG Assistant", page_icon="⚖️", layout="centered")

# --- Custom CSS for Background & Styling ---
st.markdown(
    """
    <style>
    /* Background setup with low overlay opacity to show the image clearly */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.45), rgba(15, 23, 42, 0.60)), 
                    url("https://images.unsplash.com/photo-1479142506502-19b3a3b7ff33?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Style Text Areas */
    .stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
        border-radius: 8px;
    }

    /* Style Expanders (Sources Section) */
    .stExpander {
        background-color: rgba(15, 23, 42, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

rag = import_module("07_prompting")

try:
    if not rag.OPENROUTER_API_KEY:
        rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    rag.OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", rag.OPENROUTER_MODEL)
except Exception:
    pass

st.title("Legal RAG Assistant ⚖️")
st.caption("Answers general internal policy questions on corporate governance, M&A, and IP. Not legal advice.")

question = st.text_area("Question")

if st.button("Answer") and question.strip():
    answer, sources = rag.answer_question(question)
    st.text_area("Answer", value=answer, height=220)

    with st.expander("Sources"):
        for source in sources:
            st.write(f"**{source['title']}**")
            st.write(source["chunk_text"])
