"""
Statistics Calculator

Provides statistical analysis for translation results.
"""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TrendResult:
    """
    Result of trend analysis.

    Attributes:
        slope: Slope of the trend line
        intercept: Y-intercept of the trend line
        r_squared: R-squared value (coefficient of determination)
        correlation: Pearson correlation coefficient
    """

    slope: float
    intercept: float
    r_squared: float
    correlation: float


class StatisticsCalculator:
    """
    Calculator for statistical analysis of results.

    Provides correlation, trend analysis, and summary statistics.
    """

    @staticmethod
    def calculate_correlation(x: List[float], y: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient.

        Args:
            x: First variable (e.g., error rates)
            y: Second variable (e.g., distances)

        Returns:
            Pearson correlation coefficient (-1 to 1)

        Raises:
            ValueError: If lists have different lengths or are too short
        """
        if len(x) != len(y):
            raise ValueError(
                f"Lists must have same length, got {len(x)} and {len(y)}"
            )

        if len(x) < 2:
            raise ValueError("Need at least 2 data points for correlation")

        correlation = np.corrcoef(x, y)[0, 1]
        return float(correlation)

    @staticmethod
    def calculate_trend(x: List[float], y: List[float]) -> TrendResult:
        """
        Calculate linear trend and statistics.

        Args:
            x: Independent variable (e.g., error rates)
            y: Dependent variable (e.g., distances)

        Returns:
            TrendResult with slope, intercept, and statistics

        Raises:
            ValueError: If lists have different lengths or are too short
        """
        if len(x) != len(y):
            raise ValueError(
                f"Lists must have same length, got {len(x)} and {len(y)}"
            )

        if len(x) < 2:
            raise ValueError("Need at least 2 data points for trend analysis")

        # Convert to numpy arrays
        x_arr = np.array(x)
        y_arr = np.array(y)

        # Calculate linear regression
        coefficients = np.polyfit(x_arr, y_arr, 1)
        slope, intercept = coefficients

        # Calculate R-squared
        y_pred = slope * x_arr + intercept
        ss_res = np.sum((y_arr - y_pred) ** 2)
        ss_tot = np.sum((y_arr - np.mean(y_arr)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

        # Calculate correlation
        correlation = np.corrcoef(x_arr, y_arr)[0, 1]

        return TrendResult(
            slope=float(slope),
            intercept=float(intercept),
            r_squared=float(r_squared),
            correlation=float(correlation),
        )

    @staticmethod
    def calculate_summary_stats(data: List[float]) -> dict:
        """
        Calculate summary statistics for a dataset.

        Args:
            data: List of numerical values

        Returns:
            Dictionary with summary statistics

        Raises:
            ValueError: If data list is empty
        """
        if not data:
            raise ValueError("Cannot calculate statistics for empty data")

        data_arr = np.array(data)

        return {
            "mean": float(np.mean(data_arr)),
            "median": float(np.median(data_arr)),
            "std": float(np.std(data_arr)),
            "min": float(np.min(data_arr)),
            "max": float(np.max(data_arr)),
            "q25": float(np.percentile(data_arr, 25)),
            "q75": float(np.percentile(data_arr, 75)),
            "count": len(data),
        }

    @staticmethod
    def calculate_confidence_interval(
        data: List[float], confidence: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for the mean.

        Args:
            data: List of numerical values
            confidence: Confidence level (default: 0.95)

        Returns:
            Tuple of (lower_bound, upper_bound)

        Raises:
            ValueError: If data list is empty or confidence is invalid
        """
        if not data:
            raise ValueError("Cannot calculate confidence interval for empty data")

        if not 0 < confidence < 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {confidence}")

        data_arr = np.array(data)
        mean = np.mean(data_arr)
        std_err = np.std(data_arr, ddof=1) / np.sqrt(len(data_arr))

        # Use t-distribution for small samples
        from scipy import stats

        df = len(data_arr) - 1
        t_value = stats.t.ppf((1 + confidence) / 2, df)

        margin = t_value * std_err
        return float(mean - margin), float(mean + margin)
