"""
Pydantic models for all MCP message types in the League Protocol v2.

All messages follow JSON-RPC 2.0 format with a standardized envelope.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """All supported message types in the league protocol."""

    # Registration
    REFEREE_REGISTER_REQUEST = "REFEREE_REGISTER_REQUEST"
    REFEREE_REGISTER_RESPONSE = "REFEREE_REGISTER_RESPONSE"
    LEAGUE_REGISTER_REQUEST = "LEAGUE_REGISTER_REQUEST"
    LEAGUE_REGISTER_RESPONSE = "LEAGUE_REGISTER_RESPONSE"

    # Round Management
    ROUND_ANNOUNCEMENT = "ROUND_ANNOUNCEMENT"
    ROUND_COMPLETED = "ROUND_COMPLETED"

    # Game Flow
    GAME_INVITATION = "GAME_INVITATION"
    GAME_JOIN_ACK = "GAME_JOIN_ACK"
    CHOOSE_PARITY_CALL = "CHOOSE_PARITY_CALL"
    CHOOSE_PARITY_RESPONSE = "CHOOSE_PARITY_RESPONSE"
    GAME_OVER = "GAME_OVER"
    MATCH_RESULT_REPORT = "MATCH_RESULT_REPORT"

    # Standings
    LEAGUE_STANDINGS_UPDATE = "LEAGUE_STANDINGS_UPDATE"
    LEAGUE_COMPLETED = "LEAGUE_COMPLETED"

    # Query
    LEAGUE_QUERY = "LEAGUE_QUERY"
    LEAGUE_QUERY_RESPONSE = "LEAGUE_QUERY_RESPONSE"

    # Errors
    LEAGUE_ERROR = "LEAGUE_ERROR"
    GAME_ERROR = "GAME_ERROR"


class RegistrationStatus(str, Enum):
    """Registration response status."""
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class GameStatus(str, Enum):
    """Game result status."""
    WIN = "WIN"
    DRAW = "DRAW"
    TECHNICAL_LOSS = "TECHNICAL_LOSS"


class ParityChoice(str, Enum):
    """Valid parity choices for the Even/Odd game."""
    EVEN = "even"
    ODD = "odd"


def utc_timestamp() -> str:
    """Generate current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class MCPEnvelope(BaseModel):
    """Base envelope for all MCP messages."""

    protocol: str = "league.v2"
    message_type: str
    sender: str  # Format: "type:id" (e.g., "player:P01")
    timestamp: str = Field(default_factory=utc_timestamp)
    conversation_id: str
    auth_token: Optional[str] = None
    league_id: Optional[str] = None
    round_id: Optional[int] = None
    match_id: Optional[str] = None


class MCPRequest(BaseModel):
    """JSON-RPC 2.0 request wrapper."""

    jsonrpc: str = "2.0"
    method: str
    params: dict = Field(default_factory=dict)
    id: int = 1


class MCPResponse(BaseModel):
    """JSON-RPC 2.0 response wrapper."""

    jsonrpc: str = "2.0"
    result: dict = Field(default_factory=dict)
    id: int = 1


class MCPError(BaseModel):
    """JSON-RPC 2.0 error wrapper."""

    jsonrpc: str = "2.0"
    error: dict
    id: int = 1


# Registration Models

class RefereeMeta(BaseModel):
    """Referee metadata for registration."""

    display_name: str
    version: str = "1.0.0"
    game_types: list[str] = ["even_odd"]
    contact_endpoint: str
    max_concurrent_matches: int = 2


class PlayerMeta(BaseModel):
    """Player metadata for registration."""

    display_name: str
    version: str = "1.0.0"
    game_types: list[str] = ["even_odd"]
    contact_endpoint: str


# Game Models

class PlayerStanding(BaseModel):
    """Player standing in the league."""

    rank: int
    player_id: str
    display_name: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0


class MatchInfo(BaseModel):
    """Match information for scheduling."""

    match_id: str
    game_type: str = "even_odd"
    player_A_id: str
    player_B_id: str
    referee_endpoint: Optional[str] = None


class GameChoices(BaseModel):
    """Player choices in a game."""

    player_a: str
    player_b: str


class GameResult(BaseModel):
    """Result of a completed game."""

    status: GameStatus
    winner_player_id: Optional[str] = None
    drawn_number: int
    number_parity: str
    choices: dict[str, str]
    reason: str


class MatchResult(BaseModel):
    """Match result for reporting to league manager."""

    winner: Optional[str] = None
    score: dict[str, int]
    details: dict[str, Any]


# Context Models

class PlayerContext(BaseModel):
    """Context information provided to player during parity choice."""

    opponent_id: str
    round_id: int
    your_standings: dict[str, int]


class RetryInfo(BaseModel):
    """Retry information for error handling."""

    retry_count: int
    max_retries: int = 3
    next_retry_at: Optional[str] = None


# Error Models

class ErrorCode(str, Enum):
    """Standard error codes."""

    TIMEOUT_ERROR = "E001"
    MISSING_REQUIRED_FIELD = "E003"
    INVALID_PARITY_CHOICE = "E004"
    PLAYER_NOT_REGISTERED = "E005"
    CONNECTION_ERROR = "E009"
    AUTH_TOKEN_MISSING = "E011"
    AUTH_TOKEN_INVALID = "E012"
    REFEREE_NOT_REGISTERED = "E013"
    PROTOCOL_VERSION_MISMATCH = "E018"
    INVALID_TIMESTAMP = "E021"
