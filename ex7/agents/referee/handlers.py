"""
Message handlers for the Referee.

Handles MCP communication with players and league manager.
"""

import uuid
from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SHARED.league_sdk.models import MessageType, GameStatus, utc_timestamp
from SHARED.league_sdk.http_client import MCPClient
from SHARED.league_sdk.logger import JsonLogger

from .state import RefereeState, MatchState
from .game_logic import (
    draw_number,
    determine_winner,
    validate_parity_choice,
    calculate_score,
)


class RefereeHandlers:
    """Handlers for Referee MCP operations."""

    def __init__(self, state: RefereeState, logger: JsonLogger):
        """Initialize handlers."""
        self.state = state
        self.logger = logger
        self.client = MCPClient()

    def register_to_league(self) -> bool:
        """Register with the league manager."""
        conversation_id = f"conv-ref-{uuid.uuid4().hex[:8]}"

        params = {
            "protocol": "league.v2",
            "message_type": MessageType.REFEREE_REGISTER_REQUEST.value,
            "sender": f"referee:{self.state.display_name.lower().replace(' ', '_')}",
            "timestamp": utc_timestamp(),
            "conversation_id": conversation_id,
            "referee_meta": {
                "display_name": self.state.display_name,
                "version": self.state.version,
                "game_types": self.state.game_types,
                "contact_endpoint": f"http://localhost:{self.state.port}/mcp",
                "max_concurrent_matches": self.state.max_concurrent_matches,
            },
        }

        self.logger.log_message(
            "SENT",
            MessageType.REFEREE_REGISTER_REQUEST.value,
            endpoint=self.state.league_endpoint,
        )

        response = self.client.call(
            self.state.league_endpoint,
            "register_referee",
            params,
            timeout=10,
        )

        if "error" in response:
            self.logger.error("REGISTRATION_FAILED", error=response["error"])
            return False

        result = response.get("result", {})

        if result.get("status") == "ACCEPTED":
            self.state.referee_id = result.get("referee_id")
            self.state.auth_token = result.get("auth_token")
            self.state.league_id = result.get("league_id")

            self.logger.info(
                "REGISTERED",
                referee_id=self.state.referee_id,
                league_id=self.state.league_id,
            )
            return True

        self.logger.error(
            "REGISTRATION_REJECTED",
            reason=result.get("reason"),
        )
        return False

    async def run_match(
        self,
        match_id: str,
        round_id: int,
        player_a_id: str,
        player_b_id: str,
        player_a_endpoint: str,
        player_b_endpoint: str,
    ) -> dict[str, Any]:
        """
        Run a complete match between two players.

        Returns match result.
        """
        conversation_id = f"conv-{match_id}-{uuid.uuid4().hex[:8]}"

        match = self.state.create_match(
            match_id=match_id,
            round_id=round_id,
            player_a_id=player_a_id,
            player_b_id=player_b_id,
            player_a_endpoint=player_a_endpoint,
            player_b_endpoint=player_b_endpoint,
            conversation_id=conversation_id,
        )

        self.logger.info(
            "MATCH_START",
            match_id=match_id,
            player_a=player_a_id,
            player_b=player_b_id,
        )

        # Step 1: Send game invitations
        invite_a = self._send_game_invitation(
            player_a_endpoint,
            match_id,
            round_id,
            player_a_id,
            player_b_id,
            "PLAYER_A",
            conversation_id,
        )
        invite_b = self._send_game_invitation(
            player_b_endpoint,
            match_id,
            round_id,
            player_b_id,
            player_a_id,
            "PLAYER_B",
            conversation_id,
        )

        # Check if both players accepted
        if not self._check_join_ack(invite_a, player_a_id, match_id):
            return self._handle_technical_loss(match, player_b_id, "Player A failed to join")
        if not self._check_join_ack(invite_b, player_b_id, match_id):
            return self._handle_technical_loss(match, player_a_id, "Player B failed to join")

        # Step 2: Request parity choices
        choice_a = self._request_parity_choice(
            player_a_endpoint,
            match_id,
            player_a_id,
            player_b_id,
            round_id,
            conversation_id,
        )
        choice_b = self._request_parity_choice(
            player_b_endpoint,
            match_id,
            player_b_id,
            player_a_id,
            round_id,
            conversation_id,
        )

        # Validate choices
        if not choice_a or not validate_parity_choice(choice_a):
            return self._handle_technical_loss(match, player_b_id, "Player A invalid choice")
        if not choice_b or not validate_parity_choice(choice_b):
            return self._handle_technical_loss(match, player_a_id, "Player B invalid choice")

        # Step 3: Draw number and determine winner
        number = draw_number()
        winner_role, parity, reason = determine_winner(choice_a, choice_b, number)

        # Convert role to player ID
        if winner_role == "PLAYER_A":
            winner_id = player_a_id
            status = GameStatus.WIN
        elif winner_role == "PLAYER_B":
            winner_id = player_b_id
            status = GameStatus.WIN
        else:
            winner_id = None
            status = GameStatus.DRAW

        match.drawn_number = number
        match.winner = winner_id
        match.state = MatchState.FINISHED

        self.logger.info(
            "MATCH_RESULT",
            match_id=match_id,
            number=number,
            parity=parity,
            winner=winner_id,
        )

        # Step 4: Send game over to both players
        game_result = {
            "status": status.value,
            "winner_player_id": winner_id,
            "drawn_number": number,
            "number_parity": parity,
            "choices": {
                player_a_id: choice_a,
                player_b_id: choice_b,
            },
            "reason": reason,
        }

        self._send_game_over(player_a_endpoint, match_id, game_result, conversation_id)
        self._send_game_over(player_b_endpoint, match_id, game_result, conversation_id)

        # Step 5: Report to league manager
        scores = calculate_score(winner_role, player_a_id, player_b_id)
        self._report_match_result(match_id, round_id, winner_id, scores, game_result)

        self.state.complete_match(match_id)

        return {
            "match_id": match_id,
            "winner": winner_id,
            "result": game_result,
        }

    def _send_game_invitation(
        self,
        endpoint: str,
        match_id: str,
        round_id: int,
        player_id: str,
        opponent_id: str,
        role: str,
        conversation_id: str,
    ) -> dict[str, Any]:
        """Send game invitation to a player."""
        params = {
            "protocol": "league.v2",
            "message_type": MessageType.GAME_INVITATION.value,
            "sender": f"referee:{self.state.referee_id}",
            "timestamp": utc_timestamp(),
            "conversation_id": conversation_id,
            "auth_token": self.state.auth_token,
            "league_id": self.state.league_id,
            "round_id": round_id,
            "match_id": match_id,
            "game_type": "even_odd",
            "role_in_match": role,
            "opponent_id": opponent_id,
        }

        self.logger.log_message(
            "SENT",
            MessageType.GAME_INVITATION.value,
            endpoint=endpoint,
            player_id=player_id,
        )

        return self.client.call(
            endpoint,
            "handle_game_invitation",
            params,
            timeout=5,
        )

    def _check_join_ack(
        self,
        response: dict[str, Any],
        player_id: str,
        match_id: str,
    ) -> bool:
        """Check if player accepted the game invitation."""
        if "error" in response:
            self.logger.warning(
                "JOIN_FAILED",
                player_id=player_id,
                error=response["error"],
            )
            return False

        result = response.get("result", {})
        if result.get("accept") and result.get("match_id") == match_id:
            self.state.player_joined(match_id, player_id)
            return True

        return False

    def _request_parity_choice(
        self,
        endpoint: str,
        match_id: str,
        player_id: str,
        opponent_id: str,
        round_id: int,
        conversation_id: str,
    ) -> str | None:
        """Request parity choice from a player."""
        params = {
            "protocol": "league.v2",
            "message_type": MessageType.CHOOSE_PARITY_CALL.value,
            "sender": f"referee:{self.state.referee_id}",
            "timestamp": utc_timestamp(),
            "conversation_id": conversation_id,
            "auth_token": self.state.auth_token,
            "match_id": match_id,
            "player_id": player_id,
            "game_type": "even_odd",
            "context": {
                "opponent_id": opponent_id,
                "round_id": round_id,
                "your_standings": {"wins": 0, "losses": 0, "draws": 0},
            },
            "deadline": utc_timestamp(),
        }

        self.logger.log_message(
            "SENT",
            MessageType.CHOOSE_PARITY_CALL.value,
            endpoint=endpoint,
            player_id=player_id,
        )

        response = self.client.call(
            endpoint,
            "choose_parity",
            params,
            timeout=30,
        )

        if "error" in response:
            self.logger.warning(
                "CHOICE_FAILED",
                player_id=player_id,
                error=response["error"],
            )
            return None

        result = response.get("result", {})
        choice = result.get("parity_choice")

        if choice:
            self.state.record_choice(match_id, player_id, choice)

        return choice

    def _send_game_over(
        self,
        endpoint: str,
        match_id: str,
        game_result: dict[str, Any],
        conversation_id: str,
    ) -> None:
        """Send game over notification to a player."""
        params = {
            "protocol": "league.v2",
            "message_type": MessageType.GAME_OVER.value,
            "sender": f"referee:{self.state.referee_id}",
            "timestamp": utc_timestamp(),
            "conversation_id": conversation_id,
            "auth_token": self.state.auth_token,
            "match_id": match_id,
            "game_type": "even_odd",
            "game_result": game_result,
        }

        self.logger.log_message(
            "SENT",
            MessageType.GAME_OVER.value,
            endpoint=endpoint,
        )

        # Fire and forget (don't wait for response)
        self.client.call_no_retry(
            endpoint,
            "notify_match_result",
            params,
            timeout=5,
        )

    def _report_match_result(
        self,
        match_id: str,
        round_id: int,
        winner: str | None,
        scores: dict[str, int],
        game_result: dict[str, Any],
    ) -> None:
        """Report match result to league manager."""
        conversation_id = f"conv-{match_id}-report"

        params = {
            "protocol": "league.v2",
            "message_type": MessageType.MATCH_RESULT_REPORT.value,
            "sender": f"referee:{self.state.referee_id}",
            "timestamp": utc_timestamp(),
            "conversation_id": conversation_id,
            "auth_token": self.state.auth_token,
            "league_id": self.state.league_id,
            "round_id": round_id,
            "match_id": match_id,
            "game_type": "even_odd",
            "result": {
                "winner": winner,
                "score": scores,
                "details": {
                    "drawn_number": game_result.get("drawn_number"),
                    "choices": game_result.get("choices"),
                },
            },
        }

        self.logger.log_message(
            "SENT",
            MessageType.MATCH_RESULT_REPORT.value,
            endpoint=self.state.league_endpoint,
        )

        self.client.call(
            self.state.league_endpoint,
            "report_match_result",
            params,
            timeout=10,
        )

    def _handle_technical_loss(
        self,
        match: Any,
        winner_id: str,
        reason: str,
    ) -> dict[str, Any]:
        """Handle technical loss scenario."""
        self.logger.warning(
            "TECHNICAL_LOSS",
            match_id=match.match_id,
            winner=winner_id,
            reason=reason,
        )

        match.winner = winner_id
        match.state = MatchState.FINISHED

        game_result = {
            "status": GameStatus.TECHNICAL_LOSS.value,
            "winner_player_id": winner_id,
            "drawn_number": 0,
            "number_parity": "N/A",
            "choices": {},
            "reason": reason,
        }

        # Report technical loss
        scores = {match.player_a_id: 0, match.player_b_id: 0}
        scores[winner_id] = 3

        self._report_match_result(
            match.match_id,
            match.round_id,
            winner_id,
            scores,
            game_result,
        )

        self.state.complete_match(match.match_id)

        return {
            "match_id": match.match_id,
            "winner": winner_id,
            "result": game_result,
        }
