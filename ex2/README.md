# LSTM Signal Extraction

A PyTorch-based LSTM neural network that performs conditional regression to extract individual frequency components from mixed noisy signals.

## Project Status

✅ **Complete** - A fully functional LSTM system that extracts individual frequency components from mixed noisy signals using conditional regression.

## Overview

This project implements an LSTM network that:
- Takes a mixed noisy signal `S(t)` composed of 4 different sinusoidal frequencies
- Uses a one-hot encoded frequency selector `C` to determine which frequency to extract
- Outputs the pure target frequency component `Target_i(t)` while ignoring noise

### Problem Statement

Given a mixed and noisy signal `S(t)` with random amplitude and phase noise at each sample, the system extracts each pure frequency component separately using conditional regression.

## Quick Start

### Prerequisites

- Python 3.8+ (Python 3.11 recommended)
- PyTorch 2.0+ (CPU or CUDA)
- NumPy, Matplotlib for visualization

### Installation Instructions

Follow these steps carefully to set up and run the project:

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ex2
```

Replace `<repository-url>` with the actual repository URL.

#### Step 2: Set Up Python Environment

You must use a virtual environment (venv or conda) as required. Choose one option:

**Option A: Using Conda (Recommended)**

```bash
# Create conda environment with Python 3.11
conda create -n lstm-signal python=3.11 -y

# Activate the environment
conda activate lstm-signal

# Verify Python version (should show 3.11.x)
python --version

# Install all required dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(torch|numpy|matplotlib|pytest)"
```

**Option B: Using Python venv**

```bash
# Create virtual environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Verify Python version
python --version

# Install all required dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(torch|numpy|matplotlib|pytest)"
```

**Expected Result:** 
- Virtual environment is created and activated
- Python 3.8+ is available
- All packages from `requirements.txt` are installed (torch, numpy, matplotlib, pytest)

#### Step 3: Verify PyTorch Installation

```bash
# Make sure environment is activated
conda activate lstm-signal  # or: source venv/bin/activate

# Verify PyTorch installation
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

**Expected Result:**
- PyTorch is installed and importable
- CUDA availability is reported (optional, for NVIDIA GPUs)
- MPS availability is reported (optional, for Mac with Apple Silicon)

#### Step 4: Run the Training Pipeline

```bash
# Make sure conda/venv environment is activated
conda activate lstm-signal  # or: source venv/bin/activate

# Run the training pipeline with default parameters
python -m src.main

# Or with custom parameters
python -m src.main --num-epochs 20 --hidden-size 128 --learning-rate 0.001

# Use MPS (Metal Performance Shaders) on Mac
python -m src.main --device mps

# Auto-detect best available device (default)
python -m src.main --device auto
```

**Expected Result:**
- Training pipeline starts
- Dataset is generated (40,000 training samples, 40,000 test samples)
- Model is created and trained
- MSE_train and MSE_test are calculated
- Generalization is checked
- Visualizations are generated and saved to `outputs/plots/`
- Model is saved to `outputs/models/`

#### Command-Line Arguments

```bash
python -m src.main --help
```

Available arguments:
- `--frequencies`: Frequencies in Hz (default: 1.0 3.0 5.0 7.0)
- `--sampling-rate`: Sampling rate in Hz (default: 1000.0)
- `--duration`: Signal duration in seconds (default: 10.0)
- `--train-seed`: Random seed for training set (default: 1)
- `--test-seed`: Random seed for test set (default: 2)
- `--hidden-size`: LSTM hidden state size (default: 64)
- `--num-layers`: Number of LSTM layers (default: 1)
- `--learning-rate`: Learning rate (default: 0.001)
- `--num-epochs`: Number of training epochs (default: 10)
- `--batch-size`: Batch size (default: 1)
- `--device`: Device to use ('auto', 'cpu', 'cuda', or 'mps', default: 'auto')
  - `auto`: Automatically detect best available device (CUDA > MPS > CPU)
  - `cpu`: Use CPU
  - `cuda`: Use CUDA (NVIDIA GPUs)
  - `mps`: Use MPS (Metal Performance Shaders for Mac)
