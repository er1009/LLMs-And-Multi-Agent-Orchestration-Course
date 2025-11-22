# Usage Examples

Complete examples for using all system components.

---

## Example 1: Turing Machine - Unary Increment

Increment a unary number (represented as a string of 1s).

```bash
./run.sh turing-machine \
  --config machines/unary_increment.json \
  --tape "11111" \
  --max-steps 100
```

**Expected Output:**
```
Initial tape:  11111
Final tape:    111111
Steps taken:   7
Halted:        True
```

---

## Example 2: Turing Machine - Binary Increment

Increment a binary number.

```bash
./run.sh turing-machine \
  --config machines/binary_increment.json \
  --tape "1011" \
  --max-steps 100
```

**Expected Output:**
```
Initial tape:  1011  (decimal: 11)
Final tape:    1100  (decimal: 12)
Steps taken:   6
Halted:        True
```

---

## Example 3: Error Injection

Test error injection with different rates.

```python
from src.translation import ErrorInjector

# Create injector with seed for reproducibility
injector = ErrorInjector(seed=42)

original = "Scientists discovered a remarkable new species in the Amazon rainforest"

# Test with 25% error rate
corrupted = injector.inject_errors(original, error_rate=0.25)

print(f"Original:  {original}")
print(f"Corrupted: {corrupted}")

# Get statistics
stats = injector.get_error_statistics(original, corrupted)
print(f"Actual error rate: {stats['actual_error_rate']:.2%}")
print(f"Words changed: {stats['words_changed']}/{stats['total_words']}")
```

---

## Example 4: Semantic Similarity Evaluation

Measure semantic distance between texts.

```python
from src.evaluation import HuggingFaceEmbedding, EvaluationEngine

# Initialize (first run downloads model)
embedder = HuggingFaceEmbedding()
engine = EvaluationEngine(embedder)

# Compare two texts
original = "The cat sits on the mat"
modified = "A feline rests on the rug"

result = engine.evaluate(original, modified)

print(f"Cosine distance: {result.cosine_distance:.4f}")
print(f"Euclidean distance: {result.euclidean_distance:.4f}")
```

---

## Example 5: Batch Processing

Process multiple sentences with varying error rates.

```python
from src.translation import ErrorInjector
from src.evaluation import HuggingFaceEmbedding, EvaluationEngine
import numpy as np

# Setup
injector = ErrorInjector(seed=42)
embedder = HuggingFaceEmbedding()
engine = EvaluationEngine(embedder)

sentence = "Your sentence here (minimum 15 words required for full pipeline)"
error_rates = np.linspace(0.0, 0.5, 11)  # 0% to 50%, 11 steps

results = []
for rate in error_rates:
    # Inject errors
    corrupted = injector.inject_errors(sentence, error_rate=rate)

    # Evaluate (in real scenario, would translate here)
    result = engine.evaluate(sentence, corrupted, error_rate=rate)

    results.append({
        'error_rate': rate,
        'cosine_distance': result.cosine_distance
    })

    print(f"Rate {rate*100:3.0f}%: Distance = {result.cosine_distance:.4f}")
```

---

## Example 6: Graph Generation

Create visualizations from results.

```python
from src.analysis import GraphGenerator

gen = GraphGenerator()

# Sample data
error_rates = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
distances = [0.05, 0.15, 0.28, 0.45, 0.68, 0.89]

# Generate scatter plot with trend line
gen.generate_scatter_plot(
    error_rates=error_rates,
    distances=distances,
    output_path='results/my_analysis.png',
    title='Error Rate vs Semantic Distance',
    xlabel='Spelling Error Rate',
    ylabel='Cosine Distance',
    show_trend=True,
    dpi=300
)

print("Graph saved to: results/my_analysis.png")
```

---

## Example 7: Data Export

Export results in multiple formats.

```python
from src.analysis import ResultExporter

exporter = ResultExporter()

# Your data
data = [
    {
        'sentence_id': 1,
        'original': 'Original text here',
        'translation': 'Translated text here',
        'error_rate': 0.25,
        'cosine_distance': 0.342,
        'euclidean_distance': 0.876
    },
    # ... more results
]

# Export to JSON
exporter.export_json(data, 'results/my_results.json')

# Export to CSV
exporter.export_csv(data, 'results/my_results.csv')

print("Results exported successfully!")
```

---

## Example 8: Statistical Analysis

Perform correlation and trend analysis.

```python
from src.analysis import StatisticsCalculator

calc = StatisticsCalculator()

# Your data
error_rates = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
distances = [0.05, 0.15, 0.28, 0.45, 0.68, 0.89]

# Calculate trend
trend = calc.calculate_trend(error_rates, distances)

print(f"Correlation: {trend.correlation:.4f}")
print(f"R² score: {trend.r_squared:.4f}")
print(f"Trend line: y = {trend.slope:.4f}x + {trend.intercept:.4f}")

# Summary statistics
summary = calc.calculate_summary_stats(distances)

print(f"\nDistance Statistics:")
print(f"  Mean: {summary['mean']:.4f}")
print(f"  Median: {summary['median']:.4f}")
print(f"  Std Dev: {summary['std']:.4f}")
print(f"  Range: [{summary['min']:.4f}, {summary['max']:.4f}]")
```

