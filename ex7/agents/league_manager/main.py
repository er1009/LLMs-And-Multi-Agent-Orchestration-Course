"""
League Manager - FastAPI server entry point.

Central orchestrator for the AI Agent League System.
"""

import argparse
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SHARED.league_sdk.logger import JsonLogger
from SHARED.league_sdk.models import utc_timestamp

from .state import LeagueState
from .handlers import LeagueHandlers


app = FastAPI(
    title="League Manager",
    description="Central orchestrator for the AI Agent League System",
    version="1.0.0",
)


class MCPRequest(BaseModel):
    """JSON-RPC 2.0 request model."""

    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int = 1


# Global state (initialized on startup)
state: LeagueState | None = None
handlers: LeagueHandlers | None = None
logger: JsonLogger | None = None


@app.on_event("startup")
async def startup():
    """Initialize league state on startup."""
    global state, handlers, logger

    league_id = app.state.league_id if hasattr(app.state, "league_id") else "league_2025_even_odd"

    logger = JsonLogger("league_manager", league_id=league_id)
    state = LeagueState(league_id)
    handlers = LeagueHandlers(state, logger)

    logger.info("STARTUP", league_id=league_id)


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

    if method == "register_referee":
        return handlers.handle_register_referee(params, request_id)

    elif method == "register_player":
        return handlers.handle_register_player(params, request_id)

    elif method == "report_match_result":
        return handlers.handle_report_match_result(params, request_id)

    elif method == "league_query":
        return handlers.handle_league_query(params, request_id)

    else:
        logger.warning("UNKNOWN_METHOD", method=method)
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}",
            },
            "id": request_id,
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "component": "league_manager",
        "timestamp": utc_timestamp(),
    }


@app.get("/status")
async def status():
    """Get league status."""
    global state
    if not state:
        return {"status": "not_initialized"}

    return {
        "league_id": state.league_id,
        "referees_registered": len(state.referees),
        "players_registered": len(state.players),
        "matches_scheduled": len(state.schedule),
        "current_round": state.current_round,
        "rounds_completed": state.rounds_completed,
    }


@app.get("/standings")
async def get_standings():
    """Get current standings."""
    global state
    if not state:
        return {"standings": []}

    return {"standings": state.get_ranked_standings()}


@app.post("/create_schedule")
async def create_schedule():
    """Trigger schedule creation."""
    global handlers
    if not handlers:
        return {"error": "Not initialized"}

    schedule = handlers.create_schedule()
    return {"schedule": schedule}


def main():
    """Run the league manager server."""
    parser = argparse.ArgumentParser(description="League Manager Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")
    parser.add_argument(
        "--league-id",
        type=str,
        default="league_2025_even_odd",
        help="League ID",
    )
    args = parser.parse_args()

    app.state.league_id = args.league_id

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
