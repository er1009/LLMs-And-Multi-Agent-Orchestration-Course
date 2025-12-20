# AI Agent League System - Comprehensive Coding Agent Context

## Project Overview

This project implements an **AI Agent League System** for an "Even/Odd" game using the **Model Context Protocol (MCP)**. The system consists of multiple autonomous AI agents that communicate via JSON-RPC 2.0 over HTTP to participate in a round-robin tournament.

### Key Objectives
- Build a multi-agent system where AI agents compete in games
- Implement the MCP protocol for standardized agent communication
- Create a complete league infrastructure with registration, game management, and standings
- Enable future extensibility to other game types (Tic-Tac-Toe, etc.)

---

## Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LEAGUE LAYER                              │
│  (League Manager: registration, scheduling, standings)       │
├─────────────────────────────────────────────────────────────┤
│                    REFEREE LAYER                             │
│  (Referees: game management, move validation, results)       │
├─────────────────────────────────────────────────────────────┤
│                    GAME RULES LAYER                          │
│  (Game Logic Module: Even/Odd rules, winner determination)   │
└─────────────────────────────────────────────────────────────┘
```

### Agent Types

| Agent | Port | Role | Responsibilities |
|-------|------|------|------------------|
| **League Manager** | 8000 | Orchestrator | Player/referee registration, schedule creation, standings management |
| **Referee(s)** | 8001-8010 | Game Controller | Register to league, manage individual games, report results |
| **Player Agent(s)** | 8101-8199 | Participant | Register to league, respond to game invitations, make choices |

### Communication Pattern

```
                    ┌─────────────────┐
                    │  League Manager │
                    │     :8000       │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
     ┌──────────┐     ┌──────────┐     ┌──────────┐
     │ Referee  │     │ Player 1 │     │ Player 2 │
     │  :8001   │     │  :8101   │     │  :8102   │
     └────┬─────┘     └──────────┘     └──────────┘
          │                │                │
          └────────────────┴────────────────┘
                    (Game Communication)
```

---

## Protocol Specification

### Protocol Version
- **Protocol**: `league.v2`
- **Minimum Supported**: `2.0.0`
- **Current Version**: `2.1.0`

### Transport Layer
- **Protocol**: HTTP POST
- **Endpoint**: `/mcp` on each agent's server
- **Format**: JSON-RPC 2.0
- **Timestamps**: ISO-8601 in UTC (e.g., `2025-01-15T10:30:00Z`)

### Message Envelope (Required in ALL messages)

```json
{
  "protocol": "league.v2",
  "message_type": "MESSAGE_TYPE_HERE",
  "sender": "agent_type:agent_id",
  "timestamp": "2025-01-15T10:30:00Z",
  "conversation_id": "unique-conversation-id",
  "auth_token": "tok_xxx...",
  "league_id": "league_2025_even_odd"
}
```

### Mandatory Envelope Fields

| Field | Type | Description |
|-------|------|-------------|
| `protocol` | String | Always "league.v2" |
| `message_type` | String | Type of message (e.g., GAME_INVITATION) |
| `sender` | String | Format: `type:id` (e.g., "player:P01", "referee:REF01") |
| `timestamp` | String | ISO-8601 UTC timestamp (must end with Z or +00:00) |
| `conversation_id` | String | Unique conversation identifier |

### Optional Envelope Fields (context-dependent)

| Field | Type | Description |
|-------|------|-------------|
| `auth_token` | String | Authentication token (required after registration) |
| `league_id` | String | League identifier |
| `round_id` | Integer | Round number |
| `match_id` | String | Match identifier |

---

## Complete Message Types Reference

### 1. Referee Registration Messages

#### REFEREE_REGISTER_REQUEST
**Direction**: Referee → League Manager

```json
{
  "jsonrpc": "2.0",
  "method": "register_referee",
  "params": {
    "protocol": "league.v2",
    "message_type": "REFEREE_REGISTER_REQUEST",
    "sender": "referee:alpha",
    "timestamp": "2025-01-15T10:00:00Z",
    "conversation_id": "conv-ref-alpha-reg-001",
    "referee_meta": {
      "display_name": "Referee Alpha",
      "version": "1.0.0",
      "game_types": ["even_odd"],
      "contact_endpoint": "http://localhost:8001/mcp",
      "max_concurrent_matches": 2
    }
  },
  "id": 1
}
```

#### REFEREE_REGISTER_RESPONSE
**Direction**: League Manager → Referee

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "REFEREE_REGISTER_RESPONSE",
    "sender": "league_manager",
    "timestamp": "2025-01-15T10:00:01Z",
    "conversation_id": "conv-ref-alpha-reg-001",
    "status": "ACCEPTED",
    "referee_id": "REF01",
    "auth_token": "tok-ref01-abc123",
    "league_id": "league_2025_even_odd",
    "reason": null
  },
  "id": 1
}
```

