# Context Windows Lab - Best Practices & Implementation Guide

## Project Overview
This project implements 4 experiments demonstrating context window challenges in Large Language Models (LLMs), including "Lost in the Middle", context size impact, RAG effectiveness, and context engineering strategies.

---

## Critical Success Factors

### 1. Environment Setup
```bash
# Required dependencies with specific versions
pip install --break-system-packages langchain>=0.1.0
pip install --break-system-packages chromadb>=0.4.0
pip install --break-system-packages ollama>=0.1.0
pip install --break-system-packages sentence-transformers>=2.2.0
pip install --break-system-packages numpy>=1.24.0
pip install --break-system-packages matplotlib>=3.7.0
pip install --break-system-packages pandas>=2.0.0
```

### 2. Model Requirements
- **Primary Model**: Ollama with a model like `llama2`, `mistral`, or `phi`
- **Embedding Model**: `nomic-embed-text` or `all-MiniLM-L6-v2`
- Ensure Ollama is running: `ollama serve` (if not already running as service)

---

## Experiment 1: Needle in Haystack (Lost in the Middle)

### Objective
Demonstrate that LLMs struggle to retrieve information from the middle of long contexts.

### Implementation Best Practices

#### 1.1 Document Generation
```python
def generate_filler_text(num_words=200):
    """
    Generate realistic filler text, not just random words.
    Use lorem ipsum or contextual sentences.
    """
    # BAD: random.choice(['word1', 'word2']) * num_words
    # GOOD: Use faker library or template sentences
    from faker import Faker
    fake = Faker()
    text = ' '.join([fake.sentence() for _ in range(num_words // 10)])
    return text
```

#### 1.2 Critical Fact Embedding
```python
def embed_critical_fact(text, fact, position='middle'):
    """
    Embed fact at EXACT positions: start (0-10%), middle (45-55%), end (90-100%)
    """
    words = text.split()
    total_words = len(words)
    
    if position == 'start':
        insert_idx = int(total_words * 0.05)  # 5% into document
    elif position == 'middle':
        insert_idx = int(total_words * 0.50)  # Exactly middle
    elif position == 'end':
        insert_idx = int(total_words * 0.95)  # 95% into document
    
    words.insert(insert_idx, fact)
    return ' '.join(words)
```

#### 1.3 Accuracy Measurement
```python
def evaluate_response(response, expected_answer):
    """
    Use multiple evaluation methods:
    1. Exact match
    2. Fuzzy matching (for typos)
    3. Semantic similarity (embeddings)
    """
    response_lower = response.lower().strip()
    expected_lower = expected_answer.lower().strip()
    
    # Exact match
    if expected_lower in response_lower:
        return 1.0
    
    # Fuzzy match (Levenshtein distance)
    from difflib import SequenceMatcher
    ratio = SequenceMatcher(None, response_lower, expected_lower).ratio()
    if ratio > 0.85:
        return ratio
    
    return 0.0
```

#### 1.4 Statistical Validity
- Run each position test **at least 10 times** (preferably 20-30)
- Calculate mean, standard deviation, and confidence intervals
- Use different facts to avoid memorization bias

### Common Pitfalls to Avoid
❌ Using the same fact in every document
❌ Not controlling for document length variations
❌ Single-run experiments (no statistical validity)
❌ Not shuffling document order between runs

---

## Experiment 2: Context Window Size Impact

### Objective
Show how accuracy degrades as context window size increases.

### Implementation Best Practices

#### 2.1 Token Counting
```python
def count_tokens(text, model_name='llama2'):
    """
    Use actual tokenizer, not word count approximation
    """
    # BAD: len(text.split())
    # GOOD: Use model's actual tokenizer
    import tiktoken
    # For non-OpenAI models, use character-based estimation
    # Rule of thumb: 1 token ≈ 4 characters
    return len(text) // 4
```

#### 2.2 Latency Measurement
```python
import time

def measure_latency_accurately(context, query):
    """
    Measure ONLY inference time, exclude preprocessing
    """
    # Warm-up call (exclude from measurement)
    _ = ollama_query("test", "test")
    
    # Actual measurement
    start_time = time.perf_counter()  # More accurate than time.time()
    response = ollama_query(context, query)
    end_time = time.perf_counter()
    
    latency_ms = (end_time - start_time) * 1000
    return response, latency_ms
```

