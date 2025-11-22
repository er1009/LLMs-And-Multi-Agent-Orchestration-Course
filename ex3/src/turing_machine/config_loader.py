"""
Configuration loader for Turing Machine definitions.

Supports loading TM configurations from JSON and YAML files.
"""

import json
from pathlib import Path
from typing import Dict, Any
from .tm_simulator import TMConfig


def load_tm_config(file_path: str) -> TMConfig:
    """
    Load a Turing Machine configuration from a JSON or YAML file.

    Args:
        file_path: Path to the configuration file

    Returns:
        TMConfig object

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid or required fields are missing
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    # Load file based on extension
    if path.suffix.lower() == ".json":
        data = _load_json(path)
    elif path.suffix.lower() in [".yaml", ".yml"]:
        data = _load_yaml(path)
    else:
        raise ValueError(
            f"Unsupported file format: {path.suffix}. Use .json, .yaml, or .yml"
        )

    # Parse and validate configuration
    return _parse_config(data)


def _load_json(path: Path) -> Dict[str, Any]:
    """Load JSON configuration file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML configuration file."""
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required to load YAML files. Install it with: pip install pyyaml"
        )

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_config(data: Dict[str, Any]) -> TMConfig:
    """
    Parse configuration data into TMConfig object.

    Args:
        data: Dictionary containing TM configuration

    Returns:
        TMConfig object

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Required fields
    required_fields = [
        "states",
        "alphabet",
        "transitions",
        "initial_state",
        "halting_states",
    ]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Parse states and alphabet
    states = set(data["states"])
    alphabet = set(data["alphabet"])
    halting_states = set(data["halting_states"])
    initial_state = data["initial_state"]
    blank_symbol = data.get("blank_symbol", "_")

    # Validate initial state
    if initial_state not in states:
        raise ValueError(f"Initial state '{initial_state}' not in states set")

    # Validate halting states
    if not halting_states.issubset(states):
        raise ValueError("Halting states must be a subset of states")

    # Validate blank symbol
    if blank_symbol not in alphabet:
        raise ValueError(f"Blank symbol '{blank_symbol}' not in alphabet")

    # Parse transitions
    transitions = {}
    for transition in data["transitions"]:
        # Validate transition fields
        required_trans_fields = ["state", "symbol", "new_state", "write", "move"]
        for field in required_trans_fields:
            if field not in transition:
                raise ValueError(f"Transition missing required field: {field}")

        state = transition["state"]
        symbol = transition["symbol"]
        new_state = transition["new_state"]
        write_symbol = transition["write"]
        direction = transition["move"]

        # Validate transition components
        if state not in states:
            raise ValueError(f"Unknown state in transition: {state}")
        if symbol not in alphabet:
            raise ValueError(f"Unknown symbol in transition: {symbol}")
        if new_state not in states:
            raise ValueError(f"Unknown new_state in transition: {new_state}")
        if write_symbol not in alphabet:
            raise ValueError(f"Unknown write symbol in transition: {write_symbol}")
        if direction not in ["L", "R"]:
            raise ValueError(
                f"Invalid direction in transition: {direction}. Must be 'L' or 'R'"
            )

        # Add transition to table
        key = (state, symbol)
        if key in transitions:
            raise ValueError(
                f"Duplicate transition for state={state}, symbol={symbol}"
            )
        transitions[key] = (new_state, write_symbol, direction)

    return TMConfig(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state=initial_state,
        halting_states=halting_states,
        blank_symbol=blank_symbol,
    )
