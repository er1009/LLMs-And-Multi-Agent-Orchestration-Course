# Project Structure

```
ex3/
├── README.md                    # Main documentation
├── QUICKSTART.md                # Quick start guide
├── requirements.txt             # Python dependencies
├── setup.py                     # Installation script
├── .gitignore                   # Git ignore rules
│
├── docs/                        # Project documentation
│   ├── PRD.md                   # Product Requirements Document
│   └── ARCHITECTURE.md          # Architecture Document
│
├── src/                         # Source code
│   ├── agents/                  # Translation agents (MD files)
│   │   ├── en_to_fr.md         # English → French
│   │   ├── fr_to_he.md         # French → Hebrew
│   │   └── he_to_en.md         # Hebrew → English
│   │
│   ├── turing_machine/          # TM simulator
│   │   ├── tape.py
│   │   ├── tm_simulator.py
│   │   └── config_loader.py
│   │
│   ├── translation/             # Translation orchestration
│   │   ├── error_injector.py
│   │   └── claude_agent_runner.py
│   │
│   ├── evaluation/              # Semantic evaluation
│   │   ├── hf_embedding.py     # HuggingFace embeddings
│   │   ├── distance.py
│   │   └── engine.py
│   │
│   ├── analysis/                # Analysis & visualization
│   │   ├── graph_generator.py
│   │   ├── statistics.py
│   │   └── exporter.py
│   │
│   └── cli.py                   # CLI interface
│
├── tests/                       # Unit tests
│   └── unit/
│       ├── test_turing_machine.py
│       ├── test_error_injector.py
│       └── test_distance.py
│
├── machines/                    # TM configurations
│   └── unary_increment.json
│
├── notebooks/                   # Jupyter notebooks
│   └── analysis_example.ipynb
│
├── config/                      # Configuration files
│   └── .env.example
│
├── data/                        # Data directory
│   ├── input/
│   └── output/
│
└── results/                     # Generated results
    ├── graphs/
    └── logs/
```

## Key Components

### Translation Agents (MD Files)
- No Python code for agents
- Prompts defined in Markdown
- Executed via Claude CLI

### Embeddings (HuggingFace)
- Local, no API keys
- Free and open source
- Model: `all-MiniLM-L6-v2`

### CLI Commands
1. `turing-machine` - Run TM simulator
2. `translate-once` - Single translation
3. `translate-batch` - Batch processing
4. `analyze` - Generate graphs

## Documentation

- **README.md** - Complete user guide
- **QUICKSTART.md** - 5-minute start guide
- **docs/PRD.md** - Product requirements
- **docs/ARCHITECTURE.md** - System design