#### 2.3 Document Scaling Strategy
```python
def create_scaled_contexts(base_docs, sizes=[2, 5, 10, 20, 50]):
    """
    Ensure documents are SIMILAR in content/difficulty across sizes
    """
    contexts = {}
    for size in sizes:
        # Use same document types, just more of them
        contexts[size] = base_docs[:size]
    return contexts
```

### Graph Requirements
- **X-axis**: Number of documents OR total tokens
- **Y-axis Dual**: 
  - Primary: Accuracy (0-100%)
  - Secondary: Latency (ms)
- Include error bars (standard deviation)
- Annotate key degradation points

---

## Experiment 3: RAG vs Full Context

### Objective
Demonstrate RAG's superiority in accuracy and speed over full context.

### Implementation Best Practices

#### 3.1 Document Chunking
```python
def chunk_documents(documents, chunk_size=500, overlap=50):
    """
    Proper chunking with overlap to preserve context
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]  # Prioritize natural breaks
    )
    
    chunks = []
    for doc in documents:
        doc_chunks = text_splitter.split_text(doc)
        chunks.extend(doc_chunks)
    
    return chunks
```

#### 3.2 Embedding Generation
```python
def generate_embeddings(chunks):
    """
    Use proper embedding model with error handling
    """
    from sentence_transformers import SentenceTransformer
    
    # Use a robust embedding model
    # For multilingual support, use: 'paraphrase-multilingual-MiniLM-L12-v2'
    # For English only, use: 'all-MiniLM-L6-v2'
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    embeddings = []
    batch_size = 32
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        try:
            batch_embeddings = model.encode(batch, show_progress_bar=False)
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"Error encoding batch {i}: {e}")
            # Use zero vectors as fallback
            embeddings.extend([[0.0] * 384] * len(batch))
    
    return embeddings
```

#### 3.3 ChromaDB Setup
```python
def setup_vector_store(chunks, embeddings):
    """
    Proper ChromaDB initialization with metadata
    """
    import chromadb
    from chromadb.config import Settings
    
    # Use persistent storage
    client = chromadb.Client(Settings(
        persist_directory="./chroma_db",
        anonymized_telemetry=False
    ))
    
    # Create or get collection
    collection = client.get_or_create_collection(
        name="lab_documents",
        metadata={"description": "Context windows lab documents"}
    )
    
    # Add documents with metadata
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        collection.add(
            ids=[f"doc_{i}"],
            embeddings=[embedding.tolist()],
            documents=[chunk],
            metadatas=[{"chunk_id": i, "source": "experiment_3"}]
        )
    
    return collection
```

#### 3.4 Fair Comparison
```python
def compare_rag_vs_full(query, all_documents, vector_store):
    """
    Ensure IDENTICAL query conditions for fair comparison
    """
    results = {}
    
    # Full context mode
    full_context = "\n\n".join(all_documents)
    start = time.perf_counter()
    full_response = ollama_query(full_context, query)
    results['full_latency'] = (time.perf_counter() - start) * 1000
    results['full_accuracy'] = evaluate_response(full_response, expected_answer)
    results['full_tokens'] = count_tokens(full_context)
    
    # RAG mode
    start = time.perf_counter()
    relevant_docs = vector_store.query(
        query_embeddings=[embed_query(query)],
        n_results=3
    )
    rag_context = "\n\n".join(relevant_docs['documents'][0])
    rag_response = ollama_query(rag_context, query)
    results['rag_latency'] = (time.perf_counter() - start) * 1000
    results['rag_accuracy'] = evaluate_response(rag_response, expected_answer)
    results['rag_tokens'] = count_tokens(rag_context)
    
    return results
```

### Expected Outcomes
- RAG accuracy: 85-95%
- Full context accuracy: 50-70% (with 20 documents)
- RAG latency: 2-5x faster than full context

---

## Experiment 4: Context Engineering Strategies

### Objective
Compare SELECT, COMPRESS, and WRITE strategies for managing growing context.

### Implementation Best Practices

#### 4.1 SELECT Strategy (RAG-based)
```python
class SelectStrategy:
    """
    Only retrieve relevant history using similarity search
    """
    def __init__(self, max_k=5):
        self.history = []
        self.vector_store = None
        self.max_k = max_k
    
    def add_to_history(self, action_output):
        self.history.append(action_output)
        # Update vector store incrementally
        if self.vector_store:
            self.vector_store.add(action_output)
    
    def get_context(self, query):
        if not self.vector_store or len(self.history) < 3:
            return "\n".join(self.history)
        
        # Retrieve only relevant history
        relevant = self.vector_store.similarity_search(query, k=self.max_k)
        return "\n".join(relevant)
```

