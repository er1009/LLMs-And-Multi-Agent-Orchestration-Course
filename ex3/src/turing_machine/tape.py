"""
Tape implementation for Turing Machine.

The tape is unbounded in both directions and uses a blank symbol
for uninitialized cells.
"""

from typing import List


class Tape:
    """
    Represents an infinite tape for a Turing Machine.

    The tape is implemented as a dynamic list that grows as needed.
    The head position tracks the current location on the tape.

    Attributes:
        cells: List of symbols on the tape
        head_position: Current position of the read/write head
        blank_symbol: Symbol used for blank cells
    """

    def __init__(self, content: str = "", blank_symbol: str = "_"):
        """
        Initialize the tape with optional content.

        Args:
            content: Initial content to write on the tape
            blank_symbol: Symbol to use for blank cells (default: "_")
        """
        self.blank_symbol = blank_symbol
        self.cells: List[str] = list(content) if content else [blank_symbol]
        self.head_position = 0

    def read(self) -> str:
        """
        Read the symbol at the current head position.

        Returns:
            The symbol at the current position
        """
        self._ensure_position_exists()
        return self.cells[self.head_position]

    def write(self, symbol: str) -> None:
        """
        Write a symbol at the current head position.

        Args:
            symbol: The symbol to write
        """
        self._ensure_position_exists()
        self.cells[self.head_position] = symbol

    def move(self, direction: str) -> None:
        """
        Move the head left or right.

        Args:
            direction: "L" for left, "R" for right

        Raises:
            ValueError: If direction is not "L" or "R"
        """
        if direction == "R":
            self.head_position += 1
        elif direction == "L":
            self.head_position -= 1
        else:
            raise ValueError(f"Invalid direction: {direction}. Must be 'L' or 'R'")

        self._ensure_position_exists()

    def _ensure_position_exists(self) -> None:
        """
        Extend the tape if the head position is outside current bounds.
        """
        # Extend right if needed
        while self.head_position >= len(self.cells):
            self.cells.append(self.blank_symbol)

        # Extend left if needed
        while self.head_position < 0:
            self.cells.insert(0, self.blank_symbol)
            self.head_position += 1

    def get_content(self, strip_blanks: bool = True) -> str:
        """
        Get the current tape content as a string.

        Args:
            strip_blanks: If True, remove leading/trailing blank symbols

        Returns:
            String representation of the tape content
        """
        content = "".join(self.cells)
        if strip_blanks:
            content = content.strip(self.blank_symbol)
        return content if content else self.blank_symbol

    def __str__(self) -> str:
        """String representation of the tape with head position indicator."""
        tape_str = "".join(self.cells)
        head_indicator = " " * self.head_position + "^"
        return f"{tape_str}\n{head_indicator}"
