from typing import Dict, List, Any
from importlib import import_module

documents = import_module("01_documents").documents
preprocess_text = import_module("02_preprocessing").preprocess_text


def chunk_text(text: str, chunk_size: int = 60, overlap: int = 15) -> List[str]:
    """Splits text into word chunks with a specified overlap."""
    if overlap >= chunk_size:
        raise ValueError("chunk_size must be strictly greater than overlap.")
        
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start += step

    return chunks


def build_chunks() -> List[Dict[str, Any]]:
    """Builds preprocessed search chunk dicts from document list."""
    rows = []

    for document in documents:
        doc_id = document["id"]
        doc_title = document["title"]
        is_current = document["is_current"]
        doc_text = document["text"]

        text_chunks = chunk_text(doc_text)
        
        for chunk_number, chunk in enumerate(text_chunks):
            # Combined text for keyword/embedding enrichment
            search_input = f"{doc_title} {chunk}"
            
            rows.append(
                {
                    "chunk_id": f"{doc_id}_{chunk_number}",
                    "document_id": doc_id,
                    "title": doc_title,
                    "is_current": is_current,
                    "chunk_text": chunk,
                    "search_text": preprocess_text(search_input),
                }
            )

    return rows
