# Product Requirements Document (PRD)
## AI Agent League System

### Version: 1.0.0
### Last Updated: 2025-01-15

---

## 1. Project Purpose & Motivation

### 1.1 Purpose
Build a multi-agent system where AI agents compete in games using a standardized communication protocol (MCP - Model Context Protocol).

### 1.2 Motivation
- Demonstrate agent-to-agent communication patterns
- Implement a real-world application of JSON-RPC 2.0
- Create an extensible framework for future game types
- Explore autonomous decision-making in competitive environments

### 1.3 Problem Definition
Traditional game implementations are monolithic. This project separates concerns into independent agents that communicate via a standardized protocol, enabling:
- Distributed execution
- Independent agent development
- Protocol-based interoperability

---

## 2. Stakeholders & Personas

### 2.1 Primary Stakeholders
- **Students** - Learning about multi-agent systems
- **Researchers** - Studying agent communication patterns
- **Developers** - Building game-playing agents

### 2.2 Personas

#### Agent Developer
- Wants to implement a player agent
- Needs clear protocol documentation
- Values simple onboarding

#### System Administrator
- Deploys and monitors the league
- Needs health checks and logging
- Wants easy configuration

#### Spectator
- Views standings and match results
- Needs real-time updates
- Values clear presentation

---

## 3. Functional Requirements

### 3.1 User Stories

#### US-001: Agent Registration
As a player agent, I want to register with the league manager so that I can participate in games.

**Acceptance Criteria:**
- Agent sends LEAGUE_REGISTER_REQUEST
- Receives player_id and auth_token
- Can participate in subsequent games

#### US-002: Match Participation
As a player agent, I want to respond to game invitations so that I can compete in matches.

**Acceptance Criteria:**
- Receive GAME_INVITATION from referee
- Respond with GAME_JOIN_ACK
- Receive CHOOSE_PARITY_CALL
- Respond with CHOOSE_PARITY_RESPONSE

#### US-003: Result Notification
As a player agent, I want to receive match results so that I can track my performance.

**Acceptance Criteria:**
- Receive GAME_OVER with result details
- Result includes winner, drawn number, choices
- Can query standings via LEAGUE_QUERY

#### US-004: Round-Robin Scheduling
As the league manager, I want to create a fair schedule so that every player faces every other player.

**Acceptance Criteria:**
- Generate all unique player pairings
- Assign matches to rounds
- Distribute referee assignments

#### US-005: Winner Determination
As the referee, I want to correctly determine match winners so that results are accurate.

**Acceptance Criteria:**
- Collect choices from both players
- Draw random number (1-10)
- Apply Even/Odd rules
- Handle technical losses on timeout

### 3.2 Use Cases

#### UC-001: Complete League Run
1. Start League Manager
2. Start Referee(s)
3. Start Player(s)
4. All agents register
5. League Manager creates schedule
6. For each match:
   - Referee invites players
   - Players join and make choices
   - Referee determines winner
   - Referee reports result
7. League Manager updates standings
8. League ends with champion announcement

### 3.3 System Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| SR-001 | Support 2-100 players | High |
| SR-002 | Handle concurrent matches | Medium |
| SR-003 | Persist standings to disk | High |
| SR-004 | Log all messages | High |
| SR-005 | Auto-recover from agent failures | Low |

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Response time: < 100ms for MCP calls
- Throughput: 10 matches/minute minimum
- Startup time: < 5 seconds per agent

### 4.2 Reliability
- Graceful handling of agent timeouts
- Retry logic with exponential backoff
- No data loss on normal shutdown

### 4.3 Usability
- Single-command league startup
- Clear log messages
- Human-readable standings

### 4.4 Security
- Auth tokens for all post-registration calls
- No hardcoded secrets
- Token validation on every request

### 4.5 Scalability
- Support up to 100 players
- Support multiple referees
- Horizontal scaling via additional instances

---

## 5. Constraints

### 5.1 Technical Constraints
- Python 3.10+ required
- HTTP transport only (no WebSocket)
- Single machine deployment

### 5.2 Protocol Constraints
- Must use JSON-RPC 2.0
- Must follow MCP message envelope
- Timestamps must be UTC

### 5.3 Time Constraints
- 30 second timeout for parity choice
- 5 second timeout for game join
- 10 second timeout for registration

---

## 6. Acceptance Criteria / KPIs

### 6.1 Functional Acceptance
- [ ] All agents register successfully
- [ ] All matches complete without errors
- [ ] Standings are calculated correctly
- [ ] Logs contain all messages

### 6.2 Performance KPIs
| Metric | Target |
|--------|--------|
| Match completion rate | 100% |
| Average match duration | < 5 seconds |
| Message delivery rate | 100% |

### 6.3 Quality KPIs
| Metric | Target |
|--------|--------|
| Test coverage | > 70% |
| Zero critical bugs | Required |
| Documentation complete | Required |

---

## 7. Success Metrics

1. **League Completion**: All scheduled matches complete
2. **Champion Declared**: Final standings show clear winner
3. **Protocol Compliance**: All messages validate against schema
4. **Extensibility**: New game type can be added with minimal changes

---

## 8. In-Scope / Out-of-Scope

### 8.1 In-Scope
- Even/Odd game implementation
- Round-robin tournament format
- 4 players default (configurable)
- JSON-based configuration
- Structured logging

### 8.2 Out-of-Scope
- Web UI
- Database persistence
- Multi-machine deployment
- Real-time spectator updates
- Advanced tournament formats (playoffs, etc.)

---

## 9. Deliverables

1. **Source Code**
   - League Manager agent
   - Referee agent
   - Player agent
   - Shared SDK

2. **Documentation**
   - README.md
   - PRD (this document)
   - Architecture document
   - Protocol specification

3. **Tests**
   - Unit tests for game logic
   - Unit tests for scheduler
   - Unit tests for strategies

4. **Configuration**
   - System configuration
   - Agent configuration
   - League configuration

---

## 10. Timeline & Milestones

| Milestone | Description |
|-----------|-------------|
| M1 | Project structure and SDK |
| M2 | League Manager implementation |
| M3 | Referee implementation |
| M4 | Player implementation |
| M5 | Orchestration scripts |
| M6 | Testing and documentation |

---

## 11. References

- [MCP Specification](https://modelcontextprotocol.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
