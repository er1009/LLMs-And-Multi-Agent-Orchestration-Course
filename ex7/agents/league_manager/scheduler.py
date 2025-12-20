"""
Round-robin tournament scheduler.

Creates a schedule where every player plays against every other player.
"""

from itertools import combinations
from typing import Any

from .state import Match


def create_round_robin_schedule(player_ids: list[str]) -> list[Match]:
    """
    Create a round-robin schedule for all players.

    Each player plays against every other player exactly once.

    Args:
        player_ids: List of player IDs

    Returns:
        List of Match objects
    """
    matches = []
    match_num = 1

    # Generate all pairs
    for p1, p2 in combinations(player_ids, 2):
        # Assign to rounds (2 matches per round for 4 players)
        round_id = (match_num - 1) // 2 + 1

        match = Match(
            match_id=f"R{round_id}M{match_num}",
            round_id=round_id,
            player_a_id=p1,
            player_b_id=p2,
        )
        matches.append(match)
        match_num += 1

    return matches


def get_matches_for_round(
    schedule: list[Match],
    round_id: int,
) -> list[Match]:
    """Get all matches for a specific round."""
    return [m for m in schedule if m.round_id == round_id]


def get_total_rounds(schedule: list[Match]) -> int:
    """Get total number of rounds in the schedule."""
    if not schedule:
        return 0
    return max(m.round_id for m in schedule)


def schedule_to_announcement_format(
    matches: list[Match],
    referee_endpoint: str,
) -> list[dict[str, Any]]:
    """Convert matches to ROUND_ANNOUNCEMENT format."""
    return [
        {
            "match_id": m.match_id,
            "game_type": "even_odd",
            "player_A_id": m.player_a_id,
            "player_B_id": m.player_b_id,
            "referee_endpoint": referee_endpoint,
        }
        for m in matches
    ]
