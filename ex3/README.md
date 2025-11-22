# Multi-Agent Translation Pipeline & Turing Machine Simulator

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An M.Sc. research project studying semantic drift in multi-hop machine translation and demonstrating classical Turing Machine simulation.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project implements a research tool to study how spelling errors in source text affect semantic preservation through multi-hop translation chains. It combines:

1. **Turing Machine Simulator** - Classical computational model with configurable behavior
2. **Multi-Agent Translation Pipeline** - Three Claude CLI agents (EN→FR→HE→EN)
3. **Semantic Evaluation** - HuggingFace embeddings for measuring semantic drift
4. **Analysis Framework** - Statistical analysis and visualization tools

### Research Question

**How does input noise (spelling errors) correlate with semantic drift in multi-hop translation?**

---

## Features

### Core Capabilities

- ✅ **Turing Machine Simulation**
  - Configurable via JSON/YAML files
  - Unbounded tape (extends dynamically)
  - Step-by-step execution with optional tracing
  - Halting state detection

- ✅ **Multi-Agent Translation**
  - Three independent agents (English→French→Hebrew→English)
  - Agents defined as Markdown files (triggered via Claude CLI)
  - Deterministic error injection with configurable rates
  - Reproducible results via seeding

- ✅ **Semantic Evaluation**
  - HuggingFace sentence-transformers (no API keys required!)
  - Cosine and Euclidean distance metrics
  - Batch processing for efficiency

- ✅ **Analysis & Visualization**
  - Scatter plots (error rate vs. semantic distance)
  - Trend line analysis with R² statistics
  - CSV/JSON export for further analysis
  - Multi-metric comparison plots

---

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────┐
│                CLI Interface                    │
│           (Click-based commands)                │
└────────┬───────────────────────────────┬────────┘
         │                               │
    ┌────▼────────┐               ┌─────▼──────┐
    │   Turing    │               │ Translation│
    │   Machine   │               │  Pipeline  │
    │  Simulator  │               └─────┬──────┘
    └─────────────┘                     │
                                   ┌────▼────────────┐
                                   │ Claude CLI      │
                                   │ Agents (MD)     │
                                   │ • EN→FR         │
                                   │ • FR→HE         │
                                   │ • HE→EN         │
                                   └────┬────────────┘
                                        │
                                   ┌────▼────────────┐
                                   │  Evaluation     │
                                   │  (HuggingFace)  │
                                   └────┬────────────┘
                                        │
                                   ┌────▼────────────┐
                                   │    Analysis     │
                                   │ (Graphs + Stats)│
                                   └─────────────────┘
```

### Key Design Decisions

1. **Agent-as-Markdown**: Translation logic defined in MD files, executed via Claude CLI
   - ✅ Transparent and version-controllable
   - ✅ Easy to modify and iterate
   - ✅ No LLM API keys in code

2. **Local Embeddings**: HuggingFace sentence-transformers
   - ✅ No API costs
   - ✅ Runs completely offline (after model download)
   - ✅ Fast and reproducible

3. **Modular Architecture**: Each component is independent and testable
   - Turing Machine module
   - Translation orchestration
   - Evaluation engine
   - Analysis toolkit

---

## Installation

### Prerequisites

- **Python 3.9+**
- **Claude CLI** - [Installation Guide](https://github.com/anthropics/claude-code)
- **Git**

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd ex3

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional)
cp config/.env.example .env
# Edit .env if you want to customize embedding model

# 5. Verify Claude CLI is installed
claude --version

# 6. Test installation
python -m src.cli --help
```

### First Run

On first execution, HuggingFace will download the embedding model (~90MB for default model). This happens automatically and is cached locally.

---

## Usage

### Command Overview

The CLI provides four main commands:

```bash
python -m src.cli turing-machine  # Simulate a Turing Machine
python -m src.cli translate-once  # Translate single sentence
python -m src.cli translate-batch # Batch process with varying error rates
python -m src.cli analyze         # Generate visualizations
```

---

### 1. Turing Machine Simulation

Simulate a Turing Machine from a configuration file:

```bash
python -m src.cli turing-machine \
  --config machines/unary_increment.json \
  --tape "111" \
  --max-steps 100
```

**Example Output:**
```
==================================================
RESULTS
==================================================
Initial tape:  111
Final tape:    1111
Final state:   q_halt
Steps taken:   5
Halted:        True
```

#### Creating Custom Machines

See `machines/unary_increment.json` for an example configuration. Format:

```json
{
  "states": ["q0", "q1", "q_halt"],
  "alphabet": ["1", "_"],
  "initial_state": "q0",
  "halting_states": ["q_halt"],
  "blank_symbol": "_",
  "transitions": [
    {"state": "q0", "symbol": "1", "new_state": "q1",
     "write": "0", "move": "R"}
  ]
}
```

---

### 2. Single Translation

Translate a sentence through the pipeline:

```bash
python -m src.cli translate-once \
  --sentence "The quick brown fox jumps over the lazy dog repeatedly and then rests under a tree" \
  --error-rate 0.25 \
  --seed 42
```

**What happens:**
1. Injects 25% spelling errors (deterministic with seed)
2. Translates: EN → FR → HE → EN (via Claude CLI agents)
3. Computes semantic distance using HuggingFace embeddings
4. Displays results

**Example Output:**
```
Original: The quick brown fox jumps over the lazy dog repeatedly...
Corrupted: Teh qwick brwn fox jumps ovr te lazy dog repeitedly...

TRANSLATION RESULTS
======================================================================
French:         Le renard brun rapide saute par-dessus...
Hebrew:         השועל החום המהיר קופץ מעל...
Final (EN):     The fast brown fox jumps over the lazy dog repeatedly...

Cosine distance:    0.052341
Euclidean distance: 1.234567
```

---

### 3. Batch Processing

Process the same sentence with varying error rates:

```bash
python -m src.cli translate-batch \
  --sentence "The quick brown fox jumps over the lazy dog repeatedly and then rests under a tree" \
  --min-error 0.0 \
  --max-error 0.5 \
  --steps 11 \
  --output-dir results
```

**What happens:**
- Runs 11 translations with error rates from 0% to 50%
- Exports CSV and JSON results
- Calculates correlation statistics

**Example Output:**
```
✓ Results saved:
  CSV:  results/batch_results.csv
  JSON: results/batch_results.json

📊 Statistics:
  Correlation: 0.8752
  R²: 0.7660
  Trend: y = 0.1234x + 0.0156
```

---

### 4. Analysis & Visualization

Generate graphs from batch results:

```bash
python -m src.cli analyze \
  --input results/batch_results.json \
  --output results/graphs/analysis.png
```

**Output:**
- `analysis.png` - Scatter plot with trend line
- `multi_metric_analysis.png` - Cosine + Euclidean comparison

---

## Project Structure

```
ex3/
├── src/
│   ├── agents/                   # Translation agents (MD files)
│   │   ├── en_to_fr.md          # English → French
│   │   ├── fr_to_he.md          # French → Hebrew
│   │   └── he_to_en.md          # Hebrew → English
│   ├── turing_machine/          # TM simulator
│   │   ├── tape.py
│   │   ├── tm_simulator.py
│   │   └── config_loader.py
│   ├── translation/             # Translation orchestration
│   │   ├── error_injector.py
│   │   ├── pipeline.py
│   │   └── claude_agent_runner.py
│   ├── evaluation/              # Semantic evaluation
│   │   ├── embedding_provider.py
│   │   ├── hf_embedding.py      # HuggingFace embeddings
│   │   ├── distance.py
│   │   └── engine.py
│   ├── analysis/                # Analysis tools
│   │   ├── graph_generator.py
│   │   ├── statistics.py
│   │   └── exporter.py
│   └── cli.py                   # CLI interface
├── tests/                       # Unit tests
│   ├── unit/
│   └── integration/
├── machines/                    # TM configurations
│   └── unary_increment.json
├── config/
│   └── .env.example
├── docs/
│   ├── PRD.md                   # Product requirements
│   └── ARCHITECTURE.md          # Architecture document
├── results/                     # Generated outputs
├── notebooks/                   # Jupyter notebooks
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Documentation

### Available Documentation

- **[PRD.md](docs/PRD.md)** - Product Requirements Document
  - Functional and non-functional requirements
  - Use cases and acceptance criteria
  - Timeline and deliverables

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture Document
  - C4 model diagrams
  - Component interactions
  - Technology stack justification
  - Architecture Decision Records (ADRs)

### Agent Definitions

Translation agents are defined in Markdown format:

- `src/agents/en_to_fr.md` - English to French translation guidelines
- `src/agents/fr_to_he.md` - French to Hebrew translation guidelines
- `src/agents/he_to_en.md` - Hebrew to English translation guidelines

These files are passed to Claude CLI for execution.

---

## Examples

### Example 1: Testing TM with Different Inputs

```bash
# Test with unary number 5 (represented as "11111")
python -m src.cli turing-machine \
  --config machines/unary_increment.json \
  --tape "11111" \
  --max-steps 100
