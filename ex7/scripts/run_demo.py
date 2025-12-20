#!/usr/bin/env python3
"""
Quick Demo - Run a simple league with 4 players.

This is a simplified entry point for the league orchestrator.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the demo."""
    # Run the main orchestrator with default settings
    script_path = Path(__file__).parent / "run_league.py"

    subprocess.run(
        [sys.executable, str(script_path), "--players", "4"],
        cwd=str(Path(__file__).parent.parent),
    )


if __name__ == "__main__":
    main()
