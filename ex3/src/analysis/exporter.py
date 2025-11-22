"""
Result Exporter

Exports analysis results to various formats (CSV, JSON).
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class ResultExporter:
    """
    Exporter for analysis results.

    Provides methods to export data to CSV and JSON formats
    with proper formatting and metadata.
    """

    @staticmethod
    def export_csv(data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export data to CSV file.

        Args:
            data: List of dictionaries with results
            output_path: Path to save the CSV file

        Raises:
            ValueError: If data list is empty
            IOError: If file cannot be written
        """
        if not data:
            raise ValueError("Cannot export empty data")

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Get all keys from first item (assuming consistent structure)
        fieldnames = list(data[0].keys())

        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise IOError(f"Failed to write CSV file: {str(e)}") from e

    @staticmethod
    def export_json(
        data: List[Dict[str, Any]],
        output_path: str,
        include_metadata: bool = True,
    ) -> None:
        """
        Export data to JSON file.

        Args:
            data: List of dictionaries with results
            output_path: Path to save the JSON file
            include_metadata: Whether to include export metadata

        Raises:
            ValueError: If data list is empty
            IOError: If file cannot be written
        """
        if not data:
            raise ValueError("Cannot export empty data")

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare export structure
        export_data = {"results": data}

        if include_metadata:
            export_data["metadata"] = {
                "export_timestamp": datetime.now().isoformat(),
                "num_records": len(data),
                "format_version": "1.0",
            }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Failed to write JSON file: {str(e)}") from e

    @staticmethod
    def format_results_for_export(
        results,  # List[EvaluationResult or PipelineResult]
        include_embeddings: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Format result objects for export.

        Args:
            results: List of result objects (EvaluationResult or PipelineResult)
            include_embeddings: Whether to include embedding vectors in export

        Returns:
            List of dictionaries suitable for export

        Raises:
            ValueError: If results list is empty
        """
        if not results:
            raise ValueError("Cannot format empty results")

        formatted = []

        for result in results:
            # Base fields common to most results
            record = {}

            # Handle different result types
            if hasattr(result, "original_text"):
                record["original_text"] = result.original_text

            if hasattr(result, "final_text"):
                record["final_text"] = result.final_text

            if hasattr(result, "corrupted"):
                record["corrupted_text"] = result.corrupted

            if hasattr(result, "error_rate"):
                record["error_rate"] = result.error_rate

            if hasattr(result, "cosine_distance"):
                record["cosine_distance"] = result.cosine_distance

            if hasattr(result, "euclidean_distance"):
                record["euclidean_distance"] = result.euclidean_distance

            if hasattr(result, "translation_fr"):
                record["translation_fr"] = result.translation_fr

            if hasattr(result, "translation_he"):
                record["translation_he"] = result.translation_he

            if hasattr(result, "translation_en"):
                record["translation_en"] = result.translation_en

            if hasattr(result, "word_count"):
                record["word_count"] = result.word_count

            if hasattr(result, "timestamp"):
                record["timestamp"] = result.timestamp.isoformat()

            if hasattr(result, "seed"):
                record["seed"] = result.seed

            # Include embeddings if requested (usually not recommended due to size)
            if include_embeddings:
                if hasattr(result, "original_embedding"):
                    record["original_embedding"] = result.original_embedding.tolist()
                if hasattr(result, "final_embedding"):
                    record["final_embedding"] = result.final_embedding.tolist()

            formatted.append(record)

        return formatted

    @staticmethod
    def export_summary_statistics(
        stats: Dict[str, Any], output_path: str
    ) -> None:
        """
        Export summary statistics to JSON file.

        Args:
            stats: Dictionary of summary statistics
            output_path: Path to save the JSON file

        Raises:
            ValueError: If stats dict is empty
            IOError: If file cannot be written
        """
        if not stats:
            raise ValueError("Cannot export empty statistics")

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        export_data = {
            "statistics": stats,
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "format_version": "1.0",
            },
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)
        except Exception as e:
            raise IOError(f"Failed to write statistics file: {str(e)}") from e
