"""
HuggingFace Embedding Provider

Uses sentence-transformers for free, local embedding generation.
No API key required.
"""

import numpy as np
from typing import List


class HuggingFaceEmbedding:
    """
    HuggingFace embedding provider using sentence-transformers.

    Provides free, local embedding generation without requiring API keys.
    Downloads models on first use and caches them locally.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the HuggingFace embedding provider.

        Args:
            model_name: Name of the sentence-transformer model
                       Default: "all-MiniLM-L6-v2" (384 dimensions, fast, good quality)
                       Alternatives:
                       - "all-mpnet-base-v2" (768 dim, slower, better quality)
                       - "paraphrase-MiniLM-L3-v2" (384 dim, fastest)
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for HuggingFace embeddings. "
                "Install it with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

        # Get embedding dimension
        self._dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for the given text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array

        Raises:
            ValueError: If text is empty
            RuntimeError: If embedding generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text to embed cannot be empty")

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)

        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {str(e)}") from e

    def get_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Embedding vector dimension
        """
        return self._dimension

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
            RuntimeError: If batch embedding fails
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        try:
            embeddings = self.model.encode(
                texts, convert_to_numpy=True, show_progress_bar=False
            )
            return [emb.astype(np.float32) for emb in embeddings]

        except Exception as e:
            raise RuntimeError(f"Batch embedding generation failed: {str(e)}") from e
