"""
Tests for player strategies.
"""

import pytest
from collections import Counter

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.player.strategy import (
    RandomStrategy,
    AlwaysEvenStrategy,
    AlwaysOddStrategy,
    AlternatingStrategy,
    BiasedStrategy,
    get_strategy,
    make_choice,
    STRATEGIES,
)
from agents.player.state import PlayerState


@pytest.fixture
def player_state():
    """Create a test player state."""
    return PlayerState(display_name="Test Player")


@pytest.fixture
def empty_context():
    """Create an empty context."""
    return {}


class TestRandomStrategy:
    """Tests for RandomStrategy."""

    def test_returns_valid_choice(self, player_state, empty_context):
        """Should return 'even' or 'odd'."""
        strategy = RandomStrategy()
        for _ in range(100):
            choice = strategy.choose(player_state, empty_context)
            assert choice in ("even", "odd")

    def test_distribution(self, player_state, empty_context):
        """Should have roughly equal distribution."""
        strategy = RandomStrategy()
        choices = [strategy.choose(player_state, empty_context) for _ in range(1000)]
        counts = Counter(choices)

        # Should be roughly 50/50 (within 10%)
        even_ratio = counts["even"] / 1000
        assert 0.4 <= even_ratio <= 0.6


class TestAlwaysEvenStrategy:
    """Tests for AlwaysEvenStrategy."""

    def test_always_returns_even(self, player_state, empty_context):
        """Should always return 'even'."""
        strategy = AlwaysEvenStrategy()
        for _ in range(100):
            choice = strategy.choose(player_state, empty_context)
            assert choice == "even"


class TestAlwaysOddStrategy:
    """Tests for AlwaysOddStrategy."""

    def test_always_returns_odd(self, player_state, empty_context):
        """Should always return 'odd'."""
        strategy = AlwaysOddStrategy()
        for _ in range(100):
            choice = strategy.choose(player_state, empty_context)
            assert choice == "odd"


class TestAlternatingStrategy:
    """Tests for AlternatingStrategy."""

    def test_alternates(self, player_state, empty_context):
        """Should alternate between even and odd."""
        strategy = AlternatingStrategy()

        choices = [strategy.choose(player_state, empty_context) for _ in range(10)]

        # Adjacent choices should be different
        for i in range(1, len(choices)):
            assert choices[i] != choices[i - 1]


class TestBiasedStrategy:
    """Tests for BiasedStrategy."""

    def test_biased_toward_even(self, player_state, empty_context):
        """Should be biased toward even with high probability."""
        strategy = BiasedStrategy(even_probability=0.9)
        choices = [strategy.choose(player_state, empty_context) for _ in range(1000)]
        counts = Counter(choices)

        even_ratio = counts["even"] / 1000
        assert even_ratio >= 0.8

    def test_biased_toward_odd(self, player_state, empty_context):
        """Should be biased toward odd with low probability."""
        strategy = BiasedStrategy(even_probability=0.1)
        choices = [strategy.choose(player_state, empty_context) for _ in range(1000)]
        counts = Counter(choices)

        odd_ratio = counts["odd"] / 1000
        assert odd_ratio >= 0.8


class TestGetStrategy:
    """Tests for get_strategy function."""

    def test_get_random(self):
        """Should return RandomStrategy."""
        strategy = get_strategy("random")
        assert isinstance(strategy, RandomStrategy)

    def test_get_always_even(self):
        """Should return AlwaysEvenStrategy."""
        strategy = get_strategy("always_even")
        assert isinstance(strategy, AlwaysEvenStrategy)

    def test_get_always_odd(self):
        """Should return AlwaysOddStrategy."""
        strategy = get_strategy("always_odd")
        assert isinstance(strategy, AlwaysOddStrategy)

    def test_unknown_returns_random(self):
        """Unknown strategy should return RandomStrategy."""
        strategy = get_strategy("unknown_strategy")
        assert isinstance(strategy, RandomStrategy)


class TestMakeChoice:
    """Tests for make_choice function."""

    def test_uses_player_strategy(self, empty_context):
        """Should use the player's configured strategy."""
        state = PlayerState(display_name="Test", strategy="always_even")
        choice = make_choice(state, empty_context)
        assert choice == "even"

        state = PlayerState(display_name="Test", strategy="always_odd")
        choice = make_choice(state, empty_context)
        assert choice == "odd"


class TestStrategiesRegistry:
    """Tests for STRATEGIES registry."""

    def test_all_strategies_registered(self):
        """All expected strategies should be in registry."""
        expected = [
            "random",
            "always_even",
            "always_odd",
            "alternating",
            "biased_even",
            "biased_odd",
            "counter",
        ]
        for name in expected:
            assert name in STRATEGIES
