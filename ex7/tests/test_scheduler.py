"""
Tests for the round-robin scheduler.
"""

import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.league_manager.scheduler import (
    create_round_robin_schedule,
    get_matches_for_round,
    get_total_rounds,
    schedule_to_announcement_format,
)


class TestCreateRoundRobinSchedule:
    """Tests for create_round_robin_schedule function."""

    def test_two_players(self):
        """Two players should have 1 match."""
        schedule = create_round_robin_schedule(["P01", "P02"])
        assert len(schedule) == 1
        assert schedule[0].player_a_id == "P01"
        assert schedule[0].player_b_id == "P02"

    def test_four_players(self):
        """Four players should have 6 matches (4 choose 2)."""
        schedule = create_round_robin_schedule(["P01", "P02", "P03", "P04"])
        assert len(schedule) == 6

    def test_all_pairs_covered(self):
        """Every pair of players should play exactly once."""
        players = ["P01", "P02", "P03", "P04"]
        schedule = create_round_robin_schedule(players)

        pairs = set()
        for match in schedule:
            pair = tuple(sorted([match.player_a_id, match.player_b_id]))
            pairs.add(pair)

        # Should have 6 unique pairs
        assert len(pairs) == 6

        # Verify all expected pairs
        expected_pairs = {
            ("P01", "P02"),
            ("P01", "P03"),
            ("P01", "P04"),
            ("P02", "P03"),
            ("P02", "P04"),
            ("P03", "P04"),
        }
        assert pairs == expected_pairs

    def test_match_ids_unique(self):
        """All match IDs should be unique."""
        schedule = create_round_robin_schedule(["P01", "P02", "P03", "P04"])
        match_ids = [m.match_id for m in schedule]
        assert len(match_ids) == len(set(match_ids))

    def test_round_ids_assigned(self):
        """Matches should have round IDs assigned."""
        schedule = create_round_robin_schedule(["P01", "P02", "P03", "P04"])
        for match in schedule:
            assert match.round_id >= 1

    def test_empty_players(self):
        """Empty player list should return empty schedule."""
        schedule = create_round_robin_schedule([])
        assert len(schedule) == 0

    def test_single_player(self):
        """Single player should return empty schedule."""
        schedule = create_round_robin_schedule(["P01"])
        assert len(schedule) == 0


class TestGetMatchesForRound:
    """Tests for get_matches_for_round function."""

    def test_get_round_1(self):
        """Should return matches for round 1."""
        schedule = create_round_robin_schedule(["P01", "P02", "P03", "P04"])
        round_1 = get_matches_for_round(schedule, 1)
        assert len(round_1) >= 1
        for match in round_1:
            assert match.round_id == 1

    def test_get_nonexistent_round(self):
        """Should return empty list for nonexistent round."""
        schedule = create_round_robin_schedule(["P01", "P02"])
        round_99 = get_matches_for_round(schedule, 99)
        assert len(round_99) == 0


class TestGetTotalRounds:
    """Tests for get_total_rounds function."""

    def test_two_players(self):
        """Two players should have at least 1 round."""
        schedule = create_round_robin_schedule(["P01", "P02"])
        total = get_total_rounds(schedule)
        assert total >= 1

    def test_empty_schedule(self):
        """Empty schedule should have 0 rounds."""
        total = get_total_rounds([])
        assert total == 0


class TestScheduleToAnnouncementFormat:
    """Tests for schedule_to_announcement_format function."""

    def test_format_conversion(self):
        """Should convert to announcement format."""
        schedule = create_round_robin_schedule(["P01", "P02"])
        formatted = schedule_to_announcement_format(
            schedule,
            "http://localhost:8001/mcp",
        )

        assert len(formatted) == 1
        match = formatted[0]

        assert "match_id" in match
        assert "game_type" in match
        assert match["game_type"] == "even_odd"
        assert "player_A_id" in match
        assert "player_B_id" in match
        assert match["referee_endpoint"] == "http://localhost:8001/mcp"
