from importlib import import_module
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

preprocessing = import_module("02_preprocessing")
chunks = import_module("03_chunking").build_chunks()

ALPHA = 0.6  # Weight given to dense vector search vs sparse BM25 (1 - ALPHA)
MODEL_NAME = "all-MiniLM-L6-v2"

# 1. Prepare BM25 Corpus (Preprocessed Tokens)
tokenized_chunks = [chunk["search_text"].split() for chunk in chunks]
bm25 = BM25Okapi(tokenized_chunks)

# 2. Prepare Dense Vector Corpus
model = SentenceTransformer(MODEL_NAME)
chunk_embeddings = model.encode(
    [chunk["search_text"] for chunk in chunks],
    convert_to_numpy=True,
    normalize_embeddings=True,
)


def min_max_normalize(scores: np.ndarray) -> np.ndarray:
    scores = np.array(scores, dtype=float)
    score_min, score_max = scores.min(), scores.max()
    if score_max == score_min:
        return np.zeros_like(scores)
    return (scores - score_min) / (score_max - score_min)


def hybrid_search(query: str, k: int = 4):
    # Preprocessed query for BM25 sparse matching
    clean_query = preprocessing.preprocess_text(query)
    bm25_scores = bm25.get_scores(clean_query.split())

    # Raw query for Neural Dense Embedding matching (preserves context/grammar)
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    
    # Dot product of normalized vectors equals cosine similarity
    embedding_scores = np.dot(chunk_embeddings, query_embedding.T).flatten()

    # Combine normalized scores via convex combination
    hybrid_scores = ((1 - ALPHA) * min_max_normalize(bm25_scores)) + (
        ALPHA * min_max_normalize(embedding_scores)
    )

    # Top-K ranking indices
    ranking = np.argsort(hybrid_scores)[::-1][:k]

    return [
        {**chunks[index], "score": float(hybrid_scores[index])}
        for index in ranking
    ]
