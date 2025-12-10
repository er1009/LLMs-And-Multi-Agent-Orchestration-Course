# Context Windows Lab - LLM Performance Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive experimental framework for analyzing context window limitations in Large Language Models (LLMs) through four controlled experiments.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Experiments](#experiments)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Results](#results)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project implements research-grade experiments to investigate critical challenges in LLM context windows:

1. **Lost in the Middle**: How LLMs struggle to retrieve information from middle positions
2. **Context Size Impact**: Performance degradation as context grows
3. **RAG Effectiveness**: Comparing Retrieval-Augmented Generation vs. full context
4. **Context Engineering**: Evaluating SELECT, COMPRESS, and WRITE strategies

### Key Features

- **Reproducible Research**: Seeded randomness, deterministic execution
- **Statistical Rigor**: Multiple runs with confidence intervals
- **Publication-Quality Visualizations**: 300 DPI graphs with error bars
- **Modular Architecture**: Easy to extend and modify
- **Comprehensive Testing**: ≥70% code coverage
- **Local Execution**: Privacy-preserving, no cloud dependencies

---

## Experiments

### Experiment 1: Needle in Haystack (Lost in the Middle)

Demonstrates that LLMs struggle to retrieve facts from the middle of long contexts.

**Methodology**:
- Generate 1000-2000 word documents
- Embed critical facts at: START (0-10%), MIDDLE (45-55%), END (90-100%)
- Measure retrieval accuracy across positions
- Run 10+ trials for statistical validity

**Expected Results**:
- START accuracy: 80-95%
- MIDDLE accuracy: 40-60%
- END accuracy: 80-95%

### Experiment 2: Context Window Size Impact

Analyzes accuracy and latency degradation as context size increases.

**Methodology**:
- Test with 2, 5, 10, 20, 50 documents
- Measure accuracy and latency at each size
- Track token usage
- Generate dual-axis graphs

**Expected Results**:
- Accuracy decreases with context size
- Latency increases linearly or super-linearly
- Sweet spot around 5-10 documents

### Experiment 3: RAG vs Full Context Comparison

Demonstrates RAG superiority in accuracy and speed.

**Methodology**:
- Generate 20+ realistic documents
- Implement vector-based retrieval (ChromaDB)
- Compare identical queries using both approaches
- Measure accuracy, latency, token usage

**Expected Results**:
- RAG accuracy: 85-95%
- Full context accuracy: 50-70%
- RAG latency: 2-5x faster

### Experiment 4: Context Engineering Strategies

Compares three strategies for managing growing context in multi-turn scenarios.

**Strategies**:
1. **SELECT**: RAG-based selective retrieval
2. **COMPRESS**: Automatic summarization
3. **WRITE**: External scratchpad memory

**Methodology**:
- Simulate 10+ sequential agent actions
- Track context growth, latency, accuracy
- Generate comparison tables and trend graphs

---

## Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Ollama**: Local LLM inference engine
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 10GB free space

### Step 1: Install Ollama

```bash
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai/download
```

### Step 2: Pull LLM Model

```bash
ollama pull llama2
# Or use: ollama pull mistral
# Or use: ollama pull phi
```

### Step 3: Verify Ollama

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

### Step 4: Clone Repository

```bash
git clone https://github.com/yourusername/context-windows-lab.git
cd context-windows-lab
```

### Step 5: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env to customize settings
```

---

## Quick Start

### Run All Experiments

```bash
python main.py --all
```

### Run Individual Experiment

```bash
# Experiment 1: Needle in Haystack
python main.py --experiment 1

# Experiment 2: Context Size Impact
python main.py --experiment 2

# Experiment 3: RAG Comparison
python main.py --experiment 3

# Experiment 4: Context Strategies
python main.py --experiment 4
```

### View Results

```bash
# Results are saved in results/ directory
ls results/

