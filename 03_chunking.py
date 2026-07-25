from importlib import import_module

documents = import_module("01_documents").documents
preprocess_text = import_module("02_preprocessing").preprocess_text


def chunk_text(text, chunk_size=60, overlap=15):
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start += chunk_size - overlap

    return chunks


def build_chunks():
    rows = []

    for document in documents:
        for chunk_number, chunk in enumerate(chunk_text(document["text"])):
            rows.append(
                {
                    "chunk_id": f"{document['id']}_{chunk_number}",
                    "document_id": document["id"],
                    "title": document["title"],
                    "is_current": document["is_current"],
                    "chunk_text": chunk,
                    "search_text": preprocess_text(f"{document['title']} {chunk}"),
                }
            )

    return rows

