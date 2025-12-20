# Architecture Document
## AI Agent League System

### Version: 1.0.0
### Last Updated: 2025-01-15

---

## 1. C4 Model

### 1.1 Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Agent League System                      │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │    League    │    │   Referee    │    │   Player     │       │
│  │   Manager    │◄──►│   Agent(s)   │◄──►│   Agent(s)   │       │
│  │              │    │              │    │              │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         └───────────────────┴───────────────────┘                │
│                          │                                       │
│                    JSON-RPC 2.0 / HTTP                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   File System    │
                    │  (Config, Logs,  │
                    │    Data)         │
                    └──────────────────┘
```

### 1.2 Container Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Agent League System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    League Manager                         │   │
│  │                    (FastAPI :8000)                        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │   │
│  │  │Handlers │ │Scheduler│ │  State  │ │  MCP    │        │   │
│  │  │         │ │         │ │ Manager │ │Endpoint │        │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Referee Agent                          │   │
│  │                    (FastAPI :8001)                        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │   │
│  │  │Handlers │ │  Game   │ │  Match  │ │  MCP    │        │   │
│  │  │         │ │  Logic  │ │  State  │ │ Client  │        │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Player Agent(s)                        │   │
│  │                    (FastAPI :8101+)                       │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │   │
│  │  │Handlers │ │Strategy │ │  State  │ │  MCP    │        │   │
│  │  │         │ │ Engine  │ │ Manager │ │ Client  │        │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Shared SDK                             │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │   │
│  │  │ Models  │ │  HTTP   │ │ Logger  │ │ Config  │        │   │
│  │  │(Pydantic│ │ Client  │ │  (JSON) │ │ Loader  │        │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Component Diagram - League Manager

```
┌──────────────────────────────────────────────────────────────┐
│                      League Manager                           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    main.py                               │ │
│  │  - FastAPI application                                   │ │
│  │  - /mcp endpoint                                         │ │
│  │  - /health, /status, /standings endpoints                │ │
│  └───────────────────────────┬─────────────────────────────┘ │
│                              │                                │
│  ┌───────────────────────────▼─────────────────────────────┐ │
│  │                    handlers.py                           │ │
│  │  - handle_register_referee()                             │ │
│  │  - handle_register_player()                              │ │
│  │  - handle_report_match_result()                          │ │
│  │  - handle_league_query()                                 │ │
│  └───────────────────────────┬─────────────────────────────┘ │
│                              │                                │
│  ┌────────────────────┬──────┴──────┬────────────────────┐   │
│  │                    │             │                     │   │
│  ▼                    ▼             ▼                     ▼   │
│  ┌─────────┐    ┌─────────┐   ┌─────────┐          ┌─────────┐│
│  │scheduler│    │  state  │   │  data   │          │ logger  ││
│  │  .py    │    │  .py    │   │ loader  │          │  .py    ││
│  │         │    │         │   │         │          │         ││
│  │Round-   │    │Referee/ │   │Persist  │          │JSON     ││
│  │robin    │    │Player   │   │standings│          │logging  ││
│  │schedule │    │registry │   │         │          │         ││
│  └─────────┘    └─────────┘   └─────────┘          └─────────┘│
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| Language | Python 3.10+ | Modern async support, type hints |
| Web Framework | FastAPI | Async, Pydantic integration, OpenAPI |
| HTTP Server | Uvicorn | ASGI, production-ready |
| Data Validation | Pydantic v2 | Type-safe, JSON serialization |
| HTTP Client | Requests | Simple, reliable |
| Testing | pytest | Industry standard, fixtures |

---

## 3. Deployment Architecture

### 3.1 Single Machine (Development)

