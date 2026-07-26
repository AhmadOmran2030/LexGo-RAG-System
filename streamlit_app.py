import base64
import os
import sys
from importlib import import_module
import streamlit as st
import chromadb
from chromadb.config import Settings

# 1. Page Configuration
st.set_page_config(
    page_title="LexGO | AI Legal Intelligence", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Setup Directories
DATA_DIR = "./data"
CHROMA_DB_DIR = "./chroma_db"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# 3. Custom CSS
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

    .stAppHeader, .main, .main .block-container {
        background: transparent !important;
    }

    [data-testid="stSidebarNavSeparator"], button[data-testid="baseButton-header"] {
        display: block !important;
        visibility: visible !important;
        color: #ffffff !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 900px;
    }

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

    section[data-testid="stSidebar"] button {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #e2e8f0 !important;
        font-size: 0.88rem !important;
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

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
    }

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

    .stTextArea label {
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        color: #f1f5f9 !important;
        margin-bottom: 0.5rem !important;
    }

    .stTextArea textarea {
        background: rgba(15, 23, 42, 0.60) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
        font-size: 0.98rem !important;
        padding: 1rem !important;
    }

    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3) !important;
        margin-top: 0.5rem;
    }

    div.stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45) !important;
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
    }

    .stExpander {
        background: rgba(15, 23, 42, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        margin-top: 1.5rem !important;
    }

    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# 4. Import RAG Modules
rag = import_module("07_prompting")
docs_module = import_module("01_documents")

try:
    if not getattr(rag, "OPENROUTER_API_KEY", None):
        rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    rag.OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", getattr(rag, "OPENROUTER_MODEL", ""))
except Exception:
    pass

# 5. Data Processing Functions (Directly embedded)
def save_uploaded_file(uploaded_file):
    target_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(target_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return target_path

def extract_text_from_file(target_path, file_extension):
    full_text = ""
    try:
        if file_extension == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(target_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        elif file_extension in [".docx", ".doc"]:
            import docx
            doc = docx.Document(target_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text])
    except Exception as err:
        return None, f"Error reading file: {str(err)}"

    if not full_text.strip():
        return None, "File contains no readable text."

    return full_text.strip(), None

def chunk_text(text, doc_id, doc_title, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + chunk_size
        chunk_str = text[start:end]
        chunks.append({
            "chunk_id": f"{doc_id}_c{idx}",
            "doc_id": doc_id,
            "title": doc_title,
            "is_current": True,
            "chunk_text": chunk_str
        })
        start += chunk_size - overlap
        idx += 1
    return chunks

def process_and_index_file(uploaded_file):
    # 1. Save file locally in ./data
    target_path = save_uploaded_file(uploaded_file)
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    # 2. Extract text
    full_text, error = extract_text_from_file(target_path, ext)
    if error:
        return False, error

    clean_name = os.path.splitext(uploaded_file.name)[0]
    prefix = "pdf_" if ext == ".pdf" else "docx_"
    doc_id = f"{prefix}{clean_name.lower().replace(' ', '_')}"
    doc_title = clean_name.replace("_", " ").title()

    new_doc = {
        "id": doc_id,
        "title": doc_title,
        "is_current": True,
        "text": full_text
    }

    # 3. Chunk text
    if hasattr(rag, "chunk_document"):
        new_chunks = rag.chunk_document(new_doc)
    else:
        new_chunks = chunk_text(full_text, doc_id, doc_title)

    # 4. Index in ChromaDB
    try:
        client = chromadb.PersistentClient(
            path=CHROMA_DB_DIR,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        collection = client.get_or_create_collection(name="lexgo_docs")

        ids = [c["chunk_id"] for c in new_chunks]
        documents = [c["chunk_text"] for c in new_chunks]
        metadatas = [
            {
                "doc_id": c["doc_id"],
                "title": c["title"],
                "is_current": c["is_current"],
                "chunk_text": c["chunk_text"]
            }
            for c in new_chunks
        ]

        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        return True, f"Saved to `./data` & indexed {len(new_chunks)} chunks!"
    except Exception as e:
        return False, f"Indexing failed: {str(e)}"


# 6. LEFT SIDEBAR PANEL
with st.sidebar:
    st.markdown("## ⚖️ LexGO Portal")
    st.caption("Internal Repository Assistant")
    st.divider()

    st.markdown("### 📄 Document Ingestion")
    uploaded_file = st.file_uploader(
        "Upload legal document (PDF or Word)", 
        type=["pdf", "docx", "doc"]
    )

    if uploaded_file is not None:
        if "indexed_files" not in st.session_state:
            st.session_state.indexed_files = set()

        if uploaded_file.name not in st.session_state.indexed_files:
            with st.spinner("Saving to `./data` & Training Vector DB..."):
                success, msg = process_and_index_file(uploaded_file)

                if success:
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.success(f"✅ `{uploaded_file.name}` {msg}")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"⚠️ {msg}")
        else:
            st.info(f"🟢 `{uploaded_file.name}` saved in `./data` & indexed.")

    st.divider()

    st.markdown("### 💡 Suggested Queries")
    def set_query(text):
        st.session_state["user_query"] = text

    if st.button("📌 M&A Approval Rules"):
        set_query("What are the required board and shareholder approvals for a merger?")
        st.rerun()

    if st.button("🔒 Trade Secret Policy"):
        set_query("How does the company protect proprietary source code and trade secrets?")
        st.rerun()

    if st.button("🏢 Commercial Leases"):
        set_query("What is the approval process for commercial real estate leases exceeding 12 months?")
        st.rerun()

    if st.button("🏷️ Trademark Clearance"):
        set_query("What is the policy for clearing new product or brand names before public launch?")
        st.rerun()

    st.divider()

    st.markdown("### ⚙️ Search Controls")
    include_archived = st.checkbox("Include archived policies", value=False)

    st.divider()

    saved_files = os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else []
    st.markdown("### ℹ️ Repository Info")
    st.caption(f"• **Saved Files in `./data`:** {len(saved_files)}")
    st.caption("• **Supported Formats:** PDF, DOCX, DOC")
    st.caption("• **Vector DB:** ChromaDB Hybrid Index")


# 7. MAIN CONTENT AREA
st.markdown('<h1 class="lexgo-title">LexGO ⚖️</h1>', unsafe_allow_html=True)
st.markdown('<div class="lexgo-slogan">Navigate Law with Precision</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lexgo-caption">AI-driven legal intelligence for corporate governance, M&A policies, real estate, and intellectual property. Answers are synthesized strictly from internal repository documentation.</div>', 
    unsafe_allow_html=True
)

question = st.text_area(
    "Legal Query / Policy Search", 
    value=st.session_state.get("user_query", ""),
    placeholder="Ask a question about corporate policies, director independence, or IP guidelines...", 
    height=130
)

if st.button("Analyze & Generate Answer") and question.strip():
    with st.spinner("Analyzing legal repository and verifying policy compliance..."):
        answer, sources = rag.answer_question(question)
        
        if not include_archived and sources:
            sources = [s for s in sources if s.get("is_current", True)]

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Legal Analysis")
        
        with st.container():
            st.markdown(answer)

        if sources:
            with st.expander("📌 Retrieved Internal References & Citations"):
                for idx, source in enumerate(sources, 1):
                    status_badge = "🟢 Current Policy" if source.get("is_current", True) else "🔴 Archived Notice"
                    st.markdown(f"**[{idx}] {source['title']}** &nbsp; <small style='color:#94a3b8;'>({status_badge})</small>", unsafe_allow_html=True)
                    st.caption(source["chunk_text"])
                    if idx < len(sources):
                        st.divider()
