# LSTM Signal Extraction - Architecture Document

## 1. Overview

This document describes the architecture of the LSTM Signal Extraction system, which uses a conditional LSTM neural network to extract individual frequency components from mixed noisy signals.

## 2. System Context (C4 Level 1)

### 2.1 Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LSTM Signal Extraction System            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Data       │───▶│   Training   │───▶│  Evaluation  │ │
│  │  Generation │    │   Pipeline   │    │   & Results  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                   │                    │          │
│         └───────────────────┴────────────────────┘          │
│                            │                                │
│                    ┌───────▼────────┐                       │
│                    │  Visualization │                       │
│                    └────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**Actors:**
- **Researcher/Developer**: Runs training pipeline, analyzes results
- **System**: Processes signals, trains model, generates visualizations

**External Systems:**
- **PyTorch**: Deep learning framework
- **NumPy**: Numerical computations
- **Matplotlib**: Visualization generation

## 3. Container Architecture (C4 Level 2)

### 3.1 Container Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Container                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Main Entry Point (main.py)              │  │
│  │  - Orchestrates pipeline                             │  │
│  │  - Manages device selection                          │  │
│  │  - Coordinates modules                                │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│        ┌──────────────────┼──────────────────┐             │
│        │                  │                  │             │
│  ┌─────▼─────┐    ┌──────▼──────┐   ┌─────▼─────┐       │
│  │   Data    │    │    Model     │   │ Training  │       │
│  │  Module   │    │   Module     │   │  Module   │       │
│  └───────────┘    └──────────────┘   └───────────┘       │
│        │                  │                  │             │
│        └──────────────────┼──────────────────┘             │
│                           │                                 │
│                  ┌────────▼─────────┐                      │
│                  │  Visualization    │                      │
│                  │     Module       │                      │
│                  └──────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Container Responsibilities

1. **Data Module** (`src/data/`)
   - Generates synthetic signal datasets
   - Creates train/test splits with different random seeds
   - Provides PyTorch DataLoader wrappers

2. **Model Module** (`src/model/`)
   - Defines LSTM architecture
   - Manages hidden state for temporal dependencies
   - Handles conditional input processing

3. **Training Module** (`src/training/`)
   - Implements training loop with state management
   - Calculates loss and metrics
   - Manages optimizer and learning rate scheduling

4. **Evaluation Module** (`src/training/evaluator.py`)
   - Evaluates model on test set
   - Checks generalization (train vs test MSE)
   - Generates predictions for visualization

5. **Visualization Module** (`src/visualization/`)
   - Creates comparison plots
   - Generates training history visualizations
   - Saves plots to disk

## 4. Component Architecture (C4 Level 3)

### 4.1 Data Module Components

```
┌─────────────────────────────────────────┐
│         Data Module                     │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   SignalDataset                   │ │
│  │   - generate_clean_signal()      │ │
│  │   - generate_noisy_signal()      │ │
│  │   - generate_mixed_signal()      │ │
│  │   - generate_pure_target()       │ │
│  │   - generate_dataset()            │ │
│  └───────────────────────────────────┘ │
│                 │                       │
│  ┌──────────────▼───────────────────┐ │
│  │   SignalPyTorchDataset           │ │
│  │   - PyTorch Dataset wrapper      │ │
│  └──────────────────────────────────┘ │
│                 │                       │
│  ┌──────────────▼───────────────────┐ │
│  │   create_dataloaders()           │ │
│  │   - Creates train/test loaders   │ │
│  └──────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 4.2 Model Module Components

```
┌─────────────────────────────────────────┐
│         Model Module                    │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   ConditionalLSTM                  │ │
│  │   - __init__()                    │ │
│  │   - forward()                     │ │
│  │   - reset_state()                 │ │
│  │   - predict_single()              │ │
│  │                                     │ │
│  │   Architecture:                    │ │
│  │   Input (5) → LSTM → Linear →     │ │
│  │   Output (1)                       │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 4.3 Training Module Components

