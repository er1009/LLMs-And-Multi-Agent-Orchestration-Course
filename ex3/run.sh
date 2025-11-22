#!/bin/bash

# Wrapper script to run the CLI tool
# Usage: ./run.sh <command> [arguments]

# Activate virtual environment
source venv/bin/activate

# Set Python path to src directory
export PYTHONPATH="/Users/eldadron/dev/agents-course/ex3/src"

# Run the CLI
python -m cli "$@"