### 2. Player Registration Messages

#### LEAGUE_REGISTER_REQUEST
**Direction**: Player → League Manager

```json
{
  "jsonrpc": "2.0",
  "method": "register_player",
  "params": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_REGISTER_REQUEST",
    "sender": "player:alpha",
    "timestamp": "2025-01-15T10:05:00Z",
    "conversation_id": "conv-player-alpha-reg-001",
    "player_meta": {
      "display_name": "Agent Alpha",
      "version": "1.0.0",
      "game_types": ["even_odd"],
      "contact_endpoint": "http://localhost:8101/mcp"
    }
  },
  "id": 1
}
```

#### LEAGUE_REGISTER_RESPONSE
**Direction**: League Manager → Player

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_REGISTER_RESPONSE",
    "sender": "league_manager",
    "timestamp": "2025-01-15T10:05:01Z",
    "conversation_id": "conv-player-alpha-reg-001",
    "status": "ACCEPTED",
    "player_id": "P01",
    "auth_token": "tok-p01-xyz789",
    "league_id": "league_2025_even_odd",
    "reason": null
  },
  "id": 1
}
```

### 3. Round Management Messages

#### ROUND_ANNOUNCEMENT
**Direction**: League Manager → All Players

```json
{
  "jsonrpc": "2.0",
  "method": "notify_round",
  "params": {
    "protocol": "league.v2",
    "message_type": "ROUND_ANNOUNCEMENT",
    "sender": "league_manager",
    "timestamp": "2025-01-15T10:10:00Z",
    "conversation_id": "conv-round-1-announce",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "matches": [
      {
        "match_id": "R1M1",
        "game_type": "even_odd",
        "player_A_id": "P01",
        "player_B_id": "P02",
        "referee_endpoint": "http://localhost:8001/mcp"
      },
      {
        "match_id": "R1M2",
        "game_type": "even_odd",
        "player_A_id": "P03",
        "player_B_id": "P04",
        "referee_endpoint": "http://localhost:8001/mcp"
      }
    ]
  },
  "id": 10
}
```

#### ROUND_COMPLETED
**Direction**: League Manager → All Players

```json
{
  "protocol": "league.v2",
  "message_type": "ROUND_COMPLETED",
  "sender": "league_manager",
  "timestamp": "2025-01-15T12:00:00Z",
  "conversation_id": "conv-round1-complete",
  "league_id": "league_2025_even_odd",
  "round_id": 1,
  "matches_completed": 2,
  "next_round_id": 2,
  "summary": {
    "total_matches": 2,
    "wins": 1,
    "draws": 1,
    "technical_losses": 0
  }
}
```

### 4. Game Flow Messages

#### GAME_INVITATION
**Direction**: Referee → Player

```json
{
  "jsonrpc": "2.0",
  "method": "handle_game_invitation",
  "params": {
    "protocol": "league.v2",
    "message_type": "GAME_INVITATION",
    "sender": "referee:REF01",
    "timestamp": "2025-01-15T10:15:00Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-ref01-abc123",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "match_id": "R1M1",
    "game_type": "even_odd",
    "role_in_match": "PLAYER_A",
    "opponent_id": "P02"
  },
  "id": 1001
}
```

#### GAME_JOIN_ACK
**Direction**: Player → Referee

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "GAME_JOIN_ACK",
    "sender": "player:P01",
    "timestamp": "2025-01-15T10:15:01Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-p01-xyz789",
    "match_id": "R1M1",
    "player_id": "P01",
    "arrival_timestamp": "2025-01-15T10:15:01Z",
    "accept": true
  },
  "id": 1001
}
```

#### CHOOSE_PARITY_CALL
**Direction**: Referee → Player

```json
{
  "jsonrpc": "2.0",
  "method": "choose_parity",
  "params": {
    "protocol": "league.v2",
    "message_type": "CHOOSE_PARITY_CALL",
    "sender": "referee:REF01",
    "timestamp": "2025-01-15T10:15:05Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-ref01-abc123",
    "match_id": "R1M1",
    "player_id": "P01",
    "game_type": "even_odd",
    "context": {
      "opponent_id": "P02",
      "round_id": 1,
      "your_standings": {
        "wins": 0,
        "losses": 0,
        "draws": 0
      }
    },
    "deadline": "2025-01-15T10:15:35Z"
  },
  "id": 1101
}
```

