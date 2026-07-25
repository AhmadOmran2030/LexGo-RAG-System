from importlib import import_module

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

preprocessing = import_module("02_preprocessing")
chunks = import_module("03_chunking").build_chunks()

ALPHA = 0.6
MODEL_NAME = "all-MiniLM-L6-v2"

tokenized_chunks = [chunk["search_text"].split() for chunk in chunks]
bm25 = BM25Okapi(tokenized_chunks)

model = SentenceTransformer(MODEL_NAME)
chunk_embeddings = model.encode(
    [chunk["search_text"] for chunk in chunks],
    convert_to_numpy=True,
    normalize_embeddings=True,
)


def min_max_normalize(scores):
    scores = np.array(scores, dtype=float)
    if scores.max() == scores.min():
        return np.zeros_like(scores)
    return (scores - scores.min()) / (scores.max() - scores.min())


def hybrid_search(query, k=4):
    clean_query = preprocessing.preprocess_text(query)

    bm25_scores = bm25.get_scores(clean_query.split())
    query_embedding = model.encode(
        [clean_query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    embedding_scores = cosine_similarity(query_embedding, chunk_embeddings).flatten()

    hybrid_scores = ((1 - ALPHA) * min_max_normalize(bm25_scores)) + (
        ALPHA * min_max_normalize(embedding_scores)
    )

    ranking = np.argsort(hybrid_scores)[::-1][:k]
    return [
        {**chunks[index], "score": hybrid_scores[index]}
        for index in ranking
    ]