# View graphs
open results/graphs/experiment1_lost_in_middle.png
```

---

## Usage

### Command-Line Interface

```bash
python main.py [OPTIONS]

Options:
  --all                 Run all experiments sequentially
  --experiment N        Run specific experiment (1-4)
  --num-runs N         Number of trials per test (default: 10)
  --model NAME         Ollama model to use (default: llama2)
  --seed N             Random seed for reproducibility (default: 42)
  --output-dir DIR     Results output directory (default: ./results)
  --verbose            Enable verbose logging
  --skip-viz           Skip visualization generation
  --help               Show this message and exit
```

### Python API

```python
from src.experiments import (
    NeedleHaystackExperiment,
    ContextSizeExperiment,
    RAGComparisonExperiment,
    StrategyExperiment
)

# Run Experiment 1
exp1 = NeedleHaystackExperiment(model="llama2")
results = exp1.run_full_experiment(num_runs=10, random_seed=42)
exp1.visualize_results(results)
exp1.save_results(results, output_dir="./results/experiment1")

# Results structure
print(results["statistics"]["mean_accuracy"])
print(results["statistics"]["confidence_interval_95"])
```

### Jupyter Notebooks

```bash
jupyter notebook notebooks/

# Available notebooks:
# - 01_experiment1_analysis.ipynb
# - 02_experiment2_analysis.ipynb
# - 03_experiment3_analysis.ipynb
# - 04_experiment4_analysis.ipynb
# - 05_combined_analysis.ipynb
```

---

## Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_TEMPERATURE=0.1

# Experiment Configuration
DEFAULT_NUM_RUNS=10
RANDOM_SEED=42

# Performance Tuning
BATCH_SIZE=32

# Vector Store
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Results
RESULTS_DIR=./results
GRAPH_DPI=300
```

### Programmatic Configuration

```python
from src.config import Config

config = Config(
    ollama_model="mistral",
    num_runs=20,
    random_seed=123,
    output_dir="./custom_results"
)
```

---

## Results

### Output Structure

```
results/
├── experiment1/
│   ├── raw_results.json          # All trial data
│   ├── aggregated_stats.csv      # Statistics
│   └── lost_in_middle.png        # Visualization
├── experiment2/
│   ├── raw_results.json
│   ├── context_size_stats.csv
│   └── context_size_impact.png
├── experiment3/
│   ├── raw_results.json
│   ├── rag_comparison.csv
│   └── rag_vs_full.png
└── experiment4/
    ├── raw_results.json
    ├── strategy_comparison.csv
    └── strategy_trends.png
```

### Interpreting Results

**Experiment 1 Graph**:
- X-axis: Fact position (Start, Middle, End)
- Y-axis: Accuracy percentage
- Error bars: Standard deviation across runs

**Experiment 2 Graph**:
- X-axis: Number of documents
- Y-axis (left): Accuracy percentage
- Y-axis (right): Latency in milliseconds

**Experiment 3 Table**:
| Metric | RAG | Full Context | Improvement |
|--------|-----|--------------|-------------|
| Accuracy | 89.2% | 63.5% | +40.5% |
| Latency | 1250ms | 4300ms | -71.0% |
| Tokens | 800 | 4500 | -82.2% |

---

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Run Specific Test

```bash
pytest tests/test_experiment1.py
pytest tests/test_utils.py -v
```

### Type Checking

```bash
mypy src/
```

### Code Linting

```bash
flake8 src/ tests/
black src/ tests/ --check
```

---

## Troubleshooting

### Issue: Ollama Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve &

# Verify model is available
ollama list
```

### Issue: ChromaDB Errors

```bash
# Reset ChromaDB
rm -rf ./chroma_db

