from importlib import import_module
import streamlit as st

# Config Page
st.set_page_config(
    page_title="LexGO | AI-Powered Legal Intelligence", 
    page_icon="⚖️", 
    layout="centered"
)

# --- Custom CSS for Pinterest Image Background & Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background setup using Direct URL extracted from your Pinterest link */
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.45)), 
                          url("https://i.pinimg.com/736x/21/f0/73/21f0739c9f28ec96fa2f16839f9eb8f9.jpg");
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
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #ffffff;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
        margin-bottom: 0.2rem;
    }

    /* Slogan Styling */
    .lexgo-slogan {
        font-size: 1.1rem;
        font-weight: 600;
        color: #38bdf8;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.8);
    }

    .lexgo-caption {
        font-size: 0.95rem;
        color: #e2e8f0;
        margin-bottom: 2rem;
        line-height: 1.5;
        text-shadow: 0 1px 5px rgba(0, 0, 0, 0.8);
    }

    /* Dark Glassmorphic Cards for Inputs */
    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }

    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
    }

    /* Custom Button Styling */
    div.stButton > button {
        width: 100%;
        background: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
    }

    div.stButton > button:hover {
        background: #0369a1 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6) !important;
    }

    /* Expander / Sources Styling */
    .stExpander {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }

    /* Hide Streamlit Default UI Elements */
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
