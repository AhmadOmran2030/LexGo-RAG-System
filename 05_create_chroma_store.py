from importlib import import_module
from pathlib import Path

import chromadb
from chromadb.config import Settings

vectors = import_module("04_vector_representation")

DB_PATH = Path(__file__).resolve().parent / "chroma_db"
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
            }
            for chunk in vectors.chunks
        ],
        embeddings=vectors.chunk_embeddings.tolist(),
    )

    return collection


if __name__ == "__main__":
    create_vector_store()
    print("Chroma vector store created.")