```
┌─────────────────────────────────────────┐
│         Training Module                 │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Trainer                         │ │
│  │   - train_epoch()                 │ │
│  │   - train()                       │ │
│  │   - calculate_mse()               │ │
│  │   - save_model()                  │ │
│  │   - load_model()                  │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Evaluator                       │ │
│  │   - evaluate()                    │ │
│  │   - check_generalization()        │ │
│  │   - predict_all_frequencies()      │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 5. Technology Stack

### 5.1 Core Technologies

| Technology | Version | Purpose | Justification |
|------------|---------|---------|---------------|
| Python | 3.8+ | Programming language | Standard for ML research |
| PyTorch | ≥2.0.0 | Deep learning framework | Industry standard, good state management |
| NumPy | ≥1.24.0 | Numerical computing | Efficient array operations |
| Matplotlib | ≥3.7.0 | Visualization | Standard plotting library |
| pytest | ≥7.4.0 | Testing framework | Standard Python testing |

### 5.2 Technology Choices

**PyTorch Selection:**
- **Rationale**: Provides fine-grained control over LSTM hidden states, which is critical for this exercise
- **Alternatives Considered**: TensorFlow/Keras (less control over state management)
- **Trade-off**: More verbose code but better control

**NumPy for Data Generation:**
- **Rationale**: Efficient array operations for signal generation
- **Trade-off**: Requires conversion to PyTorch tensors, but acceptable for data generation

**Matplotlib for Visualization:**
- **Rationale**: Standard, well-documented, sufficient for research plots
- **Trade-off**: Not interactive, but adequate for static visualizations

## 6. Data Flow Architecture

### 6.1 Training Pipeline Data Flow

```
┌──────────────┐
│ Random Seeds │
│ (1 for train)│
└──────┬───────┘
       │
       ▼
┌──────────────────┐      ┌──────────────┐      ┌─────────────┐
│ SignalDataset   │─────▶│ DataLoader   │─────▶│ LSTM Model  │
│ Generate Data   │      │ Batch Data   │      │ Forward Pass│
└──────────────────┘      └──────────────┘      └──────┬──────┘
                                                        │
                                                        ▼
┌──────────────────┐      ┌──────────────┐      ┌─────────────┐
│ Loss Calculation │◀─────│ Compare with  │◀─────│ Predictions │
│ (MSE)            │      │ Targets       │      └─────────────┘
└──────┬───────────┘      └──────────────┘
       │
       ▼
┌──────────────────┐
│ Backpropagation  │
│ & Optimization   │
└──────────────────┘
```

### 6.2 Evaluation Pipeline Data Flow

```
┌──────────────┐
│ Random Seed  │
│ (2 for test) │
└──────┬───────┘
       │
       ▼
┌──────────────────┐      ┌──────────────┐      ┌─────────────┐
│ SignalDataset   │─────▶│ DataLoader   │─────▶│ LSTM Model  │
│ Generate Data   │      │ Batch Data   │      │ (Eval Mode) │
└──────────────────┘      └──────────────┘      └──────┬──────┘
                                                        │
                                                        ▼
┌──────────────────┐      ┌──────────────┐      ┌─────────────┐
│ MSE Calculation  │◀─────│ Compare with │◀─────│ Predictions │
│ & Generalization │      │ Targets      │      └─────────────┘
└──────────────────┘      └──────────────┘
```

## 7. Component Interactions

### 7.1 Sequence Diagram: Training Process

```
Main → DataModule → Trainer → Model → Evaluator → Visualization
 │        │          │         │         │            │
 │        │          │         │         │            │
 │───Generate Dataset──────────│         │            │
 │        │          │         │         │            │
 │        │───Create DataLoader──────────│            │
 │        │          │         │         │            │
 │        │          │───Train Epoch─────│            │
 │        │          │    │     │         │            │
 │        │          │    │──Forward Pass│            │
 │        │          │    │     │         │            │
 │        │          │    │──Backward Pass───────────│
 │        │          │    │     │         │            │
 │        │          │───Evaluate─────────│            │
 │        │          │    │     │         │            │
 │        │          │    │──Generate Predictions────│
 │        │          │    │     │         │            │
 │        │          │    │     │         │───Create Plots
```

### 7.2 State Management Flow

```
Epoch Start
    │
    ▼
Initialize hidden_state = None
    │
    ▼
For each sample:
    │
    ├─► Check if frequency changed
    │   │
    │   ├─► Yes: Reset hidden_state
    │   └─► No: Continue with previous state
    │
    ├─► Forward pass with hidden_state
    │
    ├─► Update hidden_state from output
    │
    └─► Detach state (break computation graph)
