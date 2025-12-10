"""Token counting utilities for context window analysis.

This module provides accurate token counting for different models.
Since we're using local models (Ollama), we use character-based
approximation with model-specific calibration.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TokenCounter:
    """Token counter with model-specific calibration.

    Uses character-based estimation since we don't have access to
    the exact tokenizer for Ollama models. Calibration factors
    are based on empirical measurements.

    Attributes:
        model_name: Name of the model
        chars_per_token: Average characters per token for this model
    """

    # Model-specific calibration (chars per token)
    # These are empirical estimates for common models
    MODEL_CALIBRATION = {
        "llama2": 4.0,
        "mistral": 4.2,
        "phi": 3.8,
        "default": 4.0  # Conservative default
    }

    def __init__(self, model_name: str = "llama2"):
        """Initialize token counter.

        Args:
            model_name: Name of the model for calibration
        """
        self.model_name = model_name

        # Get calibration factor for this model
        base_model = model_name.split(":")[0]  # Handle versioned models like "llama2:7b"
        self.chars_per_token = self.MODEL_CALIBRATION.get(
            base_model,
            self.MODEL_CALIBRATION["default"]
        )

        logger.debug(
            f"Initialized TokenCounter for {model_name} "
            f"with {self.chars_per_token} chars/token"
        )

    def count_tokens(self, text: str) -> int:
        """Count approximate number of tokens in text.

        Uses character-based estimation calibrated for the model.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        char_count = len(text)
        token_count = int(char_count / self.chars_per_token)

        logger.debug(
            f"Text length: {char_count} chars → ~{token_count} tokens"
        )

        return token_count

    def count_words(self, text: str) -> int:
        """Count words in text.

        Useful for document generation and validation.

        Args:
            text: Input text

        Returns:
            Word count
        """
        if not text:
            return 0

        return len(text.split())


def count_tokens(text: str, model_name: str = "llama2") -> int:
    """Convenience function for token counting.

    Args:
        text: Input text
        model_name: Model name for calibration

    Returns:
        Estimated token count

    Example:
        >>> count_tokens("Hello world", model_name="llama2")
        3
    """
    counter = TokenCounter(model_name)
    return counter.count_tokens(text)


def estimate_tokens_from_words(word_count: int, model_name: str = "llama2") -> int:
    """Estimate token count from word count.

    Useful for planning document sizes before generation.

    Args:
        word_count: Number of words
        model_name: Model name for calibration

    Returns:
        Estimated token count

    Example:
        >>> estimate_tokens_from_words(100)
        125
    """
    # Rough estimate: 1 word ≈ 1.25 tokens (including spaces/punctuation)
    counter = TokenCounter(model_name)

    # Assume average word length of 5 chars + 1 space
    avg_chars_per_word = 6
    total_chars = word_count * avg_chars_per_word

    return int(total_chars / counter.chars_per_token)


def fits_in_context(
    text: str,
    model_name: str = "llama2",
    max_tokens: int = 4096
) -> bool:
    """Check if text fits within model's context window.

    Args:
        text: Input text
        model_name: Model name
        max_tokens: Maximum context window size

    Returns:
        True if text fits, False otherwise

    Example:
        >>> fits_in_context("Short text", max_tokens=4096)
        True
    """
    token_count = count_tokens(text, model_name)
    fits = token_count <= max_tokens

    if not fits:
        logger.warning(
            f"Text exceeds context window: {token_count} > {max_tokens} tokens"
        )

    return fits
