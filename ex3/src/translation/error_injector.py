"""
Error Injector for introducing spelling errors into text.

Provides deterministic error injection with configurable rates
and reproducible results via seeding.
"""

import random
import string
from typing import List


class ErrorInjector:
    """
    Injects spelling errors into text at a configurable rate.

    The error injection is deterministic when a seed is provided,
    ensuring reproducible experiments.
    """

    def __init__(self, seed: int = None):
        """
        Initialize the error injector.

        Args:
            seed: Random seed for reproducibility (optional)
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def inject_errors(self, text: str, error_rate: float) -> str:
        """
        Inject spelling errors into text at the specified rate.

        Args:
            text: Original text
            error_rate: Proportion of characters to corrupt (0.0 to 1.0)

        Returns:
            Text with injected errors

        Raises:
            ValueError: If error_rate is not in [0.0, 1.0]
        """
        if not 0.0 <= error_rate <= 1.0:
            raise ValueError(f"Error rate must be between 0.0 and 1.0, got {error_rate}")

        if error_rate == 0.0:
            return text

        words = text.split()
        corrupted_words = []

        for word in words:
            if self._should_corrupt_word(word):
                corrupted_word = self._corrupt_word(word, error_rate)
                corrupted_words.append(corrupted_word)
            else:
                corrupted_words.append(word)

        return " ".join(corrupted_words)

    def _should_corrupt_word(self, word: str) -> bool:
        """
        Determine if a word should be corrupted.

        Args:
            word: Word to check

        Returns:
            True if word should be corrupted, False otherwise
        """
        # Skip very short words and punctuation
        if len(word) <= 2:
            return False

        # Skip if word is all punctuation
        if all(c in string.punctuation for c in word):
            return False

        return True

    def _corrupt_word(self, word: str, error_rate: float) -> str:
        """
        Corrupt a single word by introducing errors.

        Args:
            word: Word to corrupt
            error_rate: Proportion of characters to corrupt

        Returns:
            Corrupted word
        """
        chars = list(word)
        num_chars_to_corrupt = max(1, int(len(chars) * error_rate))

        # Get indices of alphabetic characters (skip punctuation)
        alpha_indices = [i for i, c in enumerate(chars) if c.isalpha()]

        if not alpha_indices:
            return word

        # Sample indices to corrupt
        num_to_corrupt = min(num_chars_to_corrupt, len(alpha_indices))
        indices_to_corrupt = random.sample(alpha_indices, num_to_corrupt)

        # Apply random corruption to selected indices
        for idx in indices_to_corrupt:
            chars[idx] = self._corrupt_char(chars[idx])

        return "".join(chars)

    def _corrupt_char(self, char: str) -> str:
        """
        Corrupt a single character using one of several strategies.

        Strategies:
        1. Replace with adjacent keyboard key (40%)
        2. Duplicate character (20%)
        3. Delete character (20%)
        4. Replace with random letter (20%)

        Args:
            char: Character to corrupt

        Returns:
            Corrupted character (may be empty string for deletion)
        """
        strategy = random.random()

        if strategy < 0.4:
            # Adjacent keyboard key
            return self._get_adjacent_key(char)
        elif strategy < 0.6:
            # Duplicate
            return char + char
        elif strategy < 0.8:
            # Delete
            return ""
        else:
            # Random replacement
            if char.isupper():
                return random.choice(string.ascii_uppercase)
            else:
                return random.choice(string.ascii_lowercase)

    def _get_adjacent_key(self, char: str) -> str:
        """
        Get an adjacent keyboard key for the given character.

        Args:
            char: Character to find adjacent key for

        Returns:
            Adjacent character
        """
        # QWERTY keyboard layout adjacency map
        adjacency = {
            "q": "wa", "w": "qeas", "e": "wrds", "r": "etf", "t": "ryg",
            "y": "tuh", "u": "yij", "i": "uok", "o": "ipl", "p": "ol",
            "a": "qwsz", "s": "awedxz", "d": "serfcx", "f": "drtgvc",
            "g": "ftyhbv", "h": "gyujnb", "j": "huikmn", "k": "jiolm",
            "l": "kop", "z": "asx", "x": "zsdc", "c": "xdfv", "v": "cfgb",
            "b": "vghn", "n": "bhjm", "m": "njk",
        }

        lower_char = char.lower()
        if lower_char in adjacency:
            adjacent = random.choice(adjacency[lower_char])
            return adjacent.upper() if char.isupper() else adjacent
        else:
            # If not in map, return original
            return char

    def get_error_statistics(self, original: str, corrupted: str) -> dict:
        """
        Calculate statistics about the injected errors.

        Args:
            original: Original text
            corrupted: Corrupted text

        Returns:
            Dictionary with error statistics
        """
        orig_words = original.split()
        corr_words = corrupted.split()

        # Count changed words
        words_changed = sum(
            1 for o, c in zip(orig_words, corr_words) if o != c
        )

        # Count character differences
        chars_changed = sum(
            1 for o, c in zip(original, corrupted) if o != c
        )

        # Calculate actual error rate
        actual_rate = (
            chars_changed / len(original) if len(original) > 0 else 0.0
        )

        return {
            "words_changed": words_changed,
            "total_words": len(orig_words),
            "chars_changed": chars_changed,
            "total_chars": len(original),
            "actual_error_rate": actual_rate,
        }
