# Architecture Document
## Context Windows Lab - LLM Performance Analysis

**Version**: 1.0
**Date**: December 2025
**Status**: Active

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [C4 Model](#2-c4-model)
3. [Technology Stack](#3-technology-stack)
4. [Component Architecture](#4-component-architecture)
5. [Data Flow](#5-data-flow)
6. [API Interfaces](#6-api-interfaces)
7. [Data Schemas](#7-data-schemas)
8. [Architecture Decision Records (ADRs)](#8-architecture-decision-records)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Operational Considerations](#10-operational-considerations)

---

## 1. System Overview

### 1.1 Purpose
The Context Windows Lab is a research-grade experimental framework designed to systematically analyze context window limitations in Large Language Models through four controlled experiments.

### 1.2 Key Capabilities
- **Experiment Execution**: Automated running of 4 distinct experiments
- **Data Generation**: Realistic document and query generation
- **Performance Measurement**: Accuracy, latency, and token usage tracking
- **Statistical Analysis**: Multi-run experiments with confidence intervals
- **Visualization**: Publication-quality graphs and tables
- **Reproducibility**: Seeded randomness and deterministic execution

### 1.3 Design Principles
1. **Modularity**: Each experiment and utility is independently testable
2. **Extensibility**: Easy to add new experiments or strategies
3. **Reproducibility**: All results can be exactly reproduced
4. **Observability**: Comprehensive logging and progress tracking
5. **Reliability**: Robust error handling with graceful degradation

---

## 2. C4 Model

### 2.1 Context Diagram (Level 1)

```
┌─────────────────────────────────────────────────────────────┐
│                      Context Windows Lab                     │
│                                                              │
│  Experimental Framework for LLM Context Analysis           │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP API calls
                           ↓
                    ┌──────────────┐
                    │    Ollama    │
                    │   (LLM API)  │
                    └──────────────┘
                           │
                           │ Model inference
                           ↓
                    ┌──────────────┐
                    │  LLM Models  │
                    │ (llama2/phi) │
                    └──────────────┘

External Dependencies:
- Researcher/User: Runs experiments, analyzes results
- File System: Stores results, graphs, configurations
- ChromaDB: Vector embeddings storage (Experiment 3)
```

### 2.2 Container Diagram (Level 2)

```
┌──────────────────────────────────────────────────────────────────┐
│                    Context Windows Lab System                     │
│                                                                   │
│  ┌────────────────┐    ┌─────────────────┐   ┌───────────────┐ │
│  │  Main Runner   │───→│  Experiments    │   │  Utilities    │ │
│  │   (CLI App)    │    │   - Exp1-4      │   │  - Ollama     │ │
│  └────────────────┘    │   Modules       │   │  - Eval       │ │
│          │             └─────────────────┘   │  - Tokenizer  │ │
│          │                     │              └───────────────┘ │
│          ↓                     ↓                      ↓          │
│  ┌────────────────┐    ┌─────────────────┐   ┌───────────────┐ │
│  │  Visualization │    │   Data Gen      │   │  Configuration│ │
│  │    Module      │    │    Module       │   │    Manager    │ │
│  └────────────────┘    └─────────────────┘   └───────────────┘ │
│          │                                                       │
│          ↓                                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Results Storage (File System)                  │ │
│  │         - graphs/  - tables/  - raw_data/                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
         │                                    │
         │                                    │
         ↓                                    ↓
  ┌─────────────┐                    ┌───────────────┐
  │   Ollama    │                    │   ChromaDB    │
  │  (External) │                    │  (Embedded)   │
  └─────────────┘                    └───────────────┘
```

### 2.3 Component Diagram (Level 3)

**Experiment Components:**
```
experiments/
├── experiment1_needle_haystack.py
│   ├── NeedleHaystackExperiment (class)
│   │   ├── generate_filler_text()
│   │   ├── embed_critical_fact()
│   │   ├── run_single_trial()
│   │   └── run_full_experiment()
│
├── experiment2_context_size.py
│   ├── ContextSizeExperiment (class)
│   │   ├── create_scaled_contexts()
│   │   ├── measure_performance()
│   │   └── run_full_experiment()
│
├── experiment3_rag_comparison.py
│   ├── RAGComparisonExperiment (class)
│   │   ├── setup_vector_store()
│   │   ├── compare_approaches()
│   │   └── run_full_experiment()
│
└── experiment4_strategies.py
    ├── SelectStrategy (class)
    ├── CompressStrategy (class)
    ├── WriteStrategy (class)
    └── StrategyExperiment (class)
```

**Utility Components:**
```
utils/
├── ollama_client.py
│   ├── OllamaClient (class)
│   │   ├── query()
│   │   ├── check_connection()
│   │   └── get_available_models()
│
├── evaluation.py
│   ├── evaluate_exact_match()
│   ├── evaluate_fuzzy_match()
│   ├── evaluate_semantic_similarity()
│   └── evaluate_response()
│
├── tokenization.py
│   ├── count_tokens()
│   └── TokenCounter (class)
│
├── document_generator.py
│   ├── DocumentGenerator (class)
│   │   ├── generate_filler_text()
│   │   ├── generate_realistic_documents()
│   │   └── embed_fact()
│
└── visualization.py
    ├── plot_lost_in_middle()
    ├── plot_context_size_impact()
    ├── plot_rag_comparison()
    └── create_strategy_table()
```

### 2.4 Code Diagram (Level 4)

See individual module documentation for class diagrams and method signatures.

---

## 3. Technology Stack

### 3.1 Core Technologies

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| **Language** | Python | 3.8+ | Standard for ML/AI research, rich ecosystem |
| **LLM Inference** | Ollama | Latest | Local execution, privacy, no API costs |
| **LLM Framework** | LangChain | 0.1.0+ | Industry-standard, rich abstractions |
| **Vector DB** | ChromaDB | 0.4.0+ | Lightweight, embedded, easy setup |
| **Embeddings** | sentence-transformers | 2.2.0+ | High-quality, pre-trained models |
| **Data Analysis** | pandas | 2.0.0+ | Standard for data manipulation |
| **Visualization** | matplotlib | 3.7.0+ | Publication-quality plots |
| **Numerics** | numpy | 1.24.0+ | Fast array operations |
| **Testing** | pytest | 7.0.0+ | Comprehensive testing framework |

### 3.2 Development Tools

| Purpose | Tool | Justification |
|---------|------|---------------|
| **Code Quality** | flake8, black | Enforce PEP 8, consistent formatting |
| **Type Checking** | mypy | Catch type errors early |
| **Coverage** | pytest-cov | Ensure adequate test coverage |
| **Documentation** | Sphinx | Auto-generate API docs |
| **Notebooks** | Jupyter | Interactive analysis |

### 3.3 Technology Decision Trade-offs

**Why Ollama vs. OpenAI API?**
- ✓ No API costs
- ✓ Privacy (data stays local)
- ✓ Reproducibility (fixed model versions)
- ✗ Slower inference
- ✗ Limited to open-source models

**Why ChromaDB vs. Pinecone/Weaviate?**
- ✓ Embedded (no separate service)
- ✓ Simple setup
- ✓ Sufficient for research scale
- ✗ Not production-scale
- ✗ Limited multi-user support

**Why sentence-transformers vs. OpenAI embeddings?**
- ✓ Free and local
- ✓ Good quality (all-MiniLM-L6-v2)
- ✓ Fast inference
- ✗ Lower quality than ada-002
- ✗ Fixed dimensionality

---

## 4. Component Architecture

### 4.1 Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Presentation Layer                          │
│  - CLI interface (main.py)                              │
│  - Progress reporting                                   │
│  - Result display                                       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│            Experiment Layer                              │
│  - Experiment 1-4 implementations                       │
│  - Experiment orchestration                             │
│  - Results aggregation                                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Service Layer                               │
│  - Ollama client (LLM queries)                          │
│  - Vector store manager (RAG)                           │
│  - Document generator                                   │
│  - Evaluation service                                   │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              Utility Layer                               │
│  - Tokenization                                         │
│  - Visualization                                        │
│  - Configuration management                             │
│  - Logging                                              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│            Infrastructure Layer                          │
│  - File I/O                                             │
│  - Network (HTTP to Ollama)                             │
│  - ChromaDB persistence                                 │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Component Interactions

**Experiment 1 Flow:**
```
User → main.py → Experiment1
                    ↓
            DocumentGenerator → generate_filler_text()
                    ↓
            embed_critical_fact()
                    ↓
            OllamaClient.query() ← [context + question]
                    ↓
            evaluate_response() → accuracy score
                    ↓
            (repeat 10+ times)
                    ↓
            visualization.plot_lost_in_middle()
                    ↓
            Save results → results/experiment1/
```

**Experiment 3 Flow:**
```
User → main.py → Experiment3
                    ↓
            DocumentGenerator.generate_realistic_documents()
                    ↓
            chunk_documents()
                    ↓
            generate_embeddings() ← sentence-transformers
                    ↓
            ChromaDB.setup_vector_store()
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
  Full Context Path      RAG Path
        ↓                       ↓
  OllamaClient.query()    vector_store.query()
        ↓                       ↓
        └───────────┬───────────┘
                    ↓
            compare_results()
                    ↓
            visualization.plot_rag_comparison()
```

---

## 5. Data Flow

### 5.1 Experiment Data Pipeline

```
Input Data → Processing → LLM Inference → Evaluation → Aggregation → Visualization
    ↓            ↓             ↓               ↓            ↓              ↓
Documents    Chunking     Ollama API      Accuracy     Statistics      Graphs
Queries      Embedding    Latency         Fuzzy Match  Confidence      Tables
Facts        Formatting   Token Count     Semantic     Mean/Std        CSV
```

### 5.2 Data Persistence

```
results/
├── experiment1/
│   ├── raw_results.json          # All trial data
│   ├── aggregated_stats.csv      # Mean, std, confidence
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
    ├── strategy_comparison.md
    └── strategy_trends.png

chroma_db/                        # Vector store persistence
├── chroma.sqlite3
└── embeddings/
```

---

## 6. API Interfaces

### 6.1 Experiment Interface (Abstract Base)

```python
class BaseExperiment(ABC):
    """Abstract base class for all experiments."""

    @abstractmethod
    def run_full_experiment(
        self,
        num_runs: int = 10,
        random_seed: int = 42
    ) -> Dict[str, Any]:
        """Run complete experiment with multiple trials.

        Args:
            num_runs: Number of trials for statistical validity
            random_seed: Seed for reproducibility

        Returns:
            Dictionary with results, statistics, and metadata
        """
        pass

    @abstractmethod
    def visualize_results(self, results: Dict[str, Any]) -> None:
        """Generate and save visualizations."""
        pass

    @abstractmethod
    def save_results(self, results: Dict[str, Any], output_dir: str) -> None:
        """Persist results to disk."""
        pass
```

### 6.2 Ollama Client Interface

```python
class OllamaClient:
    """Client for interacting with Ollama API."""

    def query(
        self,
        context: str,
        question: str,
        model: str = "llama2",
        temperature: float = 0.1,
        timeout: int = 60,
        max_retries: int = 3
    ) -> str:
        """Send query to Ollama and return response.

        Args:
            context: Background context for the question
            question: The question to answer
            model: Model name (llama2, mistral, phi)
            temperature: Sampling temperature (low for consistency)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts

        Returns:
            Model response as string

        Raises:
            OllamaConnectionError: If Ollama is unreachable
            OllamaTimeoutError: If request times out
        """
        pass
```

### 6.3 Evaluation Interface

```python
def evaluate_response(
    response: str,
    expected_answer: str,
    method: str = "multi"
) -> float:
    """Evaluate response accuracy using multiple methods.

    Args:
        response: Model's response
        expected_answer: Ground truth answer
        method: Evaluation method (exact|fuzzy|semantic|multi)

    Returns:
        Accuracy score between 0.0 and 1.0
    """
    pass
```

---

## 7. Data Schemas

### 7.1 Experiment Result Schema

```python
ExperimentResult = {
    "experiment_id": str,              # "experiment1", "experiment2", etc.
    "timestamp": str,                  # ISO 8601 format
    "config": {
        "num_runs": int,
        "random_seed": int,
        "model": str,
        "temperature": float,
        # Experiment-specific params
    },
    "trials": [
        {
            "trial_id": int,
            "accuracy": float,
            "latency_ms": float,
            "token_count": int,
            # Experiment-specific fields
        }
    ],
    "statistics": {
        "mean_accuracy": float,
        "std_accuracy": float,
        "mean_latency": float,
        "std_latency": float,
        "confidence_interval_95": [float, float]
    },
    "metadata": {
        "total_runtime_seconds": float,
        "success_rate": float,
        "errors": []
    }
}
```

### 7.2 Document Schema

```python
Document = {
    "doc_id": str,
    "content": str,
    "domain": str,                    # "technology", "law", "medicine"
    "word_count": int,
    "has_critical_fact": bool,
    "critical_fact": Optional[str],
    "fact_position": Optional[str],   # "start", "middle", "end"
    "metadata": Dict[str, Any]
}
```

---

## 8. Architecture Decision Records (ADRs)

### ADR-001: Use Ollama for LLM Inference

**Status**: Accepted
**Date**: December 2025
**Context**: Need local LLM inference for experiments
**Decision**: Use Ollama instead of cloud APIs
**Consequences**:
- ✓ No API costs
- ✓ Complete privacy
- ✓ Reproducible (fixed model versions)
- ✗ Slower than cloud APIs
- ✗ Requires local setup

---

### ADR-002: Implement Experiments as Classes

**Status**: Accepted
**Date**: December 2025
**Context**: Need modular, testable experiment implementations
**Decision**: Use class-based architecture with BaseExperiment abstract class
**Consequences**:
- ✓ Easy to add new experiments
- ✓ Enforces consistent interface
- ✓ Better testability
- ✓ State encapsulation
- ✗ Slightly more complex than functions

---

### ADR-003: Use ChromaDB for Vector Storage

**Status**: Accepted
**Date**: December 2025
**Context**: Need vector database for Experiment 3 (RAG)
**Decision**: Use embedded ChromaDB instead of hosted solutions
**Consequences**:
- ✓ Zero setup complexity
- ✓ Works offline
- ✓ Sufficient for research scale
- ✗ Not suitable for production
- ✗ Limited concurrent access

---

### ADR-004: Multi-Method Evaluation Strategy

**Status**: Accepted
**Date**: December 2025
**Context**: LLM responses vary; need robust evaluation
**Decision**: Combine exact match, fuzzy matching, and semantic similarity
**Consequences**:
- ✓ More robust to formatting variations
- ✓ Catches semantically correct but differently worded answers
- ✓ Configurable strictness
- ✗ Slower than single method
- ✗ Requires embedding model

---

### ADR-005: Results Stored as JSON + CSV

**Status**: Accepted
**Date**: December 2025
**Context**: Need both detailed results and aggregated stats
**Decision**: Store raw results as JSON, aggregated stats as CSV
**Consequences**:
- ✓ JSON: Complete data for reanalysis
- ✓ CSV: Easy to import into Excel/R/Python
- ✓ Human-readable
- ✗ More storage than binary formats
- ✗ Requires parsing

---

### ADR-006: Temperature Set to 0.1 for Consistency

**Status**: Accepted
**Date**: December 2025
**Context**: Need reproducible results across runs
**Decision**: Use temperature=0.1 (near-deterministic) instead of 0.7
**Consequences**:
- ✓ More reproducible results
- ✓ Lower variance across runs
- ✗ Less creative responses
- ✗ May miss valid alternative answers

---

### ADR-007: Retry Logic with Exponential Backoff

**Status**: Accepted
**Date**: December 2025
**Context**: Network requests to Ollama may fail transiently
**Decision**: Implement max 3 retries with exponential backoff (2^attempt seconds)
**Consequences**:
- ✓ Handles transient failures
- ✓ Doesn't overwhelm server
- ✓ Configurable retry count
- ✗ Increases total runtime on failures

---

## 9. Deployment Architecture

### 9.1 Local Development Setup

```
Developer Machine
├── Python 3.8+ environment
├── Ollama service (localhost:11434)
│   └── Models: llama2, mistral, or phi
├── ChromaDB (embedded, ./chroma_db/)
├── Project directory structure
└── Virtual environment (venv/ or conda)
```

### 9.2 Execution Environment

**Minimum Requirements**:
- **CPU**: 4 cores (8 recommended)
- **RAM**: 8GB (16GB recommended)
- **Disk**: 10GB free (models + data)
- **OS**: macOS, Linux, or Windows with WSL
- **Network**: Internet for initial setup only

**Ollama Configuration**:
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull required model
ollama pull llama2

# Verify installation
curl http://localhost:11434/api/tags
```

---

## 10. Operational Considerations

### 10.1 Logging Strategy

**Log Levels**:
- **DEBUG**: Detailed diagnostic info (token counts, embeddings)
- **INFO**: Progress updates, experiment milestones
- **WARNING**: Degraded performance, retries
- **ERROR**: Failed trials, connection issues
- **CRITICAL**: Experiment cannot complete

**Log Format**:
```
[2025-12-10 14:32:15] [INFO] [Experiment1] Starting trial 3/10
[2025-12-10 14:32:18] [DEBUG] [OllamaClient] Query latency: 2847ms
[2025-12-10 14:32:18] [INFO] [Experiment1] Trial 3 accuracy: 0.85
```

### 10.2 Error Handling Strategy

**Error Categories**:
1. **Transient Errors**: Network issues → Retry with backoff
2. **Configuration Errors**: Missing models → Clear error message + fix instructions
3. **Validation Errors**: Invalid inputs → Fail fast with specific message
4. **Resource Errors**: Out of memory → Suggest reducing batch size

**Error Recovery**:
- Save partial results before failure
- Allow resuming from last successful trial
- Log all errors to `errors.log`

### 10.3 Performance Monitoring

**Metrics Tracked**:
- Request latency (per query)
- Token throughput (tokens/second)
- Memory usage (peak and average)
- Disk I/O for vector store
- Experiment wall-clock time

**Optimization Strategies**:
- Batch embedding generation (32 documents at a time)
- Cache repeated queries
- Lazy load models
- Incremental vector store updates

### 10.4 Scalability Considerations

**Current Scale**:
- ~100-200 LLM queries per full experiment run
- ~20-50 documents in vector store
- ~1-2 hours total runtime

**Future Scaling** (out of scope for v1.0):
- Parallel experiment execution
- Distributed vector store
- GPU acceleration for embeddings
- Larger document corpora (1000s)

---

## 11. Security Considerations

### 11.1 Data Privacy
- All data processed locally (no external APIs)
- No PII or sensitive data in generated documents
- Vector embeddings never leave local machine

### 11.2 Secrets Management
- No API keys required (local Ollama)
- `.env.example` for future cloud extensions
- `.gitignore` prevents accidental secret commits

### 11.3 Input Validation
- Validate all user inputs (file paths, parameters)
- Sanitize document content before LLM queries
- Limit context size to prevent resource exhaustion

---

## 12. Testing Strategy

### 12.1 Unit Tests
- Test each utility function in isolation
- Mock Ollama responses for determinism
- Test edge cases (empty inputs, long contexts, etc.)

### 12.2 Integration Tests
- Test experiment end-to-end with small dataset
- Verify results are saved correctly
- Test error recovery mechanisms

### 12.3 Performance Tests
- Measure latency for various context sizes
- Monitor memory usage during long experiments
- Verify experiments complete within time limits

---

## 13. Future Enhancements (Out of Scope for v1.0)

1. **Web Interface**: Dashboard for running experiments and viewing results
2. **Multi-Model Comparison**: Compare multiple LLMs side-by-side
3. **Cloud Integration**: Optional OpenAI/Anthropic API support
4. **Real-time Monitoring**: Live graphs during experiment execution
5. **Experiment Scheduler**: Queue and schedule long-running experiments
6. **Result Comparison**: Compare results across different runs
7. **Custom Experiments**: User-defined experiment templates

---

**Document Maintainer**: Architecture Team
**Last Updated**: December 2025
**Next Review**: End of Phase 3
