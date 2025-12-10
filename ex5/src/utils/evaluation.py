"""Response evaluation utilities with multiple matching methods.

This module provides robust evaluation of LLM responses using:
- Exact string matching
- Fuzzy matching (Levenshtein distance)
- Semantic similarity (embeddings)
"""

import logging
from typing import Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Optional: Semantic similarity (only import if needed)
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    logger.warning(
        "sentence-transformers not available. Semantic similarity disabled."
    )


def evaluate_exact_match(response: str, expected: str) -> float:
    """Evaluate using exact string matching.

    Case-insensitive matching with whitespace normalization.

    Args:
        response: Model's response
        expected: Expected answer

    Returns:
        1.0 if exact match, 0.0 otherwise

    Example:
        >>> evaluate_exact_match("The answer is 42", "42")
        1.0
    """
    response_clean = response.lower().strip()
    expected_clean = expected.lower().strip()

    if expected_clean in response_clean:
        logger.debug(f"Exact match found: '{expected}' in '{response}'")
        return 1.0

    logger.debug(f"No exact match: '{expected}' not in '{response}'")
    return 0.0


def evaluate_fuzzy_match(
    response: str,
    expected: str,
    threshold: float = 0.85
) -> float:
    """Evaluate using fuzzy string matching.

    Uses Levenshtein distance to handle typos and minor variations.

    Args:
        response: Model's response
        expected: Expected answer
        threshold: Minimum similarity ratio (0.0-1.0)

    Returns:
        Similarity ratio if above threshold, 0.0 otherwise

    Example:
        >>> evaluate_fuzzy_match("fourty-two", "forty-two", threshold=0.8)
        0.95
    """
    response_clean = response.lower().strip()
    expected_clean = expected.lower().strip()

    # Calculate similarity ratio
    ratio = SequenceMatcher(None, response_clean, expected_clean).ratio()

    if ratio >= threshold:
        logger.debug(
            f"Fuzzy match: ratio={ratio:.3f} (threshold={threshold})"
        )
        return ratio

    # Also check if expected is a substring (for longer responses)
    if expected_clean in response_clean:
        # Calculate ratio based on substring match
        substring_ratio = len(expected_clean) / len(response_clean)
        if substring_ratio >= threshold:
            logger.debug(
                f"Substring match: ratio={substring_ratio:.3f}"
            )
            return substring_ratio

    logger.debug(f"No fuzzy match: ratio={ratio:.3f} < {threshold}")
    return 0.0


def evaluate_semantic_similarity(
    response: str,
    expected: str,
    model_name: str = "all-MiniLM-L6-v2",
    threshold: float = 0.75
) -> float:
    """Evaluate using semantic similarity.

    Uses sentence embeddings to compare semantic meaning.
    Useful for catching semantically correct but differently worded answers.

    Args:
        response: Model's response
        expected: Expected answer
        model_name: Sentence transformer model name
        threshold: Minimum cosine similarity (0.0-1.0)

    Returns:
        Cosine similarity if above threshold, 0.0 otherwise

    Example:
        >>> evaluate_semantic_similarity(
        ...     "The capital of France is Paris",
        ...     "Paris",
        ...     threshold=0.7
        ... )
        0.82
    """
    if not SEMANTIC_AVAILABLE:
        logger.warning(
            "Semantic similarity requested but dependencies not available. "
            "Using fuzzy match instead."
        )
        return evaluate_fuzzy_match(response, expected, threshold)

    try:
        # Load model (cached after first call)
        model = SentenceTransformer(model_name)

        # Generate embeddings
        embeddings = model.encode([response, expected])

        # Calculate cosine similarity
        similarity = cosine_similarity(
            [embeddings[0]],
            [embeddings[1]]
        )[0][0]

        if similarity >= threshold:
            logger.debug(
                f"Semantic match: similarity={similarity:.3f} (threshold={threshold})"
            )
            return float(similarity)

        logger.debug(
            f"No semantic match: similarity={similarity:.3f} < {threshold}"
        )
        return 0.0

    except Exception as e:
        logger.error(f"Semantic similarity failed: {e}")
        return 0.0


