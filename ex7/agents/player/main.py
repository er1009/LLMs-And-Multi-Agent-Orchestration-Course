"""
Player Agent - FastAPI server entry point.

Game participant for the AI Agent League System.
"""

import argparse
import asyncio
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SHARED.league_sdk.logger import JsonLogger
from SHARED.league_sdk.models import utc_timestamp

from .state import PlayerState
from .handlers import PlayerHandlers


app = FastAPI(
    title="Player Agent",
    description="Game participant for the AI Agent League System",
    version="1.0.0",
)


class MCPRequest(BaseModel):
    """JSON-RPC 2.0 request model."""

    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int = 1


# Global state
state: PlayerState | None = None
handlers: PlayerHandlers | None = None
logger: JsonLogger | None = None


@app.on_event("startup")
async def startup():
    """Initialize player state on startup."""
    global state, handlers, logger

    port = app.state.port if hasattr(app.state, "port") else 8101
    league_endpoint = app.state.league_endpoint if hasattr(app.state, "league_endpoint") else "http://localhost:8000/mcp"
    display_name = app.state.display_name if hasattr(app.state, "display_name") else "Player Alpha"
    strategy = app.state.strategy if hasattr(app.state, "strategy") else "random"

    logger = JsonLogger(display_name.replace(" ", "_"))
    state = PlayerState(
        display_name=display_name,
        league_endpoint=league_endpoint,
        port=port,
        strategy=strategy,
    )
    handlers = PlayerHandlers(state, logger)

    logger.info("STARTUP", port=port, strategy=strategy)

    # Auto-register with league manager
    await asyncio.sleep(2)  # Wait for league manager to be ready
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

    if method == "handle_game_invitation":
        return handlers.handle_game_invitation(params, request_id)

    elif method == "choose_parity":
        return handlers.handle_choose_parity(params, request_id)

    elif method == "notify_match_result":
        return handlers.handle_match_result(params, request_id)

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
        "component": "player",
        "player_id": state.player_id if state else None,
        "registered": state.is_registered() if state else False,
        "timestamp": utc_timestamp(),
    }


@app.get("/status")
async def status():
    """Get player status."""
    global state
    if not state:
        return {"status": "not_initialized"}

    return {
        "player_id": state.player_id,
        "display_name": state.display_name,
        "registered": state.is_registered(),
        "league_id": state.league_id,
        "strategy": state.strategy,
        "stats": state.get_stats(),
    }


@app.get("/stats")
async def get_stats():
    """Get player statistics."""
    global state
    if not state:
        return {"stats": {}}

    return {
        "player_id": state.player_id,
        "stats": state.get_stats(),
        "win_rate": state.get_win_rate(),
    }


@app.get("/history")
async def get_history():
    """Get game history."""
    global state
    if not state:
        return {"history": []}

    return {
        "player_id": state.player_id,
        "history": [
            {
                "match_id": g.match_id,
                "opponent_id": g.opponent_id,
                "my_choice": g.my_choice,
                "opponent_choice": g.opponent_choice,
                "drawn_number": g.drawn_number,
                "result": g.result,
                "points_earned": g.points_earned,
            }
            for g in state.history
        ],
    }


def main():
    """Run the player server."""
    parser = argparse.ArgumentParser(description="Player Agent Server")
    parser.add_argument("--port", type=int, default=8101, help="Port to run on")
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
        default="Player Alpha",
        help="Display name for the player",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="random",
        choices=["random", "always_even", "always_odd", "alternating", "biased_even", "biased_odd", "counter"],
        help="Strategy to use for parity choices",
    )
    args = parser.parse_args()

    app.state.port = args.port
    app.state.league_endpoint = args.league_endpoint
    app.state.display_name = args.display_name
    app.state.strategy = args.strategy

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
