"""
Tests for the Even/Odd game logic.
"""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.referee.game_logic import (
    draw_number,
    get_parity,
    determine_winner,
    validate_parity_choice,
    calculate_score,
)


class TestGetParity:
    """Tests for get_parity function."""

    def test_even_numbers(self):
        """Even numbers should return 'even'."""
        assert get_parity(2) == "even"
        assert get_parity(4) == "even"
        assert get_parity(10) == "even"
        assert get_parity(0) == "even"

    def test_odd_numbers(self):
        """Odd numbers should return 'odd'."""
        assert get_parity(1) == "odd"
        assert get_parity(3) == "odd"
        assert get_parity(9) == "odd"
        assert get_parity(7) == "odd"


class TestDrawNumber:
    """Tests for draw_number function."""

    def test_default_range(self):
        """Number should be between 1 and 10."""
        for _ in range(100):
            num = draw_number()
            assert 1 <= num <= 10

    def test_custom_range(self):
        """Number should respect custom range."""
        for _ in range(100):
            num = draw_number(5, 15)
            assert 5 <= num <= 15


class TestDetermineWinner:
    """Tests for determine_winner function."""

    def test_player_a_wins_with_even(self):
        """Player A wins when choosing even and number is even."""
        winner, parity, _ = determine_winner("even", "odd", 8)
        assert winner == "PLAYER_A"
        assert parity == "even"

    def test_player_b_wins_with_even(self):
        """Player B wins when choosing even and number is even."""
        winner, parity, _ = determine_winner("odd", "even", 8)
        assert winner == "PLAYER_B"
        assert parity == "even"

    def test_player_a_wins_with_odd(self):
        """Player A wins when choosing odd and number is odd."""
        winner, parity, _ = determine_winner("odd", "even", 7)
        assert winner == "PLAYER_A"
        assert parity == "odd"

    def test_player_b_wins_with_odd(self):
        """Player B wins when choosing odd and number is odd."""
        winner, parity, _ = determine_winner("even", "odd", 7)
        assert winner == "PLAYER_B"
        assert parity == "odd"

    def test_draw_both_correct(self):
        """Draw when both players are correct."""
        winner, parity, _ = determine_winner("even", "even", 8)
        assert winner is None
        assert parity == "even"

    def test_draw_both_wrong(self):
        """Draw when both players are wrong."""
        winner, parity, _ = determine_winner("odd", "odd", 8)
        assert winner is None
        assert parity == "even"

    def test_case_insensitive(self):
        """Choices should be case insensitive."""
        winner, parity, _ = determine_winner("EVEN", "ODD", 8)
        assert winner == "PLAYER_A"


class TestValidateParityChoice:
    """Tests for validate_parity_choice function."""

    def test_valid_even(self):
        """'even' is a valid choice."""
        assert validate_parity_choice("even") is True

    def test_valid_odd(self):
        """'odd' is a valid choice."""
        assert validate_parity_choice("odd") is True

    def test_valid_uppercase(self):
        """Uppercase choices are valid."""
        assert validate_parity_choice("EVEN") is True
        assert validate_parity_choice("ODD") is True

    def test_invalid_choice(self):
        """Invalid choices are rejected."""
        assert validate_parity_choice("maybe") is False
        assert validate_parity_choice("") is False
        assert validate_parity_choice("123") is False


class TestCalculateScore:
    """Tests for calculate_score function."""

    def test_player_a_wins(self):
        """Player A wins - gets 3 points."""
        scores = calculate_score("PLAYER_A", "P01", "P02")
        assert scores["P01"] == 3
        assert scores["P02"] == 0

    def test_player_b_wins(self):
        """Player B wins - gets 3 points."""
        scores = calculate_score("PLAYER_B", "P01", "P02")
        assert scores["P01"] == 0
        assert scores["P02"] == 3

    def test_draw(self):
        """Draw - both get 1 point."""
        scores = calculate_score(None, "P01", "P02")
        assert scores["P01"] == 1
        assert scores["P02"] == 1
