# AI Agent League System

A multi-agent system implementing an "Even/Odd" game league using the Model Context Protocol (MCP) over JSON-RPC 2.0.

## Overview

This project implements a complete AI Agent League System where autonomous agents compete in a round-robin tournament. The system consists of three types of agents:

- **League Manager** - Central orchestrator handling registration, scheduling, and standings
- **Referee** - Game controller managing individual matches
- **Player Agents** - Autonomous participants making strategic choices

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone or navigate to the project
cd ex7

# Install dependencies
pip install -r requirements.txt
```

### Run the Demo

```bash
# Run a complete league with 4 players
python scripts/run_league.py

# Or with custom number of players
python scripts/run_league.py --players 8
```

### Example Output

![League Results](assets/run_league_results.png)

## Project Structure

```
ex7/
├── SHARED/
│   ├── config/          # Configuration files
│   ├── data/            # Runtime data (standings, matches)
│   ├── logs/            # Structured JSON logs
│   └── league_sdk/      # Shared utilities and models
├── agents/
│   ├── league_manager/  # League Manager agent
│   ├── referee/         # Referee agent
│   └── player/          # Player agent
├── tests/               # Unit tests
├── scripts/             # Orchestration scripts
└── docs/                # Documentation
```

## Architecture

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

### Communication

All agents communicate via:
- **Protocol**: HTTP POST to `/mcp` endpoint
- **Format**: JSON-RPC 2.0
- **Message Envelope**: Standardized with protocol version, sender, timestamp, etc.

### Ports

| Agent | Port Range |
|-------|------------|
| League Manager | 8000 |
| Referee(s) | 8001-8010 |
| Player(s) | 8101-8199 |

## Game Rules: Even/Odd

1. Two players participate in each match
2. Each player secretly chooses "even" or "odd"
3. Referee draws a random number between 1-10
4. If number is even → player who chose "even" wins
5. If number is odd → player who chose "odd" wins
6. If both chose the same → draw

### Scoring

| Result | Points |
|--------|--------|
| Win | 3 |
| Draw | 1 |
| Loss | 0 |

## Running Individual Agents

### League Manager

```bash
python -m agents.league_manager.main --port 8000
```

### Referee

```bash
python -m agents.referee.main --port 8001 --league-endpoint http://localhost:8000/mcp
```

### Player

```bash
python -m agents.player.main --port 8101 --display-name "Agent Alpha" --strategy random
```

Available strategies: `random`, `always_even`, `always_odd`, `alternating`, `biased_even`, `biased_odd`, `counter`

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_game_logic.py -v

# Run with coverage
pytest tests/ --cov=SHARED --cov=agents --cov-report=html
```

## API Endpoints

### League Manager (port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST | Main MCP endpoint |
| `/health` | GET | Health check |
| `/status` | GET | League status |
| `/standings` | GET | Current standings |
| `/create_schedule` | POST | Trigger schedule creation |

### Referee (port 8001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST | Main MCP endpoint |
| `/health` | GET | Health check |
| `/status` | GET | Referee status |
| `/run_match` | POST | Trigger a match |

### Player (port 8101+)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST | Main MCP endpoint |
| `/health` | GET | Health check |
| `/status` | GET | Player status |
| `/stats` | GET | Player statistics |
| `/history` | GET | Game history |

## Configuration

Configuration files are in `SHARED/config/`:

- `system.json` - Global system settings
- `agents/agents_config.json` - Agent registry
- `leagues/league_2025_even_odd.json` - League settings
- `games/games_registry.json` - Supported game types

## Logging

Logs are written in JSON-lines format to `SHARED/logs/`:

- `league/{league_id}/` - League-specific logs
- `agents/` - Individual agent logs

## Documentation

- [Product Requirements Document](docs/PRD.md)
- [Architecture Document](docs/ARCHITECTURE.md)

## License

MIT License
