"""Experiment 2: Context Window Size Impact.

This experiment analyzes how accuracy and latency degrade as
context window size increases.
"""

import logging
import time
from typing import Dict, Any, List
from pathlib import Path

from src.experiments.base import BaseExperiment
from src.utils.ollama_client import OllamaClient
from src.utils.document_generator import DocumentGenerator
from src.utils.evaluation import evaluate_response
from src.utils.tokenization import count_tokens
from src.utils.visualization import plot_context_size_impact

logger = logging.getLogger(__name__)


class ContextSizeExperiment(BaseExperiment):
    """Experiment to measure impact of context size on performance.

    Tests how accuracy and latency change as the number of documents
    in the context increases.

    Attributes:
        client: Ollama client for LLM queries
        doc_generator: Document generator
        words_per_doc: Words per document (kept constant)
    """

    def __init__(
        self,
        model: str = "llama2",
        random_seed: int = 42,
        words_per_doc: int = 200
    ):
        """Initialize Context Size Impact experiment.

        Args:
            model: LLM model name
            random_seed: Random seed for reproducibility
            words_per_doc: Number of words per document
        """
        super().__init__(
            experiment_name="Context Size Impact",
            model=model,
            random_seed=random_seed
        )

        self.words_per_doc = words_per_doc
        self.client = OllamaClient(model=model)
        self.doc_generator = DocumentGenerator(random_seed=random_seed)

        logger.info(f"Initialized with words_per_doc={words_per_doc}")

    def create_test_documents(
        self,
        num_docs: int,
        target_fact_index: int = None
    ) -> tuple[List[str], str, str]:
        """Create test documents with one containing the answer.

        Args:
            num_docs: Number of documents to create
            target_fact_index: Index where to place the fact (random if None)

        Returns:
            Tuple of (documents, fact, question)
        """
        import random

        # Select random fact
        facts = [
            ("The capital of Atlantis is Poseidonia", "What is the capital of Atlantis?"),
            ("The speed of light is 299792458 meters per second", "What is the speed of light?"),
            ("The highest mountain on Mars is Olympus Mons", "What is the highest mountain on Mars?"),
            ("The chemical formula for table salt is NaCl", "What is the chemical formula for table salt?"),
            ("The Fibonacci sequence starts with 0 and 1", "How does the Fibonacci sequence start?"),
        ]

        fact, question = random.choice(facts)
        expected_answer = fact.split(" is ")[-1] if " is " in fact else fact.split()[-1]

        # Generate documents
        docs_data = self.doc_generator.generate_realistic_documents(
            num_docs=num_docs,
            words_per_doc=self.words_per_doc,
            topics=["technology", "law", "medicine"]
        )

        documents = [doc["content"] for doc in docs_data]

        # Embed fact in one document
        if target_fact_index is None:
            target_fact_index = num_docs // 2  # Middle document

        target_fact_index = min(target_fact_index, len(documents) - 1)

        # Insert fact into target document
        words = documents[target_fact_index].split()
        insert_pos = len(words) // 2
        words.insert(insert_pos, f" {fact} ")
        documents[target_fact_index] = " ".join(words)

        return documents, expected_answer, question

    def run_single_trial(
        self,
        num_docs: int
    ) -> Dict[str, Any]:
        """Run a single trial with specified number of documents.

        Args:
            num_docs: Number of documents in context

        Returns:
            Dictionary with trial results
        """
        try:
            # Create test documents
            documents, expected_answer, question = self.create_test_documents(num_docs)

            # Combine into single context
            context = "\n\n---\n\n".join(documents)

            # Count tokens
            token_count = count_tokens(context, model_name=self.model)

            # Query model
            start_time = time.perf_counter()
            response = self.client.query(
                context=context,
                question=question
            )
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Evaluate
            accuracy = evaluate_response(response, expected_answer, method="multi")

            logger.debug(
                f"Trial: num_docs={num_docs}, tokens={token_count}, "
                f"accuracy={accuracy:.2f}, latency={latency_ms:.0f}ms"
            )

            return {
                "num_docs": num_docs,
                "token_count": token_count,
                "accuracy": accuracy,
                "latency_ms": latency_ms,
                "response": response,
                "expected_answer": expected_answer,
                "error": None
            }

        except Exception as e:
            logger.error(f"Trial failed for num_docs={num_docs}: {e}")
            return {
                "num_docs": num_docs,
                "token_count": 0,
                "accuracy": 0.0,
                "latency_ms": 0.0,
                "response": None,
                "error": str(e)
            }

    def run_full_experiment(
        self,
        num_runs: int = 10,
        doc_counts: List[int] = None
    ) -> Dict[str, Any]:
        """Run complete Context Size Impact experiment.

        Args:
            num_runs: Number of trials per document count
            doc_counts: List of document counts to test

        Returns:
            Dictionary with complete experiment results
        """
        if doc_counts is None:
            doc_counts = [2, 5, 10, 20, 50]

        logger.info(
            f"Starting experiment with {num_runs} runs per size, "
            f"doc_counts={doc_counts}"
        )

        # Warmup
        logger.info("Warming up model...")
        self.client.warmup()

        all_trials = []
        experiment_start = time.perf_counter()

        # Run trials for each document count
        for doc_count in doc_counts:
            logger.info(f"Testing with {doc_count} documents")

            for run in range(num_runs):
                logger.info(f"  Run {run + 1}/{num_runs}")

                trial_result = self.run_single_trial(num_docs=doc_count)
                trial_result["trial_id"] = len(all_trials)
                trial_result["run_number"] = run
                all_trials.append(trial_result)

        total_runtime = time.perf_counter() - experiment_start

        # Aggregate results by document count
        aggregated = []
        for doc_count in doc_counts:
            trials_for_count = [t for t in all_trials if t["num_docs"] == doc_count and t["error"] is None]

            if trials_for_count:
                import numpy as np
                accuracies = [t["accuracy"] for t in trials_for_count]
                latencies = [t["latency_ms"] for t in trials_for_count]

                aggregated.append({
                    "num_docs": doc_count,
                    "accuracy": float(np.mean(accuracies)),
                    "accuracy_std": float(np.std(accuracies)),
                    "latency": float(np.mean(latencies)),
                    "latency_std": float(np.std(latencies)),
                    "avg_tokens": float(np.mean([t["token_count"] for t in trials_for_count]))
                })

        # Create result structure
        config = {
            "num_runs": num_runs,
            "doc_counts": doc_counts,
            "words_per_doc": self.words_per_doc,
            "model": self.model,
            "random_seed": self.random_seed,
        }

        results = self.create_result_structure(
            trials=all_trials,
            config=config,
            total_runtime=total_runtime
        )

        results["aggregated_by_size"] = aggregated

        logger.info(
            f"Experiment completed in {total_runtime:.1f}s. "
            f"Success rate: {results['metadata']['success_rate']:.1%}"
        )

        return results

    def visualize_results(
        self,
        results: Dict[str, Any],
        output_dir: str
    ) -> None:
        """Generate visualization for experiment results.

        Args:
            results: Results from run_full_experiment()
            output_dir: Directory to save graphs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        graph_path = output_path / "context_size_impact.png"

        plot_context_size_impact(
            results=results["aggregated_by_size"],
            output_path=str(graph_path),
            show=False
        )

        logger.info(f"Saved visualization to {graph_path}")


def run_experiment(
    model: str = "llama2",
    num_runs: int = 10,
    output_dir: str = "./results/experiment2",
    random_seed: int = 42
) -> Dict[str, Any]:
    """Convenience function to run Experiment 2.

    Args:
        model: LLM model name
        num_runs: Number of trials per document count
        output_dir: Output directory for results
        random_seed: Random seed

    Returns:
        Experiment results dictionary
    """
    experiment = ContextSizeExperiment(
        model=model,
        random_seed=random_seed
    )

    results = experiment.run_full_experiment(num_runs=num_runs)
    experiment.save_results(results, output_dir)
    experiment.visualize_results(results, output_dir)

    return results
