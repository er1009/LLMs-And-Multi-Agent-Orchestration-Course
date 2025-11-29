"""Choice Agent implementation for Route Guide System."""

import json
import re
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

from .base_agent import AgentResult
from ..utils.logger import get_logger
from ..utils.claude_client import ClaudeClient

logger = get_logger(__name__)


@dataclass
class ChoiceResult:
    """Result from Choice Agent selection."""
    selected_type: str  # 'video', 'music', 'info'
    title: str
    content: str  # URL or text
    reason: str  # Why this was chosen
    metadata: Dict
    alternatives: List[AgentResult]  # Other options (for logging/debugging)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON output."""
        return {
            "type": self.selected_type,
            "title": self.title,
            "content": self.content,
            "reason": self.reason
        }


class ChoiceAgent:
    """
    Meta-agent that selects the best recommendation from other agents.

    Uses Claude to make an intelligent choice based on relevance and usefulness.
    Prompt is loaded from prompts/choice_agent.md
    """

    def __init__(self, claude_client: ClaudeClient, timeout: int = 30):
        """
        Initialize Choice Agent.

        Args:
            claude_client: Claude CLI client
            timeout: Execution timeout
        """
        self.claude_client = claude_client
        self.timeout = timeout
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load prompt template from markdown file."""
        prompt_path = Path(__file__).parent / "prompts" / "choice_agent.md"
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def select_best(
        self,
        address: str,
        video_result: AgentResult,
        music_result: AgentResult,
        info_result: AgentResult
    ) -> ChoiceResult:
        """
        Select the best recommendation from three agent results.

        Args:
            address: Location address
            video_result: Result from Video Agent
            music_result: Result from Music Agent
            info_result: Result from Info Agent

        Returns:
            ChoiceResult with selected recommendation

        Raises:
            Exception: If selection fails
        """
        logger.info(f"Choice Agent selecting best option for: {address}")

        try:
            # Create prompt with all three options
            prompt = self._create_prompt(address, video_result, music_result, info_result)

            # Call Claude to make selection
            response = self.claude_client.call(prompt)

            # Parse response
            choice = self._parse_response(
                response,
                address,
                video_result,
                music_result,
                info_result
            )

            logger.info(f"Choice Agent selected: {choice.selected_type} - {choice.title}")

            return choice

        except Exception as e:
            logger.error(f"Choice Agent failed: {str(e)}")
            # Fallback: prefer info if available, then video, then music
            return self._fallback_selection(
                address,
                video_result,
                music_result,
                info_result
            )

    def _create_prompt(
        self,
        address: str,
        video: AgentResult,
        music: AgentResult,
        info: AgentResult
    ) -> str:
        """
        Create prompt for Claude to select best option.

        Args:
            address: Location address
            video: Video agent result
            music: Music agent result
            info: Info agent result

        Returns:
            Prompt string
        """
        # Substitute all placeholders in template
        prompt = self.prompt_template.replace("{{ADDRESS}}", address)

        # Video placeholders
        prompt = prompt.replace("{{VIDEO_TITLE}}", video.title if video.success else "Not available")
        prompt = prompt.replace("{{VIDEO_CONTENT}}", video.content if video.success else "Failed to find video")
        prompt = prompt.replace("{{VIDEO_DESCRIPTION}}", video.metadata.get('description', 'N/A') if video.success else "N/A")
        prompt = prompt.replace("{{VIDEO_AVAILABLE}}", str(video.success))

        # Music placeholders
        prompt = prompt.replace("{{MUSIC_TITLE}}", music.title if music.success else "Not available")
        prompt = prompt.replace("{{MUSIC_CONTENT}}", music.content if music.success else "Failed to find music")
        prompt = prompt.replace("{{MUSIC_RELEVANCE}}", music.metadata.get('relevance_reason', 'N/A') if music.success else "N/A")
        prompt = prompt.replace("{{MUSIC_AVAILABLE}}", str(music.success))

        # Info placeholders
        prompt = prompt.replace("{{INFO_TITLE}}", info.title if info.success else "Not available")
        prompt = prompt.replace("{{INFO_CONTENT}}", info.content if info.success else "Failed to find info")
        prompt = prompt.replace("{{INFO_CATEGORY}}", info.metadata.get('category', 'N/A') if info.success else "N/A")
        prompt = prompt.replace("{{INFO_AVAILABLE}}", str(info.success))

        return prompt

    def _parse_response(
        self,
        response: str,
        address: str,
        video: AgentResult,
        music: AgentResult,
        info: AgentResult
    ) -> ChoiceResult:
        """
        Parse Claude's selection response.

        Args:
            response: Claude's JSON response
            address: Location address
            video: Video agent result
            music: Music agent result
            info: Info agent result

        Returns:
            ChoiceResult

        Raises:
            ValueError: If parsing fails
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group())

            # Get selection
            selected = data.get("selected", "").lower()
            reason = data.get("reason", "Selected based on relevance")

            # Map selection to result
            result_map = {
                "video": video,
                "music": music,
                "info": info
            }

            if selected not in result_map:
                raise ValueError(f"Invalid selection: {selected}")

            selected_result = result_map[selected]

            if not selected_result.success:
                raise ValueError(f"Selected agent ({selected}) failed")

            # Create choice result
            return ChoiceResult(
                selected_type=selected,
                title=selected_result.title,
                content=selected_result.content,
                reason=reason,
                metadata=selected_result.metadata.copy(),
                alternatives=[video, music, info]
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse choice agent response: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid response format: {e}")

    def _fallback_selection(
        self,
        address: str,
        video: AgentResult,
        music: AgentResult,
        info: AgentResult
    ) -> ChoiceResult:
        """
        Fallback selection when Claude fails.

        Priority: info > video > music

        Args:
            address: Location address
            video: Video result
            music: Music result
            info: Info result

        Returns:
            ChoiceResult with fallback selection
        """
        logger.warning("Using fallback selection logic")

        # Try in priority order
        for result, type_name in [(info, "info"), (video, "video"), (music, "music")]:
            if result.success:
                return ChoiceResult(
                    selected_type=type_name,
                    title=result.title,
                    content=result.content,
                    reason="Fallback selection due to choice agent failure",
                    metadata=result.metadata.copy(),
                    alternatives=[video, music, info]
                )

        # All failed - return error result
        return ChoiceResult(
            selected_type="none",
            title="No content available",
            content="",
            reason="All agents failed to find content",
            metadata={"address": address, "error": "All agents failed"},
            alternatives=[video, music, info]
        )
