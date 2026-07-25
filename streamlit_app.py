import base64
from importlib import import_module
import io
import streamlit as st

# PDF Export Library
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# 1. Page Configuration
st.set_page_config(
    page_title="LexGO | AI Legal Intelligence", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS & Styling (Dark Glassmorphism Theme)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Main Application Background */
    .stApp {
        background: linear-gradient(180deg, rgba(10, 15, 29, 0.75) 0%, rgba(10, 15, 29, 0.88) 100%), 
                    url("https://images.unsplash.com/photo-1479142506502-19b3a3b7ff33?q=80&w=1170&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* Keep main container transparent so background image shows through */
    .stAppHeader, .main, .main .block-container {
        background: transparent !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 900px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
    }

    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff !important;
        font-size: 1.05rem !important;
    }

    /* Sidebar Quick Query Buttons */
    section[data-testid="stSidebar"] button {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #e2e8f0 !important;
        font-size: 0.85rem !important;
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
        background: rgba(56, 189, 248, 0.15) !important;
    }

    /* Title & Headers */
    .lexgo-title {
        font-size: 2.6rem;
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

    /* Chat Messages Styling */
    div[data-testid="stChatMessage"] {
        background: rgba(15, 23, 42, 0.70) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 1rem !important;
        color: #f8fafc !important;
    }

    /* Chat Input Bar */
    div[data-testid="stChatInput"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 14px !important;
    }

    /* Source Citation Expander */
    .stExpander {
        background: rgba(15, 23, 42, 0.50) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        margin-top: 0.8rem !important;
    }

    /* Download PDF Button */
    .stDownloadButton > button {
        background: rgba(56, 189, 248, 0.15) !important;
        border: 1px solid #38bdf8 !important;
        color: #38bdf8 !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0.3rem 0.8rem !important;
    }

    /* Hide Default Elements */
    footer {visibility: hidden;}
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

# Helper Function: Generate PDF Report
def generate_pdf_report(query, response_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, leading=16, spaceAfter=8)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, spaceAfter=10)
    
    story = []
    story.append(Paragraph("LexGO Legal Intelligence Briefing", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Query:", heading_style))
    story.append(Paragraph(query, body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Legal Analysis & Synthesis:", heading_style))
    story.append(Paragraph(response_text.replace('\n', '<br/>'), body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# 4. Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================================================
# 5. LEFT SIDEBAR PANEL
# =========================================================
with st.sidebar:
    st.markdown("## ⚖️ LexGO Portal")
    st.caption("Internal Repository Assistant")
    st.divider()

    st.markdown("### 💡 Suggested Queries")
    
    if st.button("📌 M&A Approval Rules"):
        st.session_state["pending_input"] = "What are the required board and shareholder approvals for a merger?"

    if st.button("🔒 Trade Secret Policy"):
        st.session_state["pending_input"] = "How does the company protect proprietary source code and trade secrets?"

    if st.button("🏢 Commercial Leases"):
        st.session_state["pending_input"] = "What is the approval process for commercial real estate leases exceeding 12 months?"

    if st.button("🏷️ Trademark Clearance"):
        st.session_state["pending_input"] = "What is the policy for clearing new product or brand names before public launch?"

    st.divider()

    st.markdown("### ⚙️ Search Controls")
    include_archived = st.checkbox("Include archived policies", value=False)

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown("### ℹ️ Repository Info")
    st.caption("• **Coverage:** IP, Corporate, Real Estate, M&A")
    st.caption("• **Vector DB:** ChromaDB Hybrid Index")


# =========================================================
# 6. MAIN CONTENT AREA & CHAT INTERFACE
# =========================================================
st.markdown('<h1 class="lexgo-title">LexGO ⚖️</h1>', unsafe_allow_html=True)
st.markdown('<div class="lexgo-slogan">Navigate Law with Precision</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lexgo-caption">AI-driven legal intelligence for corporate governance, M&A policies, real estate, and intellectual property.</div>', 
    unsafe_allow_html=True
)

# Display Existing Chat Messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display Sources if available
        if message.get("sources"):
            with st.expander("📌 Retrieved Internal References"):
                for s_idx, source in enumerate(message["sources"], 1):
                    status_badge = "🟢 Current Policy" if source.get("is_current", True) else "🔴 Archived Notice"
                    st.markdown(f"**[{s_idx}] {source['title']}** &nbsp; <small style='color:#94a3b8;'>({status_badge})</small>", unsafe_allow_html=True)
                    st.caption(source["chunk_text"])
                    if s_idx < len(message["sources"]):
                        st.divider()

        # Add PDF Export Button for Assistant Answers
        if message["role"] == "assistant":
            pdf_bytes = generate_pdf_report(
                st.session_state.messages[idx-1]["content"] if idx > 0 else "Legal Query", 
                message["content"]
            )
            st.download_button(
                label="📄 Export as PDF Briefing",
                data=pdf_bytes,
                file_name=f"LexGO_Briefing_{idx}.pdf",
                mime="application/pdf",
                key=f"pdf_{idx}"
            )

# Handle Query Logic (Either from Chat Input or Suggested Query Buttons)
user_prompt = st.chat_input("Ask a legal or policy question...")

if "pending_input" in st.session_state and st.session_state["pending_input"]:
    user_prompt = st.session_state.pop("pending_input")

if user_prompt:
    # 1. Render User Message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 2. Process & Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing legal repository and verifying policy compliance..."):
            answer, sources = rag.answer_question(user_prompt)
            
            if not include_archived and sources:
                sources = [s for s in sources if s.get("is_current", True)]

            st.markdown(answer)

            if sources:
                with st.expander("📌 Retrieved Internal References"):
                    for idx, source in enumerate(sources, 1):
                        status_badge = "🟢 Current Policy" if source.get("is_current", True) else "🔴 Archived Notice"
                        st.markdown(f"**[{idx}] {source['title']}** &nbsp; <small style='color:#94a3b8;'>({status_badge})</small>", unsafe_allow_html=True)
                        st.caption(source["chunk_text"])
                        if idx < len(sources):
                            st.divider()

            # Generate PDF for immediate download
            pdf_bytes = generate_pdf_report(user_prompt, answer)
            st.download_button(
                label="📄 Export as PDF Briefing",
                data=pdf_bytes,
                file_name="LexGO_Briefing.pdf",
                mime="application/pdf",
                key=f"pdf_new_{len(st.session_state.messages)}"
            )

            # Save to Chat History
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer, 
                "sources": sources
            })
