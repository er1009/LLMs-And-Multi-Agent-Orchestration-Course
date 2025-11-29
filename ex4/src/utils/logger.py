"""Logging configuration for Route Guide System."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "route_guide",
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure logger.

    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file (None for stdout only)
        format_string: Custom format string

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Default format
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    formatter = logging.Formatter(format_string)

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "route_guide") -> logging.Logger:
    """
    Get logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Redact sensitive information from log messages
def redact_sensitive_info(message: str) -> str:
    """
    Redact API keys and other sensitive information from log messages.

    Args:
        message: Log message

    Returns:
        Redacted message
    """
    # Replace potential API keys (strings that look like keys)
    import re

    # Pattern for Google Maps API keys
    message = re.sub(
        r"key=[A-Za-z0-9_-]{20,}",
        "key=***REDACTED***",
        message
    )

    # Pattern for generic API keys
    message = re.sub(
        r"api[_-]?key[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_-]{20,}",
        "api_key=***REDACTED***",
        message,
        flags=re.IGNORECASE
    )

    return message


class SensitiveInfoFilter(logging.Filter):
    """Filter to redact sensitive information from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to redact sensitive info.

        Args:
            record: Log record

        Returns:
            True to include record, False to exclude
        """
        record.msg = redact_sensitive_info(str(record.msg))
        return True