#### CHOOSE_PARITY_RESPONSE
**Direction**: Player → Referee

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "CHOOSE_PARITY_RESPONSE",
    "sender": "player:P01",
    "timestamp": "2025-01-15T10:15:10Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-p01-xyz789",
    "match_id": "R1M1",
    "player_id": "P01",
    "parity_choice": "even"
  },
  "id": 1101
}
```

**CRITICAL**: `parity_choice` must be exactly `"even"` or `"odd"` (lowercase).

### 5. Game Result Messages

#### GAME_OVER
**Direction**: Referee → Both Players

```json
{
  "jsonrpc": "2.0",
  "method": "notify_match_result",
  "params": {
    "protocol": "league.v2",
    "message_type": "GAME_OVER",
    "sender": "referee:REF01",
    "timestamp": "2025-01-15T10:15:30Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-ref01-abc123",
    "match_id": "R1M1",
    "game_type": "even_odd",
    "game_result": {
      "status": "WIN",
      "winner_player_id": "P01",
      "drawn_number": 8,
      "number_parity": "even",
      "choices": {
        "P01": "even",
        "P02": "odd"
      },
      "reason": "P01 chose even, number was 8 (even)"
    }
  },
  "id": 1201
}
```

**Status values**: `"WIN"`, `"DRAW"`, `"TECHNICAL_LOSS"`

#### MATCH_RESULT_REPORT
**Direction**: Referee → League Manager

```json
{
  "jsonrpc": "2.0",
  "method": "report_match_result",
  "params": {
    "protocol": "league.v2",
    "message_type": "MATCH_RESULT_REPORT",
    "sender": "referee:REF01",
    "timestamp": "2025-01-15T10:15:35Z",
    "conversation_id": "conv-r1m1-report",
    "auth_token": "tok-ref01-abc123",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "match_id": "R1M1",
    "game_type": "even_odd",
    "result": {
      "winner": "P01",
      "score": {
        "P01": 3,
        "P02": 0
      },
      "details": {
        "drawn_number": 8,
        "choices": {
          "P01": "even",
          "P02": "odd"
        }
      }
    }
  },
  "id": 1301
}
```

### 6. Standings Messages

#### LEAGUE_STANDINGS_UPDATE
**Direction**: League Manager → All Players

```json
{
  "jsonrpc": "2.0",
  "method": "update_standings",
  "params": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_STANDINGS_UPDATE",
    "sender": "league_manager",
    "timestamp": "2025-01-15T10:20:00Z",
    "conversation_id": "conv-round-1-standings",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "standings": [
      {
        "rank": 1,
        "player_id": "P01",
        "display_name": "Agent Alpha",
        "played": 1,
        "wins": 1,
        "draws": 0,
        "losses": 0,
        "points": 3
      },
      {
        "rank": 2,
        "player_id": "P02",
        "display_name": "Agent Beta",
        "played": 1,
        "wins": 0,
        "draws": 0,
        "losses": 1,
        "points": 0
      }
    ]
  },
  "id": 1401
}
```

### 7. League Completion

#### LEAGUE_COMPLETED
**Direction**: League Manager → All Agents

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_COMPLETED",
  "sender": "league_manager",
  "timestamp": "2025-01-20T18:00:00Z",
  "conversation_id": "conv-league-complete",
  "league_id": "league_2025_even_odd",
  "total_rounds": 3,
  "total_matches": 6,
  "champion": {
    "player_id": "P01",
    "display_name": "Agent Alpha",
    "points": 9
  },
  "final_standings": [
    {"rank": 1, "player_id": "P01", "points": 9},
    {"rank": 2, "player_id": "P03", "points": 5},
    {"rank": 3, "player_id": "P02", "points": 3},
    {"rank": 4, "player_id": "P04", "points": 1}
  ]
}
```

### 8. Query Messages

