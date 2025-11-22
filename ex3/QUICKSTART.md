# Quick Start Guide

Get up and running with the Multi-Agent Translation Pipeline & Turing Machine Simulator in 5 minutes!

---

## Prerequisites Checklist

Before starting, ensure you have:

- ✅ **Python 3.9+** installed (`python --version`)
- ✅ **Claude CLI** installed (`claude --version`)
  - If not installed: [Install Guide](https://github.com/anthropics/claude-code)
- ✅ **Git** installed
- ✅ **Internet connection** (for first-time model download)

---

## Installation (3 steps)

### 1. Clone & Navigate

```bash
git clone <repository-url>
cd ex3
```

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Check CLI is accessible
python -m src.cli --help

# Should show 4 commands:
# - turing-machine
# - translate-once
# - translate-batch
# - analyze
```

---

## Your First Turing Machine (30 seconds)

Run a simple unary increment machine:

```bash
python -m src.cli turing-machine \
  --config machines/unary_increment.json \
  --tape "111" \
  --max-steps 100
```

**Expected output:**
```
Initial tape:  111
Final tape:    1111
Steps taken:   5
```

✅ **Success!** The machine added one `1` to your tape.

---

## Your First Translation (2 minutes)

Translate a sentence through the pipeline:

```bash
python -m src.cli translate-once \
  --sentence "The quick brown fox jumps over the lazy dog and then rests under a big tree" \
  --error-rate 0.0 \
  --seed 42
```

**What happens:**
1. Translates: English → French → Hebrew → English
2. Computes semantic similarity
3. Displays results

**Note:** First run downloads HuggingFace model (~90MB). Subsequent runs are instant.

---

## Your First Analysis (5 minutes)

Run a batch experiment and generate graphs:

### Step 1: Generate Data

```bash
python -m src.cli translate-batch \
  --sentence "Scientists discovered a new species of butterfly in the Amazon rainforest yesterday morning" \
  --min-error 0.0 \
  --max-error 0.3 \
  --steps 7 \
  --output-dir results
```

This runs 7 experiments with error rates: 0%, 5%, 10%, 15%, 20%, 25%, 30%

⏱️ **Time:** ~3-5 minutes (depends on Claude CLI response time)

### Step 2: Generate Graphs

```bash
python -m src.cli analyze \
  --input results/batch_results.json \
  --output results/graphs/analysis.png
```

### Step 3: View Results

Open these files:
- **CSV:** `results/batch_results.csv` (spreadsheet)
- **Graph:** `results/graphs/analysis.png` (scatter plot)
- **JSON:** `results/batch_results.json` (raw data)

---

## Project Structure Overview

```
ex3/
├── src/
│   ├── agents/          # Translation agents (MD files)
│   ├── turing_machine/  # TM simulator
│   ├── translation/     # Pipeline orchestration
│   ├── evaluation/      # Embeddings & distance
│   ├── analysis/        # Graphs & stats
│   └── cli.py          # Main CLI
├── machines/           # TM configurations
├── tests/              # Unit tests
├── notebooks/          # Jupyter analysis
├── docs/               # PRD & Architecture
└── results/            # Generated outputs
```

---

## Common Commands

### Test Different Error Rates

```bash
# No errors (baseline)
python -m src.cli translate-once \
  --sentence "Your sentence here..." \
  --error-rate 0.0

# 25% errors
python -m src.cli translate-once \
  --sentence "Your sentence here..." \
  --error-rate 0.25

# 50% errors (max)
python -m src.cli translate-once \
  --sentence "Your sentence here..." \
  --error-rate 0.5
```

### Save Results to File

```bash
python -m src.cli translate-once \
  --sentence "Your sentence..." \
  --error-rate 0.2 \
  --output my_results.json
```

### Create Custom TM

1. Copy `machines/unary_increment.json`
2. Modify transitions
3. Run: `python -m src.cli turing-machine --config my_machine.json --tape "..."`

---

## Next Steps

### 📚 Learn More

- Read **[README.md](README.md)** for detailed documentation
- Review **[docs/PRD.md](docs/PRD.md)** for requirements
- Check **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for design details

### 🔬 Run Experiments

- Try different sentences
- Vary error rates (0.0 to 0.5)
- Compare results across languages

### 📊 Analyze Data

- Open `notebooks/analysis_example.ipynb`
- Run statistical tests
- Generate custom visualizations

### 🧪 Run Tests

```bash
pytest                    # Run all tests
pytest --cov=src         # With coverage
```

---

## Troubleshooting

### Issue: "claude: command not found"

**Solution:** Install Claude CLI
```bash
# Follow installation guide at:
# https://github.com/anthropics/claude-code
```

### Issue: Model download fails

**Solution:** Check internet connection. Models download on first run (~90MB).

### Issue: "Sentence must contain at least 15 words"

**Solution:** Provide longer sentence:
```bash
--sentence "The quick brown fox jumps over the lazy dog and then rests peacefully under a very big tree"
```

### Issue: Import errors

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

---

## Support

- **Documentation:** See [README.md](README.md)
- **Issues:** Open an issue on GitHub
- **Architecture:** See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

**Ready to explore? Start with the Turing machine example above!** 🚀