```

## 8. Data Schemas

### 8.1 Input Schema

**Single Sample:**
```python
Input: np.ndarray, shape (5,)
  [0]: S[t] - Mixed noisy signal value at time t (float)
  [1]: C1 - One-hot frequency selector for f1 (0.0 or 1.0)
  [2]: C2 - One-hot frequency selector for f2 (0.0 or 1.0)
  [3]: C3 - One-hot frequency selector for f3 (0.0 or 1.0)
  [4]: C4 - One-hot frequency selector for f4 (0.0 or 1.0)
```

**Sequence Input:**
```python
Input: np.ndarray, shape (L, 5) where L = sequence_length
  Each row: [S[t], C1, C2, C3, C4]
```

### 8.2 Output Schema

**Single Sample:**
```python
Output: float
  Target_i[t] - Predicted pure frequency component value
```

**Sequence Output:**
```python
Output: np.ndarray, shape (L,)
  Array of predicted values for sequence
```

### 8.3 Dataset Schema

```python
Dataset Structure:
  - inputs: np.ndarray, shape (N, 5) or (N, L, 5)
  - targets: np.ndarray, shape (N,) or (N, L)
  where N = num_samples × num_frequencies
```

## 9. API Interfaces

### 9.1 Internal Module Interfaces

**SignalDataset Interface:**
```python
class SignalDataset:
    def generate_dataset(sequence_length: int) -> Tuple[np.ndarray, np.ndarray]
    def generate_mixed_signal(normalize: bool) -> np.ndarray
    def generate_pure_target(frequency: float) -> np.ndarray
    def save_dataset(filepath: str, inputs: np.ndarray, targets: np.ndarray)
    @staticmethod
    def load_dataset(filepath: str) -> Tuple[np.ndarray, np.ndarray, dict]
```

**ConditionalLSTM Interface:**
```python
class ConditionalLSTM:
    def forward(x: torch.Tensor, hidden_state: Optional[Tuple]) -> Tuple[torch.Tensor, Tuple]
    def reset_state(batch_size: int, device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]
    def predict_single(x: torch.Tensor, reset_state: bool) -> torch.Tensor
```

**Trainer Interface:**
```python
class Trainer:
    def train(train_loader: DataLoader, num_epochs: int, reset_state: bool) -> Dict[str, list]
    def calculate_mse(data_loader: DataLoader, reset_state: bool) -> float
    def save_model(filepath: str)
    def load_model(filepath: str)
```

**Evaluator Interface:**
```python
class Evaluator:
    def evaluate(test_loader: DataLoader, reset_state: bool) -> Dict[str, float]
    def check_generalization(mse_train: float, mse_test: float) -> Dict[str, any]
    def predict_all_frequencies(mixed_signal: np.ndarray, reset_state: bool) -> np.ndarray
```

## 10. Architecture Decision Records (ADRs)

### ADR 1: LSTM State Management Strategy

**Status:** Accepted  
**Context:** The exercise requires processing samples with sequence length L=1, but maintaining temporal dependencies.

**Decision:** Do NOT reset LSTM hidden state between consecutive samples of the same frequency. State is passed from one sample to the next.

**Consequences:**
- ✅ Allows learning temporal patterns across samples
- ✅ Maintains state continuity within frequency sequences
- ⚠️ Requires careful state management in training loop
- ⚠️ State must be reset when frequency changes

### ADR 2: Modular Architecture

**Status:** Accepted  
**Context:** Need to separate concerns for maintainability and testability.

**Decision:** Organize code into modules: data, model, training, evaluation, visualization.

**Consequences:**
- ✅ Clear separation of concerns
- ✅ Easy to test individual components
- ✅ Reusable modules
- ⚠️ More files to manage
- ⚠️ Requires careful interface design

### ADR 3: Synthetic Data Generation

**Status:** Accepted  
**Context:** Need reproducible datasets with controlled noise characteristics.

**Decision:** Generate synthetic signals with configurable random seeds for train/test sets.

**Consequences:**
- ✅ Full control over data characteristics
- ✅ Reproducible experiments
- ✅ No external data dependencies
- ⚠️ May not reflect real-world signal characteristics

### ADR 4: PyTorch for Deep Learning

**Status:** Accepted  
**Context:** Need fine-grained control over LSTM state management.

**Decision:** Use PyTorch instead of higher-level frameworks like Keras.

**Consequences:**
- ✅ Fine-grained control over state
- ✅ Better debugging capabilities
- ✅ Industry standard
- ⚠️ More verbose code
- ⚠️ Manual state management required

### ADR 5: Command-Line Interface

**Status:** Accepted  
**Context:** Need flexible configuration for experiments.

**Decision:** Use argparse for command-line configuration instead of config files.

**Consequences:**
- ✅ Easy to run experiments with different parameters
- ✅ No config file management needed
- ⚠️ Less convenient for complex configurations
- ⚠️ Parameters not persisted

## 11. Deployment Architecture

### 11.1 Local Development Environment

```
Developer Machine
    │
    ├─► Python 3.8+ Environment
    │   ├─► Virtual Environment (venv/conda)
    │   ├─► Dependencies (requirements.txt)
    │   └─► Source Code (src/)
    │
    ├─► Training Execution
    │   ├─► CPU (default)
    │   ├─► CUDA (if NVIDIA GPU available)
    │   └─► MPS (if Apple Silicon available)
    │
    └─► Output Storage
        ├─► Models (outputs/models/)
        ├─► Plots (outputs/plots/)
        └─► Data (outputs/data/)