```
┌─────────────────────────────────────────────────────────────┐
│                      Host Machine                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │League Manager│  │   Referee    │  │ Player Agents    │   │
│  │   :8000      │  │   :8001      │  │ :8101, :8102...  │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│         │                │                    │              │
│         └────────────────┴────────────────────┘              │
│                          │                                   │
│                    localhost                                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    File System                        │   │
│  │   SHARED/config/   SHARED/data/   SHARED/logs/       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Data Schemas

### 4.1 MCP Message Envelope

```json
{
  "protocol": "league.v2",
  "message_type": "MESSAGE_TYPE",
  "sender": "agent_type:agent_id",
  "timestamp": "2025-01-15T10:30:00Z",
  "conversation_id": "unique-id",
  "auth_token": "tok-xxx...",
  "league_id": "league_2025_even_odd"
}
```

### 4.2 Standings Data

```json
{
  "schema_version": "1.0.0",
  "league_id": "league_2025_even_odd",
  "last_updated": "2025-01-15T12:00:00Z",
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
    }
  ]
}
```

### 4.3 Match Result Data

```json
{
  "match_id": "R1M1",
  "round_id": 1,
  "player_a_id": "P01",
  "player_b_id": "P02",
  "result": {
    "winner": "P01",
    "score": {"P01": 3, "P02": 0},
    "details": {
      "drawn_number": 8,
      "choices": {"P01": "even", "P02": "odd"}
    }
  },
  "timestamp": "2025-01-15T10:15:35Z"
}
```

---

## 5. API Interfaces

### 5.1 Internal APIs (MCP Methods)

| Method | Direction | Description |
|--------|-----------|-------------|
| `register_referee` | Referee → LM | Register referee |
| `register_player` | Player → LM | Register player |
| `report_match_result` | Referee → LM | Report result |
| `league_query` | Any → LM | Query standings |
| `handle_game_invitation` | Referee → Player | Invite to game |
| `choose_parity` | Referee → Player | Request choice |
| `notify_match_result` | Referee → Player | Send result |

### 5.2 External APIs (HTTP)

| Endpoint | Agent | Description |
|----------|-------|-------------|
| `GET /health` | All | Health check |
| `GET /status` | All | Agent status |
| `GET /standings` | LM | Get standings |
| `POST /create_schedule` | LM | Create schedule |
| `POST /run_match` | Referee | Run a match |
| `GET /stats` | Player | Get statistics |
| `GET /history` | Player | Get game history |

---

## 6. Architecture Decision Records (ADRs)

### ADR-001: Use FastAPI for HTTP Server

**Status**: Accepted

**Context**: Need an HTTP server for MCP endpoints.

**Decision**: Use FastAPI with Uvicorn.

**Rationale**:
- Native async support
- Pydantic integration for request/response validation
- Automatic OpenAPI documentation
- Excellent performance

**Consequences**:
- Python 3.7+ required
- Learning curve for async patterns

---

### ADR-002: Use JSON-RPC 2.0 for Protocol

**Status**: Accepted

**Context**: Need a standardized RPC format.

**Decision**: Use JSON-RPC 2.0 as specified by MCP.

**Rationale**:
- Industry standard
- Simple request/response format
- Error handling built-in
- Protocol compliance

**Consequences**:
- Single endpoint for all methods
- Method routing logic required

---

### ADR-003: File-Based Persistence

**Status**: Accepted

**Context**: Need to persist standings and match results.

**Decision**: Use JSON files for persistence.

**Decision**: Use JSON files for persistence.

**Rationale**:
- Simple implementation
- Human-readable
- No database dependency
- Sufficient for single-machine deployment

**Consequences**:
- No concurrent write protection
- Limited scalability
- Manual backup required

---

### ADR-004: Single-Process Agents

**Status**: Accepted

**Context**: Each agent type needs to run independently.

**Decision**: Each agent runs as a separate Python process.

**Rationale**:
- Clear separation of concerns
- Independent lifecycle management
- Easy debugging
- Matches real-world distributed systems

**Consequences**:
- Multiple processes to manage
- Need orchestration script
- Higher resource usage

---

### ADR-005: Random as Default Strategy

**Status**: Accepted

**Context**: Player agents need a default decision-making strategy.

**Decision**: Use random choice as default.

**Rationale**:
- Simple to implement
- Unpredictable for opponents
- Fair (50/50 expected outcome)
- Good baseline for strategy comparison

**Consequences**:
- Not optimal strategy
- Provides variety in results

---

## 7. Security Considerations

### 7.1 Authentication
- Auth tokens generated on registration
- Tokens required for all post-registration calls
- Token validation on every request

### 7.2 Input Validation
- All inputs validated via Pydantic
- Parity choice limited to "even"/"odd"
- Timestamps validated as UTC

### 7.3 Threats Mitigated
- Unauthorized game participation (auth tokens)
- Invalid game choices (input validation)
- Message tampering (envelope validation)

### 7.4 Threats Not Addressed
- Denial of service
- Network interception (no TLS)
- Token theft

---

## 8. Operational Considerations

### 8.1 Logging
- All MCP messages logged
- JSON-lines format for parsing
- Separate logs per component
- Log levels: DEBUG, INFO, WARNING, ERROR

### 8.2 Monitoring
- Health endpoints on all agents
- Status endpoints with metrics
- File-based log aggregation

### 8.3 Recovery
- Agents auto-register on startup
- Schedule recreatable from player list
- Standings persist to disk

---

## 9. Trade-offs

| Aspect | Choice | Trade-off |
|--------|--------|-----------|
| Persistence | JSON files | Simple but limited concurrency |
| Transport | HTTP | Standard but no push notifications |
| Strategy | Random default | Fair but not optimal |
| Deployment | Single machine | Simple but not distributed |
| Auth | Simple tokens | Easy but not cryptographically secure |

---

## 10. Future Extensibility

### 10.1 New Game Types
1. Add game logic module in `agents/referee/`
2. Update `games_registry.json`
3. Implement player strategy

### 10.2 Multiple Referees
1. League Manager tracks referee availability
2. Assigns matches based on capacity
3. Referees report back independently

### 10.3 Persistent Database
1. Replace file-based DataLoader
2. Add SQLAlchemy models
3. Configure connection in system.json

### 10.4 Web UI
1. Add WebSocket support for real-time updates
2. Create frontend application
3. Expose REST API for queries
