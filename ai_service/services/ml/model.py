# # ml/model.py

# import pickle
# import numpy as np
# import os 

# MODEL_PATH = "services/ml/confidence_model.pkl"

# model = None

# def load_model():
#     global model
#     if model is None:
#         with open(MODEL_PATH, "rb") as f:
#             model = pickle.load(f)

# def predict_confidence(features):
#     num_chunks, answer_length, keyword_overlap = features

#     score = 0

#     if num_chunks >= 3:
#         score += 0.3

#     if answer_length > 200:
#         score += 0.3

#     if keyword_overlap >= 2:
#         score += 0.4

#     return round(score, 2)

import numpy as np
from numpy.linalg import norm


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Measures the angle between two vectors in embedding space.
    
    Returns 1.0  → vectors point in same direction (semantically identical)
    Returns 0.0  → vectors are perpendicular (unrelated)
    Returns -1.0 → opposite directions (opposite meaning)
    
    We use this to check: "does the retrieved chunk actually relate to the query?"
    
    Why cosine and not euclidean distance?
    Cosine ignores magnitude and only cares about direction — 
    which is exactly what we want for semantic similarity.
    """
    denom = norm(a) * norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def compute_confidence(query_vector: np.ndarray, retrieved_vectors: list) -> float:
    """
    Computes how relevant the retrieved chunks are to the user's query.

    Args:
        query_vector:      Embedding of the user's question. Shape: (1, 384)
        retrieved_vectors: List of embeddings for the top-k retrieved chunks.
                           Each item shape: (384,)

    Returns:
        Float between 0.0 and 1.0
        - High (>= 0.5): Retrieved chunks are semantically close to the query
                         → answer is likely relevant → critic will ACCEPT
        - Low  (< 0.5):  Retrieved chunks don't match the query well
                         → answer may be hallucinated → critic will RETRY

    Why average and not max?
    Max would give high confidence even if only 1 of 5 chunks is relevant.
    Average penalizes noise — if we retrieved 3 irrelevant chunks and 2 good ones,
    the score drops, triggering a retry with a refined query.
    """
    if not retrieved_vectors:
        # No chunks retrieved at all — index might be empty or broken
        return 0.0

    query_vec = query_vector[0]  # shape (1, 384) → (384,)

    similarities = [
        cosine_similarity(query_vec, chunk_vec)
        for chunk_vec in retrieved_vectors
    ]

    avg_similarity = float(np.mean(similarities))
    return round(avg_similarity, 3)