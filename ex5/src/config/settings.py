"""Configuration management for Context Windows Lab.

This module handles all configuration settings, environment variables,
and default values for experiments.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Central configuration for all experiments.

    Attributes:
        ollama_base_url: Base URL for Ollama API
        ollama_model: Default model name (llama2, mistral, phi)
        ollama_temperature: Sampling temperature for consistency
        ollama_timeout: Request timeout in seconds
        default_num_runs: Default number of trials per experiment
        random_seed: Random seed for reproducibility
        batch_size: Batch size for embedding generation
        max_workers: Maximum parallel workers
        chroma_persist_dir: ChromaDB storage directory
        embedding_model: Sentence transformer model name
        results_dir: Output directory for results
        graph_dpi: DPI for saved graphs
        save_raw_results: Whether to save raw JSON results
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Log file path
    """

    # Ollama Configuration
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    ollama_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama2")
    )
    ollama_temperature: float = field(
        default_factory=lambda: float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))
    )
    ollama_timeout: int = field(
        default_factory=lambda: int(os.getenv("OLLAMA_TIMEOUT", "60"))
    )

    # Experiment Configuration
    default_num_runs: int = field(
        default_factory=lambda: int(os.getenv("DEFAULT_NUM_RUNS", "10"))
    )
    random_seed: int = field(
        default_factory=lambda: int(os.getenv("RANDOM_SEED", "42"))
    )

    # Performance Configuration
    batch_size: int = field(
        default_factory=lambda: int(os.getenv("BATCH_SIZE", "32"))
    )
    max_workers: int = field(
        default_factory=lambda: int(os.getenv("MAX_WORKERS", "4"))
    )

    # Vector Store Configuration
    chroma_persist_dir: str = field(
        default_factory=lambda: os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )

    # Results Configuration
    results_dir: str = field(
        default_factory=lambda: os.getenv("RESULTS_DIR", "./results")
    )
    graph_dpi: int = field(
        default_factory=lambda: int(os.getenv("GRAPH_DPI", "300"))
    )
    save_raw_results: bool = field(
        default_factory=lambda: os.getenv("SAVE_RAW_RESULTS", "true").lower() == "true"
    )

    # Logging Configuration
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO")
    )
    log_file: Optional[str] = field(
        default_factory=lambda: os.getenv("LOG_FILE", "./logs/experiment.log")
    )

    def __post_init__(self):
        """Create necessary directories after initialization."""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "ollama_base_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
            "ollama_temperature": self.ollama_temperature,
            "ollama_timeout": self.ollama_timeout,
            "default_num_runs": self.default_num_runs,
            "random_seed": self.random_seed,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "chroma_persist_dir": self.chroma_persist_dir,
            "embedding_model": self.embedding_model,
            "results_dir": self.results_dir,
            "graph_dpi": self.graph_dpi,
            "save_raw_results": self.save_raw_results,
            "log_level": self.log_level,
            "log_file": self.log_file,
        }


# Global configuration instance
config = Config()
