"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing."""
    mock_client = Mock()
    mock_client.query.return_value = "This is a mock response."
    mock_client.warmup.return_value = None
    mock_client.check_connection.return_value = True
    return mock_client


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model for testing."""
    import numpy as np

    mock_model = Mock()
    mock_model.encode.return_value = np.random.rand(5, 384)  # 5 sentences, 384 dims
    return mock_model


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        "This is the first document about technology and software development.",
        "The second document discusses legal regulations and compliance requirements.",
        "Medical procedures and healthcare practices are covered in this third document.",
    ]


@pytest.fixture
def sample_question_answer_pairs():
    """Sample Q&A pairs for testing."""
    return [
        ("What is the capital of France?", "Paris"),
        ("What is 2+2?", "4"),
        ("What color is the sky?", "blue"),
    ]