- `--output-dir`: Output directory (default: 'outputs')

#### Troubleshooting

**If the training doesn't start:**
1. Verify Python environment is activated: `which python` should show the venv/conda path
2. Verify dependencies are installed: `pip list | grep torch`
3. Check for error messages in the terminal

**If training is slow:**
1. Reduce `--num-epochs` for testing
2. Reduce `--duration` to generate smaller datasets
3. Use `--device mps` on Mac with Apple Silicon (M1/M2/M3)
4. Use `--device cuda` if CUDA is available
5. Use `--device auto` to automatically select the best available device

**If MSE values are very high:**
1. Increase `--num-epochs` for more training
2. Adjust `--learning-rate` (try 0.0001 or 0.01)
3. Increase `--hidden-size` for more model capacity

## Project Structure

```
ex2/
├── README.md                 # This file
├── PRD.md                    # Product Requirements Document
├── requirements.txt          # Python dependencies
├── src/                      # Source code
│   ├── __init__.py
│   ├── main.py              # Entry point for training
│   ├── data/
│   │   ├── __init__.py
│   │   ├── dataset.py       # Dataset generation
│   │   └── dataloader.py    # PyTorch DataLoader wrapper
│   ├── model/
│   │   ├── __init__.py
│   │   └── lstm_model.py    # LSTM architecture
│   ├── training/
│   │   ├── __init__.py
│   │   ├── trainer.py       # Training loop
│   │   └── evaluator.py     # Evaluation and generalization
│   └── visualization/
│       ├── __init__.py
│       └── plots.py         # Graph generation
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_dataset.py      # Test data generation
│   ├── test_model.py        # Test LSTM model
│   └── test_integration.py  # End-to-end tests
├── Documentation/            # Development documentation
│   ├── PRD_PROMPT.md        # Initial prompt for PRD
│   ├── DEVELOPMENT.md       # Development process notes
│   └── AI_PROMPTS.md        # AI prompting documentation
└── outputs/
    ├── models/              # Saved model checkpoints
    └── plots/               # Generated graphs
```

## Unit Tests

### Running Tests

```bash
# Make sure environment is activated
conda activate lstm-signal  # or: source venv/bin/activate

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_dataset.py
pytest tests/test_model.py
pytest tests/test_integration.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Unit Tests with Expected Results

All unit tests include the expected result in their docstrings. Below are the unit tests and their expected results:

#### Test 1: `test_dataset_initialization()`
**Expected Result:** Dataset initializes with correct default parameters.
- Frequencies: [1.0, 3.0, 5.0, 7.0]
- Sampling rate: 1000.0 Hz
- Duration: 10.0 seconds
- Number of samples: 10,000

#### Test 2: `test_generate_dataset()`
**Expected Result:** Dataset generation produces correct shapes and values.
- Inputs shape: (40000, 5) - 10,000 samples × 4 frequencies
- Targets shape: (40000,)
- Input structure: [S[t], C1, C2, C3, C4] where C is one-hot encoded
- Targets range: [-1, 1] (pure sine waves)

#### Test 3: `test_model_forward_pass()`
**Expected Result:** Model forward pass produces correct output shape.
- Input shape: (batch_size, 5)
- Output shape: (batch_size, 1)
- Hidden state shape: (num_layers, batch_size, hidden_size)

#### Test 4: `test_model_reset_state()`
**Expected Result:** State reset produces zero-initialized hidden states.
- Hidden state shape: (num_layers, batch_size, hidden_size)
- All values are zero

#### Test 5: `test_full_pipeline_small()`
**Expected Result:** Full pipeline runs successfully with small dataset.
- Training completes without errors
- MSE_train is calculated and positive
- MSE_test is calculated and positive
- MSE values are reasonable (< 10.0)

#### Test 6: `test_generalization_check()`
**Expected Result:** Generalization check produces valid results.
- MSE_train and MSE_test are calculated
- Relative difference is calculated
- Generalization status is boolean

#### Test 7: `test_model_can_learn()`
**Expected Result:** Model can learn (loss decreases over epochs).
- Training loss decreases over epochs
- Final loss is positive and reasonable

### Example Test Output

**When all tests pass:**
```
test_dataset.py::test_dataset_initialization PASSED
test_dataset.py::test_generate_dataset PASSED
test_model.py::test_model_forward_pass PASSED
test_model.py::test_model_reset_state PASSED
test_integration.py::test_full_pipeline_small PASSED
test_integration.py::test_generalization_check PASSED
test_integration.py::test_model_can_learn PASSED
```

## Expected Results

### Training Output

After running the training pipeline, you should see:

```
============================================================
LSTM Signal Extraction - Training Pipeline
============================================================
Using device: MPS (Metal Performance Shaders)

