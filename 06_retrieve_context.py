from importlib import import_module

hybrid_search = import_module("04_vector_representation").hybrid_search


def build_context(question, k=4, max_sources=3):
    rows = hybrid_search(question, k=k)
    rows = sorted(rows, key=lambda row: (row["is_current"], row["score"]), reverse=True)

    selected = []
    seen_documents = set()

    for row in rows:
        if row["score"] <= 0:
            continue
        if row["document_id"] in seen_documents:
            continue
        selected.append(row)
        seen_documents.add(row["document_id"])
        if len(selected) == max_sources:
            break

    context = ""
    for source_number, row in enumerate(selected, start=1):
        status = "CURRENT" if row["is_current"] else "OUTDATED"
        context += f"[Source {source_number}] {row['title']} ({status})\n{row['chunk_text']}\n\n"

    return context.strip(), selected

