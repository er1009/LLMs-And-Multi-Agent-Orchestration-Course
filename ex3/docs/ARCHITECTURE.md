# Architecture Document
## Multi-Agent Translation Pipeline & Turing Machine Simulator

**Version:** 1.0
**Date:** November 22, 2025
**Status:** APPROVED

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [C4 Model](#2-c4-model)
3. [Technology Stack](#3-technology-stack)
4. [Component Architecture](#4-component-architecture)
5. [Data Architecture](#5-data-architecture)
6. [API Interfaces](#6-api-interfaces)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Architecture Decision Records](#8-architecture-decision-records)
9. [Security Architecture](#9-security-architecture)
10. [Operational Considerations](#10-operational-considerations)

---

## 1. System Overview

### 1.1 Purpose
This system provides a research and educational platform combining:
- Classical Turing Machine simulation
- Multi-agent LLM-based translation pipeline
- Semantic drift analysis using vector embeddings

### 1.2 Key Architectural Principles
- **Modularity:** Each component is independent and testable
- **Extensibility:** New translation agents and embedding providers can be added
- **Separation of Concerns:** Clear boundaries between TM simulation, translation, evaluation, and analysis
- **Configurability:** All external dependencies and parameters are configurable
- **Reproducibility:** Deterministic behavior with seed control

---

## 2. C4 Model

### 2.1 Context Diagram (Level 1)

```
┌─────────────────────────────────────────────────────────────┐
│                         System Context                       │
│                                                              │
│  ┌──────────┐         ┌─────────────────────┐              │
│  │   User   │────────>│   Translation &     │              │
│  │(CLI User)│         │  TM Simulator       │              │
│  └──────────┘         │     System          │              │
│                       └─────────────────────┘              │
│                              │        │                      │
│                              │        │                      │
│                       ┌──────▼───┐  ┌▼──────────────┐     │
│                       │ OpenAI   │  │  HuggingFace  │     │
│                       │   API    │  │      API      │     │
│                       └──────────┘  └───────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**External Dependencies:**
- **OpenAI API:** Translation models (GPT-4) and embeddings
- **HuggingFace API:** Alternative embedding provider
- **User:** Interacts via CLI

---

### 2.2 Container Diagram (Level 2)

```
┌────────────────────────────────────────────────────────────────┐
│                      Application Container                     │
│                                                                │
│  ┌──────────────┐                                             │
│  │  CLI Layer   │                                             │
│  │   (Click)    │                                             │
│  └──────┬───────┘                                             │
│         │                                                      │
│    ┌────▼────────────────────────────────────┐               │
│    │       Core Application Logic             │               │
│    │                                          │               │
│    │  ┌──────────────┐  ┌─────────────────┐ │               │
│    │  │   Turing     │  │   Translation   │ │               │
│    │  │   Machine    │  │     Pipeline    │ │               │
│    │  │   Simulator  │  │                 │ │               │
│    │  └──────────────┘  └─────────────────┘ │               │
│    │                                          │               │
│    │  ┌──────────────┐  ┌─────────────────┐ │               │
│    │  │  Evaluation  │  │    Analysis     │ │               │
│    │  │    Engine    │  │     Engine      │ │               │
│    │  └──────────────┘  └─────────────────┘ │               │
│    └───────────┬──────────────────┬──────────┘               │
│                │                  │                           │
│         ┌──────▼──────┐    ┌─────▼────────┐                 │
│         │  Data Layer │    │ Config Layer │                 │
│         │  (File I/O) │    │   (.env)     │                 │
│         └─────────────┘    └──────────────┘                 │
└────────────────────────────────────────────────────────────────┘
```

**Containers:**
1. **CLI Layer:** User interaction (Click framework)
2. **Core Logic:** Business logic modules
3. **Data Layer:** File operations and persistence
4. **Config Layer:** Environment and configuration management

---

### 2.3 Component Diagram (Level 3)

#### Core Components:

```
┌─────────────────────────────────────────────────────────┐
│               Turing Machine Module                     │
├─────────────────────────────────────────────────────────┤
│  - TuringMachine (class)                                │
│  - TransitionTable (dataclass)                          │
│  - Tape (class)                                         │
│  - ConfigLoader (function)                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Translation Module                          │
├─────────────────────────────────────────────────────────┤
│  - TranslationAgent (base class)                        │
│  - EnglishToFrenchAgent (class)                         │
│  - FrenchToHebrewAgent (class)                          │
│  - HebrewToEnglishAgent (class)                         │
│  - TranslationPipeline (class)                          │
│  - ErrorInjector (class)                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              Evaluation Module                           │
├─────────────────────────────────────────────────────────┤
│  - EmbeddingProvider (abstract base)                    │
│  - OpenAIEmbedding (class)                              │
│  - HuggingFaceEmbedding (class)                         │
│  - DistanceCalculator (class)                           │
│  - EvaluationEngine (class)                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               Analysis Module                            │
├─────────────────────────────────────────────────────────┤
│  - GraphGenerator (class)                               │
│  - StatisticsCalculator (class)                         │
│  - ResultExporter (class)                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                Utils Module                              │
├─────────────────────────────────────────────────────────┤
│  - Logger                                                │
│  - ConfigManager                                         │
│  - ValidationUtils                                       │
│  - FileUtils                                             │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### 3.1 Core Technologies

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| **Language** | Python | 3.9+ | Standard for ML/NLP, excellent library ecosystem |
| **CLI Framework** | Click | 8.1+ | Mature, decorator-based, widely adopted |
| **LLM Provider** | OpenAI API | Latest | Industry standard, reliable translation quality |
| **Embeddings** | OpenAI Embeddings | text-embedding-3-small | Cost-effective, good quality |
| **Config** | python-dotenv | 1.0+ | Standard for environment variable management |
| **Plotting** | Matplotlib | 3.7+ | Industry standard for scientific visualization |
| **Testing** | pytest | 7.4+ | De facto standard for Python testing |

### 3.2 Development Tools

| Tool | Purpose |
|------|---------|
| **black** | Code formatting |
| **mypy** | Static type checking |
| **pylint** | Linting |
| **pytest-cov** | Coverage reporting |

---

## 4. Component Architecture

### 4.1 Turing Machine Module

**Location:** `src/turing_machine/`

**Components:**
```python
# tm_simulator.py
class TuringMachine:
    def __init__(self, transitions, initial_state, halting_states)
    def load_tape(self, content: str)
    def step() -> bool
    def run(self, max_steps: int) -> TMResult

# tape.py
class Tape:
    def __init__(self, content: str = "", blank_symbol: str = "_")
    def read(self) -> str
    def write(self, symbol: str)
    def move(self, direction: str)

# config_loader.py
def load_tm_config(file_path: str) -> TMConfig
```

**Design Decisions:**
- Tape is unbounded via dynamic list expansion
- Transitions stored as dictionary for O(1) lookup
- Execution trace optional to minimize memory usage

---

### 4.2 Translation Module

**Location:** `src/translation/`

**Components:**
```python
# base_agent.py
class TranslationAgent(ABC):
    @abstractmethod
    def translate(self, text: str) -> str

# agents.py
class EnglishToFrenchAgent(TranslationAgent):
    def translate(self, text: str) -> str
        # Uses OpenAI with specific prompt

# pipeline.py
class TranslationPipeline:
    def __init__(self, agents: List[TranslationAgent])
    def run(self, text: str) -> PipelineResult

# error_injector.py
class ErrorInjector:
    def inject_errors(self, text: str, rate: float, seed: int) -> str
```

**Design Decisions:**
- Agent abstraction allows swapping LLM providers
- Pipeline is composable (any agent sequence)
- Error injection is deterministic with seeding
- Each agent has specialized system prompt

---

### 4.3 Evaluation Module

**Location:** `src/evaluation/`

**Components:**
```python
# embedding_provider.py
class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> np.ndarray

class OpenAIEmbedding(EmbeddingProvider):
    def embed(self, text: str) -> np.ndarray

# distance.py
class DistanceCalculator:
    @staticmethod
    def cosine_distance(v1, v2) -> float
    @staticmethod
    def euclidean_distance(v1, v2) -> float

# engine.py
class EvaluationEngine:
    def evaluate(self, original: str, result: str) -> EvaluationResult
```

**Design Decisions:**
- Abstract embedding provider for multi-provider support
- Support both cosine and Euclidean distance
- Embeddings cached during batch processing
- Results include metadata for traceability

---

### 4.4 Analysis Module

**Location:** `src/analysis/`

**Components:**
```python
# graph_generator.py
class GraphGenerator:
    def generate_scatter_plot(self, data: pd.DataFrame, output_path: str)

# statistics.py
class StatisticsCalculator:
    def calculate_correlation(self, x, y) -> float
    def calculate_trend(self, x, y) -> TrendResult

# exporter.py
class ResultExporter:
    def export_csv(self, data: List[dict], path: str)
    def export_json(self, data: List[dict], path: str)
```

**Design Decisions:**
- Matplotlib for plotting (no external dependencies)
- Statistical calculations include correlation coefficient
- Exports support both CSV and JSON for flexibility
- Graph styling follows scientific publication standards

---

### 4.5 CLI Module

**Location:** `src/cli.py`

**Structure:**
```python
@click.group()
def cli():
    pass

@cli.command()
def turing_machine(...):
    pass

@cli.command()
def translate_once(...):
    pass

@cli.command()
def translate_batch(...):
    pass

@cli.command()
def analyze(...):
    pass
```

**Design Decisions:**
- Click for decorator-based CLI (cleaner than argparse)
- Each command validates inputs before execution
- Progress bars for long-running operations
- Structured error handling with exit codes

---

## 5. Data Architecture

### 5.1 Data Flow

```
Input (User/Config)
      ↓
CLI Command Parser
      ↓
┌─────────────┬──────────────┬──────────────┐
│ TM Config   │ Sentence     │ Error Rate   │
│ (JSON/YAML) │ (String)     │ (Float)      │
└─────┬───────┴──────┬───────┴──────┬───────┘
      ↓              ↓              ↓
   TM Module    Error Injector  Translation
                                  Pipeline
                      ↓              ↓
                   Evaluation     Embeddings
                    Engine           ↓
                      ↓           Distance
                   Results         ↓
                      ↓         Analysis
                   Export       Module
                      ↓            ↓
             Files (CSV/JSON/PNG)
```

### 5.2 Data Models

**TM Configuration:**
```json
{
  "states": ["q0", "q1", "q_halt"],
  "alphabet": ["0", "1", "_"],
  "transitions": [
    {"state": "q0", "symbol": "1", "new_state": "q1", "write": "0", "move": "R"}
  ],
  "initial_state": "q0",
  "halting_states": ["q_halt"],
  "blank_symbol": "_"
}
```

**Pipeline Result:**
```python
@dataclass
class PipelineResult:
    original: str
    corrupted: str
    error_rate: float
    translation_fr: str
    translation_he: str
    translation_en: str
    timestamp: datetime
    seed: int
```

**Evaluation Result:**
```python
@dataclass
class EvaluationResult:
    original_text: str
    final_text: str
    original_embedding: np.ndarray
    final_embedding: np.ndarray
    cosine_distance: float
    euclidean_distance: float
    error_rate: float
```

---

## 6. API Interfaces

### 6.1 Internal APIs

**Turing Machine API:**
```python
tm = TuringMachine.from_file("config.json")
tm.load_tape("111")
result = tm.run(max_steps=1000)
print(result.final_tape, result.steps_taken)
```

**Translation API:**
```python
pipeline = TranslationPipeline([agent_a, agent_b, agent_c])
result = pipeline.run("Your text here", error_rate=0.25, seed=42)
```

**Evaluation API:**
```python
engine = EvaluationEngine(embedding_provider)
result = engine.evaluate(original="...", final="...")
print(result.cosine_distance)
```

### 6.2 External APIs

**OpenAI Translation:**
- Endpoint: `https://api.openai.com/v1/chat/completions`
- Model: `gpt-4`
- Temperature: 0.0 (deterministic)
- Max tokens: 1000

**OpenAI Embeddings:**
- Endpoint: `https://api.openai.com/v1/embeddings`
- Model: `text-embedding-3-small`
- Dimensions: 1536

---

## 7. Deployment Architecture

### 7.1 Deployment Model

**Type:** Single-user local CLI application

**Requirements:**
- Python 3.9+ runtime
- 100MB disk space
- Internet connection for API calls
- API keys in `.env` file

### 7.2 Installation Process

```bash
# 1. Clone repository
git clone <repo-url>
cd project

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp config/.env.example .env
# Edit .env with API keys

# 5. Verify installation
python -m src.cli --help
```

### 7.3 Runtime Environment

```
┌────────────────────────────────┐
│     User's Local Machine       │
│                                │
│  ┌──────────────────────────┐ │
│  │  Python 3.9+ Runtime     │ │
│  │                          │ │
│  │  ┌────────────────────┐  │ │
│  │  │  Virtual Env       │  │ │
│  │  │  - Click           │  │ │
│  │  │  - OpenAI SDK      │  │ │
│  │  │  - Matplotlib      │  │ │
│  │  └────────────────────┘  │ │
│  └──────────────────────────┘ │
│            │                   │
│            │ HTTPS              │
└────────────┼───────────────────┘
             │
             ▼
    ┌────────────────┐
    │  OpenAI API    │
    │  (External)    │
    └────────────────┘
```

---

## 8. Architecture Decision Records (ADRs)

### ADR-001: Choice of Python as Implementation Language

**Status:** Accepted

**Context:**
Need to choose implementation language for TM simulator and NLP pipeline.

**Decision:**
Use Python 3.9+

**Rationale:**
- Excellent NLP/ML library ecosystem
- OpenAI and HuggingFace have official Python SDKs
- Simple syntax for educational use
- Type hints available for better code quality
- Matplotlib for visualization

**Consequences:**
+ Easy integration with LLM APIs
+ Rapid development
+ Good testing frameworks
- Slower execution than compiled languages (acceptable for this use case)

---

### ADR-002: CLI Framework Selection (Click)

**Status:** Accepted

**Context:**
Need CLI framework for 4 commands with various options.

**Decision:**
Use Click over argparse or typer.

**Rationale:**
- Decorator-based API is cleaner than argparse
- More mature than typer
- Excellent documentation
- Built-in support for progress bars, colors, validation

**Consequences:**
+ Clean, maintainable CLI code
+ Easy to add new commands
+ Good error handling
- Extra dependency (minimal concern)

---

### ADR-003: Embedding Provider Abstraction

**Status:** Accepted

**Context:**
Need semantic similarity measurement, but provider may change.

**Decision:**
Create `EmbeddingProvider` abstract base class.

**Rationale:**
- OpenAI pricing may change
- Educational users may prefer free alternatives
- Research may require comparing providers
- Good software engineering practice

**Consequences:**
+ Easy to swap providers
+ Testable with mock provider
+ Future-proof
- Slight complexity increase (justified)

---

### ADR-004: Deterministic Error Injection

**Status:** Accepted

**Context:**
Spelling error injection must be reproducible for research validity.

**Decision:**
Use seeded random number generator.

**Rationale:**
- Research requires reproducibility
- Same input + seed → same errors
- Debugging is easier
- Meets academic standards

**Consequences:**
+ Reproducible experiments
+ Easier testing
+ Meets research standards
- Users must manage seeds (documented)

---

### ADR-005: File-Based Configuration for Turing Machines

**Status:** Accepted

**Context:**
Turing machine definitions need to be reusable and shareable.

**Decision:**
Use JSON/YAML files for TM configs.

**Rationale:**
- Human-readable
- Easy to version control
- Can share TM definitions
- Standard parsing libraries available
- Educational clarity

**Consequences:**
+ Reusable configurations
+ Easy to add new machines
+ Clear documentation
- File I/O required (minimal overhead)

---

### ADR-006: No Database Dependency

**Status:** Accepted

**Context:**
Need to store results for analysis.

**Decision:**
Use CSV/JSON files instead of database.

**Rationale:**
- Simpler deployment (no DB setup)
- Files are portable and inspectable
- CSV/JSON work well with data science tools
- Overkill for small-scale experiments

**Consequences:**
+ Zero infrastructure requirements
+ Easy to inspect results
+ Compatible with notebooks
- No complex queries (not needed)
- Manual file management (acceptable)

---

## 9. Security Architecture

### 9.1 Threat Model

**Threats Considered:**
1. API key exposure
2. Malicious configuration files
3. Path traversal attacks
4. Injection via user input

### 9.2 Security Controls

| Control | Implementation |
|---------|---------------|
| **Secret Management** | API keys in `.env` (gitignored), never in code |
| **Input Validation** | All CLI inputs validated before use |
| **Path Sanitization** | File paths validated, no directory traversal |
| **API Rate Limiting** | Respect OpenAI rate limits with backoff |
| **Error Messages** | No sensitive data in error messages |

### 9.3 Security Checklist

- ✅ `.env` in `.gitignore`
- ✅ `.env.example` provided without real keys
- ✅ Input validation on all CLI parameters
- ✅ File path validation (no `..` allowed)
- ✅ JSON parsing with error handling (no code execution)
- ✅ HTTPS for all API calls
- ✅ Minimal permissions required

---

## 10. Operational Considerations

### 10.1 Logging Strategy

**Log Levels:**
- **DEBUG:** Detailed execution trace (TM steps, API calls)
- **INFO:** High-level operations (translation started, completed)
- **WARNING:** Retries, degraded performance
- **ERROR:** Failures, invalid inputs

**Log Output:**
- Console for user feedback
- File (`results/logs/app.log`) for debugging

### 10.2 Error Handling

**Error Categories:**
1. **User Errors:** Invalid inputs → clear error message + exit code 1
2. **API Errors:** Network/auth failures → retry logic → fail after 3 attempts
3. **System Errors:** File I/O, permissions → descriptive error + exit code 2

**Retry Logic:**
```python
@retry(max_attempts=3, backoff=exponential)
def call_openai_api(...):
    # API call
```

### 10.3 Performance Considerations

**Bottlenecks:**
- API latency (2-5 seconds per translation)
- Embedding computation (1-2 seconds per pair)

**Optimizations:**
- Batch embedding requests where possible
- Cache embeddings during batch processing
- Async API calls (future enhancement)

**Expected Performance:**
- Single translation: 15-30 seconds
- Batch of 50: 3-5 minutes
- Graph generation: <5 seconds

### 10.4 Monitoring

**Metrics to Track:**
- API call count and costs
- Success/failure rates
- Execution times
- Error rates by type

**Implementation:**
- Logged to `results/logs/metrics.json`
- CLI option to display summary

---

## 11. Testing Strategy

### 11.1 Test Pyramid

```
        ┌─────────────┐
        │     E2E     │  (5%) - Full CLI commands
        └─────────────┘
       ┌───────────────┐
       │  Integration  │   (15%) - Module interactions
       └───────────────┘
     ┌───────────────────┐
     │   Unit Tests      │    (80%) - Individual functions
     └───────────────────┘
```

### 11.2 Test Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| Turing Machine | 85% |
| Translation Agents | 75% |
| Evaluation | 80% |
| Analysis | 70% |
| Utils | 90% |
| **Overall** | **≥75%** |

### 11.3 Testing Approach

**Unit Tests:**
- Mock external APIs (OpenAI)
- Test edge cases (empty input, large input)
- Test error handling

**Integration Tests:**
- Test agent pipeline with mock LLM
- Test file I/O operations
- Test CLI command parsing

**End-to-End Tests:**
- Test full workflow with real API (CI only)
- Validate output files generated correctly

---

## 12. Future Enhancements

### 12.1 Potential Extensions

**Priority 1:**
- Support for additional language pairs
- Alternative LLM providers (Claude, Llama)
- Async API calls for faster batch processing

**Priority 2:**
- Web interface (Gradio/Streamlit)
- Real-time streaming translation
- GPU-accelerated embeddings

**Priority 3:**
- Multi-tape Turing machines
- Non-deterministic TM support
- Distributed batch processing

### 12.2 Extension Points

**Designed for Extension:**
- `TranslationAgent` base class → add new agents
- `EmbeddingProvider` base class → add new providers
- CLI commands → add new commands via decorators
- TM config format → add new machine types

---

## 13. Conclusion

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Testability at all levels
- ✅ Extensibility for future research
- ✅ Security best practices
- ✅ Reproducibility for academic use
- ✅ Maintainable codebase

The modular design ensures each component can be developed, tested, and improved independently while maintaining system coherence.

---

**Document Status:** APPROVED
**Next Review:** After implementation phase
**Approved By:** Architecture Review Board
