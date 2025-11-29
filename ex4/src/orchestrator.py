"""Main orchestrator for Route Guide System."""

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .config.route_service import RouteService, Route, RouteServiceError
from .agents.video_agent import VideoAgent
from .agents.music_agent import MusicAgent
from .agents.info_agent import InfoAgent
from .agents.choice_agent import ChoiceAgent, ChoiceResult
from .agents.base_agent import AgentResult
from .utils.config_loader import ConfigLoader
from .utils.claude_client import ClaudeClient
from .utils.logger import get_logger, setup_logger

logger = get_logger(__name__)


@dataclass
class Stop:
    """Stop along the route with selected content."""
    address: str
    choice: Dict  # ChoiceResult as dict

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "address": self.address,
            "choice": self.choice
        }


@dataclass
class RouteGuideOutput:
    """Complete output from route guide system."""
    source: str
    destination: str
    stops: List[Stop]
    metadata: Dict

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "source": self.source,
            "destination": self.destination,
            "stops": [stop.to_dict() for stop in self.stops],
            "metadata": self.metadata
        }

    def to_json(self, pretty: bool = True) -> str:
        """Convert to JSON string."""
        if pretty:
            return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        return json.dumps(self.to_dict(), ensure_ascii=False)


class RouteGuideOrchestrator:
    """
    Main orchestrator for Route Guide System.

    Coordinates:
    - Route retrieval from Google Maps
    - Parallel agent execution for each waypoint using threads
    - Content selection
    - Output generation

    Each waypoint is processed by running Video, Music, and Info agents
    concurrently in separate threads for improved performance.
    """

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize orchestrator.

        Args:
            config: Configuration loader (creates default if None)
        """
        self.config = config or ConfigLoader()

        # Set up logging
        log_level = self.config.get_log_level()
        log_file = self.config.get("system.log_file")
        setup_logger(level=log_level, log_file=log_file)

        # Initialize services
        self._init_route_service()
        self._init_agents()

        # Thread pool for parallel agent execution
        self.parallel_execution = self.config.get("system.parallel_execution", True)
        self.max_workers = self.config.get("system.max_agent_threads", 3)

        logger.info(
            f"Route Guide Orchestrator initialized "
            f"(parallel_execution={self.parallel_execution})"
        )

    def _init_route_service(self) -> None:
        """Initialize Google Maps route service."""
        api_key = self.config.get_google_maps_api_key()
        timeout = self.config.get("api.google_maps.timeout", 10)
        max_retries = self.config.get("api.google_maps.max_retries", 3)
        retry_delay = self.config.get("api.google_maps.retry_delay", 1)

        self.route_service = RouteService(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay
        )

    def _init_agents(self) -> None:
        """Initialize all agents."""
        # Create Claude client
        claude_timeout = self.config.get("api.claude.timeout", 30)
        claude_max_retries = self.config.get("api.claude.max_retries", 2)
        claude_retry_delay = self.config.get("api.claude.retry_delay", 2)
        claude_command = self.config.get("api.claude.cli_command", "claude")

        self.claude_client = ClaudeClient(
            cli_command=claude_command,
            timeout=claude_timeout,
            max_retries=claude_max_retries,
            retry_delay=claude_retry_delay
        )

        # Create agents
        video_timeout = self.config.get("agents.video.timeout", 30)
        music_timeout = self.config.get("agents.music.timeout", 30)
        info_timeout = self.config.get("agents.info.timeout", 30)
        choice_timeout = self.config.get("agents.choice.timeout", 30)

        self.video_agent = VideoAgent(self.claude_client, timeout=video_timeout)
        self.music_agent = MusicAgent(self.claude_client, timeout=music_timeout)
        self.info_agent = InfoAgent(self.claude_client, timeout=info_timeout)
        self.choice_agent = ChoiceAgent(self.claude_client, timeout=choice_timeout)

    def process_route(
        self,
        source: str,
        destination: str
    ) -> RouteGuideOutput:
        """
        Process complete route from source to destination.

        Args:
            source: Source address
            destination: Destination address

        Returns:
            RouteGuideOutput with all stops and recommendations

        Raises:
            RouteServiceError: If route retrieval fails
            Exception: If processing fails critically
        """
        start_time = datetime.now()
        logger.info(f"Processing route: {source} → {destination}")

        # Get route
        max_waypoints = self.config.get("route.max_waypoints", 20)
        route = self.route_service.get_route(source, destination, max_waypoints)

        logger.info(f"Processing {len(route.waypoints)} waypoints")

        # Process each waypoint
        stops = []
        consecutive_failures = 0
        max_failures = self.config.get("error_handling.max_consecutive_failures", 3)

        for i, waypoint in enumerate(route.waypoints):
            logger.info(
                f"Processing waypoint {i + 1}/{len(route.waypoints)}: "
                f"{waypoint.location.address}"
            )

            try:
                choice_result = self._process_waypoint(waypoint.location.address)

                if choice_result.selected_type != "none":
                    stop = Stop(
                        address=waypoint.location.address,
                        choice=choice_result.to_dict()
                    )
                    stops.append(stop)
                    consecutive_failures = 0  # Reset on success
                else:
                    logger.warning(f"No content found for waypoint: {waypoint.location.address}")
                    consecutive_failures += 1

            except Exception as e:
                logger.error(f"Failed to process waypoint {waypoint.location.address}: {e}")
                consecutive_failures += 1

                # Check if we should continue
                if not self.config.get("error_handling.continue_on_agent_failure", True):
                    raise

            # Check consecutive failures
            if consecutive_failures >= max_failures:
                logger.error(
                    f"Too many consecutive failures ({consecutive_failures}), aborting"
                )
                break

        # Create output
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        output = RouteGuideOutput(
            source=route.source.address,
            destination=route.destination.address,
            stops=stops,
            metadata={
                "total_waypoints": len(route.waypoints),
                "processed_stops": len(stops),
                "total_distance_km": round(route.total_distance, 2),
                "estimated_duration_minutes": round(route.total_duration, 0),
                "processing_time_seconds": round(processing_time, 2),
                "timestamp": datetime.now().isoformat(),
                "route_summary": route.metadata.get("summary", "")
            }
        )

        logger.info(
            f"Route processing complete: {len(stops)} stops in {processing_time:.1f}s"
        )

        # Save to file if configured
        if self.config.get("output.save_to_file", True):
            self._save_output(output)

        return output

    def _process_waypoint(self, address: str) -> ChoiceResult:
        """
        Process single waypoint through all agents.

        If parallel_execution is enabled, runs Video, Music, and Info agents
        concurrently in separate threads. Otherwise, runs sequentially.

        Args:
            address: Waypoint address

        Returns:
            ChoiceResult with selected content

        Raises:
            Exception: If all agents fail
        """
        if self.parallel_execution:
            return self._process_waypoint_parallel(address)
        else:
            return self._process_waypoint_sequential(address)

    def _process_waypoint_sequential(self, address: str) -> ChoiceResult:
        """
        Process waypoint with sequential agent execution.

        Args:
            address: Waypoint address

        Returns:
            ChoiceResult with selected content
        """
        logger.debug(f"Processing waypoint sequentially: {address}")

        # Execute three content agents sequentially
        video_result = self.video_agent.execute(address)
        music_result = self.music_agent.execute(address)
        info_result = self.info_agent.execute(address)

        # Let choice agent select best option
        choice_result = self.choice_agent.select_best(
            address,
            video_result,
            music_result,
            info_result
        )

        return choice_result

    def _process_waypoint_parallel(self, address: str) -> ChoiceResult:
        """
        Process waypoint with parallel agent execution using threads.

        Runs Video, Music, and Info agents concurrently for improved performance.

        Args:
            address: Waypoint address

        Returns:
            ChoiceResult with selected content

        Raises:
            Exception: If thread execution fails
        """
        logger.debug(f"Processing waypoint in parallel: {address}")

        # Dictionary to store results from each agent thread
        results = {
            'video': None,
            'music': None,
            'info': None
        }

        # Define agent execution functions
        def run_video_agent():
            """Execute video agent in thread."""
            try:
                logger.debug(f"[Thread-Video] Starting for {address}")
                result = self.video_agent.execute(address)
                logger.debug(f"[Thread-Video] Completed for {address}")
                return ('video', result)
            except Exception as e:
                logger.error(f"[Thread-Video] Failed: {e}")
                return ('video', self.video_agent._create_error_result(address, str(e)))

        def run_music_agent():
            """Execute music agent in thread."""
            try:
                logger.debug(f"[Thread-Music] Starting for {address}")
                result = self.music_agent.execute(address)
                logger.debug(f"[Thread-Music] Completed for {address}")
                return ('music', result)
            except Exception as e:
                logger.error(f"[Thread-Music] Failed: {e}")
                return ('music', self.music_agent._create_error_result(address, str(e)))

        def run_info_agent():
            """Execute info agent in thread."""
            try:
                logger.debug(f"[Thread-Info] Starting for {address}")
                result = self.info_agent.execute(address)
                logger.debug(f"[Thread-Info] Completed for {address}")
                return ('info', result)
            except Exception as e:
                logger.error(f"[Thread-Info] Failed: {e}")
                return ('info', self.info_agent._create_error_result(address, str(e)))

        # Execute agents in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="AgentThread") as executor:
            # Submit all three agents to thread pool
            future_to_agent = {
                executor.submit(run_video_agent): 'video',
                executor.submit(run_music_agent): 'music',
                executor.submit(run_info_agent): 'info'
            }

            # Collect results as threads complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    agent_type, result = future.result()
                    results[agent_type] = result
                    logger.debug(f"[Parallel] {agent_name} agent completed")
                except Exception as e:
                    logger.error(f"[Parallel] {agent_name} agent thread failed: {e}")
                    # Create error result as fallback
                    results[agent_name] = AgentResult(
                        agent_type=agent_name,
                        title=f"No {agent_name} found",
                        content="",
                        metadata={"address": address, "error": str(e)},
                        success=False,
                        error_message=str(e)
                    )

        logger.info(f"All agents completed in parallel for {address}")

        # Ensure all results are present
        if None in results.values():
            logger.error("Some agents did not return results")
            for agent_type, result in results.items():
                if result is None:
                    results[agent_type] = AgentResult(
                        agent_type=agent_type,
                        title=f"No {agent_type} found",
                        content="",
                        metadata={"address": address, "error": "Agent did not complete"},
                        success=False,
                        error_message="Agent did not complete"
                    )

        # Let choice agent select best option
        choice_result = self.choice_agent.select_best(
            address,
            results['video'],
            results['music'],
            results['info']
        )

        return choice_result

    def _save_output(self, output: RouteGuideOutput) -> None:
        """
        Save output to file.

        Args:
            output: RouteGuideOutput to save
        """
        try:
            output_dir = Path(self.config.get("output.output_dir", "results"))
            output_dir.mkdir(exist_ok=True, parents=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            source_short = output.source.replace(",", "").replace(" ", "_")[:30]
            dest_short = output.destination.replace(",", "").replace(" ", "_")[:30]
            filename = f"route_{source_short}_to_{dest_short}_{timestamp}.json"

            output_path = output_dir / filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output.to_json(pretty=True))

            logger.info(f"Output saved to: {output_path}")

        except Exception as e:
            logger.error(f"Failed to save output to file: {e}")
