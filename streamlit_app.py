import base64
import os
import re
import sys
from importlib import import_module
import streamlit as st
import chromadb
from chromadb.config import Settings

# ==============================================================================
# 1. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="LexGO | AI Legal Intelligence", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup Directories
DATA_DIR = "./data"
CHROMA_DB_DIR = "./chroma_db"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# Custom CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(180deg, rgba(10, 15, 29, 0.70) 0%, rgba(10, 15, 29, 0.85) 100%), 
                    url("https://images.unsplash.com/photo-1479142506502-19b3a3b7ff33?q=80&w=1170&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 950px;
    }

    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.88) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
    }

    .lexgo-title {
        font-size: 2.8rem;
        font-weight: 800;
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

    .stExpander {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }
    
    .confidence-badge-high {
        background-color: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        border: 1px solid #22c55e;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .confidence-badge-medium {
        background-color: rgba(234, 179, 8, 0.2);
        color: #facc15;
        border: 1px solid #eab308;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 2. IMPORT RAG MODULES & INITIALIZE SESSION
# ==============================================================================
rag = import_module("07_prompting")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================================================================
# 3. HELPER & EVALUATION FUNCTIONS
# ==============================================================================
def calculate_retrieval_hit(sources):
    return 100.0 if sources and len(sources) > 0 else 0.0

def calculate_context_faithfulness(answer, sources):
    if not answer or not sources:
        return 0.0
    context_text = " ".join([s.get("chunk_text", "").lower() for s in sources])
    context_words = set(re.findall(r'\b\w{4,}\b', context_text))
    answer_words = set(re.findall(r'\b\w{4,}\b', answer.lower()))
    if not context_words or not answer_words:
        return 0.0
    shared_words = answer_words.intersection(context_words)
    return min(round((len(shared_words) / len(answer_words)) * 100, 1), 100.0)

def process_and_index_file(uploaded_file):
    target_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(target_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    full_text = ""
    try:
        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(target_path)
            full_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif ext in [".docx", ".doc"]:
            import docx
            doc = docx.Document(target_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text])
    except Exception as e:
        return False, f"Extraction Error: {str(e)}"

    if not full_text.strip():
        return False, "Empty Document"

    clean_name = os.path.splitext(uploaded_file.name)[0]
    doc_id = f"doc_{clean_name.lower().replace(' ', '_')}"
    
    # Simple chunking
    chunks = []
    chunk_size = 500
    for i in range(0, len(full_text), chunk_size - 50):
        chunks.append({
            "chunk_id": f"{doc_id}_c{len(chunks)}",
            "doc_id": doc_id,
            "title": clean_name.replace("_", " ").title(),
            "is_current": True,
            "chunk_text": full_text[i:i+chunk_size]
        })

    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        collection = client.get_or_create_collection(name="lexgo_docs")
        collection.add(
            ids=[c["chunk_id"] for c in chunks],
            documents=[c["chunk_text"] for c in chunks],
            metadatas=[{"doc_id": c["doc_id"], "title": c["title"], "is_current": True, "chunk_text": c["chunk_text"]} for c in chunks]
        )
        return True, f"Successfully indexed {len(chunks)} chunks!"
    except Exception as e:
        return False, f"Chroma Error: {str(e)}"

# ==============================================================================
# 4. SIDEBAR (DOCUMENT MANAGEMENT & QUICK CONTROLS)
# ==============================================================================
with st.sidebar:
    st.markdown("## ⚖️ LexGO Portal")
    st.caption("Internal Legal Repository Assistant")
    st.divider()

    # Upload Section
    st.markdown("### 📄 Document Ingestion")
    uploaded_file = st.file_uploader("Upload legal document", type=["pdf", "docx", "doc"])
    if uploaded_file is not None:
        if "indexed_files" not in st.session_state:
            st.session_state.indexed_files = set()

        if uploaded_file.name not in st.session_state.indexed_files:
            with st.spinner("Processing & Indexing..."):
                success, msg = process_and_index_file(uploaded_file)
                if success:
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.success(f"✅ {uploaded_file.name}")
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()

    # Active Documents List
    saved_files = os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else []
    st.markdown(f"### 📂 Active Documents ({len(saved_files)})")
    for file in saved_files:
        col_f1, col_f2 = st.columns([0.8, 0.2])
        col_f1.caption(f"• `{file}`")

    st.divider()
    
    # Clear Session
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# ==============================================================================
# 5. MAIN CHAT & RESPONSE AREA
# ==============================================================================
st.markdown('<h1 class="lexgo-title">LexGO ⚖️</h1>', unsafe_allow_html=True)
st.markdown('<div class="lexgo-slogan">Navigate Law with Precision</div>', unsafe_allow_html=True)

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "metrics" in msg:
            m = msg["metrics"]
            st.caption(f"📊 **Retrieval Hit:** {m['hit']}% | **Groundedness:** {m['faith']}% | **Sources:** {m['sources_count']}")

# Chat Input
if prompt := st.chat_input("Ask a legal or policy question..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing repository & verifying compliance..."):
            answer, sources = rag.answer_question(prompt)
            
            # Display Answer
            st.markdown(answer)
            
            # Calculate Evaluation
            hit_score = calculate_retrieval_hit(sources)
            faith_score = calculate_context_faithfulness(answer, sources)
            
            # Confidence Badge
            if faith_score >= 60:
                st.markdown('<span class="confidence-badge-high">🟢 High Confidence Match</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="confidence-badge-medium">🟡 Moderate Confidence - Review Recommended</span>', unsafe_allow_html=True)
            
            # Expander for Sources
            if sources:
                with st.expander("📌 Retrieved Sources & Context"):
                    for idx, s in enumerate(sources, 1):
                        st.markdown(f"**[{idx}] {s['title']}**")
                        st.caption(s['chunk_text'])
                        if idx < len(sources):
                            st.divider()

            # Save Assistant Response to History
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "metrics": {
                    "hit": hit_score,
                    "faith": faith_score,
                    "sources_count": len(sources) if sources else 0
                }
            })
