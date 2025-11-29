"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock
from src.utils.claude_client import ClaudeClient


@pytest.fixture
def mock_claude_client():
    """Create a mock Claude client for testing."""
    client = Mock(spec=ClaudeClient)
    client.call.return_value = "Mock response"
    client.check_availability.return_value = True
    return client


@pytest.fixture
def sample_route_data():
    """Sample Google Maps API response data."""
    return {
        "routes": [{
            "legs": [{
                "start_address": "New York, NY, USA",
                "end_address": "Boston, MA, USA",
                "start_location": {"lat": 40.7128, "lng": -74.0060},
                "end_location": {"lat": 42.3601, "lng": -71.0589},
                "distance": {"value": 346000, "text": "346 km"},
                "duration": {"value": 13500, "text": "3 hours 45 mins"},
                "steps": [
                    {
                        "distance": {"value": 1000, "text": "1 km"},
                        "duration": {"value": 120, "text": "2 mins"},
                        "end_location": {"lat": 40.7138, "lng": -74.0050},
                        "html_instructions": "Head north on Broadway",
                        "maneuver": "straight"
                    },
                    {
                        "distance": {"value": 50000, "text": "50 km"},
                        "duration": {"value": 3000, "text": "50 mins"},
                        "end_location": {"lat": 41.0, "lng": -73.5},
                        "html_instructions": "Take exit 15 toward I-95 N",
                        "maneuver": "exit"
                    }
                ]
            }],
            "summary": "I-95 N",
            "warnings": [],
            "waypoint_order": []
        }],
        "status": "OK"
    }


@pytest.fixture
def sample_agent_results():
    """Sample agent results for testing."""
    from src.agents.base_agent import AgentResult

    video = AgentResult(
        agent_type="video",
        title="Test Video",
        content="https://youtube.com/test",
        metadata={"description": "Test description"},
        success=True
    )

    music = AgentResult(
        agent_type="music",
        title="Test Song - Artist",
        content="https://spotify.com/test",
        metadata={"artist": "Artist", "genre": "Rock"},
        success=True
    )

    info = AgentResult(
        agent_type="info",
        title="Test Info",
        content="Historical information about the location.",
        metadata={"category": "History"},
        success=True
    )

    return {"video": video, "music": music, "info": info}