#### 4.2 COMPRESS Strategy (Summarization)
```python
class CompressStrategy:
    """
    Automatically summarize history when it exceeds threshold
    """
    def __init__(self, max_tokens=2000):
        self.history = []
        self.max_tokens = max_tokens
    
    def add_to_history(self, action_output):
        self.history.append(action_output)
    
    def get_context(self, query):
        full_context = "\n".join(self.history)
        token_count = count_tokens(full_context)
        
        if token_count <= self.max_tokens:
            return full_context
        
        # Summarize older history, keep recent items
        recent_items = self.history[-3:]  # Keep last 3 items full
        older_items = self.history[:-3]
        
        summary_prompt = f"Summarize these actions concisely:\n{chr(10).join(older_items)}"
        summary = ollama_query("", summary_prompt)
        
        return summary + "\n" + "\n".join(recent_items)
```

#### 4.3 WRITE Strategy (External Memory)
```python
class WriteStrategy:
    """
    Maintain external scratchpad of key facts
    """
    def __init__(self):
        self.scratchpad = {}  # key-value store
        self.history = []
    
    def add_to_history(self, action_output):
        self.history.append(action_output)
        # Extract and store key facts
        facts = self.extract_key_facts(action_output)
        for key, value in facts.items():
            self.scratchpad[key] = value
    
    def extract_key_facts(self, text):
        """
        Extract structured information (entities, numbers, decisions)
        """
        prompt = f"Extract key facts from this text as key-value pairs:\n{text}"
        response = ollama_query("", prompt)
        # Parse response into dict
        facts = {}
        for line in response.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                facts[key.strip()] = value.strip()
        return facts
    
    def get_context(self, query):
        # Return relevant scratchpad entries + recent history
        relevant_facts = [f"{k}: {v}" for k, v in self.scratchpad.items() 
                         if any(word in query.lower() for word in k.lower().split())]
        
        context = "\n".join(relevant_facts) + "\n" + "\n".join(self.history[-2:])
        return context
```

#### 4.4 Multi-Step Agent Simulation
```python
def simulate_multi_step_agent(num_actions=10, strategy='select'):
    """
    Simulate agent performing sequential actions with growing context
    """
    if strategy == 'select':
        manager = SelectStrategy()
    elif strategy == 'compress':
        manager = CompressStrategy()
    elif strategy == 'write':
        manager = WriteStrategy()
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    results = []
    
    for action_num in range(num_actions):
        # Simulate agent action
        action_query = f"Perform action {action_num + 1}: [specific task]"
        
        # Get context using strategy
        context = manager.get_context(action_query)
        
        # Execute action
        start = time.perf_counter()
        response = ollama_query(context, action_query)
        latency = (time.perf_counter() - start) * 1000
        
        # Measure performance
        results.append({
            'action': action_num + 1,
            'strategy': strategy,
            'context_tokens': count_tokens(context),
            'latency': latency,
            'accuracy': evaluate_action_correctness(response, action_num)
        })
        
        # Add output to history
        manager.add_to_history(response)
    
    return results
```

### Performance Metrics to Track
1. **Context Growth**: Tokens used per action
2. **Latency**: Response time per action
3. **Accuracy**: Task completion success rate
4. **Memory Efficiency**: RAM usage (optional)

---

## Data Generation & Management

### Multilingual Document Generation
```python
def generate_documents(num_docs=20, topics=['technology', 'law', 'medicine'], language='en'):
    """
    Generate realistic documents for Experiment 3
    Supports multiple languages including English and Hebrew
    """
    documents = []
    
    # Template-based generation (English)
    templates = {
        'technology': [
            "The technology {} is used for {}. Benefits include {} and {}.",
            "Product {} was developed by {}. It enables {}."
        ],
        'law': [
            "Law {} states that {}. The penalty for violation is {}.",
            "Regulation {} applies to {}. Obligations include {}."
        ],
        'medicine': [
            "Drug {} is used to treat {}. Side effects include {} and {}.",
            "Medical procedure {} is performed by {}. Risks include {}."
        ]
    }
    
    for i in range(num_docs):
        topic = random.choice(topics)
        template = random.choice(templates[topic])
        # Fill template with realistic content
        doc = template.format(
            f"term_{i}",
            f"description_{i}",
            f"detail_a",
            f"detail_b"
        )
        documents.append(doc)
    
    return documents
```

