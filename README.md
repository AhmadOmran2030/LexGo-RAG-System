# Legal RAG Lab

A simple retrieval-augmented generation assistant over internal legal policy
documents (corporate governance, M&A, and IP). Built as plain Python files,
following the required lab sequence, and deployed with Streamlit.

## Pipeline

```text
01_documents.py            -> raw legal policy documents (with is_current flag)
02_preprocessing.py        -> lowercase, tokenize, remove stopwords, lemmatize
03_chunking.py              -> sliding-window chunking (60 words, 15 overlap)
04_vector_representation.py -> BM25 index + all-MiniLM-L6-v2 embeddings
05_create_chroma_store.py  -> upserts chunks + embeddings into a Chroma collection
06_retrieve_context.py     -> hybrid retrieval, dedup by document, builds [Source N] context
07_prompting.py            -> grounded prompt + OpenRouter call
streamlit_app.py           -> chat UI, shows sources per answer
```

Hybrid retrieval score:

```text
hybrid = 0.4 * BM25 + 0.6 * all-MiniLM-L6-v2 embeddings
```

Retrieved chunks are ranked with CURRENT documents preferred over OUTDATED
ones (`is_current` flag on each document in `01_documents.py`), and the
prompt in `07_prompting.py` instructs the model to prefer current sources
and flag outdated ones.

## Run locally

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# edit .env and add your real OPENAI_API_KEY
python 05_create_chroma_store.py
streamlit run streamlit_app.py
```

On macOS/Linux, replace `Copy-Item .env.example .env` with `cp .env.example .env`.

## API key rules

- Never write a real API key into any `.py` file.
- Never commit or upload the real `.env` file (it's excluded via `.gitignore`).
- Locally, keys are read from `.env` via `python-dotenv`.
- When deployed, keys are read from Streamlit Cloud's TOML secrets instead.

## Deploying: GitHub -> Streamlit Community Cloud

1. **Push to GitHub**
   - Create a new repository and push this project.
   - Confirm `.env` is *not* in the repo (check `.gitignore` is committed and working).
2. **Create the Streamlit app**
   - Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
   - Click **New app**, select your GitHub repo, branch, and set the main
     file path to `streamlit_app.py`.
3. **Add secrets**
   - Once the app is created, click **Manage app** (bottom-right of the app view).
   - Open the **Secrets** tab.
   - Add the following, in valid TOML format:
     ```toml
     OPENAI_API_KEY = "your_openai_key_here"
     OPENAI_MODEL = "gpt-4o-mini"
     ```
   - Save. Streamlit will restart the app with the secrets available via
     `st.secrets`.
4. **Verify**
   - Open the deployed app URL.
   - Ask a question covered by the documents (e.g. "What vote is required
     to approve a merger?").
   - Confirm the answer cites `[Source N]` and the sources panel shows the
     matching policy text.

## Final checklist

- [ ] All required Python files exist (`01`-`07`, `streamlit_app.py`).
- [ ] `requirements.txt` exists.
- [ ] No real API key in the ZIP or GitHub repo.
- [ ] Streamlit secrets configured in valid TOML format.
- [ ] The Streamlit app runs successfully.
- [ ] The answer uses retrieved context.
- [ ] The answer cites sources.
