"""
Parity choice strategies for the Even/Odd game.

Implements different strategies that players can use.
"""

import random
from abc import ABC, abstractmethod
from typing import Any

from .state import PlayerState


class Strategy(ABC):
    """Base class for parity choice strategies."""

    @abstractmethod
    def choose(self, state: PlayerState, context: dict[str, Any]) -> str:
        """
        Choose even or odd.

        Args:
            state: Current player state
            context: Game context (opponent_id, round_id, standings)

        Returns:
            "even" or "odd"
        """
        pass


class RandomStrategy(Strategy):
    """Randomly choose even or odd with equal probability."""

    def choose(self, state: PlayerState, context: dict[str, Any]) -> str:
        return random.choice(["even", "odd"])


class AlwaysEvenStrategy(Strategy):
    """Always choose even."""

    def choose(self, state: PlayerState, context: dict[str, Any]) -> str:
        return "even"


class AlwaysOddStrategy(Strategy):
    """Always choose odd."""

    def choose(self, state: PlayerState, context: dict[str, Any]) -> str:
        return "odd"


class AlternatingStrategy(Strategy):
    """Alternate between even and odd."""

    def __init__(self):
        self.last_choice = "odd"

    def choose(self, state: PlayerState, context: dict[str, Any]) -> str:
        self.last_choice = "even" if self.last_choice == "odd" else "odd"
        return self.last_choice


class BiasedStrategy(Strategy):
    """Choose with a bias toward one option."""

    def __init__(self, even_probability: float = 0.7):
        self.even_probability = even_probability

    def choose(self, state: PlayerState, context: dict[str, Any]) -> str:
        return "even" if random.random() < self.even_probability else "odd"


class CounterStrategy(Strategy):
    """
    Try to counter opponent's patterns.

    Looks at opponent's history and chooses the opposite of their most common choice.
    """

    def choose(self, state: PlayerState, context: dict[str, Any]) -> str:
        opponent_id = context.get("opponent_id")
        if not opponent_id:
            return random.choice(["even", "odd"])

        # Get history against this opponent
        history = state.get_opponent_history(opponent_id)
        if not history:
            return random.choice(["even", "odd"])

        # Count opponent's choices
        even_count = sum(1 for g in history if g.opponent_choice == "even")
        odd_count = sum(1 for g in history if g.opponent_choice == "odd")

        # Choose the same as opponent's most common (since we want to match the number)
        # If opponent often picks "even", they think even numbers will come up
        # We should also pick "even" to have the same chance
        if even_count > odd_count:
            return "even"
        elif odd_count > even_count:
            return "odd"
        else:
            return random.choice(["even", "odd"])


# Strategy registry
STRATEGIES: dict[str, Strategy] = {
    "random": RandomStrategy(),
    "always_even": AlwaysEvenStrategy(),
    "always_odd": AlwaysOddStrategy(),
    "alternating": AlternatingStrategy(),
    "biased_even": BiasedStrategy(0.7),
    "biased_odd": BiasedStrategy(0.3),
    "counter": CounterStrategy(),
}


def get_strategy(name: str) -> Strategy:
    """Get a strategy by name."""
    return STRATEGIES.get(name, RandomStrategy())


def make_choice(state: PlayerState, context: dict[str, Any]) -> str:
    """Make a parity choice using the player's configured strategy."""
    strategy = get_strategy(state.strategy)
    return strategy.choose(state, context)
