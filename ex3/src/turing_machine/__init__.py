"""
Turing Machine Simulator Module

This module provides a classical Turing Machine implementation with:
- Unbounded tape (expandable in both directions)
- Configurable transition table
- Step-by-step execution with optional tracing
- JSON/YAML configuration support
"""

from .tape import Tape
from .tm_simulator import TuringMachine, TMResult, TMConfig
from .config_loader import load_tm_config

__all__ = [
    "Tape",
    "TuringMachine",
    "TMResult",
    "TMConfig",
    "load_tm_config",
]
