"""
Tests for Pydantic models.
"""

import pytest
from datetime import datetime, timezone

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from SHARED.league_sdk.models import (
    MCPEnvelope,
    MCPRequest,
    MCPResponse,
    MessageType,
    RegistrationStatus,
    GameStatus,
    ParityChoice,
    utc_timestamp,
    RefereeMeta,
    PlayerMeta,
    PlayerStanding,
    MatchInfo,
    GameResult,
)


class TestUtcTimestamp:
    """Tests for utc_timestamp function."""

    def test_format(self):
        """Timestamp should be in correct format."""
        ts = utc_timestamp()
        # Should end with Z
        assert ts.endswith("Z")
        # Should be parseable
        datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")

    def test_is_utc(self):
        """Timestamp should be in UTC."""
        ts = utc_timestamp()
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
        # Should be close to current UTC time
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        assert abs((dt - now).total_seconds()) < 5


class TestMCPEnvelope:
    """Tests for MCPEnvelope model."""

    def test_default_protocol(self):
        """Protocol should default to 'league.v2'."""
        envelope = MCPEnvelope(
            message_type="TEST",
            sender="test:001",
            conversation_id="conv-001",
        )
        assert envelope.protocol == "league.v2"

    def test_timestamp_auto_generated(self):
        """Timestamp should be auto-generated."""
        envelope = MCPEnvelope(
            message_type="TEST",
            sender="test:001",
            conversation_id="conv-001",
        )
        assert envelope.timestamp.endswith("Z")

    def test_optional_fields(self):
        """Optional fields should default to None."""
        envelope = MCPEnvelope(
            message_type="TEST",
            sender="test:001",
            conversation_id="conv-001",
        )
        assert envelope.auth_token is None
        assert envelope.league_id is None
        assert envelope.round_id is None
        assert envelope.match_id is None


class TestMCPRequest:
    """Tests for MCPRequest model."""

    def test_default_jsonrpc(self):
        """jsonrpc should default to '2.0'."""
        request = MCPRequest(method="test_method")
        assert request.jsonrpc == "2.0"

    def test_default_params(self):
        """params should default to empty dict."""
        request = MCPRequest(method="test_method")
        assert request.params == {}

    def test_default_id(self):
        """id should default to 1."""
        request = MCPRequest(method="test_method")
        assert request.id == 1


class TestMCPResponse:
    """Tests for MCPResponse model."""

    def test_default_jsonrpc(self):
        """jsonrpc should default to '2.0'."""
        response = MCPResponse()
        assert response.jsonrpc == "2.0"

    def test_default_result(self):
        """result should default to empty dict."""
        response = MCPResponse()
        assert response.result == {}


class TestEnums:
    """Tests for enum values."""

    def test_message_types(self):
        """MessageType enum should have expected values."""
        assert MessageType.REFEREE_REGISTER_REQUEST.value == "REFEREE_REGISTER_REQUEST"
        assert MessageType.LEAGUE_REGISTER_REQUEST.value == "LEAGUE_REGISTER_REQUEST"
        assert MessageType.GAME_INVITATION.value == "GAME_INVITATION"
        assert MessageType.CHOOSE_PARITY_CALL.value == "CHOOSE_PARITY_CALL"
        assert MessageType.GAME_OVER.value == "GAME_OVER"

    def test_registration_status(self):
        """RegistrationStatus enum should have expected values."""
        assert RegistrationStatus.ACCEPTED.value == "ACCEPTED"
        assert RegistrationStatus.REJECTED.value == "REJECTED"

    def test_game_status(self):
        """GameStatus enum should have expected values."""
        assert GameStatus.WIN.value == "WIN"
        assert GameStatus.DRAW.value == "DRAW"
        assert GameStatus.TECHNICAL_LOSS.value == "TECHNICAL_LOSS"

    def test_parity_choice(self):
        """ParityChoice enum should have lowercase values."""
        assert ParityChoice.EVEN.value == "even"
        assert ParityChoice.ODD.value == "odd"


class TestRefereeMeta:
    """Tests for RefereeMeta model."""

    def test_default_values(self):
        """RefereeMeta should have sensible defaults."""
        meta = RefereeMeta(
            display_name="Test Referee",
            contact_endpoint="http://localhost:8001/mcp",
        )
        assert meta.version == "1.0.0"
        assert meta.game_types == ["even_odd"]
        assert meta.max_concurrent_matches == 2


class TestPlayerMeta:
    """Tests for PlayerMeta model."""

    def test_default_values(self):
        """PlayerMeta should have sensible defaults."""
        meta = PlayerMeta(
            display_name="Test Player",
            contact_endpoint="http://localhost:8101/mcp",
        )
        assert meta.version == "1.0.0"
        assert meta.game_types == ["even_odd"]


class TestPlayerStanding:
    """Tests for PlayerStanding model."""

    def test_default_values(self):
        """PlayerStanding should have zero defaults."""
        standing = PlayerStanding(
            rank=1,
            player_id="P01",
            display_name="Test Player",
        )
        assert standing.played == 0
        assert standing.wins == 0
        assert standing.draws == 0
        assert standing.losses == 0
        assert standing.points == 0


class TestMatchInfo:
    """Tests for MatchInfo model."""

    def test_default_game_type(self):
        """MatchInfo should default to even_odd."""
        match = MatchInfo(
            match_id="R1M1",
            player_A_id="P01",
            player_B_id="P02",
        )
        assert match.game_type == "even_odd"
        assert match.referee_endpoint is None
