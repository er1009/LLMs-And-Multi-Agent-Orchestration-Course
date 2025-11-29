"""Unit tests for agent implementations."""

import pytest
from unittest.mock import Mock, MagicMock
from src.agents.base_agent import AgentResult
from src.agents.video_agent import VideoAgent
from src.agents.music_agent import MusicAgent
from src.agents.info_agent import InfoAgent
from src.agents.choice_agent import ChoiceAgent, ChoiceResult


class TestBaseAgent:
    """Tests for base agent functionality."""

    def test_agent_result_creation(self):
        """Test AgentResult creation."""
        result = AgentResult(
            agent_type="test",
            title="Test Title",
            content="Test Content",
            metadata={"key": "value"},
            success=True
        )
        assert result.agent_type == "test"
        assert result.title == "Test Title"
        assert result.success is True

    def test_agent_result_to_dict(self):
        """Test AgentResult conversion to dict."""
        result = AgentResult(
            agent_type="test",
            title="Test",
            content="Content",
            metadata={},
            success=True
        )
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["type"] == "test"
        assert result_dict["title"] == "Test"


class TestVideoAgent:
    """Tests for VideoAgent."""

    def test_create_prompt(self):
        """Test video agent prompt creation."""
        claude_mock = Mock()
        agent = VideoAgent(claude_mock)

        prompt = agent._create_prompt("Times Square, New York", {})

        assert "Times Square, New York" in prompt
        assert "YouTube" in prompt
        assert "JSON" in prompt

    def test_parse_valid_response(self):
        """Test parsing valid video agent response."""
        claude_mock = Mock()
        agent = VideoAgent(claude_mock)

        response = """
        {
            "title": "Times Square Walking Tour",
            "url": "https://www.youtube.com/watch?v=abc123",
            "description": "A virtual tour of Times Square",
            "channel": "NYC Tours"
        }
        """

        result = agent._parse_response(response, "Times Square")

        assert result.success is True
        assert result.agent_type == "video"
        assert "Times Square" in result.title
        assert "youtube.com" in result.content.lower()

    def test_parse_invalid_response(self):
        """Test parsing invalid response raises error."""
        claude_mock = Mock()
        agent = VideoAgent(claude_mock)

        response = "Not valid JSON"

        with pytest.raises(ValueError):
            agent._parse_response(response, "Test Location")


class TestMusicAgent:
    """Tests for MusicAgent."""

    def test_create_prompt(self):
        """Test music agent prompt creation."""
        claude_mock = Mock()
        agent = MusicAgent(claude_mock)

        prompt = agent._create_prompt("Nashville, TN", {})

        assert "Nashville, TN" in prompt
        assert "music" in prompt.lower()
        assert "song" in prompt.lower()

    def test_parse_valid_response(self):
        """Test parsing valid music agent response."""
        claude_mock = Mock()
        agent = MusicAgent(claude_mock)

        response = """
        {
            "title": "Sweet Home Alabama",
            "artist": "Lynyrd Skynyrd",
            "url": "https://www.youtube.com/watch?v=xyz789",
            "genre": "Southern Rock"
        }
        """

        result = agent._parse_response(response, "Alabama")

        assert result.success is True
        assert result.agent_type == "music"
        assert "Sweet Home Alabama" in result.title
        assert "Lynyrd Skynyrd" in result.title


class TestInfoAgent:
    """Tests for InfoAgent."""

    def test_create_prompt(self):
        """Test info agent prompt creation."""
        claude_mock = Mock()
        agent = InfoAgent(claude_mock)

        prompt = agent._create_prompt("Boston, MA", {})

        assert "Boston, MA" in prompt
        assert "historical" in prompt.lower() or "information" in prompt.lower()

    def test_parse_valid_response(self):
        """Test parsing valid info agent response."""
        claude_mock = Mock()
        agent = InfoAgent(claude_mock)

        response = """
        {
            "title": "Historic Boston",
            "summary": "Boston is one of the oldest cities in the United States.",
            "highlights": ["Founded in 1630", "Site of Boston Tea Party"],
            "category": "History"
        }
        """

        result = agent._parse_response(response, "Boston")

        assert result.success is True
        assert result.agent_type == "info"
        assert "Historic Boston" in result.title
        assert "oldest cities" in result.content


class TestChoiceAgent:
    """Tests for ChoiceAgent."""

    def test_fallback_selection_info_priority(self):
        """Test fallback selection prefers info."""
        claude_mock = Mock()
        agent = ChoiceAgent(claude_mock)

        video_result = AgentResult("video", "Video", "url", {}, success=True)
        music_result = AgentResult("music", "Music", "url", {}, success=True)
        info_result = AgentResult("info", "Info", "text", {}, success=True)

        choice = agent._fallback_selection(
            "Test Address",
            video_result,
            music_result,
            info_result
        )

        assert choice.selected_type == "info"

    def test_fallback_selection_video_when_info_fails(self):
        """Test fallback selects video when info fails."""
        claude_mock = Mock()
        agent = ChoiceAgent(claude_mock)

        video_result = AgentResult("video", "Video", "url", {}, success=True)
        music_result = AgentResult("music", "Music", "url", {}, success=True)
        info_result = AgentResult("info", "Info", "text", {}, success=False)

        choice = agent._fallback_selection(
            "Test Address",
            video_result,
            music_result,
            info_result
        )

        assert choice.selected_type == "video"

    def test_fallback_selection_all_failed(self):
        """Test fallback when all agents fail."""
        claude_mock = Mock()
        agent = ChoiceAgent(claude_mock)

        video_result = AgentResult("video", "Video", "url", {}, success=False)
        music_result = AgentResult("music", "Music", "url", {}, success=False)
        info_result = AgentResult("info", "Info", "text", {}, success=False)

        choice = agent._fallback_selection(
            "Test Address",
            video_result,
            music_result,
            info_result
        )

        assert choice.selected_type == "none"

    def test_choice_result_to_dict(self):
        """Test ChoiceResult conversion to dict."""
        choice = ChoiceResult(
            selected_type="video",
            title="Test Video",
            content="https://youtube.com/test",
            reason="Most relevant",
            metadata={},
            alternatives=[]
        )

        choice_dict = choice.to_dict()
        assert isinstance(choice_dict, dict)
        assert choice_dict["type"] == "video"
        assert choice_dict["title"] == "Test Video"
        assert choice_dict["reason"] == "Most relevant"
