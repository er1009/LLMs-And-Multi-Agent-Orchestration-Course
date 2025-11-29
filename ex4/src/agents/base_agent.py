"""Base agent class for Route Guide System."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..utils.logger import get_logger
from ..utils.claude_client import ClaudeClient

logger = get_logger(__name__)


@dataclass
class AgentResult:
    """Standardized result from an agent execution."""
    agent_type: str  # 'video', 'music', 'info'
    title: str
    content: str  # URL or text content
    metadata: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.agent_type,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "success": self.success,
            "error_message": self.error_message
        }


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Implements template method pattern for agent execution.
    Subclasses must implement specific content search logic.
    """

    def __init__(
        self,
        claude_client: ClaudeClient,
        agent_type: str,
        timeout: int = 30
    ):
        """
        Initialize base agent.

        Args:
            claude_client: Claude CLI client instance
            agent_type: Type identifier ('video', 'music', 'info')
            timeout: Execution timeout in seconds
        """
        self.claude_client = claude_client
        self.agent_type = agent_type
        self.timeout = timeout

    def execute(self, address: str, context: Optional[Dict] = None) -> AgentResult:
        """
        Execute agent logic for given address (template method).

        Args:
            address: Location address to find content for
            context: Optional additional context

        Returns:
            AgentResult with content recommendation

        Raises:
            Exception: If agent execution fails critically
        """
        logger.info(f"{self.agent_type.capitalize()} Agent executing for: {address}")

        try:
            # Validate input
            self._validate_input(address)

            # Create prompt for Claude
            prompt = self._create_prompt(address, context or {})

            # Call Claude to get recommendation
            response = self._call_claude(prompt)

            # Parse and validate response
            result = self._parse_response(response, address)

            logger.info(
                f"{self.agent_type.capitalize()} Agent success: {result.title}"
            )

            return result

        except Exception as e:
            logger.error(
                f"{self.agent_type.capitalize()} Agent failed for {address}: {str(e)}"
            )
            return self._create_error_result(address, str(e))

    def _validate_input(self, address: str) -> None:
        """
        Validate input address.

        Args:
            address: Address to validate

        Raises:
            ValueError: If address is invalid
        """
        if not address or not isinstance(address, str):
            raise ValueError("Address must be a non-empty string")

        if len(address) < 3:
            raise ValueError("Address too short")

    @abstractmethod
    def _create_prompt(self, address: str, context: Dict) -> str:
        """
        Create Claude prompt for this agent type.

        Args:
            address: Location address
            context: Additional context

        Returns:
            Prompt string for Claude
        """
        pass

    def _call_claude(self, prompt: str) -> str:
        """
        Call Claude with prompt.

        Args:
            prompt: Prompt to send

        Returns:
            Claude's response

        Raises:
            Exception: If Claude call fails
        """
        return self.claude_client.call(prompt)

    @abstractmethod
    def _parse_response(self, response: str, address: str) -> AgentResult:
        """
        Parse Claude's response into AgentResult.

        Args:
            response: Claude's response text
            address: Original address (for error handling)

        Returns:
            AgentResult

        Raises:
            Exception: If parsing fails
        """
        pass

    def _create_error_result(self, address: str, error_message: str) -> AgentResult:
        """
        Create error result when agent fails.

        Args:
            address: Address that failed
            error_message: Error description

        Returns:
            AgentResult indicating failure
        """
        return AgentResult(
            agent_type=self.agent_type,
            title=f"No {self.agent_type} found",
            content="",
            metadata={"address": address, "error": error_message},
            success=False,
            error_message=error_message
        )

    def get_type(self) -> str:
        """
        Get agent type identifier.

        Returns:
            Agent type string
        """
        return self.agent_type
