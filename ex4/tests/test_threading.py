"""Unit tests for parallel threading functionality."""

import time
import pytest
from unittest.mock import Mock, MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

from src.orchestrator import RouteGuideOrchestrator
from src.agents.base_agent import AgentResult
from src.agents.choice_agent import ChoiceResult


class TestParallelExecution:
    """Tests for parallel agent execution."""

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration with parallel execution enabled."""
        config = Mock()
        config.get_google_maps_api_key.return_value = "test_key"
        config.get_log_level.return_value = "INFO"
        config.get.side_effect = lambda key, default=None: {
            "api.google_maps.timeout": 10,
            "api.google_maps.max_retries": 3,
            "api.google_maps.retry_delay": 1,
            "api.claude.timeout": 30,
            "api.claude.max_retries": 2,
            "api.claude.retry_delay": 2,
            "api.claude.cli_command": "claude",
            "agents.video.timeout": 30,
            "agents.music.timeout": 30,
            "agents.info.timeout": 30,
            "agents.choice.timeout": 30,
            "system.parallel_execution": True,  # Enable parallel execution
            "system.max_agent_threads": 3,
            "system.log_file": None,
            "output.save_to_file": False
        }.get(key, default)
        return config

    @pytest.fixture
    def mock_claude_client(self):
        """Create mock Claude client."""
        client = Mock()
        client.call.return_value = '{"test": "response"}'
        return client

    def test_parallel_execution_enabled(self, mock_config):
        """Test that parallel execution is enabled from config."""
        orchestrator = RouteGuideOrchestrator(config=mock_config)
        assert orchestrator.parallel_execution is True
        assert orchestrator.max_workers == 3

    def test_sequential_fallback(self, mock_config):
        """Test that sequential execution works as fallback."""
        # Disable parallel execution
        def custom_get(key, default=None):
            if key == "system.parallel_execution":
                return False
            return mock_config.get(key, default)

        mock_config.get.side_effect = custom_get

        orchestrator = RouteGuideOrchestrator(config=mock_config)
        assert orchestrator.parallel_execution is False

    @patch('src.orchestrator.VideoAgent')
    @patch('src.orchestrator.MusicAgent')
    @patch('src.orchestrator.InfoAgent')
    @patch('src.orchestrator.ChoiceAgent')
    def test_parallel_agents_called_concurrently(
        self,
        mock_choice_cls,
        mock_info_cls,
        mock_music_cls,
        mock_video_cls,
        mock_config
    ):
        """Test that agents are called in parallel."""
        # Track execution times to verify concurrency
        execution_times = []

        def slow_execute(address, delay=0.1):
            """Simulate slow agent execution."""
            start = time.time()
            time.sleep(delay)
            end = time.time()
            execution_times.append((start, end))
            return AgentResult(
                agent_type="test",
                title="Test",
                content="test",
                metadata={},
                success=True
            )

        # Set up mock agents
        mock_video_agent = Mock()
        mock_video_agent.execute.side_effect = lambda addr: slow_execute(addr, 0.1)
        mock_video_agent._create_error_result = Mock(return_value=AgentResult(
            "video", "Error", "", {}, False, "Error"
        ))
        mock_video_cls.return_value = mock_video_agent

        mock_music_agent = Mock()
        mock_music_agent.execute.side_effect = lambda addr: slow_execute(addr, 0.1)
        mock_music_agent._create_error_result = Mock(return_value=AgentResult(
            "music", "Error", "", {}, False, "Error"
        ))
        mock_music_cls.return_value = mock_music_agent

        mock_info_agent = Mock()
        mock_info_agent.execute.side_effect = lambda addr: slow_execute(addr, 0.1)
        mock_info_agent._create_error_result = Mock(return_value=AgentResult(
            "info", "Error", "", {}, False, "Error"
        ))
        mock_info_cls.return_value = mock_info_agent

        # Set up choice agent
        mock_choice_agent = Mock()
        mock_choice_agent.select_best.return_value = ChoiceResult(
            selected_type="info",
            title="Test",
            content="test",
            reason="test reason",
            metadata={},
            alternatives=[]
        )
        mock_choice_cls.return_value = mock_choice_agent

        # Create orchestrator and process waypoint
        orchestrator = RouteGuideOrchestrator(config=mock_config)

        start_time = time.time()
        result = orchestrator._process_waypoint_parallel("Test Address")
        end_time = time.time()

        # Verify all agents were called
        assert mock_video_agent.execute.called
        assert mock_music_agent.execute.called
        assert mock_info_agent.execute.called

        # Verify execution was parallel (should take ~0.1s, not ~0.3s)
        # With parallel execution, all three 0.1s tasks run concurrently
        total_time = end_time - start_time
        assert total_time < 0.25, f"Parallel execution took {total_time}s, expected < 0.25s"

        # With sequential, it would take ~0.3s (3 * 0.1s)
        # With parallel, it should take ~0.1s (max of three 0.1s tasks)

    @patch('src.orchestrator.VideoAgent')
    @patch('src.orchestrator.MusicAgent')
    @patch('src.orchestrator.InfoAgent')
    @patch('src.orchestrator.ChoiceAgent')
    def test_thread_error_handling(
        self,
        mock_choice_cls,
        mock_info_cls,
        mock_music_cls,
        mock_video_cls,
        mock_config
    ):
        """Test that thread errors are handled gracefully."""
        # Set up video agent to fail
        mock_video_agent = Mock()
        mock_video_agent.execute.side_effect = Exception("Video agent failed")
        mock_video_agent._create_error_result.return_value = AgentResult(
            agent_type="video",
            title="No video found",
            content="",
            metadata={"error": "Video agent failed"},
            success=False,
            error_message="Video agent failed"
        )
        mock_video_cls.return_value = mock_video_agent

        # Set up music and info agents to succeed
        mock_music_agent = Mock()
        mock_music_agent.execute.return_value = AgentResult(
            "music", "Music", "url", {}, True
        )
        mock_music_cls.return_value = mock_music_agent

        mock_info_agent = Mock()
        mock_info_agent.execute.return_value = AgentResult(
            "info", "Info", "text", {}, True
        )
        mock_info_cls.return_value = mock_info_agent

        # Set up choice agent
        mock_choice_agent = Mock()
        mock_choice_agent.select_best.return_value = ChoiceResult(
            selected_type="info",
            title="Info",
            content="text",
            reason="Video failed, selected info",
            metadata={},
            alternatives=[]
        )
        mock_choice_cls.return_value = mock_choice_agent

        # Create orchestrator and process waypoint
        orchestrator = RouteGuideOrchestrator(config=mock_config)
        result = orchestrator._process_waypoint_parallel("Test Address")

        # Verify result was returned despite video failure
        assert result is not None
        assert result.selected_type == "info"

        # Verify error result was created for video
        mock_video_agent._create_error_result.assert_called_once()

    @patch('src.orchestrator.VideoAgent')
    @patch('src.orchestrator.MusicAgent')
    @patch('src.orchestrator.InfoAgent')
    @patch('src.orchestrator.ChoiceAgent')
    def test_sequential_vs_parallel_choice(
        self,
        mock_choice_cls,
        mock_info_cls,
        mock_music_cls,
        mock_video_cls,
        mock_config
    ):
        """Test that _process_waypoint chooses parallel or sequential correctly."""
        # Set up agents
        for mock_agent_cls in [mock_video_cls, mock_music_cls, mock_info_cls]:
            mock_agent = Mock()
            mock_agent.execute.return_value = AgentResult(
                "test", "Test", "test", {}, True
            )
            mock_agent_cls.return_value = mock_agent

        mock_choice_agent = Mock()
        mock_choice_agent.select_best.return_value = ChoiceResult(
            "info", "Test", "test", "reason", {}, []
        )
        mock_choice_cls.return_value = mock_choice_agent

        # Test with parallel enabled
        orchestrator = RouteGuideOrchestrator(config=mock_config)
        orchestrator.parallel_execution = True

        with patch.object(orchestrator, '_process_waypoint_parallel') as mock_parallel:
            with patch.object(orchestrator, '_process_waypoint_sequential') as mock_sequential:
                mock_parallel.return_value = ChoiceResult("info", "Test", "test", "reason", {}, [])
                orchestrator._process_waypoint("Test")
                mock_parallel.assert_called_once()
                mock_sequential.assert_not_called()

        # Test with parallel disabled
        orchestrator.parallel_execution = False

        with patch.object(orchestrator, '_process_waypoint_parallel') as mock_parallel:
            with patch.object(orchestrator, '_process_waypoint_sequential') as mock_sequential:
                mock_sequential.return_value = ChoiceResult("info", "Test", "test", "reason", {}, [])
                orchestrator._process_waypoint("Test")
                mock_sequential.assert_called_once()
                mock_parallel.assert_not_called()


class TestThreadSafety:
    """Tests for thread safety of agents."""

    def test_agents_are_independent(self, mock_claude_client):
        """Test that agent instances don't share state."""
        from src.agents.video_agent import VideoAgent
        from src.agents.music_agent import MusicAgent
        from src.agents.info_agent import InfoAgent

        # Create multiple instances
        video1 = VideoAgent(mock_claude_client)
        video2 = VideoAgent(mock_claude_client)
        music1 = MusicAgent(mock_claude_client)
        info1 = InfoAgent(mock_claude_client)

        # Verify they are separate instances
        assert video1 is not video2
        assert video1.claude_client is mock_claude_client
        assert video2.claude_client is mock_claude_client

        # Verify agents have different types
        assert video1.agent_type != music1.agent_type
        assert video1.agent_type != info1.agent_type

    def test_concurrent_agent_execution(self, mock_claude_client, sample_agent_results):
        """Test multiple agents can execute concurrently without interference."""
        from src.agents.video_agent import VideoAgent
        from src.agents.music_agent import MusicAgent
        from src.agents.info_agent import InfoAgent

        # Create agents
        video_agent = VideoAgent(mock_claude_client)
        music_agent = MusicAgent(mock_claude_client)
        info_agent = InfoAgent(mock_claude_client)

        # Mock their execute methods to return immediately
        video_agent.execute = Mock(return_value=sample_agent_results['video'])
        music_agent.execute = Mock(return_value=sample_agent_results['music'])
        info_agent.execute = Mock(return_value=sample_agent_results['info'])

        # Execute in thread pool
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(video_agent.execute, "Test Address"),
                executor.submit(music_agent.execute, "Test Address"),
                executor.submit(info_agent.execute, "Test Address")
            ]

            results = [f.result() for f in futures]

        # Verify all executed successfully
        assert len(results) == 3
        assert all(r.success for r in results)
