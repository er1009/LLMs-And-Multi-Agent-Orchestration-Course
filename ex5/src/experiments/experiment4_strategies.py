"""Experiment 4: Context Engineering Strategies.

This experiment compares SELECT, COMPRESS, and WRITE strategies
for managing growing context in multi-turn scenarios.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from src.experiments.base import BaseExperiment
from src.utils.ollama_client import OllamaClient
from src.utils.tokenization import count_tokens
from src.utils.visualization import create_strategy_comparison_table, plot_strategy_trends
from src.config.settings import config

logger = logging.getLogger(__name__)


class ContextStrategy(ABC):
    """Abstract base class for context management strategies."""

    def __init__(self, model: str = "llama2"):
        """Initialize strategy.

        Args:
            model: Model name for token counting
        """
        self.model = model
        self.history = []

    @abstractmethod
    def add_to_history(self, action_output: str) -> None:
        """Add new action output to history.

        Args:
            action_output: Output from latest action
        """
        pass

    @abstractmethod
    def get_context(self, query: str) -> str:
        """Get context for next query.

        Args:
            query: Current query

        Returns:
            Context string to use
        """
        pass

    def get_context_size(self) -> int:
        """Get current context size in tokens.

        Returns:
            Token count
        """
        context = self.get_context("")
        return count_tokens(context, model_name=self.model)


class SelectStrategy(ContextStrategy):
    """SELECT strategy: RAG-based selective retrieval.

    Only retrieves relevant history using similarity search.
    """

    def __init__(self, model: str = "llama2", max_k: int = 5):
        """Initialize SELECT strategy.

        Args:
            model: Model name
            max_k: Maximum number of items to retrieve
        """
        super().__init__(model)
        self.max_k = max_k
        self.embedding_model = SentenceTransformer(config.embedding_model)

        # Setup vector store
        chroma_client = chromadb.PersistentClient(path=config.chroma_persist_dir)

        collection_name = f"select_strategy_{id(self)}"
        try:
            chroma_client.delete_collection(name=collection_name)
        except:
            pass

        self.vector_store = chroma_client.create_collection(name=collection_name)
        self.doc_count = 0

    def add_to_history(self, action_output: str) -> None:
        """Add to history and vector store.

        Args:
            action_output: Action output to add
        """
        self.history.append(action_output)

        # Add to vector store
        embedding = self.embedding_model.encode([action_output])[0]
        self.vector_store.add(
            ids=[f"action_{self.doc_count}"],
            embeddings=[embedding.tolist()],
            documents=[action_output]
        )
        self.doc_count += 1

    def get_context(self, query: str) -> str:
        """Get relevant context using similarity search.

        Args:
            query: Current query

        Returns:
            Context with most relevant history items
        """
        if not self.history:
            return ""

        if len(self.history) < 3:
            # Too few items, return all
            return "\n\n".join(self.history)

        # Query vector store
        query_embedding = self.embedding_model.encode([query])[0]
        results = self.vector_store.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=min(self.max_k, len(self.history))
        )

        relevant_docs = results["documents"][0]
        return "\n\n".join(relevant_docs)


class CompressStrategy(ContextStrategy):
    """COMPRESS strategy: Automatic summarization.

    Summarizes older history when it exceeds threshold.
    """

    def __init__(
        self,
        model: str = "llama2",
        max_tokens: int = 2000,
        client: Optional[OllamaClient] = None
    ):
        """Initialize COMPRESS strategy.

        Args:
            model: Model name
            max_tokens: Maximum context tokens before compression
            client: Ollama client for summarization
        """
        super().__init__(model)
        self.max_tokens = max_tokens
        self.client = client or OllamaClient(model=model)
        self.summary = None

    def add_to_history(self, action_output: str) -> None:
        """Add to history.

        Args:
            action_output: Action output to add
        """
        self.history.append(action_output)

    def get_context(self, query: str) -> str:
        """Get context with compression if needed.

        Args:
            query: Current query

        Returns:
            Context (compressed if necessary)
        """
        if not self.history:
            return ""

        full_context = "\n\n".join(self.history)
        token_count = count_tokens(full_context, model_name=self.model)

        if token_count <= self.max_tokens:
            return full_context

        # Need to compress: keep recent items full, summarize older ones
        recent_items = self.history[-3:]  # Keep last 3 items
        older_items = self.history[:-3]

        if older_items:
            # Summarize older items
            try:
                summary_prompt = (
                    "Summarize the following action history concisely, "
                    "preserving key information:\n\n" +
                    "\n\n".join(older_items)
                )
                self.summary = self.client.query(context="", question=summary_prompt)
                logger.debug(f"Compressed {len(older_items)} items into summary")
            except Exception as e:
                logger.warning(f"Summarization failed: {e}, using truncation")
                self.summary = "\n\n".join(older_items[:2])

            return self.summary + "\n\n" + "\n\n".join(recent_items)

        return "\n\n".join(recent_items)


class WriteStrategy(ContextStrategy):
    """WRITE strategy: External scratchpad memory.

    Maintains external key-value store of facts.
    """

    def __init__(self, model: str = "llama2", client: Optional[OllamaClient] = None):
        """Initialize WRITE strategy.

        Args:
            model: Model name
            client: Ollama client for fact extraction
        """
        super().__init__(model)
        self.scratchpad = {}  # key-value store
        self.client = client or OllamaClient(model=model)

    def extract_key_facts(self, text: str) -> Dict[str, str]:
        """Extract key facts from text.

        Args:
            text: Text to extract facts from

        Returns:
            Dictionary of key-value facts
        """
        try:
            prompt = (
                "Extract key facts from this text as simple key-value pairs. "
                "Format: 'Key: Value' one per line. Maximum 5 facts.\n\n" + text
            )
            response = self.client.query(context="", question=prompt)

            # Parse response
            facts = {}
            for line in response.split("\n"):
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    facts[key.strip()] = value.strip()

            return facts

        except Exception as e:
            logger.warning(f"Fact extraction failed: {e}")
            return {}

    def add_to_history(self, action_output: str) -> None:
        """Add to history and extract facts to scratchpad.

        Args:
            action_output: Action output to add
        """
        self.history.append(action_output)

        # Extract and store facts
        facts = self.extract_key_facts(action_output)
        self.scratchpad.update(facts)

    def get_context(self, query: str) -> str:
        """Get context from scratchpad and recent history.

        Args:
            query: Current query

        Returns:
            Context with relevant scratchpad entries and recent history
        """
        # Get relevant scratchpad entries
        query_words = set(query.lower().split())
        relevant_facts = []

        for key, value in self.scratchpad.items():
            key_words = set(key.lower().split())
            if query_words & key_words:  # Any overlap
                relevant_facts.append(f"{key}: {value}")

        # Combine with recent history
        recent_history = self.history[-2:] if len(self.history) >= 2 else self.history

        context_parts = []
        if relevant_facts:
            context_parts.append("Scratchpad:\n" + "\n".join(relevant_facts))
        if recent_history:
            context_parts.append("Recent History:\n" + "\n\n".join(recent_history))

        return "\n\n".join(context_parts) if context_parts else ""


class StrategyExperiment(BaseExperiment):
    """Experiment to compare context management strategies.

    Attributes:
        client: Ollama client
        strategies: Dictionary of strategy instances
    """

    def __init__(self, model: str = "llama2", random_seed: int = 42):
        """Initialize Strategy Experiment.

        Args:
            model: LLM model name
            random_seed: Random seed
        """
        super().__init__(
            experiment_name="Context Strategies",
            model=model,
            random_seed=random_seed
        )

        self.client = OllamaClient(model=model)

        # Will be initialized per strategy during experiment
        self.strategies = {}

    def run_single_trial(self, *args, **kwargs) -> Dict[str, Any]:
        """Run a single trial.
        
        Note: This experiment uses simulate_action instead of run_single_trial
        for its sequential nature. This method is implemented to satisfy
        the abstract base class requirements.
        """
        return {}

    def simulate_action(
        self,
        action_num: int,
        strategy: ContextStrategy,
        strategy_name: str
    ) -> Dict[str, Any]:
        """Simulate a single agent action.

        Args:
            action_num: Action number
            strategy: Strategy instance
            strategy_name: Strategy name

        Returns:
            Dictionary with action results
        """
        # Simulate different types of actions
        action_types = [
            ("search", "Search for information about {topic}"),
            ("analyze", "Analyze the data related to {topic}"),
            ("summarize", "Summarize findings about {topic}"),
            ("compare", "Compare results for {topic}"),
            ("conclude", "Draw conclusions about {topic}"),
        ]

        topics = ["user behavior", "system performance", "data quality", "trends", "anomalies"]

        action_type, template = action_types[action_num % len(action_types)]
        topic = topics[action_num % len(topics)]
        query = template.format(topic=topic)

        try:
            # Get context using strategy
            context = strategy.get_context(query)
            context_tokens = count_tokens(context, model_name=self.model)

            # Execute action
            start_time = time.perf_counter()
            response = self.client.query(context=context, question=query)
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Simple accuracy: check if response is reasonable (not empty, not error)
            accuracy = 1.0 if len(response) > 50 else 0.5

            # Add response to history
            action_output = f"Action {action_num} ({action_type} - {topic}): {response[:200]}"
            strategy.add_to_history(action_output)

            logger.debug(
                f"{strategy_name} action {action_num}: "
                f"tokens={context_tokens}, latency={latency_ms:.0f}ms"
            )

            return {
                "action": action_num + 1,
                "strategy": strategy_name,
                "action_type": action_type,
                "topic": topic,
                "context_tokens": context_tokens,
                "latency": latency_ms,
                "accuracy": accuracy,
                "error": None
            }

        except Exception as e:
            logger.error(f"Action {action_num} failed for {strategy_name}: {e}")
            return {
                "action": action_num + 1,
                "strategy": strategy_name,
                "context_tokens": 0,
                "latency": 0.0,
                "accuracy": 0.0,
                "error": str(e)
            }

    def run_full_experiment(
        self,
        num_actions: int = 10,
        strategies_to_test: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run complete Strategy Comparison experiment.

        Args:
            num_actions: Number of sequential actions to simulate
            strategies_to_test: List of strategy names (default: all)

        Returns:
            Dictionary with complete experiment results
        """
        if strategies_to_test is None:
            strategies_to_test = ["select", "compress", "write"]

        logger.info(
            f"Starting experiment with {num_actions} actions, "
            f"strategies={strategies_to_test}"
        )

        # Warmup
        logger.info("Warming up model...")
        self.client.warmup()

        all_results = []
        experiment_start = time.perf_counter()

        # Test each strategy
        for strategy_name in strategies_to_test:
            logger.info(f"Testing {strategy_name.upper()} strategy")

            # Initialize strategy
            if strategy_name == "select":
                strategy = SelectStrategy(model=self.model, max_k=5)
            elif strategy_name == "compress":
                strategy = CompressStrategy(
                    model=self.model,
                    max_tokens=2000,
                    client=self.client
                )
            elif strategy_name == "write":
                strategy = WriteStrategy(model=self.model, client=self.client)
            else:
                raise ValueError(f"Unknown strategy: {strategy_name}")

            # Run actions
            for action_num in range(num_actions):
                logger.info(f"  {strategy_name}: Action {action_num + 1}/{num_actions}")

                result = self.simulate_action(action_num, strategy, strategy_name)
                all_results.append(result)

        total_runtime = time.perf_counter() - experiment_start

        # Create result structure
        config_dict = {
            "num_actions": num_actions,
            "strategies": strategies_to_test,
            "model": self.model,
            "random_seed": self.random_seed,
        }

        # Convert to format for base structure
        trials_for_base = [
            {
                "accuracy": r["accuracy"],
                "latency_ms": r["latency"],
                "error": r["error"]
            }
            for r in all_results
        ]

        results = self.create_result_structure(
            trials=trials_for_base,
            config=config_dict,
            total_runtime=total_runtime
        )

        results["all_results"] = all_results

        logger.info(
            f"Experiment completed in {total_runtime:.1f}s. "
            f"Tested {len(strategies_to_test)} strategies"
        )

        return results

    def visualize_results(
        self,
        results: Dict[str, Any],
        output_dir: str
    ) -> None:
        """Generate visualizations for experiment results.

        Args:
            results: Results from run_full_experiment()
            output_dir: Directory to save graphs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create comparison table
        table_path = output_path / "strategy_comparison.csv"
        create_strategy_comparison_table(
            results=results["all_results"],
            output_path=str(table_path)
        )

        # Create trend graphs
        graph_path = output_path / "strategy_trends.png"
        plot_strategy_trends(
            results=results["all_results"],
            output_path=str(graph_path),
            show=False
        )

        logger.info(f"Saved visualizations to {output_path}")


def run_experiment(
    model: str = "llama2",
    num_actions: int = 10,
    output_dir: str = "./results/experiment4",
    random_seed: int = 42
) -> Dict[str, Any]:
    """Convenience function to run Experiment 4.

    Args:
        model: LLM model name
        num_actions: Number of actions to simulate
        output_dir: Output directory
        random_seed: Random seed

    Returns:
        Experiment results dictionary
    """
    experiment = StrategyExperiment(
        model=model,
        random_seed=random_seed
    )

    results = experiment.run_full_experiment(num_actions=num_actions)
    experiment.save_results(results, output_dir)
    experiment.visualize_results(results, output_dir)

    return results
