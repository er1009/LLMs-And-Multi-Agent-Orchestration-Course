"""
Referee state management.

Tracks active matches and their states.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MatchState(str, Enum):
    """Match state machine states."""

    WAITING_FOR_PLAYERS = "WAITING_FOR_PLAYERS"
    COLLECTING_CHOICES = "COLLECTING_CHOICES"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


@dataclass
class ActiveMatch:
    """State of an active match."""

    match_id: str
    round_id: int
    player_a_id: str
    player_b_id: str
    player_a_endpoint: str
    player_b_endpoint: str
    state: MatchState = MatchState.WAITING_FOR_PLAYERS
    player_a_joined: bool = False
    player_b_joined: bool = False
    player_a_choice: str | None = None
    player_b_choice: str | None = None
    drawn_number: int | None = None
    winner: str | None = None
    conversation_id: str = ""


@dataclass
class RefereeState:
    """Manages the state of the referee."""

    referee_id: str | None = None
    auth_token: str | None = None
    league_id: str | None = None
    league_endpoint: str = "http://localhost:8000/mcp"
    display_name: str = "Referee"
    version: str = "1.0.0"
    game_types: list[str] = field(default_factory=lambda: ["even_odd"])
    max_concurrent_matches: int = 2

    # Active matches
    active_matches: dict[str, ActiveMatch] = field(default_factory=dict)

    def is_registered(self) -> bool:
        """Check if referee is registered."""
        return self.referee_id is not None and self.auth_token is not None

    def create_match(
        self,
        match_id: str,
        round_id: int,
        player_a_id: str,
        player_b_id: str,
        player_a_endpoint: str,
        player_b_endpoint: str,
        conversation_id: str,
    ) -> ActiveMatch:
        """Create a new active match."""
        match = ActiveMatch(
            match_id=match_id,
            round_id=round_id,
            player_a_id=player_a_id,
            player_b_id=player_b_id,
            player_a_endpoint=player_a_endpoint,
            player_b_endpoint=player_b_endpoint,
            conversation_id=conversation_id,
        )
        self.active_matches[match_id] = match
        return match

    def get_match(self, match_id: str) -> ActiveMatch | None:
        """Get an active match by ID."""
        return self.active_matches.get(match_id)

    def complete_match(self, match_id: str) -> None:
        """Remove match from active matches."""
        if match_id in self.active_matches:
            del self.active_matches[match_id]

    def player_joined(self, match_id: str, player_id: str) -> bool:
        """Record that a player has joined the match."""
        match = self.get_match(match_id)
        if not match:
            return False

        if player_id == match.player_a_id:
            match.player_a_joined = True
        elif player_id == match.player_b_id:
            match.player_b_joined = True
        else:
            return False

        # Check if both players joined
        if match.player_a_joined and match.player_b_joined:
            match.state = MatchState.COLLECTING_CHOICES

        return True

    def record_choice(self, match_id: str, player_id: str, choice: str) -> bool:
        """Record a player's parity choice."""
        match = self.get_match(match_id)
        if not match:
            return False

        if player_id == match.player_a_id:
            match.player_a_choice = choice
        elif player_id == match.player_b_id:
            match.player_b_choice = choice
        else:
            return False

        return True

    def both_choices_received(self, match_id: str) -> bool:
        """Check if both players have made their choices."""
        match = self.get_match(match_id)
        if not match:
            return False
        return match.player_a_choice is not None and match.player_b_choice is not None
