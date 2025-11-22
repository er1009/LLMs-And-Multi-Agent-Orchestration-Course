# Multi-Agent Translation Pipeline & Turing Machine

### **Formal Implementation Specification (for LLM/Agent Execution)**

------------------------------------------------------------------------

## 1. Overview

This specification defines the system requirements for implementing:

1.  A **Command-Line Interface (CLI)** tool.
2.  A **Turing Machine simulator** runnable from the CLI.
3.  A **three-agent multilingual translation pipeline** (EN→FR→HE→EN).
4.  An **evaluation module** that computes vector embeddings and
    semantic distance.
5.  An **analysis module** that generates a graph correlating
    spelling-error rate with semantic drift.

This document is formatted for direct consumption by an LLM-based coding
agent.

------------------------------------------------------------------------

## 2. System Components

### 2.1 CLI Tool

Implement a CLI application providing the following commands:

    my_tool turing-machine
    my_tool translate-once
    my_tool translate-batch
    my_tool analyze

The CLI may use frameworks such as `argparse`, `click`, `typer`, or
equivalent.

------------------------------------------------------------------------

## 3. Turing Machine Simulator

### 3.1 Requirements

-   Must simulate a classical Turing Machine with:
    -   A tape (unbounded to both sides).
    -   A head position.
    -   A finite set of states.
    -   A transition table of the form:\
        `(state, symbol) → (new_state, new_symbol, direction)`
-   Must allow loading the machine definition from a JSON/YAML file.
-   Must support specifying:
    -   Initial tape content.
    -   Maximum number of execution steps.
-   Must safely halt on:
    -   Reaching a halting state.
    -   Exceeding the step limit.

### 3.2 CLI Usage Example

    my_tool turing-machine   --config machines/unary_increment.json   --tape "111"   --max-steps 100

### 3.3 Output Requirements

-   Initial tape\
-   Final tape\
-   Final state\
-   Step count\
-   Optional execution trace

------------------------------------------------------------------------

## 4. Translation Agents

### 4.1 Required Agents ("Skills")

Implement three independent translation agents:

-   **Agent A:** English → French\
-   **Agent B:** French → Hebrew\
-   **Agent C:** Hebrew → English

Each agent must:\
- Preserve semantic meaning as much as possible.\
- Avoid adding, removing, or hallucinating content.\
- Transform only the language.

------------------------------------------------------------------------

## 5. Translation Pipeline

### 5.1 Pipeline Steps

1.  Input: English sentence(s) of **at least 15 words**.\
2.  Inject **≥25% spelling errors**.\
3.  Forward to **Agent A** → French.\
4.  Forward to **Agent B** → Hebrew.\
5.  Forward to **Agent C** → English (final result).

All intermediate outputs must be captured.

### 5.2 CLI Example

    my_tool translate-once --sentence "your sentence here" --error-rate 0.30

------------------------------------------------------------------------

## 6. Evaluation & Embeddings

### 6.1 Requirements

-   Compute embeddings for:
    -   Original clean sentence\
    -   Final English output\
-   Use any valid embedding method (e.g., OpenAI, HuggingFace).\
-   Compute vector distance (cosine or Euclidean).

### 6.2 Batch Evaluation

For error rates from **0% to 50%**, compute: - Corrupted sentence\
- Final translation\
- Vector distance

Output structured data (CSV or JSON).

------------------------------------------------------------------------

## 7. Graph Generation

### 7.1 Requirements

Generate a graph where: - **X-axis:** spelling error rate (0--50%)\
- **Y-axis:** embedding distance

Output: PNG image.

------------------------------------------------------------------------

## 8. Submission Requirements

Provide: - Sentences used (clean + corrupted)\
- Sentence lengths\
- Agent skills (definitions/prompts)\
- Graph file\
- Any generated CSV/JSON

------------------------------------------------------------------------

## 9. Notes for LLM Implementation

-   Ensure reproducibility (random seed for noise generation).\
-   Ensure no step depends on undefined global state.\
-   Ensure all CLI commands accept structured input and provide
    deterministic output.

------------------------------------------------------------------------
