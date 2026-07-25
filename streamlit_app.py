import base64
from importlib import import_module
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="LexGO | AI Legal Intelligence", 
    page_icon="⚖️", 
    layout="centered"
)

# 2. Custom CSS & Styling (Guaranteed Visible Background + Glass Container)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Force background on main App container */
    .stApp {
        background: linear-gradient(180deg, rgba(10, 15, 29, 0.70) 0%, rgba(10, 15, 29, 0.85) 100%), 
                    url("https://images.unsplash.com/photo-1479142506502-19b3a3b7ff33?q=80&w=1170&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* Keep main container background completely transparent */
    .stAppHeader, .main, .main .block-container {
        background: transparent !important;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 4rem;
        max-width: 800px;
    }

    /* Header Styling */
    .lexgo-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #ffffff;
        margin: 0;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .lexgo-slogan {
        font-size: 0.85rem;
        font-weight: 700;
        color: #38bdf8;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 0.2rem;
        margin-bottom: 0.8rem;
    }

    .lexgo-caption {
        font-size: 0.92rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }

    /* Suggested Query Buttons */
    div[data-testid="stHorizontalBlock"] button {
        background: rgba(30, 41, 59, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #e2e8f0 !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        border-radius: 20px !important;
        padding: 0.4rem 0.8rem !important;
        backdrop-filter: blur(8px) !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stHorizontalBlock"] button:hover {
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.15) !important;
    }

    /* Text Area Styling */
    .stTextArea label {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #f1f5f9 !important;
        margin-bottom: 0.5rem !important;
    }

    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
        font-size: 0.98rem !important;
        padding: 1rem !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
    }

    /* Main Action Button Styling */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3) !important;
        margin-top: 0.5rem;
    }

    div.stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45) !important;
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
    }

    /* Source Citation Expander */
    .stExpander {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        margin-top: 1.5rem !important;
    }

    /* Checkbox Label Styling */
    .stCheckbox label {
        color: #cbd5e1 !important;
        font-size: 0.88rem !important;
    }

    /* Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Import RAG Backend
rag = import_module("07_prompting")

try:
    if not rag.OPENROUTER_API_KEY:
        rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    rag.OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", rag.OPENROUTER_MODEL)
except Exception:
    pass

# 4. Header Section
st.markdown('<h1 class="lexgo-title">LexGO ⚖️</h1>', unsafe_allow_html=True)
st.markdown('<div class="lexgo-slogan">Navigate Law with Precision</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lexgo-caption">AI-driven legal intelligence for corporate governance, M&A policies, real estate, and intellectual property. Answers are synthesized strictly from internal repository documentation.</div>', 
    unsafe_allow_html=True
)

# 5. Feature: Quick Sample Query Pills
st.markdown("<p style='font-size:0.85rem; color:#94a3b8; margin-bottom:0.4rem; font-weight:600;'>SUGGESTED QUERIES</p>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

if col1.button("📌 M&A Approval Rules"):
    st.session_state["user_query"] = "What are the required board and shareholder approvals for a merger?"

if col2.button("🔒 Trade Secret Policy"):
    st.session_state["user_query"] = "How does the company protect proprietary source code and trade secrets?"

if col3.button("🏢 Commercial Leases"):
    st.session_state["user_query"] = "What is the approval process for commercial real estate leases exceeding 12 months?"

# 6. Input Section
question = st.text_area(
    "Legal Query / Policy Search", 
    value=st.session_state.get("user_query", ""),
    placeholder="Ask a question about corporate policies, director independence, or IP guidelines...", 
    height=110
)

# 7. Optional Controls (Filter Archived Policies)
include_archived = st.checkbox("Include archived/legacy policy notices in search", value=False)

# 8. Action & Result Execution
if st.button("Analyze & Generate Answer") and question.strip():
    with st.spinner("Analyzing legal repository and verifying policy compliance..."):
        answer, sources = rag.answer_question(question)
        
        # Filter archived if toggle is disabled
        if not include_archived and sources:
            sources = [s for s in sources if s.get("is_current", True)]

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Legal Analysis")
        st.markdown(
            f"""
            <div style='background: rgba(15, 23, 42, 0.70); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 1.4rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.15); color: #f8fafc; line-height: 1.7;'>
                {answer}
            </div>
            """, 
            unsafe_allow_html=True
        )

        if sources:
            with st.expander("📌 Retrieved Internal References & Citations"):
                for idx, source in enumerate(sources, 1):
                    status_badge = "🟢 Current Policy" if source.get("is_current", True) else "🔴 Archived Notice"
                    st.markdown(f"**[{idx}] {source['title']}** &nbsp; <small style='color:#94a3b8;'>({status_badge})</small>", unsafe_allow_html=True)
                    st.caption(source["chunk_text"])
                    if idx < len(sources):
                        st.divider()
