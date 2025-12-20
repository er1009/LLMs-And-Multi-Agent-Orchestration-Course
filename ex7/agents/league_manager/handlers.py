"""
Message handlers for the League Manager.

Handles all incoming MCP requests.
"""

from typing import Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SHARED.league_sdk.models import (
    MessageType,
    RegistrationStatus,
    utc_timestamp,
)
from SHARED.league_sdk.logger import JsonLogger

from .state import LeagueState
from .scheduler import create_round_robin_schedule


class LeagueHandlers:
    """Handlers for League Manager MCP methods."""

    def __init__(self, state: LeagueState, logger: JsonLogger):
        """Initialize handlers."""
        self.state = state
        self.logger = logger

    def handle_register_referee(
        self,
        params: dict[str, Any],
        request_id: int,
    ) -> dict[str, Any]:
        """Handle referee registration request."""
        referee_meta = params.get("referee_meta", {})

        self.logger.info(
            "REFEREE_REGISTRATION",
            display_name=referee_meta.get("display_name"),
            endpoint=referee_meta.get("contact_endpoint"),
        )

        try:
            referee = self.state.register_referee(
                display_name=referee_meta.get("display_name", "Unknown Referee"),
                endpoint=referee_meta.get("contact_endpoint", ""),
                version=referee_meta.get("version", "1.0.0"),
                game_types=referee_meta.get("game_types", ["even_odd"]),
                max_concurrent_matches=referee_meta.get("max_concurrent_matches", 2),
            )

            self.logger.info(
                "REFEREE_REGISTERED",
                referee_id=referee.referee_id,
            )

            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": MessageType.REFEREE_REGISTER_RESPONSE.value,
                    "sender": "league_manager",
                    "timestamp": utc_timestamp(),
                    "conversation_id": params.get("conversation_id", ""),
                    "status": RegistrationStatus.ACCEPTED.value,
                    "referee_id": referee.referee_id,
                    "auth_token": referee.auth_token,
                    "league_id": self.state.league_id,
                    "reason": None,
                },
                "id": request_id,
            }

        except Exception as e:
            self.logger.error("REFEREE_REGISTRATION_FAILED", error=str(e))
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": MessageType.REFEREE_REGISTER_RESPONSE.value,
                    "sender": "league_manager",
                    "timestamp": utc_timestamp(),
                    "conversation_id": params.get("conversation_id", ""),
                    "status": RegistrationStatus.REJECTED.value,
                    "referee_id": None,
                    "auth_token": None,
                    "league_id": self.state.league_id,
                    "reason": str(e),
                },
                "id": request_id,
            }

    def handle_register_player(
        self,
        params: dict[str, Any],
        request_id: int,
    ) -> dict[str, Any]:
        """Handle player registration request."""
        player_meta = params.get("player_meta", {})

        self.logger.info(
            "PLAYER_REGISTRATION",
            display_name=player_meta.get("display_name"),
            endpoint=player_meta.get("contact_endpoint"),
        )

        try:
            player = self.state.register_player(
                display_name=player_meta.get("display_name", "Unknown Player"),
                endpoint=player_meta.get("contact_endpoint", ""),
                version=player_meta.get("version", "1.0.0"),
                game_types=player_meta.get("game_types", ["even_odd"]),
            )

            self.logger.info(
                "PLAYER_REGISTERED",
                player_id=player.player_id,
            )

            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": MessageType.LEAGUE_REGISTER_RESPONSE.value,
                    "sender": "league_manager",
                    "timestamp": utc_timestamp(),
                    "conversation_id": params.get("conversation_id", ""),
                    "status": RegistrationStatus.ACCEPTED.value,
                    "player_id": player.player_id,
                    "auth_token": player.auth_token,
                    "league_id": self.state.league_id,
                    "reason": None,
                },
                "id": request_id,
            }

        except Exception as e:
            self.logger.error("PLAYER_REGISTRATION_FAILED", error=str(e))
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": MessageType.LEAGUE_REGISTER_RESPONSE.value,
                    "sender": "league_manager",
                    "timestamp": utc_timestamp(),
                    "conversation_id": params.get("conversation_id", ""),
                    "status": RegistrationStatus.REJECTED.value,
                    "player_id": None,
                    "auth_token": None,
                    "league_id": self.state.league_id,
                    "reason": str(e),
                },
                "id": request_id,
            }

    def handle_report_match_result(
        self,
        params: dict[str, Any],
        request_id: int,
    ) -> dict[str, Any]:
        """Handle match result report from referee."""
        match_id = params.get("match_id")
        result = params.get("result", {})
        round_id = params.get("round_id")

        self.logger.info(
            "MATCH_RESULT_RECEIVED",
            match_id=match_id,
            winner=result.get("winner"),
        )

        # Find the match in schedule
        for match in self.state.schedule:
            if match.match_id == match_id:
                match.status = "COMPLETED"
                match.winner = result.get("winner")
                match.result = result

                # Update standings
                self.state.update_standings_for_match(
                    match.player_a_id,
                    match.player_b_id,
                    result.get("winner"),
                )

                # Save match result
                self.state.save_match_result(match_id, {
                    "match_id": match_id,
                    "round_id": round_id,
                    "player_a_id": match.player_a_id,
                    "player_b_id": match.player_b_id,
                    "result": result,
                    "timestamp": utc_timestamp(),
                })
                break

        return {
            "jsonrpc": "2.0",
            "result": {
                "protocol": "league.v2",
                "message_type": "MATCH_RESULT_ACK",
                "sender": "league_manager",
                "timestamp": utc_timestamp(),
                "conversation_id": params.get("conversation_id", ""),
                "match_id": match_id,
                "status": "RECORDED",
            },
            "id": request_id,
        }

    def handle_league_query(
        self,
        params: dict[str, Any],
        request_id: int,
    ) -> dict[str, Any]:
        """Handle league query requests."""
        query_type = params.get("query_type", "GET_STANDINGS")

        if query_type == "GET_STANDINGS":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": MessageType.LEAGUE_QUERY_RESPONSE.value,
                    "sender": "league_manager",
                    "timestamp": utc_timestamp(),
                    "conversation_id": params.get("conversation_id", ""),
                    "league_id": self.state.league_id,
                    "query_type": query_type,
                    "standings": self.state.get_ranked_standings(),
                },
                "id": request_id,
            }

        elif query_type == "GET_SCHEDULE":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": MessageType.LEAGUE_QUERY_RESPONSE.value,
                    "sender": "league_manager",
                    "timestamp": utc_timestamp(),
                    "conversation_id": params.get("conversation_id", ""),
                    "league_id": self.state.league_id,
                    "query_type": query_type,
                    "schedule": [
                        {
                            "match_id": m.match_id,
                            "round_id": m.round_id,
                            "player_A_id": m.player_a_id,
                            "player_B_id": m.player_b_id,
                            "status": m.status,
                        }
                        for m in self.state.schedule
                    ],
                },
                "id": request_id,
            }

        elif query_type == "GET_PLAYER_STATS":
            player_id = params.get("query_params", {}).get("player_id")
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": MessageType.LEAGUE_QUERY_RESPONSE.value,
                    "sender": "league_manager",
                    "timestamp": utc_timestamp(),
                    "conversation_id": params.get("conversation_id", ""),
                    "league_id": self.state.league_id,
                    "query_type": query_type,
                    "player_id": player_id,
                    "stats": self.state.get_player_stats(player_id) if player_id else {},
                },
                "id": request_id,
            }

        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,
                "message": f"Unknown query type: {query_type}",
            },
            "id": request_id,
        }

    def create_schedule(self) -> list[dict[str, Any]]:
        """Create the tournament schedule."""
        player_ids = list(self.state.players.keys())
        self.state.schedule = create_round_robin_schedule(player_ids)

        self.logger.info(
            "SCHEDULE_CREATED",
            total_matches=len(self.state.schedule),
            players=len(player_ids),
        )

        return [
            {
                "match_id": m.match_id,
                "round_id": m.round_id,
                "player_A_id": m.player_a_id,
                "player_B_id": m.player_b_id,
            }
            for m in self.state.schedule
        ]
