"""
Evaluation Engine

Orchestrates embedding generation and distance calculation
for semantic similarity evaluation.
"""

from dataclasses import dataclass
import numpy as np
from .distance import DistanceCalculator


@dataclass
class EvaluationResult:
    """
    Result of semantic similarity evaluation.

    Attributes:
        original_text: Original input text
        final_text: Final output text after translation
        original_embedding: Embedding vector for original text
        final_embedding: Embedding vector for final text
        cosine_distance: Cosine distance between embeddings
        euclidean_distance: Euclidean distance between embeddings
        error_rate: Error rate used in pipeline (if applicable)
    """

    original_text: str
    final_text: str
    original_embedding: np.ndarray
    final_embedding: np.ndarray
    cosine_distance: float
    euclidean_distance: float
    error_rate: float = 0.0


class EvaluationEngine:
    """
    Engine for evaluating semantic similarity using embeddings.

    Coordinates embedding generation and distance calculation
    to measure semantic drift between texts.
    """

    def __init__(self, embedding_provider):
        """
        Initialize the evaluation engine.

        Args:
            embedding_provider: Provider for generating embeddings (HuggingFaceEmbedding)
        """
        self.embedding_provider = embedding_provider
        self.distance_calculator = DistanceCalculator()

    def evaluate(
        self, original: str, final: str, error_rate: float = 0.0
    ) -> EvaluationResult:
        """
        Evaluate semantic similarity between original and final texts.

        Args:
            original: Original text
            final: Final text after transformation
            error_rate: Error rate used (for tracking)

        Returns:
            EvaluationResult with embeddings and distances

        Raises:
            ValueError: If texts are empty
            RuntimeError: If embedding or distance calculation fails
        """
        if not original or not original.strip():
            raise ValueError("Original text cannot be empty")

        if not final or not final.strip():
            raise ValueError("Final text cannot be empty")

        try:
            # Generate embeddings
            original_embedding = self.embedding_provider.embed(original)
            final_embedding = self.embedding_provider.embed(final)

            # Calculate distances
            cosine_dist = self.distance_calculator.cosine_distance(
                original_embedding, final_embedding
            )
            euclidean_dist = self.distance_calculator.euclidean_distance(
                original_embedding, final_embedding
            )

            return EvaluationResult(
                original_text=original,
                final_text=final,
                original_embedding=original_embedding,
                final_embedding=final_embedding,
                cosine_distance=cosine_dist,
                euclidean_distance=euclidean_dist,
                error_rate=error_rate,
            )

        except Exception as e:
            raise RuntimeError(f"Evaluation failed: {str(e)}") from e

    def evaluate_batch(
        self, original_texts: list[str], final_texts: list[str], error_rates: list[float]
    ) -> list[EvaluationResult]:
        """
        Evaluate multiple text pairs in batch.

        Args:
            original_texts: List of original texts
            final_texts: List of final texts
            error_rates: List of error rates

        Returns:
            List of EvaluationResult objects

        Raises:
            ValueError: If input lists have different lengths
            RuntimeError: If batch evaluation fails
        """
        if len(original_texts) != len(final_texts):
            raise ValueError(
                f"Original and final texts must have same length, "
                f"got {len(original_texts)} and {len(final_texts)}"
            )

        if len(original_texts) != len(error_rates):
            raise ValueError(
                f"Texts and error rates must have same length, "
                f"got {len(original_texts)} and {len(error_rates)}"
            )

        try:
            # Generate embeddings in batch for efficiency
            original_embeddings = self.embedding_provider.embed_batch(original_texts)
            final_embeddings = self.embedding_provider.embed_batch(final_texts)

            # Calculate distances for each pair
            results = []
            for i, (orig, final, orig_emb, final_emb, error_rate) in enumerate(
                zip(
                    original_texts,
                    final_texts,
                    original_embeddings,
                    final_embeddings,
                    error_rates,
                )
            ):
                cosine_dist = self.distance_calculator.cosine_distance(
                    orig_emb, final_emb
                )
                euclidean_dist = self.distance_calculator.euclidean_distance(
                    orig_emb, final_emb
                )

                results.append(
                    EvaluationResult(
                        original_text=orig,
                        final_text=final,
                        original_embedding=orig_emb,
                        final_embedding=final_emb,
                        cosine_distance=cosine_dist,
                        euclidean_distance=euclidean_dist,
                        error_rate=error_rate,
                    )
                )

            return results

        except Exception as e:
            raise RuntimeError(f"Batch evaluation failed: {str(e)}") from e