# Reinstall ChromaDB
pip uninstall chromadb -y
pip install chromadb
```

### Issue: Out of Memory

**Solution 1**: Reduce batch size in `.env`:
```
BATCH_SIZE=16  # Instead of 32
```

**Solution 2**: Use smaller model:
```
OLLAMA_MODEL=phi  # Instead of llama2
```

**Solution 3**: Limit context size in code:
```python
config.max_tokens = 4096  # Instead of 8192
```

### Issue: Slow Experiments

**Solution 1**: Reduce number of runs:
```bash
python main.py --experiment 1 --num-runs 5
```

**Solution 2**: Use faster model:
```bash
python main.py --model phi
```

**Solution 3**: Skip visualizations:
```bash
python main.py --skip-viz
```

### Issue: Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Inconsistent Results

**Cause**: Non-deterministic LLM behavior

**Solution**: Verify settings in `.env`:
```
OLLAMA_TEMPERATURE=0.1  # Low temperature for consistency
RANDOM_SEED=42          # Fixed seed
```

---

## Project Structure

```
context-windows-lab/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── main.py                    # Main entry point
│
├── docs/                      # Documentation
│   ├── PRD.md                # Product Requirements
│   ├── ARCHITECTURE.md       # Architecture design
│   └── API.md                # API documentation
│
├── src/                       # Source code
│   ├── __init__.py
│   ├── experiments/          # Experiment implementations
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract base class
│   │   ├── experiment1_needle_haystack.py
│   │   ├── experiment2_context_size.py
│   │   ├── experiment3_rag_comparison.py
│   │   └── experiment4_strategies.py
│   │
│   ├── utils/                # Utility modules
│   │   ├── __init__.py
│   │   ├── ollama_client.py
│   │   ├── evaluation.py
│   │   ├── tokenization.py
│   │   ├── document_generator.py
│   │   └── visualization.py
│   │
│   └── config/               # Configuration
│       ├── __init__.py
│       └── settings.py
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_experiment1.py
│   ├── test_experiment2.py
│   ├── test_experiment3.py
│   ├── test_experiment4.py
│   ├── test_utils.py
│   └── conftest.py
│
├── notebooks/                 # Jupyter notebooks
│   ├── 01_experiment1_analysis.ipynb
│   ├── 02_experiment2_analysis.ipynb
│   ├── 03_experiment3_analysis.ipynb
│   ├── 04_experiment4_analysis.ipynb
│   └── 05_combined_analysis.ipynb
│
├── results/                   # Experiment results
│   └── (generated at runtime)
│
└── data/                      # Generated data
    └── (generated at runtime)
```

---

## Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/context-windows-lab.git
cd context-windows-lab

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pre-commit install
```

### Code Style

This project follows:
- **PEP 8** style guide
- **Black** formatting (line length 100)
- **Google-style** docstrings
- **Type hints** for all functions

### Running Development Tools

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run tests with coverage
pytest --cov=src
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write** tests for your changes
4. **Ensure** all tests pass (`pytest`)
5. **Format** code (`black src/ tests/`)
6. **Commit** changes (`git commit -m 'Add amazing feature'`)
7. **Push** to branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Contribution Guidelines

- Add tests for new features
- Update documentation
- Follow existing code style
- Keep PRs focused and small
- Write clear commit messages

---

## Citation

If you use this code in your research, please cite:

```bibtex
@software{context_windows_lab_2025,
  title = {Context Windows Lab: LLM Performance Analysis},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/context-windows-lab}
}
```

---

## References

- Liu et al. (2023). "Lost in the Middle: How Language Models Use Long Contexts"
- Lewis et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- [LangChain Documentation](https://python.langchain.com/docs/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Inspired by the "Lost in the Middle" research by Liu et al.
- Built with Ollama, LangChain, and ChromaDB
- Developed for M.Sc. research in Computer Science

---

## Contact

- **Author**: Your Name
- **Email**: your.email@example.com
- **Project Link**: https://github.com/yourusername/context-windows-lab
- **Issues**: https://github.com/yourusername/context-windows-lab/issues

---

**Happy Experimenting!** 🚀