---

## Example 9: Translation with Claude CLI (Requires Installation)

Translate a sentence through the full pipeline.

```bash
./run.sh translate-once \
  --sentence "The quick brown fox jumps over the lazy dog repeatedly and rests peacefully under a tree" \
  --error-rate 0.25 \
  --seed 42 \
  --output results/translation_result.json
```

**What happens:**
1. Injects 25% spelling errors
2. Translates EN → FR (via Claude CLI + `src/agents/en_to_fr.md`)
3. Translates FR → HE (via Claude CLI + `src/agents/fr_to_he.md`)
4. Translates HE → EN (via Claude CLI + `src/agents/he_to_en.md`)
5. Computes semantic distance (HuggingFace embeddings)
6. Saves results to JSON

---

## Example 10: Comprehensive Experiment Suite

Run all experiments at scale.

```bash
python run_comprehensive_experiments.py
```

**This runs:**
- 12 Turing Machine tests
- 30 error injection combinations
- 110 semantic evaluations
- Statistical analysis
- Graph generation
- Complete data export

**Output location:**
```
results/experiments/exp_YYYYMMDD_HHMMSS/
├── turing_machine_results.json
├── error_injection_results.json
├── large_scale_results.json
├── large_scale_results.csv
├── semantic_drift_results.json
├── experiment_summary.json
├── graph_overall_analysis.png
├── graph_multi_metric.png
├── graph_distribution.png
└── EXPERIMENT_REPORT.md
```

---

## Example 11: Custom Turing Machine

Create your own Turing machine configuration.

**File:** `machines/my_machine.json`
```json
{
  "description": "My custom machine",
  "states": ["q0", "q1", "q_halt"],
  "alphabet": ["a", "b", "_"],
  "initial_state": "q0",
  "halting_states": ["q_halt"],
  "blank_symbol": "_",
  "transitions": [
    {
      "state": "q0",
      "symbol": "a",
      "new_state": "q1",
      "write": "b",
      "move": "R"
    },
    {
      "state": "q1",
      "symbol": "_",
      "new_state": "q_halt",
      "write": "_",
      "move": "R"
    }
  ]
}
```

**Run it:**
```bash
./run.sh turing-machine --config machines/my_machine.json --tape "aaa"
```

---

## Example 12: Loading Sample Sentences

Use the provided sample sentence corpus.

```python
# Load sentences from file
sentences = []
with open('data/input/sample_sentences.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if len(line.split()) >= 15:  # Minimum length check
                sentences.append(line)

print(f"Loaded {len(sentences)} sentences")

# Use in your experiments
from src.translation import ErrorInjector
from src.evaluation import HuggingFaceEmbedding, EvaluationEngine

injector = ErrorInjector(seed=42)
embedder = HuggingFaceEmbedding()
engine = EvaluationEngine(embedder)

# Process first sentence
sentence = sentences[0]
corrupted = injector.inject_errors(sentence, error_rate=0.3)
result = engine.evaluate(sentence, corrupted)

print(f"Original: {sentence[:60]}...")
print(f"Corrupted: {corrupted[:60]}...")
print(f"Distance: {result.cosine_distance:.4f}")
```

---

## Tips and Best Practices

### 1. Error Rates
- Start with 0.15-0.30 for realistic tests
- Use 0.0 as baseline (no errors)
- Maximum recommended: 0.50 (50%)

### 2. Reproducibility
- Always set a seed for error injection
- Document all seeds used
- Same seed + same input = same output

### 3. Performance
- Batch processing is more efficient than individual calls
- First embedding generation is slower (model loading)
- Subsequent calls are fast (~50ms per sentence)

### 4. Sentence Length
- Minimum 15 words required for translation commands
- Longer sentences show more variation in results
- Use diverse sentence types for better analysis

### 5. Output Organization
- Use timestamped directories for experiments
- Keep original and processed data separate
- Export both JSON (complete) and CSV (analysis)

---

## Common Workflows

### Research Workflow
1. Prepare sentences in `data/input/`
2. Run `run_comprehensive_experiments.py`
3. Analyze results in `results/experiments/`
4. Generate additional graphs as needed
5. Export data for publication

### Development Workflow
1. Test individual components with `demo.py`
2. Create custom TM configurations
3. Test with `./run.sh turing-machine`
4. Iterate on agent prompts in `src/agents/*.md`

### Teaching Workflow
1. Show Turing machine examples
2. Demonstrate error injection
3. Explain semantic similarity
4. Run live experiments with student input

---

**For more examples, see:**
- `demo.py` - Component demonstrations
- `run_comprehensive_experiments.py` - Full experiment suite
- `notebooks/analysis_example.ipynb` - Jupyter notebook examples
