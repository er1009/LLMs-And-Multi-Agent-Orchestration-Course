"""
Distance Calculation Module

Provides various distance metrics for comparing embedding vectors.
"""

import numpy as np
from typing import Tuple


class DistanceCalculator:
    """
    Calculator for various distance metrics between vectors.

    Supports both cosine distance and Euclidean distance
    for semantic similarity measurement.
    """

    @staticmethod
    def cosine_distance(v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculate cosine distance between two vectors.

        Cosine distance = 1 - cosine similarity
        Range: [0, 2], where 0 means identical direction

        Args:
            v1: First vector
            v2: Second vector

        Returns:
            Cosine distance

        Raises:
            ValueError: If vectors have different dimensions or are zero vectors
        """
        if v1.shape != v2.shape:
            raise ValueError(
                f"Vectors must have same shape, got {v1.shape} and {v2.shape}"
            )

        # Normalize vectors
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            raise ValueError("Cannot calculate cosine distance for zero vector")

        # Calculate cosine similarity
        similarity = np.dot(v1, v2) / (norm1 * norm2)

        # Clamp to [-1, 1] to handle numerical errors
        similarity = np.clip(similarity, -1.0, 1.0)

        # Return cosine distance (1 - similarity)
        return float(1.0 - similarity)

    @staticmethod
    def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two vectors.

        Also known as L2 distance.
        Range: [0, ∞)

        Args:
            v1: First vector
            v2: Second vector

        Returns:
            Euclidean distance

        Raises:
            ValueError: If vectors have different dimensions
        """
        if v1.shape != v2.shape:
            raise ValueError(
                f"Vectors must have same shape, got {v1.shape} and {v2.shape}"
            )

        return float(np.linalg.norm(v1 - v2))

    @staticmethod
    def manhattan_distance(v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculate Manhattan distance between two vectors.

        Also known as L1 distance.
        Range: [0, ∞)

        Args:
            v1: First vector
            v2: Second vector

        Returns:
            Manhattan distance

        Raises:
            ValueError: If vectors have different dimensions
        """
        if v1.shape != v2.shape:
            raise ValueError(
                f"Vectors must have same shape, got {v1.shape} and {v2.shape}"
            )

        return float(np.sum(np.abs(v1 - v2)))

    @staticmethod
    def all_distances(
        v1: np.ndarray, v2: np.ndarray
    ) -> Tuple[float, float, float]:
        """
        Calculate all distance metrics at once.

        Args:
            v1: First vector
            v2: Second vector

        Returns:
            Tuple of (cosine_distance, euclidean_distance, manhattan_distance)

        Raises:
            ValueError: If vectors have different dimensions or are invalid
        """
        cosine = DistanceCalculator.cosine_distance(v1, v2)
        euclidean = DistanceCalculator.euclidean_distance(v1, v2)
        manhattan = DistanceCalculator.manhattan_distance(v1, v2)

        return cosine, euclidean, manhattan

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.

        Range: [-1, 1], where 1 means identical direction

        Args:
            v1: First vector
            v2: Second vector

        Returns:
            Cosine similarity

        Raises:
            ValueError: If vectors have different dimensions or are zero vectors
        """
        distance = DistanceCalculator.cosine_distance(v1, v2)
        return 1.0 - distance