def evaluate_response(
    response: str,
    expected_answer: str,
    method: str = "multi",
    fuzzy_threshold: float = 0.85,
    semantic_threshold: float = 0.75
) -> float:
    """Evaluate response using specified method(s).

    Main evaluation function that delegates to specific methods.

    Args:
        response: Model's response
        expected_answer: Ground truth answer
        method: Evaluation method:
            - "exact": Exact string matching only
            - "fuzzy": Fuzzy matching only
            - "semantic": Semantic similarity only
            - "multi": Try all methods, return highest score
        fuzzy_threshold: Threshold for fuzzy matching
        semantic_threshold: Threshold for semantic similarity

    Returns:
        Accuracy score between 0.0 and 1.0

    Example:
        >>> evaluate_response("The answer is 42", "42", method="multi")
        1.0
    """
    if not response or not expected_answer:
        logger.warning("Empty response or expected answer")
        return 0.0

    if method == "exact":
        return evaluate_exact_match(response, expected_answer)

    elif method == "fuzzy":
        return evaluate_fuzzy_match(
            response,
            expected_answer,
            threshold=fuzzy_threshold
        )

    elif method == "semantic":
        return evaluate_semantic_similarity(
            response,
            expected_answer,
            threshold=semantic_threshold
        )

    elif method == "multi":
        # Try all methods and return highest score
        scores = []

        # Exact match
        exact_score = evaluate_exact_match(response, expected_answer)
        scores.append(("exact", exact_score))

        # Fuzzy match
        fuzzy_score = evaluate_fuzzy_match(
            response,
            expected_answer,
            threshold=fuzzy_threshold
        )
        scores.append(("fuzzy", fuzzy_score))

        # Semantic similarity (if available)
        if SEMANTIC_AVAILABLE:
            semantic_score = evaluate_semantic_similarity(
                response,
                expected_answer,
                threshold=semantic_threshold
            )
            scores.append(("semantic", semantic_score))

        # Get best score
        best_method, best_score = max(scores, key=lambda x: x[1])

        logger.debug(
            f"Multi-method evaluation: "
            f"best={best_method} (score={best_score:.3f}), "
            f"all_scores={scores}"
        )

        return best_score

    else:
        raise ValueError(
            f"Unknown evaluation method: {method}. "
            f"Use 'exact', 'fuzzy', 'semantic', or 'multi'."
        )


def evaluate_batch(
    responses: list[str],
    expected_answers: list[str],
    method: str = "multi"
) -> list[float]:
    """Evaluate multiple responses in batch.

    Args:
        responses: List of model responses
        expected_answers: List of expected answers
        method: Evaluation method

    Returns:
        List of accuracy scores

    Example:
        >>> evaluate_batch(
        ...     ["Paris", "London", "Berlin"],
        ...     ["Paris", "London", "Madrid"]
        ... )
        [1.0, 1.0, 0.0]
    """
    if len(responses) != len(expected_answers):
        raise ValueError(
            f"Mismatched lengths: {len(responses)} responses vs "
            f"{len(expected_answers)} expected answers"
        )

    scores = []
    for response, expected in zip(responses, expected_answers):
        score = evaluate_response(response, expected, method=method)
        scores.append(score)

    return scores


def calculate_accuracy_stats(scores: list[float]) -> dict:
    """Calculate statistical summary of accuracy scores.

    Args:
        scores: List of accuracy scores (0.0-1.0)

    Returns:
        Dictionary with mean, std, min, max, and other stats

    Example:
        >>> calculate_accuracy_stats([1.0, 0.8, 0.9, 1.0])
        {
            'mean': 0.925,
            'std': 0.095,
            'min': 0.8,
            'max': 1.0,
            'median': 0.95,
            'count': 4
        }
    """
    if not scores:
        return {
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "median": 0.0,
            "count": 0
        }

    import numpy as np

    scores_array = np.array(scores)

    return {
        "mean": float(np.mean(scores_array)),
        "std": float(np.std(scores_array)),
        "min": float(np.min(scores_array)),
        "max": float(np.max(scores_array)),
        "median": float(np.median(scores_array)),
        "count": len(scores)
    }