```

### 11.2 Execution Flow

1. **Setup Phase:**
   - Create virtual environment
   - Install dependencies
   - Verify PyTorch installation

2. **Data Generation Phase:**
   - Generate training dataset (seed=1)
   - Generate test dataset (seed=2)
   - Save datasets to disk (optional caching)

3. **Training Phase:**
   - Initialize LSTM model
   - Train for N epochs
   - Calculate MSE_train

4. **Evaluation Phase:**
   - Evaluate on test set
   - Calculate MSE_test
   - Check generalization

5. **Visualization Phase:**
   - Generate predictions
   - Create plots
   - Save to disk

## 12. Operational Considerations

### 12.1 Performance

- **Training Time:** Depends on number of epochs, dataset size, and device
- **Memory Usage:** Moderate (depends on batch size and sequence length)
- **Device Selection:** Auto-detects best available (CUDA > MPS > CPU)

### 12.2 Scalability

- **Current Limitation:** Single-machine execution
- **Future Enhancement:** Could support distributed training with PyTorch DDP
- **Dataset Size:** Configurable via duration and sampling rate parameters

### 12.3 Monitoring and Logging

- **Training Progress:** Progress bars via tqdm
- **Metrics:** MSE_train tracked per epoch
- **Output:** Console logging for key steps

### 12.4 Error Handling

- **Device Availability:** Graceful fallback (CUDA → MPS → CPU)
- **File I/O:** Error handling for dataset save/load
- **Model Loading:** Checkpoint validation

## 13. Security Considerations

- **No External Data:** All data is synthetically generated
- **No Network Access:** No external API calls
- **Local Execution:** All processing happens locally
- **No Secrets:** No API keys or credentials required

## 14. Trade-offs and Limitations

### 14.1 Trade-offs

1. **State Management Complexity vs. Flexibility:**
   - More complex code for better control over temporal dependencies

2. **Synthetic Data vs. Real Data:**
   - Full control but may not reflect real-world scenarios

3. **Modularity vs. Simplicity:**
   - More files but better maintainability

### 14.2 Current Limitations

1. **Single Machine:** No distributed training support
2. **Fixed Architecture:** LSTM architecture is fixed (configurable but not dynamically chosen)
3. **No Hyperparameter Tuning:** Manual parameter selection
4. **Limited Visualization:** Static plots only, no interactive exploration

## 15. Future Enhancements

1. **Hyperparameter Tuning:** Automated search (Optuna, Ray Tune)
2. **Model Variants:** Support for different architectures (GRU, Transformer)
3. **Real Data Support:** Load external signal datasets
4. **Interactive Visualization:** Web-based dashboard for result exploration
5. **Distributed Training:** Multi-GPU support
6. **Model Serving:** API for inference on new signals

## 16. References

- PyTorch LSTM Documentation: https://pytorch.org/docs/stable/generated/torch.nn.LSTM.html
- C4 Model: https://c4model.com/
- ISO/IEC 25010 Software Quality Model