[1/6] Generating datasets...
  Training samples: 40000
  Test samples: 40000

[2/6] Creating LSTM model...
  Model parameters: 4,225

[3/6] Training model...
Epoch 1/10 - Loss: 0.123456 - MSE_train: 0.123456
Epoch 2/10 - Loss: 0.098765 - MSE_train: 0.098765
...
Epoch 10/10 - Loss: 0.012345 - MSE_train: 0.012345

  Final MSE_train: 0.012345

[4/6] Evaluating on test set...
  MSE_test: 0.012678

[5/6] Checking generalization...
  Relative difference: 0.0269
  ✓ Model generalizes well!

[6/6] Generating predictions for visualization...
[7/6] Creating visualizations...
Saved plot to outputs/plots/single_frequency_comparison.png
Saved plot to outputs/plots/all_frequencies.png
Saved plot to outputs/plots/training_history.png
Saved plot to outputs/plots/mse_comparison.png

[8/6] Saving model...
  Model saved to outputs/models/lstm_model.pt

============================================================
Training Complete!
============================================================
MSE_train: 0.012345
MSE_test: 0.012678
Generalization: Good

Outputs saved to: outputs
  - Model: outputs/models
  - Plots: outputs/plots
============================================================
```

### Success Criteria

1. **MSE_train and MSE_test are calculated correctly**
   - Both values should be positive
   - Values should decrease over training epochs

2. **MSE_test ≈ MSE_train (good generalization)**
   - Relative difference should be < 0.1 (10%)
   - Model should generalize well to unseen noise

3. **Visualizations are generated**
   - `single_frequency_comparison.png`: Comparison for one frequency
   - `all_frequencies.png`: All 4 frequency extractions
   - `training_history.png`: Training loss and MSE over epochs
   - `mse_comparison.png`: MSE_train vs MSE_test comparison

4. **Model is saved**
   - `lstm_model.pt`: Saved model checkpoint

## Key Technical Points

1. **Sequence Length L=1:** Each sample is processed independently, but state is passed from one sample to the next
2. **State Management:** Critical for this exercise - do NOT reset `h_t` and `c_t` between consecutive samples; pass state from previous sample to current sample
3. **Conditional Input:** One-hot vector tells LSTM which frequency to extract
4. **Data Generation:** Two separate datasets with different seeds for train/test generalization check
5. **Noise Variation:** Amplitude and phase noise vary at every sample `t`

## Documentation

See `Documentation/` folder for detailed development documentation:

- **PRD_PROMPT.md**: Initial prompt used to create the Product Requirements Document
- **AI_PROMPTS.md**: All prompts used with AI assistants, iterations, and lessons learned
- **DEVELOPMENT.md**: Complete development process, decisions, challenges, and solutions

These documents provide full transparency into:
- How the PRD was created
- How AI assistants were used and prompted
- Development decisions and rationale
- Challenges encountered and solutions
- Lessons learned throughout the project

## Contributors

_To be added: Team members_

## License

_To be added if applicable_