#### LEAGUE_QUERY
**Direction**: Player/Referee → League Manager

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_QUERY",
  "sender": "player:P01",
  "timestamp": "2025-01-15T14:00:00Z",
  "conversation_id": "conv-query-001",
  "auth_token": "tok_p01_abc123...",
  "league_id": "league_2025_even_odd",
  "query_type": "GET_STANDINGS",
  "query_params": {}
}
```

**Query types**: `GET_STANDINGS`, `GET_SCHEDULE`, `GET_NEXT_MATCH`, `GET_PLAYER_STATS`

### 9. Error Messages

#### LEAGUE_ERROR
**Direction**: League Manager → Agent

```json
{
  "protocol": "league.v2",
  "message_type": "LEAGUE_ERROR",
  "sender": "league_manager",
  "timestamp": "2025-01-15T10:05:30Z",
  "conversation_id": "conv-error-001",
  "error_code": "E012",
  "error_description": "AUTH_TOKEN_INVALID",
  "original_message_type": "LEAGUE_QUERY",
  "context": {
    "provided_token": "tok-invalid-xxx",
    "expected_format": "tok-{agent_id}-{hash}"
  }
}
```

#### GAME_ERROR
**Direction**: Referee → Player

```json
{
  "protocol": "league.v2",
  "message_type": "GAME_ERROR",
  "sender": "referee:REF01",
  "timestamp": "2025-01-15T10:16:00Z",
  "conversation_id": "conv-r1m1-001",
  "match_id": "R1M1",
  "error_code": "E001",
  "error_description": "TIMEOUT_ERROR",
  "affected_player": "P02",
  "action_required": "CHOOSE_PARITY_RESPONSE",
  "retry_info": {
    "retry_count": 1,
    "max_retries": 3,
    "next_retry_at": "2025-01-15T10:16:02Z"
  },
  "consequence": "Technical loss if max retries exceeded"
}
```

### Error Codes Reference

| Code | Name | Description |
|------|------|-------------|
| E001 | TIMEOUT_ERROR | Response not received in time |
| E003 | MISSING_REQUIRED_FIELD | Required field missing |
| E004 | INVALID_PARITY_CHOICE | Invalid choice (not "even" or "odd") |
| E005 | PLAYER_NOT_REGISTERED | Player ID not found |
| E009 | CONNECTION_ERROR | Connection failure |
| E011 | AUTH_TOKEN_MISSING | Auth token required but not provided |
| E012 | AUTH_TOKEN_INVALID | Auth token invalid or expired |
| E013 | REFEREE_NOT_REGISTERED | Referee must register first |
| E018 | PROTOCOL_VERSION_MISMATCH | Incompatible protocol version |
| E021 | INVALID_TIMESTAMP | Timestamp not in UTC |

---

## Timeouts Configuration

| Message Type | Timeout | Notes |
|--------------|---------|-------|
| REFEREE_REGISTER | 10 sec | Referee registration |
| LEAGUE_REGISTER | 10 sec | Player registration |
| GAME_JOIN_ACK | 5 sec | Confirm game attendance |
| CHOOSE_PARITY | 30 sec | Make a game choice |
| GAME_OVER | 5 sec | Receive game result |
| MATCH_RESULT_REPORT | 10 sec | Report result to league |
| LEAGUE_QUERY | 10 sec | Query information |
| Default | 10 sec | All other messages |

### Retry Policy
- Maximum retries: 3
- Delay between retries: 2 seconds
- Backoff strategy: Exponential
- Retryable errors: E001 (timeout), E009 (connection)

---

## Game Rules: Even/Odd

### Rules
1. Two players participate
2. Each player chooses "even" or "odd"
3. Choices are made simultaneously (hidden from opponent)
4. Referee draws a random number between 1-10
5. If number is even → player who chose "even" wins
6. If number is odd → player who chose "odd" wins
7. If both chose the same and were wrong/right → draw

### Scoring
| Result | Winner Points | Loser Points |
|--------|---------------|--------------|
| Win | 3 | 0 |
| Draw | 1 | 1 |
| Loss | 0 | 0 |

### Winner Determination Logic

```python
def determine_winner(choice_a: str, choice_b: str, number: int) -> str:
    is_even = (number % 2 == 0)
    parity = "even" if is_even else "odd"
    
    a_correct = (choice_a == parity)
    b_correct = (choice_b == parity)
    
    if a_correct and not b_correct:
        return "PLAYER_A"
    elif b_correct and not a_correct:
        return "PLAYER_B"
    else:
        return "DRAW"
