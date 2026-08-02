# Legal RAG Lab

A Retrieval-Augmented Generation (RAG) assistant for answering questions about internal corporate policy documents. The system combines traditional keyword search (BM25) with semantic search (Sentence Transformers) to retrieve the most relevant policy documents before generating grounded responses using an LLM through OpenRouter.

---

# Features

- Hybrid Retrieval (BM25 + Sentence Transformers)
- Paragraph-based document chunking
- Automatic text preprocessing
- ChromaDB vector storage
- Duplicate document filtering
- Prioritization of CURRENT policies over OUTDATED policies
- Source citation for every answer
- OpenRouter LLM integration
- Interactive Streamlit interface

---

# Project Architecture

```text
                    Documents
                        │
                        ▼
               01_documents.py
                        │
                        ▼
             02_preprocessing.py
                        │
                        ▼
                03_chunking.py
                        │
                        ▼
         04_vector_representation.py
          (BM25 + Sentence Embeddings)
                        │
                        ▼
         05_create_chroma_store.py
                        │
                        ▼
          06_retrieve_context.py
        (Hybrid Retrieval + Ranking)
                        │
                        ▼
               07_prompting.py
              (Grounded Prompt)
                        │
                        ▼
                 OpenRouter LLM
                        │
                        ▼
                  Final Response
```

---

# Project Structure

```text
Legal-RAG/

├── data/
├── chroma_db/
├── 01_documents.py
├── 02_preprocessing.py
├── 03_chunking.py
├── 04_vector_representation.py
├── 05_create_chroma_store.py
├── 06_retrieve_context.py
├── 07_prompting.py
├── streamlit_app.py
├── requirements.txt
├── README.md
└── .env.example
```

---

# Pipeline

| File | Description |
|------|-------------|
| **01_documents.py** | Stores the internal corporate policy documents and metadata (`is_current`). |
| **02_preprocessing.py** | Lowercases text, removes stopwords, tokenizes, and lemmatizes text for retrieval. |
| **03_chunking.py** | Splits documents into paragraph-based chunks (maximum 300 words with 1-paragraph overlap). |
| **04_vector_representation.py** | Builds BM25 and Sentence Transformer indexes, then performs Hybrid Retrieval. |
| **05_create_chroma_store.py** | Stores document chunks and embeddings inside ChromaDB. |
| **06_retrieve_context.py** | Retrieves the best chunks, removes duplicate documents, prioritizes CURRENT policies, and builds the final context. |
| **07_prompting.py** | Builds the prompt and queries the LLM through OpenRouter. |
| **streamlit_app.py** | Provides the web-based chat interface. |

---

# Hybrid Retrieval

The retrieval system combines lexical search and semantic search.

```text
Hybrid Score =
0.4 × BM25 Score
+
0.6 × Sentence Transformer Similarity
```

Where:

- **BM25** captures keyword matching.
- **Sentence Transformers** capture semantic similarity.
- Scores are normalized before combination.
- Results below the similarity threshold are discarded.
- CURRENT policies are ranked ahead of OUTDATED policies.

---

# Tech Stack

- Python
- Streamlit
- ChromaDB
- Sentence Transformers
- Rank-BM25
- NLTK
- NumPy
- OpenRouter API
- python-dotenv

---

# Running Locally

```powershell
python -m pip install -r requirements.txt

Copy-Item .env.example .env
```

Edit `.env` and add your OpenRouter API key.

```powershell
python 05_create_chroma_store.py

streamlit run streamlit_app.py
```

For macOS/Linux:

```bash
cp .env.example .env
```

---

# Environment Variables

```text
OPENROUTER_API_KEY=your_api_key
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

---

# API Key Rules

- Never hardcode an API key.
- Never commit the `.env` file.
- Store local secrets in `.env`.
- Store deployed secrets in Streamlit Cloud Secrets.

---

# Deploying to Streamlit Community Cloud

### 1. Push the project to GitHub

Create a GitHub repository and push the project.

---

### 2. Create the Streamlit App

Go to

https://share.streamlit.io

Create a new application and choose:

- Repository
- Branch
- Main file:
  `streamlit_app.py`

---

### 3. Configure Secrets

Add:

```toml
OPENROUTER_API_KEY="your_api_key"
OPENROUTER_MODEL="meta-llama/llama-3.3-70b-instruct:free"
```

Save the secrets and restart the application.

---

### 4. Verify Deployment

Ask a question such as:

> What vote is required to approve a merger?

Expected behavior:

- Relevant policy is retrieved.
- Sources are cited.
- CURRENT policies are preferred.
- Source documents are displayed.

---

# Example

### User Question

```text
What vote is required to approve a merger?
```

### Retrieved Context

```text
Source 1:
Merger Approval Policy
```

### Generated Answer

```text
A merger requires approval by a two-thirds vote of the board. [Source 1]
```

---

# Limitations

- Answers are limited to the indexed policy documents.
- The assistant does not use external knowledge.
- Retrieval quality depends on the quality of the indexed documents.
- Very large documents may benefit from more advanced chunking strategies.

---

# Future Improvements

- Cross-Encoder Re-ranking
- Incremental indexing
- Metadata filtering
- PDF page references
- Streaming responses
- Multi-language support
- Better retrieval evaluation metrics

---

# Final Checklist

- [ ] All required Python files exist.
- [ ] ChromaDB is successfully created.
- [ ] No real API keys are committed.
- [ ] Streamlit secrets are configured.
- [ ] The application runs successfully.
- [ ] Answers are generated from retrieved context only.
- [ ] Sources are cited correctly.
