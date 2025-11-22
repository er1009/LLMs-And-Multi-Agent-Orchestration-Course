"""
Turing Machine Simulator

Implements a classical Turing Machine with:
- State-based transitions
- Tape read/write operations
- Step-by-step execution
- Halting conditions
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
from .tape import Tape


@dataclass
class TMConfig:
    """
    Configuration for a Turing Machine.

    Attributes:
        states: Set of all valid states
        alphabet: Set of valid tape symbols
        transitions: Transition table mapping (state, symbol) to (new_state, write_symbol, direction)
        initial_state: Starting state
        halting_states: Set of states that cause the machine to halt
        blank_symbol: Symbol used for blank cells
    """

    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[Tuple[str, str], Tuple[str, str, str]]
    initial_state: str
    halting_states: Set[str]
    blank_symbol: str = "_"


@dataclass
class TMResult:
    """
    Result of Turing Machine execution.

    Attributes:
        initial_tape: Content of tape before execution
        final_tape: Content of tape after execution
        final_state: State when execution stopped
        steps_taken: Number of steps executed
        halted: Whether machine reached a halting state
        trace: Optional list of execution steps
    """

    initial_tape: str
    final_tape: str
    final_state: str
    steps_taken: int
    halted: bool
    trace: Optional[List[str]] = None


class TuringMachine:
    """
    Classical Turing Machine simulator.

    Executes a Turing Machine according to a transition table,
    supporting step-by-step execution and configurable halting.
    """

    def __init__(self, config: TMConfig):
        """
        Initialize the Turing Machine.

        Args:
            config: TMConfig object containing machine definition
        """
        self.config = config
        self.current_state = config.initial_state
        self.tape = Tape(blank_symbol=config.blank_symbol)
        self.steps = 0
        self.trace: List[str] = []

    def load_tape(self, content: str) -> None:
        """
        Load initial content onto the tape.

        Args:
            content: String to write on the tape
        """
        self.tape = Tape(content, blank_symbol=self.config.blank_symbol)
        self.current_state = self.config.initial_state
        self.steps = 0
        self.trace = []

    def step(self, record_trace: bool = False) -> bool:
        """
        Execute a single step of the Turing Machine.

        Args:
            record_trace: If True, record this step in the trace

        Returns:
            True if the machine should continue, False if it should halt

        Raises:
            RuntimeError: If an invalid transition is encountered
        """
        # Check if in halting state
        if self.current_state in self.config.halting_states:
            return False

        # Read current symbol
        current_symbol = self.tape.read()

        # Look up transition
        transition_key = (self.current_state, current_symbol)
        if transition_key not in self.config.transitions:
            # No defined transition - treat as implicit halt
            return False

        new_state, write_symbol, direction = self.config.transitions[transition_key]

        # Record trace if requested
        if record_trace:
            self.trace.append(
                f"Step {self.steps}: State={self.current_state}, "
                f"Read={current_symbol}, Write={write_symbol}, "
                f"Move={direction}, NewState={new_state}"
            )

        # Execute transition
        self.tape.write(write_symbol)
        self.tape.move(direction)
        self.current_state = new_state
        self.steps += 1

        return True

    def run(self, max_steps: int = 10000, record_trace: bool = False) -> TMResult:
        """
        Run the Turing Machine until it halts or reaches max_steps.

        Args:
            max_steps: Maximum number of steps to execute
            record_trace: If True, record execution trace

        Returns:
            TMResult containing execution details
        """
        initial_tape_content = self.tape.get_content()

        # Execute steps
        while self.steps < max_steps:
            should_continue = self.step(record_trace)
            if not should_continue:
                break

        # Determine if halted normally
        halted = self.current_state in self.config.halting_states

        return TMResult(
            initial_tape=initial_tape_content,
            final_tape=self.tape.get_content(),
            final_state=self.current_state,
            steps_taken=self.steps,
            halted=halted,
            trace=self.trace if record_trace else None,
        )

    def reset(self) -> None:
        """Reset the machine to its initial state."""
        self.current_state = self.config.initial_state
        self.tape = Tape(blank_symbol=self.config.blank_symbol)
        self.steps = 0
        self.trace = []

    @classmethod
    def from_config_file(cls, file_path: str) -> "TuringMachine":
        """
        Create a TuringMachine from a configuration file.

        Args:
            file_path: Path to JSON or YAML config file

        Returns:
            Initialized TuringMachine instance
        """
        from .config_loader import load_tm_config

        config = load_tm_config(file_path)
        return cls(config)
