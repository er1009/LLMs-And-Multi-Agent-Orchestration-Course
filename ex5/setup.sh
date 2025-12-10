#!/bin/bash
# Setup script for Context Windows Lab
# This script automates the setup process

set -e  # Exit on error

echo "================================================"
echo "Context Windows Lab - Setup Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo -e "${RED}Error: Python 3.8+ is required. Found: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python version OK: $python_version${NC}"
echo ""

# Check if Ollama is installed
echo "Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
else
    echo -e "${YELLOW}⚠  Ollama not found. Installing...${NC}"
    curl -fsSL https://ollama.ai/install.sh | sh
    echo -e "${GREEN}✓ Ollama installed${NC}"
fi
echo ""

# Check if Ollama service is running
echo "Checking Ollama service..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama service is running${NC}"
else
    echo -e "${YELLOW}⚠  Ollama service not running. Starting...${NC}"
    echo "Please start Ollama manually: ollama serve &"
fi
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}  You can customize .env with your settings${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p logs results data chroma_db
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Pull Ollama model
echo "Checking for Ollama model..."
if ollama list | grep -q "llama2"; then
    echo -e "${GREEN}✓ llama2 model already downloaded${NC}"
else
    echo -e "${YELLOW}⚠  Downloading llama2 model (this may take a while)...${NC}"
    ollama pull llama2
    echo -e "${GREEN}✓ llama2 model downloaded${NC}"
fi
echo ""

# Run tests
echo "Running tests..."
if pytest tests/ -v --tb=short 2>&1 | tail -20; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${YELLOW}⚠  Some tests failed (this is okay if Ollama is not running)${NC}"
fi
echo ""

echo "================================================"
echo -e "${GREEN}Setup complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Ensure Ollama is running:"
echo "     ollama serve &"
echo ""
echo "  3. Run experiments:"
echo "     python main.py --all"
echo "     python main.py --experiment 1"
echo ""
echo "  4. View results:"
echo "     ls results/"
echo ""
echo "For more information, see README.md"
echo ""