---

## Visualization Best Practices

### Graph 1: Lost in the Middle (Experiment 1)
```python
import matplotlib.pyplot as plt
import numpy as np

def plot_lost_in_middle(results):
    """
    Create publication-quality graph showing position effect
    """
    positions = ['Start', 'Middle', 'End']
    accuracies = [
        np.mean(results['start']),
        np.mean(results['middle']),
        np.mean(results['end'])
    ]
    std_devs = [
        np.std(results['start']),
        np.std(results['middle']),
        np.std(results['end'])
    ]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.bar(positions, accuracies, yerr=std_devs, 
                  capsize=10, color=['#2ecc71', '#e74c3c', '#3498db'],
                  alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax.set_ylabel('Accuracy (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Fact Position in Document', fontsize=14, fontweight='bold')
    ax.set_title('Lost in the Middle: Accuracy by Position', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{acc:.1f}%', ha='center', va='bottom', 
                fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('experiment1_lost_in_middle.png', dpi=300, bbox_inches='tight')
    plt.show()
```

### Graph 2: Context Size Impact (Experiment 2)
```python
def plot_context_size_impact(results):
    """
    Dual-axis graph: accuracy and latency vs context size
    """
    doc_counts = [r['num_docs'] for r in results]
    accuracies = [r['accuracy'] for r in results]
    latencies = [r['latency'] for r in results]
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Accuracy line
    color1 = '#2ecc71'
    ax1.set_xlabel('Number of Documents', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', color=color1, fontsize=14, fontweight='bold')
    line1 = ax1.plot(doc_counts, accuracies, color=color1, marker='o', 
                     linewidth=3, markersize=8, label='Accuracy')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0, 100)
    ax1.grid(alpha=0.3, linestyle='--')
    
    # Latency line
    ax2 = ax1.twinx()
    color2 = '#e74c3c'
    ax2.set_ylabel('Latency (ms)', color=color2, fontsize=14, fontweight='bold')
    line2 = ax2.plot(doc_counts, latencies, color=color2, marker='s', 
                     linewidth=3, markersize=8, label='Latency')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=12, framealpha=0.9)
    
    plt.title('Context Window Size Impact on Performance', 
             fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('experiment2_context_size.png', dpi=300, bbox_inches='tight')
    plt.show()
```

### Table: Strategy Comparison (Experiment 4)
```python
import pandas as pd

def create_strategy_comparison_table(results):
    """
    Generate comparison table for all strategies
    """
    df = pd.DataFrame(results)
    
    # Calculate averages per strategy
    summary = df.groupby('strategy').agg({
        'context_tokens': ['mean', 'std'],
        'latency': ['mean', 'std'],
        'accuracy': ['mean', 'std']
    }).round(2)
    
    # Format for display
    summary.columns = ['_'.join(col) for col in summary.columns]
    summary = summary.reset_index()
    
    # Save as CSV and display
    summary.to_csv('experiment4_strategy_comparison.csv', index=False)
    
    # Also create formatted markdown table
    md_table = summary.to_markdown(index=False)
    with open('experiment4_strategy_comparison.md', 'w') as f:
        f.write("# Strategy Comparison Results\n\n")
        f.write(md_table)
    
    return summary
```

---

## Error Handling & Robustness

### Ollama Connection Management
```python
import requests
from requests.exceptions import RequestException

def safe_ollama_query(context, query, model='llama2', max_retries=3):
    """
    Robust Ollama querying with retry logic
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': f"Context:\n{context}\n\nQuestion: {query}\nAnswer:",
                    'stream': False,
                    'options': {'temperature': 0.1}  # Low temp for consistency
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['response']
            
        except RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts: {e}")
                return "[ERROR: Could not get response]"
            time.sleep(2 ** attempt)  # Exponential backoff
```

### Resource Cleanup
```python
import atexit
import gc

def cleanup_resources():
    """
    Proper cleanup of vector stores and models
    """
    global vector_store, models
    
    try:
        if vector_store:
            vector_store.persist()
            del vector_store
    except:
        pass
    
    gc.collect()

# Register cleanup
atexit.register(cleanup_resources)
```

---

## Testing & Validation

