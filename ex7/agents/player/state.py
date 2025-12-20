"""
Player state management.

Tracks registration, game history, and statistics.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameRecord:
    """Record of a completed game."""

    match_id: str
    opponent_id: str
    my_choice: str
    opponent_choice: str | None
    drawn_number: int
    result: str  # WIN, LOSS, DRAW
    points_earned: int


@dataclass
class PlayerState:
    """Manages the state of a player."""

    display_name: str = "Player"
    version: str = "1.0.0"
    game_types: list[str] = field(default_factory=lambda: ["even_odd"])
    strategy: str = "random"

    # Registration state
    player_id: str | None = None
    auth_token: str | None = None
    league_id: str | None = None
    league_endpoint: str = "http://localhost:8000/mcp"
    port: int = 8101

    # Statistics
    wins: int = 0
    losses: int = 0
    draws: int = 0
    points: int = 0

    # Game history
    history: list[GameRecord] = field(default_factory=list)

    # Current game state
    current_match_id: str | None = None
    current_opponent: str | None = None

    def is_registered(self) -> bool:
        """Check if player is registered."""
        return self.player_id is not None and self.auth_token is not None

    def record_game(
        self,
        match_id: str,
        opponent_id: str,
        my_choice: str,
        opponent_choice: str | None,
        drawn_number: int,
        winner_id: str | None,
    ) -> None:
        """Record a completed game."""
        if winner_id == self.player_id:
            result = "WIN"
            points = 3
            self.wins += 1
        elif winner_id is None:
            result = "DRAW"
            points = 1
            self.draws += 1
        else:
            result = "LOSS"
            points = 0
            self.losses += 1

        self.points += points

        record = GameRecord(
            match_id=match_id,
            opponent_id=opponent_id,
            my_choice=my_choice,
            opponent_choice=opponent_choice,
            drawn_number=drawn_number,
            result=result,
            points_earned=points,
        )
        self.history.append(record)

    def get_stats(self) -> dict[str, int]:
        """Get player statistics."""
        return {
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "points": self.points,
            "games_played": len(self.history),
        }

    def get_win_rate(self) -> float:
        """Calculate win rate."""
        total = len(self.history)
        if total == 0:
            return 0.0
        return self.wins / total

    def get_opponent_history(self, opponent_id: str) -> list[GameRecord]:
        """Get history of games against a specific opponent."""
        return [g for g in self.history if g.opponent_id == opponent_id]
