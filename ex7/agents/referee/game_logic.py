"""
Game logic for Even/Odd game.

Implements the rules and winner determination.
"""

import random
from typing import Literal


def draw_number(min_val: int = 1, max_val: int = 10) -> int:
    """Draw a random number for the game."""
    return random.randint(min_val, max_val)


def get_parity(number: int) -> Literal["even", "odd"]:
    """Determine if a number is even or odd."""
    return "even" if number % 2 == 0 else "odd"


def determine_winner(
    choice_a: str,
    choice_b: str,
    number: int,
) -> tuple[str | None, str, str]:
    """
    Determine the winner of an Even/Odd game.

    Args:
        choice_a: Player A's choice ("even" or "odd")
        choice_b: Player B's choice ("even" or "odd")
        number: The drawn number

    Returns:
        Tuple of (winner, parity, reason)
        - winner: "PLAYER_A", "PLAYER_B", or None (draw)
        - parity: "even" or "odd"
        - reason: Human-readable explanation
    """
    parity = get_parity(number)

    a_correct = choice_a.lower() == parity
    b_correct = choice_b.lower() == parity

    if a_correct and not b_correct:
        return "PLAYER_A", parity, f"Player A chose {choice_a}, number was {number} ({parity})"
    elif b_correct and not a_correct:
        return "PLAYER_B", parity, f"Player B chose {choice_b}, number was {number} ({parity})"
    else:
        # Both correct or both wrong = draw
        return None, parity, f"Draw - both chose {'correctly' if a_correct else 'incorrectly'}, number was {number} ({parity})"


def validate_parity_choice(choice: str) -> bool:
    """Validate that a parity choice is valid."""
    return choice.lower() in ("even", "odd")


def calculate_score(winner: str | None, player_a_id: str, player_b_id: str) -> dict[str, int]:
    """
    Calculate scores for both players.

    Returns:
        Dictionary mapping player IDs to their scores
    """
    if winner is None:
        # Draw
        return {player_a_id: 1, player_b_id: 1}
    elif winner == "PLAYER_A":
        return {player_a_id: 3, player_b_id: 0}
    else:
        return {player_a_id: 0, player_b_id: 3}