# Expected: "111111" (adds one 1)
```

### Example 2: Sensitivity Analysis

Run batch processing with different error ranges:

```bash
# Fine-grained analysis (0-30%, 16 steps)
python -m src.cli translate-batch \
  --sentence "Your test sentence here with at least fifteen words to meet requirements" \
  --min-error 0.0 \
  --max-error 0.3 \
  --steps 16 \
  --output-dir results/fine_grained
```

### Example 3: Export with Custom Seed

```bash
# Reproducible results with custom seed
python -m src.cli translate-once \
  --sentence "Scientists discovered a new species of butterfly in the Amazon rainforest yesterday" \
  --error-rate 0.20 \
  --seed 12345 \
  --output results/sample_output.json
```

---

## Troubleshooting

### Common Issues

**1. Claude CLI not found**
```
Error: claude: command not found
```
**Solution:** Install Claude CLI - [Installation Guide](https://github.com/anthropics/claude-code)

**2. Model download fails**
```
Error: Connection timeout downloading model
```
**Solution:** Check internet connection. Model downloads automatically on first run.

**3. Sentence too short**
```
Error: Sentence must contain at least 15 words (got 8)
```
**Solution:** Provide a sentence with ≥15 words as required by specification.

**4. Import errors**
```
ModuleNotFoundError: No module named 'sentence_transformers'
```
**Solution:** Install dependencies: `pip install -r requirements.txt`

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test module
pytest tests/unit/test_turing_machine.py
```

### Test Structure

```
tests/
├── unit/
│   ├── test_turing_machine.py
│   ├── test_error_injector.py
│   ├── test_embedding.py
│   └── test_distance.py
└── integration/
    ├── test_pipeline.py
    └── test_cli.py
```

---

## Performance Considerations

### Embedding Model Comparison

| Model | Dimensions | Speed | Quality | Size |
|-------|-----------|-------|---------|------|
| `all-MiniLM-L6-v2` (default) | 384 | Fast | Good | ~90MB |
| `all-mpnet-base-v2` | 768 | Slower | Better | ~420MB |
| `paraphrase-MiniLM-L3-v2` | 384 | Fastest | Fair | ~60MB |

To change model, set in `.env`:
```bash
EMBEDDING_MODEL=all-mpnet-base-v2
```

### Batch Processing Performance

- Single translation: ~30-60 seconds (depends on Claude CLI)
- Batch of 10: ~5-10 minutes
- Embedding generation: ~0.1-0.5 seconds per sentence (after model load)

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Follow code style (PEP 8)
4. Add tests for new features
5. Update documentation
6. Submit a pull request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- **Dr. Yoram Segal** - For M.Sc. project guidelines
- **HuggingFace** - For sentence-transformers library
- **Anthropic** - For Claude CLI
- **Python Community** - For excellent open-source libraries

---

## Citation

If you use this project in your research, please cite:

```bibtex
@software{translation_tm_simulator_2025,
  author = {M.Sc. Project Team},
  title = {Multi-Agent Translation Pipeline & Turing Machine Simulator},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/yourusername/ex3}
}
```

---

## Contact

For questions or issues, please:
- Open an issue on GitHub
- Contact the project maintainers
- See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details

---
