"""Tests for utility modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.utils.tokenization import (
    TokenCounter,
    count_tokens,
    estimate_tokens_from_words,
    fits_in_context
)
from src.utils.evaluation import (
    evaluate_exact_match,
    evaluate_fuzzy_match,
    evaluate_response,
    evaluate_batch,
    calculate_accuracy_stats
)
from src.utils.document_generator import DocumentGenerator


class TestTokenization:
    """Tests for tokenization utilities."""

    def test_token_counter_initialization(self):
        """Test TokenCounter initialization."""
        counter = TokenCounter(model_name="llama2")
        assert counter.model_name == "llama2"
        assert counter.chars_per_token == 4.0

    def test_count_tokens_basic(self):
        """Test basic token counting."""
        counter = TokenCounter()
        text = "Hello world"
        tokens = counter.count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_count_tokens_empty(self):
        """Test counting tokens in empty text."""
        counter = TokenCounter()
        assert counter.count_tokens("") == 0

    def test_count_tokens_function(self):
        """Test convenience function."""
        tokens = count_tokens("Hello world", model_name="llama2")
        assert tokens > 0

    def test_estimate_tokens_from_words(self):
        """Test token estimation from word count."""
        tokens = estimate_tokens_from_words(100, model_name="llama2")
        assert tokens > 100  # Should be slightly more than word count
        assert tokens < 200  # But not too much more

    def test_fits_in_context_true(self):
        """Test context window check - fits."""
        short_text = "Hello"
        assert fits_in_context(short_text, max_tokens=4096) is True

    def test_fits_in_context_false(self):
        """Test context window check - exceeds."""
        long_text = "word " * 10000
        assert fits_in_context(long_text, max_tokens=100) is False


class TestEvaluation:
    """Tests for evaluation utilities."""

    def test_evaluate_exact_match_success(self):
        """Test exact match with successful match."""
        response = "The answer is Paris"
        expected = "Paris"
        assert evaluate_exact_match(response, expected) == 1.0

    def test_evaluate_exact_match_failure(self):
        """Test exact match with no match."""
        response = "The answer is London"
        expected = "Paris"
        assert evaluate_exact_match(response, expected) == 0.0

    def test_evaluate_exact_match_case_insensitive(self):
        """Test exact match is case insensitive."""
        response = "The answer is PARIS"
        expected = "paris"
        assert evaluate_exact_match(response, expected) == 1.0

    def test_evaluate_fuzzy_match_similar(self):
        """Test fuzzy match with similar strings."""
        response = "The answer is Parise"  # Typo
        expected = "Paris"
        score = evaluate_fuzzy_match(response, expected, threshold=0.7)
        assert score > 0.0

    def test_evaluate_fuzzy_match_dissimilar(self):
        """Test fuzzy match with very different strings."""
        response = "The answer is Tokyo"
        expected = "Paris"
        score = evaluate_fuzzy_match(response, expected, threshold=0.85)
        assert score == 0.0

    def test_evaluate_response_exact_method(self):
        """Test evaluate_response with exact method."""
        score = evaluate_response(
            "The answer is 42",
            "42",
            method="exact"
        )
        assert score == 1.0

    def test_evaluate_response_multi_method(self):
        """Test evaluate_response with multi method."""
        score = evaluate_response(
            "The answer is Paris",
            "Paris",
            method="multi"
        )
        assert score >= 0.0
        assert score <= 1.0

    def test_evaluate_batch(self):
        """Test batch evaluation."""
        responses = ["Paris", "London", "Berlin"]
        expected = ["Paris", "London", "Madrid"]

        scores = evaluate_batch(responses, expected)

        assert len(scores) == 3
        assert scores[0] == 1.0  # Exact match
        assert scores[1] == 1.0  # Exact match
        assert scores[2] == 0.0  # No match

    def test_calculate_accuracy_stats(self):
        """Test accuracy statistics calculation."""
        scores = [1.0, 0.8, 0.9, 1.0, 0.7]
        stats = calculate_accuracy_stats(scores)

        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
        assert stats["mean"] == pytest.approx(0.88, rel=0.01)
        assert stats["min"] == 0.7
        assert stats["max"] == 1.0
        assert stats["count"] == 5

    def test_calculate_accuracy_stats_empty(self):
        """Test statistics with empty list."""
        stats = calculate_accuracy_stats([])
        assert stats["mean"] == 0.0
        assert stats["count"] == 0


class TestDocumentGenerator:
    """Tests for document generation."""

    def test_initialization(self):
        """Test DocumentGenerator initialization."""
        gen = DocumentGenerator(random_seed=42)
        assert gen.random_seed == 42
        assert gen.fake is not None

    def test_generate_filler_text_sentences(self):
        """Test filler text generation with sentences."""
        gen = DocumentGenerator(random_seed=42)
        text = gen.generate_filler_text(200, style="sentences")

        word_count = len(text.split())
        assert word_count >= 180  # Allow 10% variance
        assert word_count <= 220

    def test_generate_filler_text_paragraphs(self):
        """Test filler text generation with paragraphs."""
        gen = DocumentGenerator(random_seed=42)
        text = gen.generate_filler_text(200, style="paragraphs")

        assert "\n\n" in text  # Should have paragraph breaks
        word_count = len(text.split())
        assert word_count >= 180

    def test_embed_critical_fact_middle(self):
        """Test fact embedding at middle position."""
        gen = DocumentGenerator(random_seed=42)
        text = "word " * 100
        fact = "CRITICAL_FACT"

        result = gen.embed_critical_fact(text, fact, position="middle")

        assert fact in result
        words = result.split()
        fact_index = [i for i, w in enumerate(words) if fact in w][0]

        # Should be around middle (40-60%)
        relative_pos = fact_index / len(words)
        assert 0.4 < relative_pos < 0.6

    def test_embed_critical_fact_start(self):
        """Test fact embedding at start position."""
        gen = DocumentGenerator(random_seed=42)
        text = "word " * 100
        fact = "CRITICAL_FACT"

        result = gen.embed_critical_fact(text, fact, position="start")

        words = result.split()
        fact_index = [i for i, w in enumerate(words) if fact in w][0]

        # Should be near start (0-10%)
        relative_pos = fact_index / len(words)
        assert relative_pos < 0.1

    def test_embed_critical_fact_end(self):
        """Test fact embedding at end position."""
        gen = DocumentGenerator(random_seed=42)
        text = "word " * 100
        fact = "CRITICAL_FACT"

        result = gen.embed_critical_fact(text, fact, position="end")

        words = result.split()
        fact_index = [i for i, w in enumerate(words) if fact in w][0]

        # Should be near end (90-100%)
        relative_pos = fact_index / len(words)
        assert relative_pos > 0.9

    def test_generate_realistic_documents(self):
        """Test realistic document generation."""
        gen = DocumentGenerator(random_seed=42)
        docs = gen.generate_realistic_documents(
            num_docs=5,
            words_per_doc=100,
            topics=["technology", "law"]
        )

        assert len(docs) == 5

        for doc in docs:
            assert "doc_id" in doc
            assert "content" in doc
            assert "domain" in doc
            assert doc["domain"] in ["technology", "law"]
            assert len(doc["content"]) > 0

    def test_create_needle_haystack_document(self):
        """Test needle-in-haystack document creation."""
        gen = DocumentGenerator(random_seed=42)
        doc = gen.create_needle_haystack_document(
            haystack_words=500,
            needle="SECRET_CODE",
            position="middle"
        )

        assert "content" in doc
        assert "SECRET_CODE" in doc["content"]
        assert "needle" in doc
        assert doc["needle"] == "SECRET_CODE"
        assert doc["position"] == "middle"

    def test_reproducibility_with_seed(self):
        """Test that same seed produces same results."""
        gen1 = DocumentGenerator(random_seed=42)
        gen2 = DocumentGenerator(random_seed=42)

        text1 = gen1.generate_filler_text(100)
        text2 = gen2.generate_filler_text(100)

        assert text1 == text2
