from importlib import import_module
from typing import Tuple, List, Dict, Any

hybrid_search = import_module("04_vector_representation").hybrid_search


def build_context(question: str, k: int = 10, max_sources: int = 3) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Retrieves hybrid search results, filters out duplicates and negative scores,
    prioritizes active policies over outdated ones, and formats the output string.
    """
    # Fetch a larger candidate pool (k=10) to ensure we get max_sources after deduplication
    rows = hybrid_search(question, k=k)

    # Coerce is_current safely to boolean for sort ordering
    def sort_key(row):
        is_curr = row["is_current"]
        if isinstance(is_curr, str):
            is_curr = is_curr.lower() == "true"
        return (bool(is_curr), row.get("score", 0.0))

    # Sort primarily by policy currency (CURRENT first), then by relevance score
    rows = sorted(rows, key=sort_key, reverse=True)

    selected = []
    seen_documents = set()

    for row in rows:
        # Avoid dropping min-max normalized zero-scores unless score is strictly negative
        if row.get("score", 0) < 0:
            continue
            
        doc_id = row["document_id"]
        if doc_id in seen_documents:
            continue
            
        selected.append(row)
        seen_documents.add(doc_id)
        
        if len(selected) == max_sources:
            break

    # Construct formatted LLM context string
    context_blocks = []
    for source_number, row in enumerate(selected, start=1):
        is_curr = row["is_current"]
        if isinstance(is_curr, str):
            is_curr = is_curr.lower() == "true"
            
        status = "CURRENT" if is_curr else "OUTDATED"
        context_blocks.append(
            f"[Source {source_number}] {row['title']} ({status})\n{row['chunk_text']}"
        )

    context = "\n\n".join(context_blocks)
    return context.strip(), selected
