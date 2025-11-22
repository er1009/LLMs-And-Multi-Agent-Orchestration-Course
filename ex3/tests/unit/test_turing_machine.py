"""
Unit tests for Turing Machine module.
"""

import pytest
from src.turing_machine import Tape, TuringMachine, TMConfig


class TestTape:
    """Tests for Tape class."""

    def test_tape_initialization(self):
        """Test tape initialization with content."""
        tape = Tape("101")
        assert tape.read() == "1"
        assert tape.get_content() == "101"

    def test_tape_empty_initialization(self):
        """Test tape initialization without content."""
        tape = Tape()
        assert tape.read() == "_"

    def test_tape_write(self):
        """Test writing to tape."""
        tape = Tape("101")
        tape.write("X")
        assert tape.read() == "X"
        assert tape.get_content() == "X01"

    def test_tape_move_right(self):
        """Test moving head right."""
        tape = Tape("101")
        tape.move("R")
        assert tape.read() == "0"

    def test_tape_move_left(self):
        """Test moving head left."""
        tape = Tape("101")
        tape.move("R")
        tape.move("L")
        assert tape.read() == "1"

    def test_tape_extend_right(self):
        """Test tape extends when moving right past boundary."""
        tape = Tape("1")
        tape.move("R")
        assert tape.read() == "_"  # Should auto-extend

    def test_tape_invalid_direction(self):
        """Test invalid direction raises error."""
        tape = Tape("1")
        with pytest.raises(ValueError, match="Invalid direction"):
            tape.move("X")


class TestTuringMachine:
    """Tests for TuringMachine class."""

    @pytest.fixture
    def simple_config(self):
        """Create a simple TM configuration for testing."""
        return TMConfig(
            states={"q0", "q_halt"},
            alphabet={"0", "1", "_"},
            transitions={
                ("q0", "1"): ("q_halt", "0", "R"),
            },
            initial_state="q0",
            halting_states={"q_halt"},
            blank_symbol="_",
        )

    def test_tm_initialization(self, simple_config):
        """Test TM initialization."""
        tm = TuringMachine(simple_config)
        assert tm.current_state == "q0"
        assert tm.steps == 0

    def test_tm_load_tape(self, simple_config):
        """Test loading tape."""
        tm = TuringMachine(simple_config)
        tm.load_tape("111")
        assert tm.tape.get_content() == "111"

    def test_tm_step(self, simple_config):
        """Test single step execution."""
        tm = TuringMachine(simple_config)
        tm.load_tape("1")
        should_continue = tm.step()
        assert not should_continue  # Should halt after one step
        assert tm.current_state == "q_halt"
        assert tm.tape.get_content() == "0"

    def test_tm_run(self, simple_config):
        """Test running TM until halt."""
        tm = TuringMachine(simple_config)
        tm.load_tape("1")
        result = tm.run(max_steps=100)

        assert result.initial_tape == "1"
        assert result.final_tape == "0"
        assert result.final_state == "q_halt"
        assert result.steps_taken == 1
        assert result.halted is True

    def test_tm_reset(self, simple_config):
        """Test resetting TM."""
        tm = TuringMachine(simple_config)
        tm.load_tape("1")
        tm.step()
        tm.reset()

        assert tm.current_state == "q0"
        assert tm.steps == 0

    def test_tm_max_steps(self):
        """Test TM respects max steps limit."""
        # Create a non-halting configuration
        config = TMConfig(
            states={"q0"},
            alphabet={"1", "_"},
            transitions={
                ("q0", "1"): ("q0", "1", "R"),
                ("q0", "_"): ("q0", "_", "R"),
            },
            initial_state="q0",
            halting_states=set(),
            blank_symbol="_",
        )

        tm = TuringMachine(config)
        tm.load_tape("1")
        result = tm.run(max_steps=10)

        assert result.steps_taken == 10
        assert result.halted is False
