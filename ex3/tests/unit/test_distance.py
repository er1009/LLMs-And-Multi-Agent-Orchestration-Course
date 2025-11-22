"""
Unit tests for distance calculation module.
"""

import pytest
import numpy as np
from src.evaluation.distance import DistanceCalculator


class TestDistanceCalculator:
    """Tests for DistanceCalculator class."""

    def test_cosine_distance_identical_vectors(self):
        """Test cosine distance for identical vectors."""
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([1.0, 2.0, 3.0])

        distance = DistanceCalculator.cosine_distance(v1, v2)
        assert distance == pytest.approx(0.0, abs=1e-6)

    def test_cosine_distance_opposite_vectors(self):
        """Test cosine distance for opposite vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([-1.0, 0.0, 0.0])

        distance = DistanceCalculator.cosine_distance(v1, v2)
        assert distance == pytest.approx(2.0, abs=1e-6)

    def test_cosine_distance_orthogonal_vectors(self):
        """Test cosine distance for orthogonal vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])

        distance = DistanceCalculator.cosine_distance(v1, v2)
        assert distance == pytest.approx(1.0, abs=1e-6)

    def test_euclidean_distance_identical(self):
        """Test Euclidean distance for identical vectors."""
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([1.0, 2.0, 3.0])

        distance = DistanceCalculator.euclidean_distance(v1, v2)
        assert distance == pytest.approx(0.0, abs=1e-6)

    def test_euclidean_distance_calculation(self):
        """Test Euclidean distance calculation."""
        v1 = np.array([0.0, 0.0, 0.0])
        v2 = np.array([3.0, 4.0, 0.0])

        distance = DistanceCalculator.euclidean_distance(v1, v2)
        assert distance == pytest.approx(5.0, abs=1e-6)  # 3-4-5 triangle

    def test_manhattan_distance_calculation(self):
        """Test Manhattan distance calculation."""
        v1 = np.array([0.0, 0.0, 0.0])
        v2 = np.array([3.0, 4.0, 0.0])

        distance = DistanceCalculator.manhattan_distance(v1, v2)
        assert distance == pytest.approx(7.0, abs=1e-6)  # 3 + 4

    def test_dimension_mismatch_error(self):
        """Test error on dimension mismatch."""
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([1.0, 2.0])

        with pytest.raises(ValueError, match="must have same shape"):
            DistanceCalculator.cosine_distance(v1, v2)

        with pytest.raises(ValueError, match="must have same shape"):
            DistanceCalculator.euclidean_distance(v1, v2)

    def test_zero_vector_error(self):
        """Test error on zero vector for cosine distance."""
        v1 = np.array([0.0, 0.0, 0.0])
        v2 = np.array([1.0, 2.0, 3.0])

        with pytest.raises(ValueError, match="zero vector"):
            DistanceCalculator.cosine_distance(v1, v2)

    def test_all_distances(self):
        """Test calculating all distances at once."""
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([4.0, 5.0, 6.0])

        cosine, euclidean, manhattan = DistanceCalculator.all_distances(v1, v2)

        assert cosine > 0
        assert euclidean > 0
        assert manhattan > 0
        assert isinstance(cosine, float)
        assert isinstance(euclidean, float)
        assert isinstance(manhattan, float)

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        v1 = np.array([1.0, 2.0, 3.0])
        v2 = np.array([1.0, 2.0, 3.0])

        similarity = DistanceCalculator.cosine_similarity(v1, v2)
        assert similarity == pytest.approx(1.0, abs=1e-6)

        # Verify similarity = 1 - distance
        distance = DistanceCalculator.cosine_distance(v1, v2)
        assert similarity == pytest.approx(1.0 - distance, abs=1e-6)
