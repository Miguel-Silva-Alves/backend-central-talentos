import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embedding(text: str) -> list[float]:
    """
    Embedding rápido usando SentenceTransformers (open-source).
    """
    if not text or not text.strip():
        return [0.0]

    vec = model.encode(text)
    return vec.tolist()
