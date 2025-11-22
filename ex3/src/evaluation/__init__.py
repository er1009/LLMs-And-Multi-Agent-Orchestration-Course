"""
Evaluation Module

Provides semantic similarity evaluation using:
- Vector embeddings (HuggingFace sentence-transformers, local, no API key)
- Distance metrics (cosine, Euclidean)
- Batch evaluation capabilities
"""

from .hf_embedding import HuggingFaceEmbedding
from .distance import DistanceCalculator
from .engine import EvaluationEngine, EvaluationResult

__all__ = [
    "HuggingFaceEmbedding",
    "DistanceCalculator",
    "EvaluationEngine",
    "EvaluationResult",
]
