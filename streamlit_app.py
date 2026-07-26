# -------------------------------------------------------------------
# Helper: Processing & Indexing uploaded file directly into ChromaDB
# -------------------------------------------------------------------
def process_and_index_file(uploaded_file, target_path):
    """
    Extracts text from PDF/DOCX, converts to document schema,
    chunks it, and inserts new vectors into ChromaDB dynamically.
    """
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    full_text = ""

    # 1. Extract Text
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

    # 2. Chunk & Embed dynamically via standard RAG pipeline
    try:
        # Assuming your chunking module exists (e.g. 03_chunking or 07_prompting)
        chunking_module = import_module("03_chunking")
        new_chunks = chunking_module.chunk_document(new_doc)
        
        # Access Chroma collection from rag / vector store module
        if hasattr(rag, "collection"):
            collection = rag.collection
        elif hasattr(rag, "vector_store"):
            collection = rag.vector_store
        else:
            # Fallback if collection is in vector store module
            vs_module = import_module("05_vector_store")
            collection = vs_module.collection

        # Prepare for ChromaDB insertion
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

        # Direct Upsert/Add to ChromaDB
        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        return True, f"Successfully indexed {len(new_chunks)} chunks!"
    except Exception as e:
        return False, f"Indexing error: {str(e)}"


# -------------------------------------------------------------------
# 4. LEFT SIDEBAR PANEL (Updated Document Ingestion)
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚖️ LexGO Portal")
    st.caption("Internal Repository Assistant")
    st.divider()

    # 📄 Document Upload Section
    st.markdown("### 📄 Document Ingestion")
    uploaded_file = st.file_uploader(
        "Upload legal document (PDF or Word)", 
        type=["pdf", "docx", "doc"]
    )

    if uploaded_file is not None:
        target_path = os.path.join(DATA_DIR, uploaded_file.name)
        
        # Track processed files in Session State
        if "indexed_files" not in st.session_state:
            st.session_state.indexed_files = set()

        if uploaded_file.name not in st.session_state.indexed_files:
            with st.spinner("Processing & Indexing document into Vector DB..."):
                # Save file to disk
                with open(target_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Index in ChromaDB immediately
                success, msg = process_and_index_file(uploaded_file, target_path)

                if success:
                    st.session_state.indexed_files.add(uploaded_file.name)
                    st.success(f"✅ `{uploaded_file.name}` ingested successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"⚠️ {msg}")
        else:
            st.info(f"🟢 `{uploaded_file.name}` is indexed and ready.")

    st.divider()
    # ... بقية كود الـ Sidebar (Suggested Queries, Controls, Info) يفضل كما هو
