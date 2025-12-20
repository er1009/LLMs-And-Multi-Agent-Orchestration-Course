"""
League state management.

Handles in-memory state and JSON persistence for the league.
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SHARED.league_sdk.config_loader import DataLoader
from SHARED.league_sdk.models import utc_timestamp


@dataclass
class RegisteredReferee:
    """Registered referee information."""

    referee_id: str
    display_name: str
    endpoint: str
    auth_token: str
    version: str = "1.0.0"
    game_types: list[str] = field(default_factory=lambda: ["even_odd"])
    max_concurrent_matches: int = 2
    active_matches: int = 0


@dataclass
class RegisteredPlayer:
    """Registered player information."""

    player_id: str
    display_name: str
    endpoint: str
    auth_token: str
    version: str = "1.0.0"
    game_types: list[str] = field(default_factory=lambda: ["even_odd"])


@dataclass
class PlayerStanding:
    """Player standing in the league."""

    player_id: str
    display_name: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0

    def to_dict(self, rank: int) -> dict[str, Any]:
        """Convert to dictionary with rank."""
        return {
            "rank": rank,
            "player_id": self.player_id,
            "display_name": self.display_name,
            "played": self.played,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "points": self.points,
        }


@dataclass
class Match:
    """Match information."""

    match_id: str
    round_id: int
    player_a_id: str
    player_b_id: str
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED
    winner: str | None = None
    result: dict[str, Any] | None = None


class LeagueState:
    """Manages the state of the league."""

    def __init__(self, league_id: str, data_root: str = "SHARED/data"):
        """Initialize league state."""
        self.league_id = league_id
        self.data_loader = DataLoader(data_root)

        # Registration state
        self.referees: dict[str, RegisteredReferee] = {}
        self.players: dict[str, RegisteredPlayer] = {}
        self.auth_tokens: dict[str, str] = {}  # token -> agent_id

        # League state
        self.standings: dict[str, PlayerStanding] = {}
        self.schedule: list[Match] = []
        self.current_round: int = 0
        self.rounds_completed: int = 0

        # ID counters
        self._next_referee_num = 1
        self._next_player_num = 1

    def generate_auth_token(self) -> str:
        """Generate a secure auth token."""
        return f"tok-{secrets.token_hex(16)}"

    def register_referee(
        self,
        display_name: str,
        endpoint: str,
        version: str = "1.0.0",
        game_types: list[str] | None = None,
        max_concurrent_matches: int = 2,
    ) -> RegisteredReferee:
        """Register a new referee."""
        referee_id = f"REF{self._next_referee_num:02d}"
        self._next_referee_num += 1

        auth_token = self.generate_auth_token()

        referee = RegisteredReferee(
            referee_id=referee_id,
            display_name=display_name,
            endpoint=endpoint,
            auth_token=auth_token,
            version=version,
            game_types=game_types or ["even_odd"],
            max_concurrent_matches=max_concurrent_matches,
        )

        self.referees[referee_id] = referee
        self.auth_tokens[auth_token] = referee_id

        return referee

    def register_player(
        self,
        display_name: str,
        endpoint: str,
        version: str = "1.0.0",
        game_types: list[str] | None = None,
    ) -> RegisteredPlayer:
        """Register a new player."""
        player_id = f"P{self._next_player_num:02d}"
        self._next_player_num += 1

        auth_token = self.generate_auth_token()

        player = RegisteredPlayer(
            player_id=player_id,
            display_name=display_name,
            endpoint=endpoint,
            auth_token=auth_token,
            version=version,
            game_types=game_types or ["even_odd"],
        )

        self.players[player_id] = player
        self.auth_tokens[auth_token] = player_id

        # Initialize standings
        self.standings[player_id] = PlayerStanding(
            player_id=player_id,
            display_name=display_name,
        )

        return player

    def validate_auth_token(self, token: str) -> str | None:
        """Validate auth token and return agent ID."""
        return self.auth_tokens.get(token)

    def get_player_endpoint(self, player_id: str) -> str | None:
        """Get player endpoint by ID."""
        player = self.players.get(player_id)
        return player.endpoint if player else None

    def get_available_referee(self) -> RegisteredReferee | None:
        """Get an available referee for a match."""
        for referee in self.referees.values():
            if referee.active_matches < referee.max_concurrent_matches:
                return referee
        return None

    def update_standings_for_match(
        self,
        player_a_id: str,
        player_b_id: str,
        winner: str | None,
    ) -> None:
        """Update standings after a match."""
        standing_a = self.standings.get(player_a_id)
        standing_b = self.standings.get(player_b_id)

        if not standing_a or not standing_b:
            return

        standing_a.played += 1
        standing_b.played += 1

        if winner is None:
            # Draw
            standing_a.draws += 1
            standing_b.draws += 1
            standing_a.points += 1
            standing_b.points += 1
        elif winner == player_a_id:
            standing_a.wins += 1
            standing_a.points += 3
            standing_b.losses += 1
        else:
            standing_b.wins += 1
            standing_b.points += 3
            standing_a.losses += 1

        self._save_standings()

    def get_ranked_standings(self) -> list[dict[str, Any]]:
        """Get standings sorted by points."""
        sorted_standings = sorted(
            self.standings.values(),
            key=lambda s: (-s.points, -s.wins, -s.draws),
        )
        return [s.to_dict(rank + 1) for rank, s in enumerate(sorted_standings)]

    def _save_standings(self) -> None:
        """Persist standings to disk."""
        data = {
            "schema_version": "1.0.0",
            "league_id": self.league_id,
            "last_updated": utc_timestamp(),
            "rounds_completed": self.rounds_completed,
            "standings": self.get_ranked_standings(),
        }
        self.data_loader.save_standings(self.league_id, data)

    def save_match_result(
        self,
        match_id: str,
        result: dict[str, Any],
    ) -> None:
        """Save match result to disk."""
        self.data_loader.save_match(self.league_id, match_id, result)

    def get_player_stats(self, player_id: str) -> dict[str, int]:
        """Get player statistics."""
        standing = self.standings.get(player_id)
        if not standing:
            return {"wins": 0, "losses": 0, "draws": 0}
        return {
            "wins": standing.wins,
            "losses": standing.losses,
            "draws": standing.draws,
        }
