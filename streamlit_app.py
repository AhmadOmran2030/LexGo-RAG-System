import base64
import os
from importlib import import_module
import streamlit as st

# 1. Page Configuration (MUST be the first Streamlit command)
st.set_page_config(
    page_title="LexGO | AI Legal Intelligence", 
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure ./data directory exists for uploads
DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

# 2. Custom CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Background image styling */
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

    /* Sidebar Glassmorphism */
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

    /* File Uploader Custom Styling */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
        border: 1px dashed rgba(255, 255, 255, 0.2) !important;
    }

    /* Typography */
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
        font-weight: 600 !important;
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

    .stCheckbox label {
        color: #cbd5e1 !important;
        font-size: 0.88rem !important;
    }

    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Import RAG Modules
rag = import_module("07_prompting")
docs_module = import_module("01_documents")

try:
    if not getattr(rag, "OPENROUTER_API_KEY", None):
        rag.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    rag.OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", getattr(rag, "OPENROUTER_MODEL", ""))
except Exception:
    pass


# 4. Helper Function for Processing & Indexing Uploaded Document
def process_and_index_file(uploaded_file, target_path):
    """
    Extracts text, creates chunks, and inserts into ChromaDB safely.
    """
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    full_text = ""

    # 1. Extract Text based on file format
    try:
        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(target_path)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    full_text += t + "\n"
        elif ext in [".docx", ".doc"]:
            import docx
            doc = docx.Document(target_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text])
    except Exception as err:
        return False, f"Error reading file: {str(err)}"

    if not full_text.strip():
        return False, "File contains no readable text."

    clean_name = os.path.splitext(uploaded_file.name)[0]
    prefix = "pdf_" if ext == ".pdf" else "docx_"
    doc_id = f"{prefix}{clean_name.lower().replace(' ', '_')}"
    doc_title = clean_name.replace("_", " ").title()

    new_doc = {
        "id": doc_id,
        "title": doc_title,
        "is_current": True,
        "text": full_text.strip()
    }

    # 2. Chunking Logic (Safe Fallback)
    try:
        if hasattr(rag, "chunk_document"):
            new_chunks = rag.chunk_document(new_doc)
        else:
            text = new_doc["text"]
            chunk_size = 500
            overlap = 50
            chunks_list = []
            start = 0
            idx = 0
            while start < len(text):
                end = start + chunk_size
                chunk_str = text[start:end]
                chunks_list.append({
                    "chunk_id": f"{doc_id}_c{idx}",
                    "doc_id": doc_id,
                    "title": doc_title,
                    "is_current": True,
                    "chunk_text": chunk_str
                })
                start += chunk_size - overlap
                idx += 1
            new_chunks = chunks_list

        # 3. Access Chroma Collection Instance
        collection_obj = None

        # Check in rag module
        for attr in ["collection", "vector_store", "chroma_collection", "db"]:
            if hasattr(rag, attr):
                collection_obj = getattr(rag, attr)
                break

        # Check in docs_module
        if collection_obj is None:
            for attr in ["collection", "vector_store", "chroma_collection", "db"]:
                if hasattr(docs_module, attr):
                    collection_obj = getattr(docs_module, attr)
                    break

        # Fallback: Create direct ChromaDB Client connection
        if collection_obj is None:
            import chromadb
            client = chromadb.PersistentClient(path="./chroma_db")
            collection_obj = client.get_or_create_collection(name="lexgo_docs")

        # 4. Direct Insertion into Vector DB
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

        collection_obj.add(ids=ids, documents=documents, metadatas=metadatas)
        return True, f"Successfully indexed {len(new_chunks)} chunks!"

    except Exception as e:
        return False, f"Indexing failed: {str(e)}"


# 5. LEFT SIDEBAR PANEL
with st.sidebar:
    st.markdown("## ⚖️ LexGO Portal")
    st.caption("Internal Repository Assistant")
    st.divider()

    # 📄 Document Upload Section (Supports PDF & Word Files)
    st.markdown("### 📄 Document Ingestion")
    uploaded_file = st.file_uploader(
        "Upload legal document (PDF or Word)", 
        type=["pdf", "docx", "doc"]
    )

    if uploaded_file is not None:
        target_path = os.path.join(DATA_DIR, uploaded_file.name)
        
        if "indexed_files" not in st.session_state:
            st.session_state.indexed_files = set()

        if uploaded_file.name not in st.session_state.indexed_files:
            with st.spinner("Processing & Indexing document into Vector DB..."):
                with open(target_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                success, msg = process_and_index_file(uploaded_file, target_path)

                if success:
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.success(f"✅ `{uploaded_file.name}` ingested successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"⚠️ {msg}")
        else:
            st.info(f"🟢 `{uploaded_file.name}` is loaded and indexed.")

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

    # Dynamic document status count
    current_docs = docs_module.get_documents() if hasattr(docs_module, "get_documents") else getattr(docs_module, "documents", [])
    user_uploaded_docs = [
        d for d in current_docs 
        if d.get("id", "").startswith("pdf_") or d.get("id", "").startswith("docx_") or d.get("id", "").startswith("doc_")
    ]

    st.markdown("### ℹ️ Repository Info")
    st.caption(f"• **Total Documents:** {len(current_docs)}")
    st.caption(f"• **User Uploaded Docs:** {len(user_uploaded_docs)}")
    st.caption("• **Supported Formats:** PDF, DOCX, DOC")
    st.caption("• **Coverage:** IP, Corporate Governance, Real Estate, M&A")
    st.caption("• **Vector DB:** ChromaDB Hybrid Index")


# 6. MAIN CONTENT AREA
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
        
        # Filter archived sources if unchecked
        if not include_archived and sources:
            sources = [s for s in sources if s.get("is_current", True)]

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Legal Analysis")
        
        # Container box
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