```

---

## Project Structure

```
project/
├── SHARED/
│   ├── config/
│   │   ├── system.json              # Global system settings
│   │   ├── agents/
│   │   │   └── agents_config.json   # All agents registry
│   │   ├── leagues/
│   │   │   └── league_2025_even_odd.json
│   │   ├── games/
│   │   │   └── games_registry.json  # Supported game types
│   │   └── defaults/
│   │       ├── referee.json
│   │       └── player.json
│   │
│   ├── data/
│   │   ├── leagues/
│   │   │   └── league_2025_even_odd/
│   │   │       ├── standings.json   # Current standings
│   │   │       └── rounds.json      # Round history
│   │   ├── matches/
│   │   │   └── league_2025_even_odd/
│   │   │       ├── R1M1.json
│   │   │       └── R1M2.json
│   │   └── players/
│   │       ├── P01/history.json
│   │       └── P02/history.json
│   │
│   ├── logs/
│   │   ├── league/
│   │   │   └── league_2025_even_odd/
│   │   │       └── league.log.jsonl
│   │   ├── agents/
│   │   │   ├── REF01.log.jsonl
│   │   │   └── P01.log.jsonl
│   │   └── system/
│   │       └── orchestrator.log.jsonl
│   │
│   └── league_sdk/
│       ├── __init__.py
│       ├── config_models.py         # Dataclass definitions
│       ├── config_loader.py         # ConfigLoader class
│       ├── repositories.py          # Data repositories
│       └── logger.py                # JsonLogger class
│
├── agents/
│   ├── league_manager/
│   │   ├── main.py
│   │   ├── handlers.py
│   │   ├── scheduler.py
│   │   └── requirements.txt
│   │
│   ├── referee/
│   │   ├── main.py
│   │   ├── game_logic.py
│   │   ├── handlers.py
│   │   └── requirements.txt
│   │
│   └── player/
│       ├── main.py
│       ├── strategy.py
│       ├── handlers.py
│       └── requirements.txt
│
└── doc/
    └── protocol-spec.md
```

---

## Implementation Guide

### 1. Basic MCP Server (FastAPI)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI()

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int = 1

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: dict = {}
    id: int = 1

@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    if request.method == "tool_name":
        result = handle_tool(request.params)
        return MCPResponse(result=result, id=request.id)
    return MCPResponse(result={"error": "Unknown method"})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8101)
```

### 2. Player Agent Implementation

```python
import random
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone

app = FastAPI()

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict = {}
    id: int = 1

# Player state
class PlayerState:
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.auth_token = None
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.history = []

state = PlayerState("P01")

@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    if request.method == "handle_game_invitation":
        return handle_invitation(request.params, request.id)
    elif request.method == "choose_parity":
        return handle_choose_parity(request.params, request.id)
    elif request.method == "notify_match_result":
        return handle_result(request.params, request.id)
    return {"jsonrpc": "2.0", "error": {"message": "Unknown method"}, "id": request.id}

def handle_invitation(params: dict, request_id: int):
    return {
        "jsonrpc": "2.0",
        "result": {
            "protocol": "league.v2",
            "message_type": "GAME_JOIN_ACK",
            "sender": f"player:{state.player_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "conversation_id": params.get("conversation_id"),
            "auth_token": state.auth_token,
            "match_id": params.get("match_id"),
            "player_id": state.player_id,
            "arrival_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "accept": True
        },
        "id": request_id
    }

def handle_choose_parity(params: dict, request_id: int):
    # Simple random strategy
    choice = random.choice(["even", "odd"])
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "protocol": "league.v2",
            "message_type": "CHOOSE_PARITY_RESPONSE",
            "sender": f"player:{state.player_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "conversation_id": params.get("conversation_id"),
            "auth_token": state.auth_token,
            "match_id": params.get("match_id"),
            "player_id": state.player_id,
            "parity_choice": choice
        },
        "id": request_id
    }

def handle_result(params: dict, request_id: int):
    game_result = params.get("game_result", {})
    winner = game_result.get("winner_player_id")
    
    if winner == state.player_id:
        state.wins += 1
    elif game_result.get("status") == "DRAW":
        state.draws += 1
    else:
        state.losses += 1
    
    state.history.append({
        "match_id": params.get("match_id"),
        "result": game_result
    })
    
    return {"jsonrpc": "2.0", "result": {"status": "ok"}, "id": request_id}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8101)
```

### 3. Referee Implementation

```python
import random
import requests
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI()

class RefereeState:
    def __init__(self, referee_id: str):
        self.referee_id = referee_id
        self.auth_token = None
        self.current_matches = {}

state = RefereeState("REF01")

def register_to_league(league_endpoint: str):
    payload = {
        "jsonrpc": "2.0",
        "method": "register_referee",
        "params": {
            "protocol": "league.v2",
            "message_type": "REFEREE_REGISTER_REQUEST",
            "sender": f"referee:{state.referee_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "conversation_id": f"conv-ref-{state.referee_id}-reg",
            "referee_meta": {
                "display_name": f"Referee {state.referee_id}",
                "version": "1.0.0",
                "game_types": ["even_odd"],
                "contact_endpoint": "http://localhost:8001/mcp",
                "max_concurrent_matches": 2
            }
        },
        "id": 1
    }
    response = requests.post(league_endpoint, json=payload, timeout=10)
    result = response.json().get("result", {})
    if result.get("status") == "ACCEPTED":
        state.auth_token = result.get("auth_token")
        return True
    return False

def determine_winner(choice_a: str, choice_b: str, number: int):
    is_even = (number % 2 == 0)
    parity = "even" if is_even else "odd"
    
    a_correct = (choice_a == parity)
    b_correct = (choice_b == parity)
    
    if a_correct and not b_correct:
        return "PLAYER_A", parity
    elif b_correct and not a_correct:
        return "PLAYER_B", parity
    else:
        return "DRAW", parity

def call_player_tool(endpoint: str, method: str, params: dict, timeout: int = 30):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
        return response.json()
    except requests.Timeout:
        return {"error": "TIMEOUT"}
    except Exception as e:
        return {"error": str(e)}
```

