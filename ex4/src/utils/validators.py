"""Input validation utilities for Route Guide System."""

import re
from typing import Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_address(address: str) -> str:
    """
    Validate address string.

    Args:
        address: Address to validate

    Returns:
        Cleaned address string

    Raises:
        ValidationError: If address is invalid
    """
    if not address or not isinstance(address, str):
        raise ValidationError("Address must be a non-empty string")

    # Remove excessive whitespace
    cleaned = " ".join(address.split())

    if len(cleaned) < 3:
        raise ValidationError("Address too short (minimum 3 characters)")

    if len(cleaned) > 500:
        raise ValidationError("Address too long (maximum 500 characters)")

    return cleaned


def validate_coordinates(lat: float, lng: float) -> tuple[float, float]:
    """
    Validate geographic coordinates.

    Args:
        lat: Latitude
        lng: Longitude

    Returns:
        Tuple of validated (lat, lng)

    Raises:
        ValidationError: If coordinates are invalid
    """
    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Invalid coordinate format: {e}")

    if not -90 <= lat <= 90:
        raise ValidationError(f"Latitude must be between -90 and 90, got {lat}")

    if not -180 <= lng <= 180:
        raise ValidationError(f"Longitude must be between -180 and 180, got {lng}")

    return lat, lng


def validate_api_key(api_key: str, min_length: int = 20) -> str:
    """
    Validate API key format.

    Args:
        api_key: API key to validate
        min_length: Minimum expected length

    Returns:
        Validated API key

    Raises:
        ValidationError: If API key is invalid
    """
    if not api_key or not isinstance(api_key, str):
        raise ValidationError("API key must be a non-empty string")

    # Remove whitespace
    cleaned = api_key.strip()

    if len(cleaned) < min_length:
        raise ValidationError(
            f"API key too short (minimum {min_length} characters)"
        )

    # Check for placeholder values
    placeholders = [
        "your_api_key",
        "your_google_maps_api_key_here",
        "insert_key_here",
        "xxx",
        "000"
    ]

    if cleaned.lower() in placeholders:
        raise ValidationError("API key appears to be a placeholder value")

    return cleaned


def validate_waypoint_count(count: int, max_waypoints: int = 50) -> int:
    """
    Validate waypoint count.

    Args:
        count: Number of waypoints
        max_waypoints: Maximum allowed waypoints

    Returns:
        Validated count

    Raises:
        ValidationError: If count is invalid
    """
    try:
        count = int(count)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Invalid waypoint count: {e}")

    if count < 1:
        raise ValidationError("Must have at least 1 waypoint")

    if count > max_waypoints:
        raise ValidationError(
            f"Too many waypoints (maximum {max_waypoints}, got {count})"
        )

    return count


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove dangerous characters.

    Args:
        filename: Filename to sanitize

    Returns:
        Safe filename
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")

    # Remove or replace dangerous characters
    # Keep alphanumeric, dash, underscore, and dot
    safe = re.sub(r'[^\w\-.]', '_', filename)

    # Remove leading/trailing dots and dashes
    safe = safe.strip('.-')

    if not safe:
        raise ValidationError("Filename contains no valid characters")

    # Limit length
    max_length = 255
    if len(safe) > max_length:
        name, ext = safe.rsplit('.', 1) if '.' in safe else (safe, '')
        safe = name[:max_length - len(ext) - 1] + '.' + ext if ext else name[:max_length]

    return safe


def validate_url(url: str) -> str:
    """
    Basic URL validation.

    Args:
        url: URL to validate

    Returns:
        Validated URL

    Raises:
        ValidationError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")

    url = url.strip()

    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if not url_pattern.match(url):
        raise ValidationError(f"Invalid URL format: {url}")

    return url
