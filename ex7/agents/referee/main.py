"""
Referee Agent - FastAPI server entry point.

Game controller for the AI Agent League System.
"""

import argparse
import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SHARED.league_sdk.logger import JsonLogger
from SHARED.league_sdk.models import utc_timestamp

from .state import RefereeState
from .handlers import RefereeHandlers


app = FastAPI(
    title="Referee Agent",
    description="Game controller for the AI Agent League System",
    version="1.0.0",
)


class MCPRequest(BaseModel):
    """JSON-RPC 2.0 request model."""

    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int = 1


class MatchRequest(BaseModel):
    """Request to run a match."""

    match_id: str
    round_id: int
    player_a_id: str
    player_b_id: str
    player_a_endpoint: str
    player_b_endpoint: str


# Global state
state: RefereeState | None = None
handlers: RefereeHandlers | None = None
logger: JsonLogger | None = None


@app.on_event("startup")
async def startup():
    """Initialize referee state on startup."""
    global state, handlers, logger

    port = app.state.port if hasattr(app.state, "port") else 8001
    league_endpoint = app.state.league_endpoint if hasattr(app.state, "league_endpoint") else "http://localhost:8000/mcp"
    display_name = app.state.display_name if hasattr(app.state, "display_name") else "Referee Alpha"

    logger = JsonLogger(display_name.replace(" ", "_"))
    state = RefereeState(
        display_name=display_name,
        league_endpoint=league_endpoint,
    )
    state.port = port
    handlers = RefereeHandlers(state, logger)

    logger.info("STARTUP", port=port)

    # Auto-register with league manager
    await asyncio.sleep(1)  # Wait for league manager to be ready
    success = handlers.register_to_league()
    if not success:
        logger.error("REGISTRATION_FAILED", message="Could not register with league manager")


@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest) -> dict[str, Any]:
    """Main MCP endpoint for JSON-RPC 2.0 requests."""
    global handlers, logger

    method = request.method
    params = request.params
    request_id = request.id

    logger.log_message(
        "RECEIVED",
        params.get("message_type", method),
        sender=params.get("sender"),
    )

    # Referee receives match assignments from league manager
    if method == "assign_match":
        # Extract match details and run match
        match_id = params.get("match_id")
        round_id = params.get("round_id", 1)
        player_a_id = params.get("player_A_id")
        player_b_id = params.get("player_B_id")
        player_a_endpoint = params.get("player_A_endpoint")
        player_b_endpoint = params.get("player_B_endpoint")

        result = await handlers.run_match(
            match_id=match_id,
            round_id=round_id,
            player_a_id=player_a_id,
            player_b_id=player_b_id,
            player_a_endpoint=player_a_endpoint,
            player_b_endpoint=player_b_endpoint,
        )

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id,
        }

    logger.warning("UNKNOWN_METHOD", method=method)
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": f"Method not found: {method}",
        },
        "id": request_id,
    }


@app.post("/run_match")
async def run_match(request: MatchRequest) -> dict[str, Any]:
    """HTTP endpoint to trigger a match."""
    global handlers

    if not handlers:
        return {"error": "Not initialized"}

    if not state.is_registered():
        return {"error": "Referee not registered with league"}

    result = await handlers.run_match(
        match_id=request.match_id,
        round_id=request.round_id,
        player_a_id=request.player_a_id,
        player_b_id=request.player_b_id,
        player_a_endpoint=request.player_a_endpoint,
        player_b_endpoint=request.player_b_endpoint,
    )

    return result


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "component": "referee",
        "referee_id": state.referee_id if state else None,
        "registered": state.is_registered() if state else False,
        "timestamp": utc_timestamp(),
    }


@app.get("/status")
async def status():
    """Get referee status."""
    global state
    if not state:
        return {"status": "not_initialized"}

    return {
        "referee_id": state.referee_id,
        "registered": state.is_registered(),
        "league_id": state.league_id,
        "active_matches": len(state.active_matches),
    }


def main():
    """Run the referee server."""
    parser = argparse.ArgumentParser(description="Referee Agent Server")
    parser.add_argument("--port", type=int, default=8001, help="Port to run on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument(
        "--league-endpoint",
        type=str,
        default="http://localhost:8000/mcp",
        help="League manager endpoint",
    )
    parser.add_argument(
        "--display-name",
        type=str,
        default="Referee Alpha",
        help="Display name for the referee",
    )
    args = parser.parse_args()

    app.state.port = args.port
    app.state.league_endpoint = args.league_endpoint
    app.state.display_name = args.display_name

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
