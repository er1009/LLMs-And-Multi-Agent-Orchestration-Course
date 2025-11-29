"""Unit tests for validators module."""

import pytest
from src.utils.validators import (
    validate_address,
    validate_coordinates,
    validate_api_key,
    validate_waypoint_count,
    sanitize_filename,
    validate_url,
    ValidationError
)


class TestValidateAddress:
    """Tests for address validation."""

    def test_valid_address(self):
        """Test valid address passes validation."""
        address = "123 Main St, Boston, MA"
        result = validate_address(address)
        assert result == address

    def test_address_with_extra_whitespace(self):
        """Test address with extra whitespace is cleaned."""
        address = "  123   Main  St  "
        result = validate_address(address)
        assert result == "123 Main St"

    def test_empty_address(self):
        """Test empty address raises error."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_address("")

    def test_none_address(self):
        """Test None address raises error."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_address(None)

    def test_short_address(self):
        """Test too-short address raises error."""
        with pytest.raises(ValidationError, match="too short"):
            validate_address("AB")

    def test_long_address(self):
        """Test too-long address raises error."""
        long_address = "A" * 501
        with pytest.raises(ValidationError, match="too long"):
            validate_address(long_address)


class TestValidateCoordinates:
    """Tests for coordinate validation."""

    def test_valid_coordinates(self):
        """Test valid coordinates pass validation."""
        lat, lng = validate_coordinates(42.3601, -71.0589)
        assert lat == 42.3601
        assert lng == -71.0589

    def test_boundary_coordinates(self):
        """Test boundary values are accepted."""
        validate_coordinates(90, 180)
        validate_coordinates(-90, -180)
        validate_coordinates(0, 0)

    def test_invalid_latitude(self):
        """Test invalid latitude raises error."""
        with pytest.raises(ValidationError, match="Latitude must be between"):
            validate_coordinates(91, 0)

        with pytest.raises(ValidationError, match="Latitude must be between"):
            validate_coordinates(-91, 0)

    def test_invalid_longitude(self):
        """Test invalid longitude raises error."""
        with pytest.raises(ValidationError, match="Longitude must be between"):
            validate_coordinates(0, 181)

        with pytest.raises(ValidationError, match="Longitude must be between"):
            validate_coordinates(0, -181)

    def test_invalid_format(self):
        """Test non-numeric coordinates raise error."""
        with pytest.raises(ValidationError, match="Invalid coordinate format"):
            validate_coordinates("invalid", 0)


class TestValidateApiKey:
    """Tests for API key validation."""

    def test_valid_api_key(self):
        """Test valid API key passes."""
        key = "a" * 30
        result = validate_api_key(key)
        assert result == key

    def test_short_api_key(self):
        """Test too-short API key raises error."""
        with pytest.raises(ValidationError, match="too short"):
            validate_api_key("short")

    def test_placeholder_api_key(self):
        """Test placeholder values are rejected."""
        with pytest.raises(ValidationError, match="placeholder"):
            validate_api_key("your_api_key")

        with pytest.raises(ValidationError, match="placeholder"):
            validate_api_key("your_google_maps_api_key_here")


class TestValidateWaypointCount:
    """Tests for waypoint count validation."""

    def test_valid_count(self):
        """Test valid count passes."""
        assert validate_waypoint_count(10) == 10

    def test_zero_count(self):
        """Test zero raises error."""
        with pytest.raises(ValidationError, match="at least 1"):
            validate_waypoint_count(0)

    def test_excessive_count(self):
        """Test excessive count raises error."""
        with pytest.raises(ValidationError, match="Too many waypoints"):
            validate_waypoint_count(100, max_waypoints=50)

    def test_invalid_format(self):
        """Test non-integer raises error."""
        with pytest.raises(ValidationError, match="Invalid waypoint count"):
            validate_waypoint_count("ten")


class TestSanitizeFilename:
    """Tests for filename sanitization."""

    def test_safe_filename(self):
        """Test safe filename passes through."""
        filename = "route_output.json"
        result = sanitize_filename(filename)
        assert result == filename

    def test_dangerous_characters(self):
        """Test dangerous characters are replaced."""
        filename = "route/with\\bad:chars*.json"
        result = sanitize_filename(filename)
        assert "/" not in result
        assert "\\" not in result
        assert ":" not in result
        assert "*" not in result

    def test_empty_filename(self):
        """Test empty filename raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            sanitize_filename("")

    def test_long_filename(self):
        """Test very long filename is truncated."""
        long_name = "a" * 300 + ".json"
        result = sanitize_filename(long_name)
        assert len(result) <= 255


class TestValidateUrl:
    """Tests for URL validation."""

    def test_valid_http_url(self):
        """Test valid HTTP URL passes."""
        url = "http://example.com/path"
        result = validate_url(url)
        assert result == url

    def test_valid_https_url(self):
        """Test valid HTTPS URL passes."""
        url = "https://www.youtube.com/watch?v=123"
        result = validate_url(url)
        assert result == url

    def test_invalid_url_format(self):
        """Test invalid URL format raises error."""
        with pytest.raises(ValidationError, match="Invalid URL format"):
            validate_url("not a url")

    def test_empty_url(self):
        """Test empty URL raises error."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_url("")
