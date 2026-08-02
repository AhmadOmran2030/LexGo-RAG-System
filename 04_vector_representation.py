from importlib import import_module
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

preprocessing = import_module("02_preprocessing")
chunks = import_module("03_chunking").build_chunks()

# ==============================================================================
# Configuration
# ==============================================================================
ALPHA = 0.6
MODEL_NAME = "all-MiniLM-L6-v2"

# Minimum acceptable hybrid similarity score
SIMILARITY_THRESHOLD = 0.45

# ==============================================================================
# BM25 Index
# ==============================================================================
tokenized_chunks = [chunk["search_text"].split() for chunk in chunks]
bm25 = BM25Okapi(tokenized_chunks)

# ==============================================================================
# Dense Embeddings
# ==============================================================================
model = SentenceTransformer(MODEL_NAME)

chunk_embeddings = model.encode(
    [chunk["search_text"] for chunk in chunks],
    convert_to_numpy=True,
    normalize_embeddings=True,
)


def min_max_normalize(scores):
    scores = np.array(scores, dtype=float)

    score_min = scores.min()
    score_max = scores.max()

    if score_max == score_min:
        return np.zeros_like(scores)

    return (scores - score_min) / (score_max - score_min)


def hybrid_search(query: str, k: int = 4):

    # -----------------------------
    # Sparse Search (BM25)
    # -----------------------------
    clean_query = preprocessing.preprocess_text(query)
    bm25_scores = bm25.get_scores(clean_query.split())

    # -----------------------------
    # Dense Search (Embeddings)
    # -----------------------------
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embedding_scores = np.dot(
        chunk_embeddings,
        query_embedding.T
    ).flatten()

    # -----------------------------
    # Hybrid Score
    # -----------------------------
    hybrid_scores = (
        (1 - ALPHA) * min_max_normalize(bm25_scores)
        +
        ALPHA * min_max_normalize(embedding_scores)
    )

    # Sort from highest score
    ranking = np.argsort(hybrid_scores)[::-1]

    results = []

    for index in ranking:

        score = float(hybrid_scores[index])

        # Ignore weak matches
        if score < SIMILARITY_THRESHOLD:
            continue

        results.append({
            **chunks[index],
            "score": score
        })

        if len(results) == k:
            break

    return results