### 4. League Manager Implementation

```python
from itertools import combinations
from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI()

class LeagueState:
    def __init__(self, league_id: str):
        self.league_id = league_id
        self.referees = {}  # referee_id -> {endpoint, auth_token, ...}
        self.players = {}   # player_id -> {endpoint, auth_token, ...}
        self.schedule = []
        self.standings = {}
        self.current_round = 0
        self.next_referee_id = 1
        self.next_player_id = 1

state = LeagueState("league_2025_even_odd")

def create_schedule(player_ids: list) -> list:
    """Create Round-Robin schedule"""
    matches = []
    round_num = 1
    match_num = 1
    
    for p1, p2 in combinations(player_ids, 2):
        matches.append({
            "match_id": f"R{round_num}M{match_num}",
            "round_id": round_num,
            "player_A_id": p1,
            "player_B_id": p2
        })
        match_num += 1
    
    return matches

def update_standings(player_id: str, result: str, points: int):
    if player_id not in state.standings:
        state.standings[player_id] = {
            "player_id": player_id,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "points": 0
        }
    
    state.standings[player_id]["played"] += 1
    state.standings[player_id]["points"] += points
    
    if result == "WIN":
        state.standings[player_id]["wins"] += 1
    elif result == "DRAW":
        state.standings[player_id]["draws"] += 1
    else:
        state.standings[player_id]["losses"] += 1

@app.post("/mcp")
async def mcp_endpoint(request: dict):
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id", 1)
    
    if method == "register_referee":
        return handle_register_referee(params, request_id)
    elif method == "register_player":
        return handle_register_player(params, request_id)
    elif method == "report_match_result":
        return handle_match_result(params, request_id)
    elif method == "league_query":
        return handle_query(params, request_id)
    
    return {"jsonrpc": "2.0", "error": {"message": "Unknown method"}, "id": request_id}
```

### 5. HTTP Client with Retry

```python
import time
import requests
from typing import Dict, Any, Optional

class RetryConfig:
    MAX_RETRIES = 3
    BASE_DELAY = 2.0
    BACKOFF_MULTIPLIER = 2.0

def call_with_retry(endpoint: str, method: str, params: Dict[str, Any], 
                    timeout: int = 30) -> Dict[str, Any]:
    """Send MCP request with retry logic."""
    last_error = None
    
    for attempt in range(RetryConfig.MAX_RETRIES):
        try:
            response = requests.post(
                endpoint,
                json={
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params,
                    "id": 1
                },
                timeout=timeout
            )
            return response.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            last_error = e
            if attempt < RetryConfig.MAX_RETRIES - 1:
                delay = RetryConfig.BASE_DELAY * (RetryConfig.BACKOFF_MULTIPLIER ** attempt)
                time.sleep(delay)
    
    return {
        "error": {
            "error_code": "E009",
            "error_description": f"Max retries exceeded: {last_error}"
        }
    }
```

### 6. Structured Logger

```python
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

class JsonLogger:
    LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]
    
    def __init__(self, component: str, league_id: Optional[str] = None,
                 log_root: Path = Path("SHARED/logs")):
        self.component = component
        
        if league_id:
            subdir = log_root / "league" / league_id
        else:
            subdir = log_root / "agents"
        
        subdir.mkdir(parents=True, exist_ok=True)
        self.log_file = subdir / f"{component}.log.jsonl"
    
    def log(self, event_type: str, level: str = "INFO", **details):
        entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "component": self.component,
            "event_type": event_type,
            "level": level,
            **details
        }
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def debug(self, event_type: str, **details):
        self.log(event_type, level="DEBUG", **details)
    
    def info(self, event_type: str, **details):
        self.log(event_type, level="INFO", **details)
    
    def warning(self, event_type: str, **details):
        self.log(event_type, level="WARNING", **details)
    
    def error(self, event_type: str, **details):
        self.log(event_type, level="ERROR", **details)
```

