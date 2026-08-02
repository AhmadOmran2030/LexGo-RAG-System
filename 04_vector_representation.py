from importlib import import_module

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# ==============================================================================
# Imports
# ==============================================================================
preprocessing = import_module("02_preprocessing")
chunks = import_module("03_chunking").build_chunks()

# ==============================================================================
# Configuration
# ==============================================================================
ALPHA = 0.6
MODEL_NAME = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.45

# ==============================================================================
# BM25 Index
# ==============================================================================
tokenized_chunks = [chunk["search_text"].split() for chunk in chunks]
bm25 = BM25Okapi(tokenized_chunks)

# ==============================================================================
# Embedding Model
# ==============================================================================
model = SentenceTransformer(MODEL_NAME)

chunk_embeddings = model.encode(
    [chunk["search_text"] for chunk in chunks],
    convert_to_numpy=True,
    normalize_embeddings=True,
)


def min_max_normalize(scores: np.ndarray) -> np.ndarray:
    """Normalize scores to the range [0, 1]."""

    scores = np.asarray(scores, dtype=float)

    if len(scores) == 0:
        return scores

    score_min = scores.min()
    score_max = scores.max()

    if score_max == score_min:
        return np.zeros_like(scores)

    return (scores - score_min) / (score_max - score_min)


def hybrid_search(query: str, k: int = 4) -> list[dict]:
    """
    Hybrid Retrieval using BM25 + Sentence Transformers.

    Returns:
        Top-k relevant chunks whose hybrid score exceeds
        SIMILARITY_THRESHOLD.
    """

    if not query.strip():
        return []

    if len(chunks) == 0:
        return []

    # ------------------------------------------------------------------
    # Sparse Retrieval (BM25)
    # ------------------------------------------------------------------
    clean_query = preprocessing.preprocess_text(query)

    bm25_scores = bm25.get_scores(
        clean_query.split()
    )

    # ------------------------------------------------------------------
    # Dense Retrieval (Embeddings)
    # ------------------------------------------------------------------
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embedding_scores = np.dot(
        chunk_embeddings,
        query_embedding.T,
    ).flatten()

    # ------------------------------------------------------------------
    # Hybrid Score
    # ------------------------------------------------------------------
    hybrid_scores = (
        (1 - ALPHA) * min_max_normalize(bm25_scores)
        + ALPHA * min_max_normalize(embedding_scores)
    )

    ranking = np.argsort(hybrid_scores)[::-1]

    results = []

    for index in ranking:

        score = float(hybrid_scores[index])

        if score < SIMILARITY_THRESHOLD:
            continue

        results.append(
            {
                **chunks[index],
                "score": round(score, 4),
            }
        )

        if len(results) >= k:
            break

    return results
