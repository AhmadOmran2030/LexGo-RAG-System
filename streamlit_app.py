from importlib import import_module
import streamlit as st

# Config Page
st.set_page_config(
    page_title="LexGO | AI-Powered Legal Intelligence", 
    page_icon="⚖️", 
    layout="centered"
)

# --- Custom CSS for Professional Modern UI ---
st.markdown(
    """
    <style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background setup with sophisticated Dark Blue / Charcoal gradient overlay */
    .stApp {
        background: linear-gradient(135deg, rgba(10, 15, 30, 0.85) 0%, rgba(15, 23, 42, 0.92) 100%), 
                    url("https://images.unsplash.com/photo-1479142506502-19b3a3b7ff33?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 800px;
    }

    /* Title Styling */
    .lexgo-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    /* Slogan & Subtitle Styling */
    .lexgo-slogan {
        font-size: 1.1rem;
        font-weight: 500;
        color: #38bdf8;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    .lexgo-caption {
        font-size: 0.92rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        line-height: 1.5;
    }

    /* Input & Text Area Cards (Glassmorphism Effect) */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
        font-size: 0.98rem !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
    }

    .stTextArea textarea:focus {
        border-color: #0284c7 !important;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.3) !important;
    }

    /* Custom Button Styling */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.5) !important;
    }

    /* Expander / Sources Styling */
    .stExpander {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        overflow: hidden;
        margin-top: 1rem;
    }

    /* Hide Streamlit Header & Footer for Clean Look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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

# Header Section
st.markdown('<div class="lexgo-title">LexGO ⚖️</div>', unsafe_allow_html=True)
st.markdown('<div class="lexgo-slogan">Navigate Law with Precision</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lexgo-caption">AI-driven legal intelligence for corporate governance, M&A policies, and intellectual property. Answers are based strictly on internal documentation and do not constitute formal legal advice.</div>', 
    unsafe_allow_html=True
)

# Input Section
question = st.text_area("Question", placeholder="Type your corporate governance or policy question here...", height=120)

# Execution Section
if st.button("Generate Answer") and question.strip():
    answer, sources = rag.answer_question(question)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.text_area("Answer", value=answer, height=220)

    if sources:
        with st.expander("📌 Retrieved Sources & Citations"):
            for idx, source in enumerate(sources, 1):
                st.markdown(f"**Source {idx}: {source['title']}**")
                st.caption(source["chunk_text"])
                if idx < len(sources):
                    st.divider()