---

## Configuration Files

### system.json

```json
{
  "schema_version": "1.0.0",
  "system_id": "league_system_prod",
  "protocol_version": "league.v2",
  "default_league_id": "league_2025_even_odd",
  "network": {
    "base_host": "localhost",
    "default_league_manager_port": 8000,
    "default_referee_port_range": [8001, 8010],
    "default_player_port_range": [8101, 8199]
  },
  "security": {
    "enable_auth_tokens": true,
    "token_length": 32,
    "token_ttl_hours": 24
  },
  "timeouts": {
    "register_referee_timeout_sec": 10,
    "register_player_timeout_sec": 10,
    "game_join_ack_timeout_sec": 5,
    "move_timeout_sec": 30,
    "generic_response_timeout_sec": 10
  },
  "retry_policy": {
    "max_retries": 3,
    "base_delay_sec": 2.0,
    "backoff_strategy": "exponential"
  }
}
```

### agents_config.json

```json
{
  "schema_version": "1.0.0",
  "last_updated": "2025-01-15T10:00:00Z",
  "league_manager": {
    "display_name": "Central League Manager",
    "endpoint": "http://localhost:8000/mcp",
    "version": "1.0.0"
  },
  "referees": [
    {
      "referee_id": "REF01",
      "display_name": "Referee Alpha",
      "endpoint": "http://localhost:8001/mcp",
      "version": "1.0.0",
      "game_types": ["even_odd"],
      "max_concurrent_matches": 2,
      "active": true
    }
  ],
  "players": [
    {
      "player_id": "P01",
      "display_name": "Agent Alpha",
      "version": "1.0.0",
      "game_types": ["even_odd"],
      "default_endpoint": "http://localhost:8101/mcp",
      "active": true
    },
    {
      "player_id": "P02",
      "display_name": "Agent Beta",
      "version": "1.0.0",
      "game_types": ["even_odd"],
      "default_endpoint": "http://localhost:8102/mcp",
      "active": true
    }
  ]
}
```

### league_config.json

```json
{
  "schema_version": "1.0.0",
  "league_id": "league_2025_even_odd",
  "display_name": "Even/Odd League 2025",
  "game_type": "even_odd",
  "status": "ACTIVE",
  "created_at": "2025-01-01T00:00:00Z",
  "scoring": {
    "win_points": 3,
    "draw_points": 1,
    "loss_points": 0,
    "technical_loss_points": 0,
    "tiebreakers": ["wins", "head_to_head", "draws"]
  },
  "scheduling": {
    "format": "round_robin",
    "matches_per_round": 2
  },
  "participants": {
    "min_players": 2,
    "max_players": 100
  }
}
```

### standings.json

```json
{
  "schema_version": "1.0.0",
  "league_id": "league_2025_even_odd",
  "last_updated": "2025-01-15T12:00:00Z",
  "version": 5,
  "rounds_completed": 2,
  "standings": [
    {
      "rank": 1,
      "player_id": "P01",
      "display_name": "Agent Alpha",
      "played": 2,
      "wins": 2,
      "draws": 0,
      "losses": 0,
      "points": 6
    },
    {
      "rank": 2,
      "player_id": "P02",
      "display_name": "Agent Beta",
      "played": 2,
      "wins": 1,
      "draws": 0,
      "losses": 1,
      "points": 3
    }
  ]
}
```

---

## Startup Sequence

### Order of Operations

```
1. Start League Manager (port 8000)
   └── Wait for server ready

2. Start Referees (ports 8001-8010)
   └── Each referee registers with League Manager
   └── Receives referee_id and auth_token

3. Start Players (ports 8101+)
   └── Each player registers with League Manager
   └── Receives player_id and auth_token

4. League Manager creates schedule
   └── Round-Robin pairing of all players

5. For each round:
   a. League Manager sends ROUND_ANNOUNCEMENT
   b. Referees manage assigned matches
   c. Results reported via MATCH_RESULT_REPORT
   d. League Manager updates standings
   e. LEAGUE_STANDINGS_UPDATE sent to all

6. After all rounds: LEAGUE_COMPLETED
```

### Terminal Commands

```bash
# Terminal 1 - League Manager
cd agents/league_manager
python main.py --port 8000 --league-id league_2025_even_odd

# Terminal 2 - Referee
cd agents/referee
python main.py --port 8001 --referee-id REF01 --league-id league_2025_even_odd

# Terminal 3-6 - Players
cd agents/player
python main.py --port 8101 --player-id P01
python main.py --port 8102 --player-id P02
python main.py --port 8103 --player-id P03
python main.py --port 8104 --player-id P04
```

