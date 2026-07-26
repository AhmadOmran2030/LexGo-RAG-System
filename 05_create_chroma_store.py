from importlib import import_module
from pathlib import Path

import chromadb
from chromadb.config import Settings

vectors = import_module("04_vector_representation")

# Safe path resolution for both scripts and notebooks
try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()

DB_PATH = BASE_DIR / "chroma_db"
COLLECTION_NAME = "legal_docs"


def create_vector_store():
    client = chromadb.PersistentClient(
        path=str(DB_PATH),
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(COLLECTION_NAME)

    collection.upsert(
        ids=[chunk["chunk_id"] for chunk in vectors.chunks],
        documents=[chunk["chunk_text"] for chunk in vectors.chunks],
        metadatas=[
            {
                "document_id": chunk["document_id"],
                "title": chunk["title"],
                "is_current": str(chunk["is_current"]),
                "search_text": chunk.get("search_text", ""),
            }
            for chunk in vectors.chunks
        ],
        embeddings=vectors.chunk_embeddings.tolist(),
    )

    return collection


if __name__ == "__main__":
    create_vector_store()
    print(f"Chroma vector store created at: {DB_PATH}")
