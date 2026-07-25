import base64
from importlib import import_module
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="LexGO | AI Legal Intelligence", 
    page_icon="⚖️", 
    layout="wide"
)

# 2. Custom CSS & Styling (Sidebar Glassmorphism + Main Interface)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Force background on main App container */
    .stApp {
        background: linear-gradient(180deg, rgba(10, 15, 29, 0.75) 0%, rgba(10, 15, 29, 0.88) 100%), 
                    url("https://images.unsplash.com/photo-1479142506502-19b3a3b7ff33?q=80&w=1170&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* Transparent Main Container & Header */
    .stAppHeader, .main, .main .block-container {
        background: transparent !important;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 4rem;
        max-width: 900px;
    }

    /* Sidebar Custom Styling */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        letter-spacing: -0.01em !important;
    }

    /* Sidebar Quick Query Buttons */
    section[data-testid="stSidebar"] button {
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #e2e8f0 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.8rem !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        margin-bottom: 0.2rem !important;
    }

    section[data-testid="stSidebar"] button:hover {
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        background: rgba(56, 189, 248, 0.12) !important;
    }

    /* Title Styling */
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
        font-size: 0.95rem;
        color: #94a3b8;
        line-height: 1.6;
        margin-bottom: 2rem;
    }

    /* Text Area Styling */
    .stTextArea label {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #f1f5f9 !important;
        margin-bottom: 0.5rem !important;
    }

    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.70) !important;
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
        background: rgba(15, 23, 42, 0.70) !important;
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


# =========================================================
# 4. LEFT SIDEBAR PANEL (Features & Navigation)
# =========================================================
with st.sidebar:
    st.markdown("## ⚖️ LexGO Portal")
    st.caption("Internal Repository Assistant")
    st.divider()

    # --- Feature 1: Suggested Quick Queries ---
    st.markdown("### 💡 Suggested Queries")
    
    if st.button("📌 M&A Approval Rules"):
        st.session_state["user_query"] = "What are the required board and shareholder approvals for a merger?"

    if st.button("🔒 Trade Secret Policy"):
        st.session_state["user_query"] = "How does the company protect proprietary source code and trade secrets?"

    if st.button("🏢 Commercial Leases"):
        st.session_state["user_query"] = "What is the approval process for commercial real estate leases exceeding 12 months?"

    if st.button("🏷️ Trademark Clearance"):
        st.session_state["user_query"] = "What is the policy for clearing new product or brand names before public launch?"

    st.divider()

    # --- Feature 2: Retrieval Settings ---
    st.markdown("### ⚙️ Search Controls")
    include_archived = st.checkbox("Include archived policies", value=False)

    st.divider()

    # --- Feature 3: Repository Metadata ---
    st.markdown("### ℹ️ Repository Info")
    st.caption("• **Coverage:** IP, Corporate Governance, Real Estate, M&A")
    st.caption("• **Vector DB:** ChromaDB Hybrid Index")
    st.caption("• **Engine:** RAG + OpenRouter")


# =========================================================
# 5. MAIN CONTENT AREA
# =========================================================
st.markdown('<h1 class="lexgo-title">LexGO ⚖️</h1>', unsafe_allow_html=True)
st.markdown('<div class="lexgo-slogan">Navigate Law with Precision</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lexgo-caption">AI-driven legal intelligence for corporate governance, M&A policies, real estate, and intellectual property. Answers are synthesized strictly from internal repository documentation.</div>', 
    unsafe_allow_html=True
)

# Input Section
question = st.text_area(
    "Legal Query / Policy Search", 
    value=st.session_state.get("user_query", ""),
    placeholder="Ask a question about corporate policies, director independence, or IP guidelines...", 
    height=130
)

# Action & Execution
if st.button("Analyze & Generate Answer") and question.strip():
    with st.spinner("Analyzing legal repository and verifying policy compliance..."):
        answer, sources = rag.answer_question(question)
        
        # Filter archived if toggle is disabled in sidebar
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
