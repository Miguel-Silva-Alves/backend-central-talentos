import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

# Carrega uma única vez (fica em RAM e é reaproveitado)
model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embedding(text: str) -> List[float]:
    """
    Gera embedding rápido usando SentenceTransformers.
    """
    if not text or not text.strip():
        return [0.0]

    vec = model.encode(text)
    return vec.tolist()

def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))