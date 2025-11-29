#!/usr/bin/env python3
"""Launcher script for Route Guide System GUI."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui import main

if __name__ == "__main__":
    main()
