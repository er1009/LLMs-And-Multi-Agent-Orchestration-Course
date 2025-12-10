"""Experiment 3: RAG vs Full Context Comparison.

This experiment demonstrates RAG's superiority in accuracy and speed
over full context processing.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from src.experiments.base import BaseExperiment
from src.utils.ollama_client import OllamaClient
from src.utils.document_generator import DocumentGenerator
from src.utils.evaluation import evaluate_response
from src.utils.tokenization import count_tokens
from src.utils.visualization import plot_rag_comparison
from src.config.settings import config

logger = logging.getLogger(__name__)


class RAGComparisonExperiment(BaseExperiment):
    """Experiment to compare RAG vs Full Context approaches.

    Attributes:
        client: Ollama client
        doc_generator: Document generator
        embedding_model: Sentence transformer for embeddings
        vector_store: ChromaDB collection
        num_docs: Number of documents to generate
        chunk_size: Size of chunks for RAG
        chunk_overlap: Overlap between chunks
        top_k: Number of documents to retrieve in RAG
    """

    def __init__(
        self,
        model: str = "llama2",
        random_seed: int = 42,
        num_docs: int = 20,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        top_k: int = 3
    ):
        """Initialize RAG Comparison experiment.

        Args:
            model: LLM model name
            random_seed: Random seed
            num_docs: Number of documents
            chunk_size: Chunk size in characters
            chunk_overlap: Overlap between chunks
            top_k: Number of chunks to retrieve
        """
        super().__init__(
            experiment_name="RAG vs Full Context",
            model=model,
            random_seed=random_seed
        )

        self.num_docs = num_docs
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k

        self.client = OllamaClient(model=model)
        self.doc_generator = DocumentGenerator(random_seed=random_seed)

        # Load embedding model
        logger.info(f"Loading embedding model: {config.embedding_model}")
        self.embedding_model = SentenceTransformer(config.embedding_model)

        # ChromaDB will be initialized during experiment
        self.vector_store = None
        self.documents = []
        self.chunks = []

        logger.info(
            f"Initialized with num_docs={num_docs}, chunk_size={chunk_size}, top_k={top_k}"
        )

    def chunk_documents(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Chunk documents with overlap.

        Args:
            documents: List of document texts

        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        chunk_id = 0

        for doc_id, doc in enumerate(documents):
            # Simple character-based chunking
            doc_length = len(doc)
            start = 0

            while start < doc_length:
                end = start + self.chunk_size
                chunk_text = doc[start:end]

                # Try to break at sentence boundary
                if end < doc_length:
                    last_period = chunk_text.rfind('.')
                    if last_period > self.chunk_size * 0.7:  # At least 70% of chunk
                        end = start + last_period + 1
                        chunk_text = doc[start:end]

                chunks.append({
                    "chunk_id": f"chunk_{chunk_id}",
                    "doc_id": doc_id,
                    "text": chunk_text.strip(),
                    "start_pos": start,
                    "end_pos": end
                })

                chunk_id += 1
                start = end - self.chunk_overlap

        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks

    def setup_vector_store(self) -> None:
        """Set up ChromaDB vector store with documents."""
        logger.info("Setting up vector store...")

        # Generate documents
        logger.info(f"Generating {self.num_docs} realistic documents...")
        docs_data = self.doc_generator.generate_realistic_documents(
            num_docs=self.num_docs,
            words_per_doc=200,
            topics=["technology", "law", "medicine"]
        )
        self.documents = [doc["content"] for doc in docs_data]

        # Chunk documents
        self.chunks = self.chunk_documents(self.documents)

        # Create ChromaDB client
        chroma_client = chromadb.PersistentClient(path=config.chroma_persist_dir)

        # Create or get collection
        collection_name = f"exp3_{self.random_seed}"
        try:
            chroma_client.delete_collection(name=collection_name)
        except:
            pass

        self.vector_store = chroma_client.create_collection(
            name=collection_name,
            metadata={"description": "Experiment 3 documents"}
        )

        # Generate embeddings
        logger.info("Generating embeddings...")
        chunk_texts = [c["text"] for c in self.chunks]

        batch_size = 32
        for i in range(0, len(chunk_texts), batch_size):
            batch = chunk_texts[i:i+batch_size]
            embeddings = self.embedding_model.encode(batch, show_progress_bar=False)

            # Add to vector store
            ids = [self.chunks[i+j]["chunk_id"] for j in range(len(batch))]
            metadatas = [{"doc_id": self.chunks[i+j]["doc_id"]} for j in range(len(batch))]

            self.vector_store.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=batch,
                metadatas=metadatas
            )

        logger.info(f"Vector store ready with {len(chunk_texts)} chunks")

    def query_rag(self, question: str) -> tuple[str, float, int]:
        """Query using RAG approach.

        Args:
            question: Question to answer

        Returns:
            Tuple of (response, latency_ms, token_count)
        """
        start_time = time.perf_counter()

        # Generate query embedding
        query_embedding = self.embedding_model.encode([question])[0]

        # Retrieve relevant chunks
        results = self.vector_store.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=self.top_k
        )

        # Build context from retrieved chunks
        retrieved_docs = results["documents"][0]
        context = "\n\n".join(retrieved_docs)

        # Query model
        response = self.client.query(context=context, question=question)

        latency_ms = (time.perf_counter() - start_time) * 1000
        token_count = count_tokens(context, model_name=self.model)

        return response, latency_ms, token_count

    def query_full_context(self, question: str) -> tuple[str, float, int]:
        """Query using full context approach.

        Args:
            question: Question to answer

        Returns:
            Tuple of (response, latency_ms, token_count)
        """
        start_time = time.perf_counter()

        # Use all documents as context
        context = "\n\n---\n\n".join(self.documents)

        # Query model
        response = self.client.query(context=context, question=question)

        latency_ms = (time.perf_counter() - start_time) * 1000
        token_count = count_tokens(context, model_name=self.model)

        return response, latency_ms, token_count

    def run_single_trial(
        self,
        question: str,
        expected_answer: str
    ) -> Dict[str, Any]:
        """Run a single comparison trial.

        Args:
            question: Question to ask
            expected_answer: Expected answer

        Returns:
            Dictionary with results for both approaches
        """
        try:
            # RAG approach
            logger.debug("Querying with RAG...")
            rag_response, rag_latency, rag_tokens = self.query_rag(question)
            rag_accuracy = evaluate_response(rag_response, expected_answer, method="multi")

            # Full context approach
            logger.debug("Querying with full context...")
            full_response, full_latency, full_tokens = self.query_full_context(question)
            full_accuracy = evaluate_response(full_response, expected_answer, method="multi")

            logger.debug(
                f"RAG: acc={rag_accuracy:.2f}, latency={rag_latency:.0f}ms, tokens={rag_tokens}"
            )
            logger.debug(
                f"Full: acc={full_accuracy:.2f}, latency={full_latency:.0f}ms, tokens={full_tokens}"
            )

            return {
                "question": question,
                "expected_answer": expected_answer,
                "rag": {
                    "response": rag_response,
                    "accuracy": rag_accuracy,
                    "latency_ms": rag_latency,
                    "token_count": rag_tokens
                },
                "full": {
                    "response": full_response,
                    "accuracy": full_accuracy,
                    "latency_ms": full_latency,
                    "token_count": full_tokens
                },
                "error": None
            }

        except Exception as e:
            logger.error(f"Trial failed: {e}")
            return {
                "question": question,
                "expected_answer": expected_answer,
                "rag": {"accuracy": 0.0, "latency_ms": 0.0, "token_count": 0},
                "full": {"accuracy": 0.0, "latency_ms": 0.0, "token_count": 0},
                "error": str(e)
            }

    def run_full_experiment(
        self,
        num_runs: int = 10,
        custom_questions: Optional[List[tuple]] = None
    ) -> Dict[str, Any]:
        """Run complete RAG vs Full Context experiment.

        Args:
            num_runs: Number of trials
            custom_questions: List of (question, answer) tuples

        Returns:
            Dictionary with complete experiment results
        """
        logger.info(f"Starting experiment with {num_runs} runs")

        # Setup vector store
        self.setup_vector_store()

        # Warmup
        logger.info("Warming up model...")
        self.client.warmup()

        # Questions to test
        if custom_questions is None:
            questions = [
                ("What are the key features mentioned in the technology documents?", "features"),
                ("What regulations are discussed?", "regulations"),
                ("What medical procedures are described?", "procedures"),
                ("What companies are mentioned?", "companies"),
                ("What are the side effects mentioned?", "side effects"),
            ]
        else:
            questions = custom_questions

        all_trials = []
        experiment_start = time.perf_counter()

        # Run trials
        for run in range(num_runs):
            question, expected = questions[run % len(questions)]
            logger.info(f"Run {run + 1}/{num_runs}: {question[:50]}...")

            trial_result = self.run_single_trial(question, expected)
            trial_result["trial_id"] = run
            all_trials.append(trial_result)

        total_runtime = time.perf_counter() - experiment_start

        # Aggregate results
        import numpy as np

        successful_trials = [t for t in all_trials if t["error"] is None]

        rag_accuracies = [t["rag"]["accuracy"] for t in successful_trials]
        rag_latencies = [t["rag"]["latency_ms"] for t in successful_trials]
        rag_tokens = [t["rag"]["token_count"] for t in successful_trials]

        full_accuracies = [t["full"]["accuracy"] for t in successful_trials]
        full_latencies = [t["full"]["latency_ms"] for t in successful_trials]
        full_tokens = [t["full"]["token_count"] for t in successful_trials]

        aggregated = {
            "rag": {
                "accuracy": float(np.mean(rag_accuracies)),
                "accuracy_std": float(np.std(rag_accuracies)),
                "latency": float(np.mean(rag_latencies)),
                "latency_std": float(np.std(rag_latencies)),
                "tokens": float(np.mean(rag_tokens)),
            },
            "full": {
                "accuracy": float(np.mean(full_accuracies)),
                "accuracy_std": float(np.std(full_accuracies)),
                "latency": float(np.mean(full_latencies)),
                "latency_std": float(np.std(full_latencies)),
                "tokens": float(np.mean(full_tokens)),
            }
        }

        # Create result structure
        config_dict = {
            "num_runs": num_runs,
            "num_docs": self.num_docs,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.top_k,
            "model": self.model,
            "random_seed": self.random_seed,
        }

        # Create trials list for base structure (using RAG results)
        trials_for_base = [
            {
                "accuracy": t["rag"]["accuracy"],
                "latency_ms": t["rag"]["latency_ms"],
                "error": t["error"]
            }
            for t in all_trials
        ]

        results = self.create_result_structure(
            trials=trials_for_base,
            config=config_dict,
            total_runtime=total_runtime
        )

        results["aggregated"] = aggregated
        results["all_trials"] = all_trials

        logger.info(
            f"Experiment completed in {total_runtime:.1f}s. "
            f"RAG accuracy: {aggregated['rag']['accuracy']:.2%}, "
            f"Full accuracy: {aggregated['full']['accuracy']:.2%}"
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

        graph_path = output_path / "rag_vs_full.png"

        plot_rag_comparison(
            rag_results=results["aggregated"]["rag"],
            full_results=results["aggregated"]["full"],
            output_path=str(graph_path),
            show=False
        )

        logger.info(f"Saved visualization to {graph_path}")


def run_experiment(
    model: str = "llama2",
    num_runs: int = 10,
    output_dir: str = "./results/experiment3",
    random_seed: int = 42
) -> Dict[str, Any]:
    """Convenience function to run Experiment 3.

    Args:
        model: LLM model name
        num_runs: Number of trials
        output_dir: Output directory
        random_seed: Random seed

    Returns:
        Experiment results dictionary
    """
    experiment = RAGComparisonExperiment(
        model=model,
        random_seed=random_seed
    )

    results = experiment.run_full_experiment(num_runs=num_runs)
    experiment.save_results(results, output_dir)
    experiment.visualize_results(results, output_dir)

    return results
