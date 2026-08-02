from importlib import import_module
from typing import Tuple, List, Dict, Any

hybrid_search = import_module("04_vector_representation").hybrid_search


def build_context(
    question: str,
    k: int = 10,
    max_sources: int = 3,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Build an LLM context using hybrid retrieval.

    Steps:
    1. Retrieve Top-K candidate chunks.
    2. Prioritize CURRENT policies.
    3. Remove duplicate documents.
    4. Return at most max_sources unique documents.
    """

    # Retrieve candidate chunks
    rows = hybrid_search(question, k=k)

    # No relevant results
    if not rows:
        return "", []

    # ------------------------------------------------------------------
    # Sort:
    #   1- Current policies first
    #   2- Higher similarity score
    # ------------------------------------------------------------------
    def sort_key(row):

        is_current = row["is_current"]

        if isinstance(is_current, str):
            is_current = is_current.lower() == "true"

        return (
            bool(is_current),
            row.get("score", 0.0),
        )

    rows = sorted(rows, key=sort_key, reverse=True)

    # ------------------------------------------------------------------
    # Remove duplicate documents
    # ------------------------------------------------------------------
    selected = []
    seen_documents = set()

    for row in rows:

        doc_id = row["document_id"]

        if doc_id in seen_documents:
            continue

        selected.append(row)
        seen_documents.add(doc_id)

        if len(selected) >= max_sources:
            break

    # Safety check
    if not selected:
        return "", []

    # ------------------------------------------------------------------
    # Build Context
    # ------------------------------------------------------------------
    context_blocks = []

    for source_number, row in enumerate(selected, start=1):

        is_current = row["is_current"]

        if isinstance(is_current, str):
            is_current = is_current.lower() == "true"

        status = "CURRENT" if is_current else "OUTDATED"

        context_blocks.append(
            f"[Source {source_number}] "
            f"{row['title']} "
            f"({status})\n"
            f"{row['chunk_text']}"
        )

    context = "\n\n".join(context_blocks)

    return context.strip(), selected
