"""
Unit tests for error injection module.
"""

import pytest
from src.translation.error_injector import ErrorInjector


class TestErrorInjector:
    """Tests for ErrorInjector class."""

    def test_no_errors(self):
        """Test with 0% error rate."""
        injector = ErrorInjector(seed=42)
        text = "The quick brown fox jumps"
        result = injector.inject_errors(text, error_rate=0.0)
        assert result == text

    def test_with_seed_reproducible(self):
        """Test that same seed produces same errors."""
        text = "The quick brown fox jumps over the lazy dog"

        injector1 = ErrorInjector(seed=42)
        result1 = injector1.inject_errors(text, error_rate=0.25)

        injector2 = ErrorInjector(seed=42)
        result2 = injector2.inject_errors(text, error_rate=0.25)

        assert result1 == result2

    def test_different_seeds_different_results(self):
        """Test that different seeds produce different errors."""
        text = "The quick brown fox jumps over the lazy dog"

        injector1 = ErrorInjector(seed=42)
        result1 = injector1.inject_errors(text, error_rate=0.25)

        injector2 = ErrorInjector(seed=99)
        result2 = injector2.inject_errors(text, error_rate=0.25)

        assert result1 != result2

    def test_error_rate_validation(self):
        """Test error rate validation."""
        injector = ErrorInjector()

        with pytest.raises(ValueError, match="Error rate must be between"):
            injector.inject_errors("test text", error_rate=-0.1)

        with pytest.raises(ValueError, match="Error rate must be between"):
            injector.inject_errors("test text", error_rate=1.1)

    def test_errors_introduced(self):
        """Test that errors are actually introduced."""
        injector = ErrorInjector(seed=42)
        text = "The quick brown fox jumps over the lazy dog"
        result = injector.inject_errors(text, error_rate=0.5)

        assert result != text  # Should be different
        assert len(result.split()) == len(text.split())  # Word count should be similar

    def test_get_error_statistics(self):
        """Test error statistics calculation."""
        injector = ErrorInjector(seed=42)
        original = "The quick brown fox"
        corrupted = injector.inject_errors(original, error_rate=0.25)

        stats = injector.get_error_statistics(original, corrupted)

        assert "words_changed" in stats
        assert "total_words" in stats
        assert "chars_changed" in stats
        assert "actual_error_rate" in stats
        assert stats["total_words"] == 4

    def test_empty_text(self):
        """Test behavior with empty text."""
        injector = ErrorInjector()
        result = injector.inject_errors("", error_rate=0.25)
        assert result == ""