---

## Game State Machine

### Match States

```
WAITING_FOR_PLAYERS → COLLECTING_CHOICES → DRAWING_NUMBER → FINISHED
        ↓                    ↓                   ↓
    (timeout)            (timeout)          (auto)
        ↓                    ↓                   ↓
   GAME_ERROR           GAME_ERROR         GAME_OVER
```

| State | Description | Transition |
|-------|-------------|------------|
| WAITING_FOR_PLAYERS | Waiting for GAME_JOIN_ACK from both players | Both ACK received |
| COLLECTING_CHOICES | Waiting for CHOOSE_PARITY_RESPONSE from both | Both choices received |
| DRAWING_NUMBER | Referee draws number and determines winner | Automatic |
| FINISHED | Game complete, results sent | Terminal |

### Agent Lifecycle States

```
INIT → REGISTERED → ACTIVE → SUSPENDED → SHUTDOWN
  ↓        ↓          ↓          ↓
(error) (league   (timeout) (recover)
         start)
```

---

## Required Tools per Agent

### Player Agent Tools

| Tool | Description | Response |
|------|-------------|----------|
| `handle_game_invitation` | Accept game invitation | GAME_JOIN_ACK |
| `choose_parity` | Make even/odd choice | CHOOSE_PARITY_RESPONSE |
| `notify_match_result` | Receive game result | Acknowledgment |

### Referee Tools

| Tool | Description |
|------|-------------|
| `register_to_league` | Register self with League Manager |
| `start_match` | Initialize a new match |
| `collect_choices` | Request choices from players |
| `draw_number` | Generate random number |
| `finalize_match` | Determine winner and report |

### League Manager Tools

| Tool | Description |
|------|-------------|
| `register_referee` | Register a new referee |
| `register_player` | Register a new player |
| `create_schedule` | Generate Round-Robin schedule |
| `report_match_result` | Receive match results |
| `get_standings` | Return current standings |
| `league_query` | Handle various queries |

---

## Testing Checklist

### Pre-submission Tests

- [ ] Agent starts without errors
- [ ] Agent responds to all required message types
- [ ] JSON structures match protocol exactly
- [ ] Timestamps are in UTC format
- [ ] `parity_choice` is exactly "even" or "odd"
- [ ] All responses include required envelope fields
- [ ] Agent handles timeouts gracefully
- [ ] Agent handles error messages correctly
- [ ] Auth token is included after registration
- [ ] Agent can complete a full game cycle

### Integration Tests

- [ ] Run local league with 4 player instances
- [ ] Verify all registrations complete
- [ ] Verify round-robin schedule is correct
- [ ] Verify standings update after each match
- [ ] Verify LEAGUE_COMPLETED message at end
- [ ] Test with another student's agent (protocol compatibility)

---

## Common Pitfalls

1. **Wrong timestamp format**: Must be UTC with `Z` suffix
2. **Wrong parity choice format**: Must be lowercase `"even"` or `"odd"`
3. **Missing auth_token**: Required in all messages after registration
4. **Missing envelope fields**: All messages need protocol, message_type, sender, timestamp
5. **Timeout handling**: Agent crashes instead of handling timeout gracefully
6. **Case sensitivity**: Message types and field names are case-sensitive
7. **Port conflicts**: Each agent needs a unique port
8. **Startup order**: League Manager must start first

---

## Dependencies

### Python Requirements

```
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
requests>=2.31.0
python-dateutil>=2.8.2
```

### Installation

```bash
pip install fastapi uvicorn pydantic requests python-dateutil
```

---

## File Submission Requirements

1. **Source code** - All agent source files
2. **README.md** - Setup and run instructions
3. **requirements.txt** - Python dependencies
4. **Report** including:
   - Architecture description
   - Strategy explanation
   - Challenges and solutions
   - Development process documentation
   - Conclusions and recommendations

---

## References

- MCP Specification: https://modelcontextprotocol.io/
- JSON-RPC 2.0 Specification: https://www.jsonrpc.org/specification
- FastAPI Documentation: https://fastapi.tiangolo.com/

---

## Summary

This project implements a complete AI Agent League System using MCP protocol. Key components:

1. **League Manager** - Central orchestrator managing registration, scheduling, and standings
2. **Referee(s)** - Game controllers managing individual matches
3. **Player Agents** - Autonomous participants making strategic choices

All communication uses JSON-RPC 2.0 over HTTP with standardized message envelopes. The system is designed for extensibility to support additional game types in the future.

**Good luck with your implementation!**
