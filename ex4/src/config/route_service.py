"""Google Maps route service for Route Guide System."""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import requests

from ..utils.logger import get_logger
from ..utils.validators import validate_address, ValidationError

logger = get_logger(__name__)


@dataclass
class Location:
    """Geographic location with address and coordinates."""
    address: str
    lat: float
    lng: float


@dataclass
class Waypoint:
    """Waypoint along a route."""
    location: Location
    index: int
    distance_from_start: float  # km
    instruction: Optional[str] = None


@dataclass
class Route:
    """Complete route information."""
    source: Location
    destination: Location
    waypoints: List[Waypoint]
    total_distance: float  # km
    total_duration: float  # minutes
    metadata: Dict


class RouteServiceError(Exception):
    """Exception raised for route service errors."""
    pass


class RouteService:
    """
    Service for retrieving and processing routes using Google Maps API.

    Handles:
    - Route retrieval from Google Maps Directions API
    - Waypoint extraction from route steps
    - Distance and duration calculations
    """

    DIRECTIONS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"

    def __init__(
        self,
        api_key: str,
        timeout: int = 10,
        max_retries: int = 3,
        retry_delay: int = 1
    ):
        """
        Initialize route service.

        Args:
            api_key: Google Maps API key
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def get_route(
        self,
        source: str,
        destination: str,
        max_waypoints: int = 20
    ) -> Route:
        """
        Get route with waypoints between source and destination.

        Args:
            source: Source address
            destination: Destination address
            max_waypoints: Maximum number of waypoints to extract

        Returns:
            Route object with waypoints

        Raises:
            RouteServiceError: If route retrieval fails
            ValidationError: If addresses are invalid
        """
        # Validate inputs
        source = validate_address(source)
        destination = validate_address(destination)

        logger.info(f"Retrieving route from '{source}' to '{destination}'")

        # Call Directions API
        directions = self._call_directions_api(source, destination)

        # Extract route information
        route = self._parse_route(directions, max_waypoints)

        logger.info(
            f"Route retrieved: {len(route.waypoints)} waypoints, "
            f"{route.total_distance:.1f} km, "
            f"{route.total_duration:.0f} minutes"
        )

        return route

    def _call_directions_api(
        self,
        origin: str,
        destination: str
    ) -> Dict:
        """
        Call Google Maps Directions API.

        Args:
            origin: Origin address
            destination: Destination address

        Returns:
            API response dictionary

        Raises:
            RouteServiceError: If API call fails
        """
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "driving",
            "key": self.api_key
        }

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(
                    self.DIRECTIONS_API_URL,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()

                # Check API response status
                if data.get("status") != "OK":
                    error_message = data.get("error_message", data.get("status"))
                    raise RouteServiceError(
                        f"Google Maps API error: {error_message}"
                    )

                return data

            except requests.Timeout:
                if attempt < self.max_retries:
                    logger.warning(
                        f"API timeout (attempt {attempt + 1}/{self.max_retries + 1}), retrying..."
                    )
                    time.sleep(self.retry_delay)
                else:
                    raise RouteServiceError(
                        f"API timeout after {self.max_retries + 1} attempts"
                    )

            except requests.RequestException as e:
                if attempt < self.max_retries:
                    logger.warning(
                        f"API request error (attempt {attempt + 1}/{self.max_retries + 1}), retrying..."
                    )
                    time.sleep(self.retry_delay)
                else:
                    raise RouteServiceError(f"API request failed: {str(e)}")

        raise RouteServiceError("Failed to retrieve route after all attempts")

    def _parse_route(self, directions: Dict, max_waypoints: int) -> Route:
        """
        Parse route from Directions API response.

        Args:
            directions: API response
            max_waypoints: Maximum waypoints to extract

        Returns:
            Route object

        Raises:
            RouteServiceError: If parsing fails
        """
        try:
            if not directions.get("routes"):
                raise RouteServiceError("No routes found in API response")

            route_data = directions["routes"][0]
            leg = route_data["legs"][0]

            # Extract source and destination
            source = Location(
                address=leg["start_address"],
                lat=leg["start_location"]["lat"],
                lng=leg["start_location"]["lng"]
            )

            destination = Location(
                address=leg["end_address"],
                lat=leg["end_location"]["lat"],
                lng=leg["end_location"]["lng"]
            )

            # Extract waypoints from steps
            waypoints = self._extract_waypoints(leg["steps"], max_waypoints)

            # Calculate totals
            total_distance = leg["distance"]["value"] / 1000  # meters to km
            total_duration = leg["duration"]["value"] / 60  # seconds to minutes

            return Route(
                source=source,
                destination=destination,
                waypoints=waypoints,
                total_distance=total_distance,
                total_duration=total_duration,
                metadata={
                    "summary": route_data.get("summary", ""),
                    "warnings": route_data.get("warnings", []),
                    "waypoint_order": route_data.get("waypoint_order", [])
                }
            )

        except (KeyError, IndexError, TypeError) as e:
            raise RouteServiceError(f"Failed to parse route data: {str(e)}")

    def _extract_waypoints(
        self,
        steps: List[Dict],
        max_waypoints: int
    ) -> List[Waypoint]:
        """
        Extract significant waypoints from route steps.

        Uses heuristics to identify major junctions and significant maneuvers.

        Args:
            steps: Route steps from API
            max_waypoints: Maximum waypoints to extract

        Returns:
            List of waypoints
        """
        if not steps:
            return []

        waypoints = []
        total_distance = 0  # Running total in km

        # Calculate step importance scores
        scored_steps = []
        for i, step in enumerate(steps):
            distance = step["distance"]["value"] / 1000  # meters to km
            instruction = step.get("html_instructions", "")

            # Score based on:
            # 1. Distance (longer steps are more significant)
            # 2. Maneuver type (exits, merges are significant)
            # 3. Road type changes
            score = self._calculate_step_importance(step, distance, instruction)

            scored_steps.append((score, i, step, total_distance))
            total_distance += distance

        # Sort by score (descending) and select top waypoints
        scored_steps.sort(key=lambda x: x[0], reverse=True)

        # Select top waypoints, but maintain route order
        selected_indices = sorted([x[1] for x in scored_steps[:max_waypoints]])

        for i in selected_indices:
            score, idx, step, dist = next(x for x in scored_steps if x[1] == i)

            waypoint = Waypoint(
                location=Location(
                    address=self._extract_address_from_step(step),
                    lat=step["end_location"]["lat"],
                    lng=step["end_location"]["lng"]
                ),
                index=len(waypoints),
                distance_from_start=dist,
                instruction=step.get("html_instructions")
            )
            waypoints.append(waypoint)

        return waypoints

    def _calculate_step_importance(
        self,
        step: Dict,
        distance: float,
        instruction: str
    ) -> float:
        """
        Calculate importance score for a route step.

        Args:
            step: Step dictionary
            distance: Step distance in km
            instruction: HTML instruction text

        Returns:
            Importance score (higher = more important)
        """
        score = 0.0

        # Base score from distance
        score += distance

        # Boost for maneuver types
        maneuver = step.get("maneuver", "").lower()
        important_maneuvers = {
            "ramp": 5.0,
            "fork": 5.0,
            "exit": 8.0,
            "merge": 4.0,
            "roundabout": 3.0,
            "ferry": 10.0
        }

        for keyword, boost in important_maneuvers.items():
            if keyword in maneuver:
                score += boost

        # Boost for highway/major road mentions in instructions
        instruction_lower = instruction.lower()
        if any(keyword in instruction_lower for keyword in ["highway", "interstate", "freeway", "motorway"]):
            score += 3.0

        # Boost for exits and entrances
        if any(keyword in instruction_lower for keyword in ["exit", "enter", "merge"]):
            score += 2.0

        return score

    def _extract_address_from_step(self, step: Dict) -> str:
        """
        Extract or construct address from step.

        Args:
            step: Step dictionary

        Returns:
            Address string
        """
        # Try to get address from step (may not always be present)
        if "start_address" in step:
            return step["start_address"]

        # Fallback: construct from coordinates and instruction
        lat = step["end_location"]["lat"]
        lng = step["end_location"]["lng"]
        instruction = step.get("html_instructions", "").strip()

        # Remove HTML tags from instruction
        import re
        clean_instruction = re.sub(r'<[^>]+>', '', instruction)

        # Use instruction or coordinates
        if clean_instruction and len(clean_instruction) > 10:
            return clean_instruction[:100]  # Truncate

        return f"{lat:.6f}, {lng:.6f}"
