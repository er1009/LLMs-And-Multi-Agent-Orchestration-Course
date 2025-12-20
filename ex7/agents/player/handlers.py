"""
Message handlers for the Player.

Handles MCP communication with referees and league manager.
"""

import uuid
from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SHARED.league_sdk.models import MessageType, utc_timestamp
from SHARED.league_sdk.http_client import MCPClient
from SHARED.league_sdk.logger import JsonLogger

from .state import PlayerState
from .strategy import make_choice


class PlayerHandlers:
    """Handlers for Player MCP operations."""

    def __init__(self, state: PlayerState, logger: JsonLogger):
        """Initialize handlers."""
        self.state = state
        self.logger = logger
        self.client = MCPClient()

    def register_to_league(self) -> bool:
        """Register with the league manager."""
        conversation_id = f"conv-player-{uuid.uuid4().hex[:8]}"

        params = {
            "protocol": "league.v2",
            "message_type": MessageType.LEAGUE_REGISTER_REQUEST.value,
            "sender": f"player:{self.state.display_name.lower().replace(' ', '_')}",
            "timestamp": utc_timestamp(),
            "conversation_id": conversation_id,
            "player_meta": {
                "display_name": self.state.display_name,
                "version": self.state.version,
                "game_types": self.state.game_types,
                "contact_endpoint": f"http://localhost:{self.state.port}/mcp",
            },
        }

        self.logger.log_message(
            "SENT",
            MessageType.LEAGUE_REGISTER_REQUEST.value,
            endpoint=self.state.league_endpoint,
        )

        response = self.client.call(
            self.state.league_endpoint,
            "register_player",
            params,
            timeout=10,
        )

        if "error" in response:
            self.logger.error("REGISTRATION_FAILED", error=response["error"])
            return False

        result = response.get("result", {})

        if result.get("status") == "ACCEPTED":
            self.state.player_id = result.get("player_id")
            self.state.auth_token = result.get("auth_token")
            self.state.league_id = result.get("league_id")

            self.logger.info(
                "REGISTERED",
                player_id=self.state.player_id,
                league_id=self.state.league_id,
            )
            return True

        self.logger.error(
            "REGISTRATION_REJECTED",
            reason=result.get("reason"),
        )
        return False

    def handle_game_invitation(
        self,
        params: dict[str, Any],
        request_id: int,
    ) -> dict[str, Any]:
        """Handle game invitation from referee."""
        match_id = params.get("match_id")
        opponent_id = params.get("opponent_id")
        round_id = params.get("round_id")
        role = params.get("role_in_match")

        self.logger.info(
            "GAME_INVITATION",
            match_id=match_id,
            opponent=opponent_id,
            role=role,
        )

        # Store current game info
        self.state.current_match_id = match_id
        self.state.current_opponent = opponent_id

        # Always accept game invitations
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocol": "league.v2",
                "message_type": MessageType.GAME_JOIN_ACK.value,
                "sender": f"player:{self.state.player_id}",
                "timestamp": utc_timestamp(),
                "conversation_id": params.get("conversation_id", ""),
                "auth_token": self.state.auth_token,
                "match_id": match_id,
                "player_id": self.state.player_id,
                "arrival_timestamp": utc_timestamp(),
                "accept": True,
            },
            "id": request_id,
        }

    def handle_choose_parity(
        self,
        params: dict[str, Any],
        request_id: int,
    ) -> dict[str, Any]:
        """Handle parity choice request from referee."""
        match_id = params.get("match_id")
        context = params.get("context", {})

        # Make choice using strategy
        choice = make_choice(self.state, context)

        self.logger.info(
            "PARITY_CHOICE",
            match_id=match_id,
            choice=choice,
            strategy=self.state.strategy,
        )

        return {
            "jsonrpc": "2.0",
            "result": {
                "protocol": "league.v2",
                "message_type": MessageType.CHOOSE_PARITY_RESPONSE.value,
                "sender": f"player:{self.state.player_id}",
                "timestamp": utc_timestamp(),
                "conversation_id": params.get("conversation_id", ""),
                "auth_token": self.state.auth_token,
                "match_id": match_id,
                "player_id": self.state.player_id,
                "parity_choice": choice,
            },
            "id": request_id,
        }

    def handle_match_result(
        self,
        params: dict[str, Any],
        request_id: int,
    ) -> dict[str, Any]:
        """Handle match result notification from referee."""
        match_id = params.get("match_id")
        game_result = params.get("game_result", {})

        winner_id = game_result.get("winner_player_id")
        drawn_number = game_result.get("drawn_number", 0)
        choices = game_result.get("choices", {})

        my_choice = choices.get(self.state.player_id, "")
        opponent_choice = None

        # Find opponent's choice
        for pid, choice in choices.items():
            if pid != self.state.player_id:
                opponent_choice = choice
                opponent_id = pid
                break
        else:
            opponent_id = self.state.current_opponent

        # Record the game
        self.state.record_game(
            match_id=match_id,
            opponent_id=opponent_id,
            my_choice=my_choice,
            opponent_choice=opponent_choice,
            drawn_number=drawn_number,
            winner_id=winner_id,
        )

        result = "WIN" if winner_id == self.state.player_id else "DRAW" if winner_id is None else "LOSS"

        self.logger.info(
            "MATCH_RESULT",
            match_id=match_id,
            result=result,
            my_choice=my_choice,
            opponent_choice=opponent_choice,
            drawn_number=drawn_number,
            stats=self.state.get_stats(),
        )

        # Clear current game
        self.state.current_match_id = None
        self.state.current_opponent = None

        return {
            "jsonrpc": "2.0",
            "result": {
                "status": "acknowledged",
            },
            "id": request_id,
        }