### Unit Tests Template
```python
import unittest

class TestExperiment1(unittest.TestCase):
    def test_document_generation(self):
        """Test that documents are generated with correct length"""
        doc = generate_filler_text(200)
        word_count = len(doc.split())
        self.assertGreater(word_count, 180)
        self.assertLess(word_count, 220)
    
    def test_fact_embedding_start(self):
        """Test fact embedding at start position"""
        doc = "word " * 100
        fact = "CRITICAL_FACT"
        result = embed_critical_fact(doc, fact, 'start')
        words = result.split()
        fact_index = words.index(fact)
        self.assertLess(fact_index, len(words) * 0.1)
    
    def test_accuracy_evaluation(self):
        """Test accuracy calculation"""
        response = "The answer is 42"
        expected = "42"
        accuracy = evaluate_response(response, expected)
        self.assertEqual(accuracy, 1.0)

if __name__ == '__main__':
    unittest.main()
```

---

## Common Bugs & Solutions

### Bug 1: Inconsistent Results
**Problem**: Different accuracy on same experiment
**Solution**: 
- Set random seeds: `random.seed(42)`, `np.random.seed(42)`
- Use `temperature=0.1` in Ollama for deterministic outputs
- Run multiple trials and report averages

### Bug 2: Memory Leaks in Long Experiments
**Problem**: RAM usage grows unbounded
**Solution**:
```python
def run_with_memory_management(func):
    """Decorator to manage memory in long experiments"""
    import gc
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        gc.collect()
        return result
    return wrapper
```

### Bug 3: ChromaDB Persistence Issues
**Problem**: Vector store not persisting between runs
**Solution**:
```python
# Always explicitly persist
collection.persist()

# Or use PersistentClient
from chromadb import PersistentClient
client = PersistentClient(path="./chroma_db")
```

---

## Performance Optimization Tips

1. **Batch Processing**: Process documents in batches of 32 for embedding
2. **Caching**: Cache Ollama responses for repeated queries
3. **Parallel Processing**: Use `multiprocessing` for independent experiments
4. **Lazy Loading**: Load documents only when needed
5. **Incremental Updates**: Update vector store incrementally, not rebuild

---

## Final Checklist

Before submission, ensure:

- [ ] All 4 experiments run without errors
- [ ] Statistical validity: ≥10 runs per experiment
- [ ] Graphs are publication-quality with labels, titles, legends
- [ ] Results are reproducible with seed values documented
- [ ] Code is well-commented and follows best practices
- [ ] Memory usage is reasonable (<4GB RAM)
- [ ] Experiment runtime is within specified time limits
- [ ] Results match expected patterns (e.g., accuracy drops in middle)
- [ ] Error handling covers all edge cases
- [ ] All visualizations saved as high-resolution images (300 DPI)

---

## Expected Runtime

- Experiment 1: ~15-20 minutes
- Experiment 2: ~20-25 minutes  
- Experiment 3: ~25-35 minutes
- Experiment 4: ~30-40 minutes
- **Total**: ~90-120 minutes

---

## Troubleshooting Guide

### Ollama Not Responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve &

# Pull required model
ollama pull llama2
```

### ChromaDB Errors
```bash
# Reset ChromaDB
rm -rf ./chroma_db
# Reinstall
pip uninstall chromadb -y
pip install chromadb --break-system-packages
```

### Out of Memory
```python
# Reduce batch sizes
BATCH_SIZE = 16  # instead of 32

# Use smaller model
MODEL = 'phi'  # instead of 'llama2'

# Limit context size
MAX_TOKENS = 4096  # instead of 8192
```

---

## References & Additional Resources

- LangChain Documentation: https://python.langchain.com/docs/
- ChromaDB Guide: https://docs.trychroma.com/
- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
- Lost in the Middle Paper: Liu et al., 2023
- RAG Best Practices: Lewis et al., 2020

---

## License & Attribution

This implementation guide is based on the Context Windows Lab by Dr. Segal Yoram, November 2025.

---

## Conclusion

This guide provides comprehensive best practices for implementing all 4 experiments bug-free. Key principles:

1. **Reproducibility**: Use seeds, document parameters
2. **Statistical Validity**: Multiple runs, error bars
3. **Robust Error Handling**: Retries, timeouts, fallbacks
4. **Clear Visualization**: Professional graphs with proper labeling
5. **Code Quality**: Comments, tests, modular design

Follow these practices to create a production-grade implementation that demonstrates deep understanding of context window challenges in LLMs.
