"""
Translation Module

Provides multi-agent translation orchestration using:
- Claude CLI agents (defined in MD files)
- Error injection for robustness testing
- Pipeline orchestration
"""

from .error_injector import ErrorInjector
from .claude_agent_runner import ClaudeAgentRunner, run_translation_pipeline

__all__ = [
    "ErrorInjector",
    "ClaudeAgentRunner",
    "run_translation_pipeline",
]
