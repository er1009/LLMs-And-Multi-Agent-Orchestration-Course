"""Tests for experiment modules."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from src.experiments.base import BaseExperiment
from src.experiments.experiment1_needle_haystack import NeedleHaystackExperiment
from src.experiments.experiment2_context_size import ContextSizeExperiment


class TestBaseExperiment:
    """Tests for BaseExperiment class."""

    def test_initialization(self):
        """Test base experiment initialization."""
        # Create a concrete implementation for testing
        class ConcreteExperiment(BaseExperiment):
            def run_single_trial(self):
                pass

            def run_full_experiment(self, num_runs=10):
                pass

            def visualize_results(self, results, output_dir):
                pass

        exp = ConcreteExperiment(
            experiment_name="Test",
            model="llama2",
            random_seed=42
        )

        assert exp.experiment_name == "Test"
        assert exp.model == "llama2"
        assert exp.random_seed == 42

    def test_create_result_structure(self):
        """Test result structure creation."""
        class ConcreteExperiment(BaseExperiment):
            def run_single_trial(self):
                pass

            def run_full_experiment(self, num_runs=10):
                pass

            def visualize_results(self, results, output_dir):
                pass

        exp = ConcreteExperiment("Test", "llama2", 42)

        trials = [
            {"accuracy": 0.9, "latency_ms": 1000, "error": None},
            {"accuracy": 0.8, "latency_ms": 1200, "error": None},
            {"accuracy": 0.85, "latency_ms": 1100, "error": None},
        ]

        config = {"model": "llama2", "num_runs": 3}
        runtime = 10.5

        results = exp.create_result_structure(trials, config, runtime)

        assert "experiment_id" in results
        assert "timestamp" in results
        assert "config" in results
        assert "trials" in results
        assert "statistics" in results
        assert "metadata" in results

        assert results["statistics"]["mean_accuracy"] == pytest.approx(0.85, rel=0.01)
        assert results["metadata"]["total_runtime_seconds"] == 10.5
        assert results["metadata"]["num_trials"] == 3

    def test_save_results(self):
        """Test saving results to disk."""
        class ConcreteExperiment(BaseExperiment):
            def run_single_trial(self):
                pass

            def run_full_experiment(self, num_runs=10):
                pass

            def visualize_results(self, results, output_dir):
                pass

        exp = ConcreteExperiment("Test", "llama2", 42)

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            results = {
                "statistics": {
                    "mean_accuracy": 0.85,
                    "std_accuracy": 0.05
                },
                "trials": [],
                "config": {}
            }

            exp.save_results(results, tmpdir, save_raw=True)

            # Check files were created
            output_path = Path(tmpdir)
            assert (output_path / "raw_results.json").exists()
            assert (output_path / "aggregated_stats.csv").exists()


class TestNeedleHaystackExperiment:
    """Tests for Experiment 1."""

    @patch('src.experiments.experiment1_needle_haystack.OllamaClient')
    def test_initialization(self, mock_client_class):
        """Test experiment initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        exp = NeedleHaystackExperiment(
            model="llama2",
            random_seed=42,
            haystack_words=1000
        )

        assert exp.model == "llama2"
        assert exp.random_seed == 42
        assert exp.haystack_words == 1000

    @patch('src.experiments.experiment1_needle_haystack.OllamaClient')
    def test_run_single_trial(self, mock_client_class):
        """Test running a single trial."""
        mock_client = Mock()
        mock_client.query.return_value = "The secret code is 7482"
        mock_client_class.return_value = mock_client

        exp = NeedleHaystackExperiment(random_seed=42, haystack_words=200)

        result = exp.run_single_trial(
            position="middle",
            needle="The secret code is 7482",
            question="What is the secret code?"
        )

        assert "position" in result
        assert "accuracy" in result
        assert "latency_ms" in result
        assert result["position"] == "middle"
        assert result["accuracy"] >= 0.0
        assert result["accuracy"] <= 1.0

    @patch('src.experiments.experiment1_needle_haystack.OllamaClient')
    def test_run_single_trial_error_handling(self, mock_client_class):
        """Test error handling in single trial."""
        mock_client = Mock()
        mock_client.query.side_effect = Exception("Connection error")
        mock_client_class.return_value = mock_client

        exp = NeedleHaystackExperiment(random_seed=42)

        result = exp.run_single_trial(
            position="middle",
            needle="test",
            question="test?"
        )

        assert result["error"] is not None
        assert result["accuracy"] == 0.0


class TestContextSizeExperiment:
    """Tests for Experiment 2."""

    @patch('src.experiments.experiment2_context_size.OllamaClient')
    def test_initialization(self, mock_client_class):
        """Test experiment initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        exp = ContextSizeExperiment(
            model="llama2",
            random_seed=42,
            words_per_doc=200
        )

        assert exp.model == "llama2"
        assert exp.random_seed == 42
        assert exp.words_per_doc == 200

    @patch('src.experiments.experiment2_context_size.OllamaClient')
    def test_create_test_documents(self, mock_client_class):
        """Test document creation."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        exp = ContextSizeExperiment(random_seed=42, words_per_doc=100)

        docs, answer, question = exp.create_test_documents(num_docs=5)

        assert len(docs) == 5
        assert isinstance(answer, str)
        assert isinstance(question, str)
        assert len(answer) > 0
        assert len(question) > 0

    @patch('src.experiments.experiment2_context_size.OllamaClient')
    def test_run_single_trial(self, mock_client_class):
        """Test running a single trial."""
        mock_client = Mock()
        mock_client.query.return_value = "Paris"
        mock_client_class.return_value = mock_client

        exp = ContextSizeExperiment(random_seed=42, words_per_doc=50)

        result = exp.run_single_trial(num_docs=3)

        assert "num_docs" in result
        assert result["num_docs"] == 3
        assert "accuracy" in result
        assert "latency_ms" in result
        assert "token_count" in result


class TestExperimentIntegration:
    """Integration tests for experiments."""

    @patch('src.experiments.experiment1_needle_haystack.OllamaClient')
    def test_experiment1_full_run_small(self, mock_client_class):
        """Test full run of Experiment 1 with small parameters."""
        mock_client = Mock()
        mock_client.query.return_value = "7482"
        mock_client.warmup.return_value = None
        mock_client_class.return_value = mock_client

        exp = NeedleHaystackExperiment(random_seed=42, haystack_words=100)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Run with minimal parameters
            results = exp.run_full_experiment(
                num_runs=2,
                positions=["start", "middle"]
            )

            # Save results
            exp.save_results(results, tmpdir)

            # Verify structure
            assert "statistics" in results
            assert "metadata" in results
            assert "position_results" in results
            assert len(results["position_results"]) == 2

            # Verify files created
            output_path = Path(tmpdir)
            assert (output_path / "raw_results.json").exists()

    @patch('src.experiments.experiment2_context_size.OllamaClient')
    def test_experiment2_full_run_small(self, mock_client_class):
        """Test full run of Experiment 2 with small parameters."""
        mock_client = Mock()
        mock_client.query.return_value = "Answer"
        mock_client.warmup.return_value = None
        mock_client_class.return_value = mock_client

        exp = ContextSizeExperiment(random_seed=42, words_per_doc=50)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Run with minimal parameters
            results = exp.run_full_experiment(
                num_runs=2,
                doc_counts=[2, 5]
            )

            # Save results
            exp.save_results(results, tmpdir)

            # Verify structure
            assert "statistics" in results
            assert "aggregated_by_size" in results
            assert len(results["aggregated_by_size"]) == 2
