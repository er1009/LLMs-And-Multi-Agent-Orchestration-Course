# Architecture Document
## Route Guide System

**Version:** 1.0
**Date:** 2025-11-29
**Status:** Initial Design

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [C4 Model](#2-c4-model)
3. [Technology Stack](#3-technology-stack)
4. [Component Architecture](#4-component-architecture)
5. [Data Models](#5-data-models)
6. [API Interfaces](#6-api-interfaces)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Architecture Decision Records (ADRs)](#8-architecture-decision-records-adrs)
9. [Quality Attributes](#9-quality-attributes)
10. [Trade-offs & Constraints](#10-trade-offs--constraints)

---

## 1. Introduction

### 1.1 Purpose
This document describes the software architecture of the Route Guide System, a multi-agent application that enhances driving routes with contextual content recommendations.

### 1.2 Scope
The architecture covers:
- System context and external dependencies
- Container and component structures
- Data flow and interactions
- Technology choices and justifications
- Key architectural decisions

### 1.3 Architectural Goals
- **Modularity:** Clear separation between agents and core logic
- **Extensibility:** Easy addition of new agent types
- **Maintainability:** Clean interfaces, comprehensive documentation
- **Reliability:** Graceful error handling, fallback mechanisms
- **Testability:** Isolated components, dependency injection

---

## 2. C4 Model

### 2.1 Context Diagram (Level 1)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                          USER                                   │
│                    (Travel Planner)                             │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ Provides source/destination
                 │ Receives enriched route
                 ↓
┌────────────────────────────────────────────────────────────────┐
│                                                                 │
│              ROUTE GUIDE SYSTEM                                 │
│         (Multi-Agent Content Discovery)                         │
│          Uses Claude CLI for all agents                         │
│                                                                 │
└──┬─────────────────────────────────────────────────────────────┬┘
   │                                                              │
   │                                                              │
   ↓                                                              ↓
┌────────────────────┐                              ┌──────────────────┐
│  Google Maps API   │                              │   Claude CLI     │
│  (Route Retrieval) │                              │ (All 4 Agents)   │
│                    │                              │                  │
│  - Directions API  │                              │ - Video Agent    │
│  - Geocoding       │                              │ - Music Agent    │
│                    │                              │ - Info Agent     │
│                    │                              │ - Choice Agent   │
└────────────────────┘                              └──────────────────┘
```

**External Systems:**
- **Google Maps API:** Route and waypoint retrieval only
- **Claude CLI:** All agent logic executed via command-line calls to Claude
  - Video Agent: Finds YouTube video recommendations
  - Music Agent: Finds music/Spotify recommendations
  - Info Agent: Retrieves historical/factual information
  - Choice Agent: Selects best recommendation
- **User:** Provides input and consumes output

---

### 2.2 Container Diagram (Level 2)

```
┌────────────────────────────────────────────────────────────────┐
│                    Route Guide System                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              CLI Application (Python)                    │   │
│  │                                                          │   │
│  │  - Argument parsing                                      │   │
│  │  - User interaction                                      │   │
│  │  - Output formatting                                     │   │
│  └────────────────────┬────────────────────────────────────┘   │
│                       │                                         │
│                       ↓                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Route Guide Orchestrator (Core Logic)            │   │
│  │                                                          │   │
│  │  - Coordinates agent execution                           │   │
│  │  - Manages workflow                                      │   │
│  │  - Error handling & aggregation                          │   │
│  └────┬─────────────────────────────────────────────────┬──┘   │
│       │                                                 │       │
│       ↓                                                 ↓       │
│  ┌─────────────────────────┐       ┌────────────────────────┐  │
│  │   Route Service         │       │   Agent Framework      │  │
│  │                         │       │                        │  │
│  │  - Google Maps API      │       │  - Video Agent         │  │
│  │  - Waypoint extraction  │       │  - Music Agent         │  │
│  │  - Route parsing        │       │  - Info Agent          │  │
│  │                         │       │  - Choice Agent        │  │
│  └─────────────────────────┘       └────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Configuration & Utilities                        │   │
│  │                                                          │   │
│  │  - Config loader                                         │   │
│  │  - API client factory                                    │   │
│  │  - Logging                                               │   │
│  │  - Validators                                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

### 2.3 Component Diagram (Level 3)

```
┌────────────────────────────────────────────────────────────────┐
│                  Agent Framework Components                     │
│                                                                 │
│  ┌──────────────┐                                               │
│  │ Base Agent   │ (Abstract)                                    │
│  │              │                                               │
│  │ + execute()  │                                               │
│  │ + validate() │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│         │ inherits                                              │
│    ┌────┴─────┬────────────┬────────────┐                      │
│    ↓          ↓            ↓            ↓                      │
│  ┌────────┐ ┌────────┐  ┌────────┐  ┌────────┐                │
│  │Video   │ │Music   │  │Info    │  │Choice  │                │
│  │Agent   │ │Agent   │  │Agent   │  │Agent   │                │
│  │        │ │        │  │        │  │        │                │
│  │YouTube │ │Spotify │  │Wiki    │  │Selector│                │
│  │Search  │ │Search  │  │Search  │  │Logic   │                │
│  └────────┘ └────────┘  └────────┘  └────────┘                │
│      │          │            │           │                     │
│      └──────────┴────────────┴───────────┘                     │
│                 │                                               │
│                 ↓                                               │
│         ┌───────────────┐                                       │
│         │ Agent Result  │                                       │
│         │   (Data)      │                                       │
│         └───────────────┘                                       │
└────────────────────────────────────────────────────────────────┘
```

---

### 2.4 Code Diagram (Level 4) - Key Classes

```python
# Core abstractions

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    @abstractmethod
    def execute(self, address: str, context: dict) -> AgentResult

    def validate_result(self, result: AgentResult) -> bool


class AgentResult:
    """Standardized agent output"""
    type: str
    title: str
    content: str
    metadata: dict
    confidence: float


class RouteGuideOrchestrator:
    """Main workflow coordinator"""
    def __init__(self, config: Config)
    def process_route(self, source: str, dest: str) -> RouteOutput
    def _execute_agents_for_waypoint(self, address: str) -> ChoiceResult


class RouteService:
    """Google Maps integration"""
    def get_route(self, source: str, dest: str) -> List[str]
    def extract_waypoints(self, directions: dict) -> List[str]
```

---

## 3. Technology Stack

### 3.1 Core Technologies

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Language | Python | 3.8+ | Rich ecosystem, excellent for API integration, rapid development |
| HTTP Client | requests | 2.31+ | Industry standard, reliable, well-documented |
| Environment | python-dotenv | 1.0+ | Secure environment variable management |
| Testing | pytest | 7.0+ | Powerful, flexible testing framework |
| Code Quality | pylint/black | Latest | Code consistency and quality |

### 3.2 External Dependencies

| Service | Interface | Purpose | Rate Limit |
|---------|-----------|---------|-----------|
| Google Maps | Directions API | Route retrieval | 40,000 req/month (free) |
| Claude | CLI (subprocess) | All agent logic execution | Per user's Claude account |

**Note:** All agent logic (Video, Music, Info, Choice) is executed by calling Claude via CLI with carefully crafted prompts. Each agent constructs a specific prompt and invokes the `claude` command-line tool.

### 3.3 Development Tools

- **Version Control:** Git
- **Package Management:** pip, requirements.txt
- **Documentation:** Markdown, Sphinx (optional)
- **CI/CD:** GitHub Actions (optional)
- **Containerization:** Docker (optional)

---

## 4. Component Architecture

### 4.1 System Layers

```
┌─────────────────────────────────────────────────┐
│         Presentation Layer (CLI)                │
│  - Argument parsing                             │
│  - Output formatting                            │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────↓────────────────────────────────┐
│         Application Layer (Orchestrator)        │
│  - Workflow coordination                        │
│  - Business logic                               │
│  - Error handling                               │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────↓────────────────────────────────┐
│         Domain Layer (Agents & Services)        │
│  - Agent implementations                        │
│  - Route service                                │
│  - Domain models                                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────↓────────────────────────────────┐
│    Infrastructure Layer (API Clients, Utils)    │
│  - HTTP clients                                 │
│  - Configuration                                │
│  - Logging                                      │
└─────────────────────────────────────────────────┘
```

### 4.2 Agent Architecture

**Design Pattern:** Strategy Pattern + Template Method

Each agent implements a common interface but has unique execution logic:

```python
class BaseAgent(ABC):
    """Template method pattern"""

    def execute(self, address: str, context: dict) -> AgentResult:
        # Template method
        self._validate_input(address)
        raw_result = self._search_content(address, context)
        processed_result = self._process_result(raw_result)
        return self._create_agent_result(processed_result)

    @abstractmethod
    def _search_content(self, address: str, context: dict):
        """Strategy - implemented by subclasses"""
        pass
```

### 4.3 Parallel Execution Architecture

**Threading Model:**

The orchestrator uses Python's `ThreadPoolExecutor` to run agents concurrently:

```
Per Waypoint Processing Flow:

Main Thread
    │
    ├─→ Submit 3 tasks to ThreadPoolExecutor
    │   │
    │   ├─→ [Thread-1] Video Agent
    │   │       ├─ Load prompt template
    │   │       ├─ Call Claude CLI (subprocess)
    │   │       ├─ Parse JSON response
    │   │       └─ Return AgentResult
    │   │
    │   ├─→ [Thread-2] Music Agent
    │   │       ├─ Load prompt template
    │   │       ├─ Call Claude CLI (subprocess)
    │   │       ├─ Parse JSON response
    │   │       └─ Return AgentResult
    │   │
    │   └─→ [Thread-3] Info Agent
    │           ├─ Load prompt template
    │           ├─ Call Claude CLI (subprocess)
    │           ├─ Parse JSON response
    │           └─ Return AgentResult
    │
    ├─→ Wait for all threads (as_completed)
    │
    └─→ Choice Agent selects best result
            └─ Return ChoiceResult
```

**Thread Safety:**
- Each agent instance is independent
- No shared mutable state between agents
- Claude client uses subprocess (inherently thread-safe)
- Python logging is thread-safe by default
- Results collected in thread-local dictionaries

**Configuration:**
```yaml
system:
  parallel_execution: true  # Enable/disable
  max_agent_threads: 3      # Thread pool size
```

**Performance Impact:**
- Sequential: ~30 seconds per waypoint (10s × 3 agents)
- Parallel: ~10 seconds per waypoint (max of 3 concurrent calls)
- **3x speedup** for typical routes

### 4.4 Error Handling Strategy

**Layered Error Handling:**

1. **Agent Level:** Try-catch within each agent, return error status
2. **Thread Level:** Catch exceptions in each thread, create error results
3. **Orchestrator Level:** Aggregate errors, decide on continuation
4. **Presentation Level:** Format user-friendly error messages

**Error Categories:**
- **Transient Errors:** Retry with exponential backoff
- **Permanent Errors:** Log and continue with degraded output
- **Critical Errors:** Abort and report to user

**Thread Error Handling:**
- Each thread has try-except wrapper
- Thread failures don't crash main program
- Failed agents return error AgentResult
- Choice agent works even if some agents fail

---

## 5. Data Models

### 5.1 Core Data Structures

```python
# Input
class RouteRequest:
    source_address: str
    destination_address: str
    options: Optional[dict]  # Future: preferences, filters

# Route representation
class Route:
    source: str
    destination: str
    waypoints: List[Waypoint]
    metadata: dict

class Waypoint:
    address: str
    location: Location  # lat, lng
    index: int

# Agent outputs
class AgentResult:
    agent_type: str  # 'video', 'music', 'info'
    title: str
    content: str  # URL or text
    metadata: dict
    confidence: float
    timestamp: str

# Final recommendation
class ChoiceResult:
    selected_type: str
    title: str
    content: str
    reason: str
    alternatives: List[AgentResult]  # Not shown to user, for logging

# Complete output
class RouteGuideOutput:
    source: str
    destination: str
    stops: List[Stop]
    metadata: dict

class Stop:
    address: str
    choice: ChoiceResult
```

### 5.2 Configuration Schema

```yaml
# config/config.yaml
api:
  google_maps:
    timeout: 10
    max_retries: 3
  youtube:
    timeout: 8
    max_results: 5
  spotify:
    timeout: 8
    max_results: 5

agents:
  video:
    enabled: true
    weight: 1.0
  music:
    enabled: true
    weight: 1.0
  info:
    enabled: true
    weight: 1.2  # Prefer educational content

system:
  max_waypoints: 50
  parallel_execution: false  # Future enhancement
  log_level: INFO
```

---

## 6. API Interfaces

### 6.1 External API Integration

#### Google Maps Directions API
```
Endpoint: https://maps.googleapis.com/maps/api/directions/json
Method: GET
Parameters:
  - origin: source address
  - destination: destination address
  - key: API key
  - mode: driving
Response: Route with steps, waypoints, geometry
```

#### YouTube Data API
```
Endpoint: https://www.googleapis.com/youtube/v3/search
Method: GET
Parameters:
  - q: search query (address + context)
  - type: video
  - key: API key
  - maxResults: 5
Response: Video list with IDs, titles, descriptions
```

#### Spotify Web API
```
Endpoint: https://api.spotify.com/v1/search
Method: GET
Headers:
  - Authorization: Bearer {token}
Parameters:
  - q: search query
  - type: track
  - limit: 5
Response: Track list with IDs, names, URIs
```

### 6.2 Internal Interfaces

```python
# Route Service Interface
class IRouteService(Protocol):
    def get_route(self, source: str, destination: str) -> Route:
        """Retrieve route with waypoints"""
        ...

# Agent Interface
class IAgent(Protocol):
    def execute(self, address: str, context: dict) -> AgentResult:
        """Execute agent logic for given address"""
        ...

    def get_type(self) -> str:
        """Return agent type identifier"""
        ...

# Choice Agent Interface
class IChoiceAgent(Protocol):
    def select_best(
        self,
        video: AgentResult,
        music: AgentResult,
        info: AgentResult
    ) -> ChoiceResult:
        """Select best content from agent results"""
        ...
```

---

## 7. Deployment Architecture

### 7.1 Deployment Options

**Option 1: Local Command-Line Tool (MVP)**
```
┌────────────────────────────────────┐
│     User's Local Machine           │
│                                    │
│  ┌──────────────────────────────┐  │
│  │  Python 3.8+ Runtime         │  │
│  │                              │  │
│  │  Route Guide Application     │  │
│  │  (CLI)                       │  │
│  └──────────────────────────────┘  │
│                                    │
└────────────────────────────────────┘
         │
         │ HTTPS
         ↓
┌────────────────────────────────────┐
│   External APIs (Cloud)            │
│  - Google Maps                     │
│  - YouTube                         │
│  - Spotify                         │
└────────────────────────────────────┘
```

**Option 2: Docker Container (Future)**
```
┌────────────────────────────────────┐
│  Docker Container                  │
│                                    │
│  ┌──────────────────────────────┐  │
│  │ Python 3.8 Alpine Image      │  │
│  │                              │  │
│  │ + Application Code           │  │
│  │ + Dependencies               │  │
│  │ + Config (env vars)          │  │
│  └──────────────────────────────┘  │
└────────────────────────────────────┘
```

### 7.2 Operational Considerations

**Environment Setup:**
- Python virtual environment (venv)
- API keys via environment variables (.env file)
- Configuration file (config.yaml)

**Logging:**
- Log level configurable (DEBUG, INFO, WARNING, ERROR)
- Logs to stdout/stderr
- Structured logging with timestamps
- Sensitive data redaction (API keys, tokens)

**Monitoring:**
- API call tracking (count, latency)
- Error rate monitoring
- Agent success/failure rates

**Security:**
- API keys stored in .env (gitignored)
- No hardcoded credentials
- HTTPS for all external calls
- Input sanitization

---

## 8. Architecture Decision Records (ADRs)

### ADR-001: Parallel Agent Execution Using Threads

**Date:** 2025-11-29
**Status:** Accepted

**Context:**
For each waypoint, three content agents (Video, Music, Info) need to execute. These can run sequentially or in parallel.

**Decision:**
Implement parallel agent execution using Python threading (ThreadPoolExecutor).

**Rationale:**
- **Significant performance improvement:** Reduces per-waypoint time from ~30s to ~10s (3x faster)
- **Independent operations:** Agents don't depend on each other's results
- **I/O-bound tasks:** All agents wait on Claude CLI subprocess calls - ideal for threading
- **Simple concurrency model:** Python's ThreadPoolExecutor provides clean, safe thread management
- **Resource efficient:** Threads share memory, minimal overhead compared to processes
- **Configurable:** Can be disabled for debugging or environments where threading is problematic

**Implementation:**
- Use `concurrent.futures.ThreadPoolExecutor` with max 3 workers (one per agent)
- Each agent runs in its own thread
- Main thread waits for all three to complete using `as_completed()`
- Results collected and passed to Choice Agent
- Comprehensive error handling per thread

**Threading Safety:**
- Agents are designed to be independent and thread-safe
- Each agent has its own Claude client instance (subprocess calls are thread-safe)
- No shared mutable state between agents
- Logging is thread-safe in Python

**Consequences:**
- ✅ 3x faster processing time (~10s vs ~30s per waypoint)
- ✅ Better resource utilization during I/O waits
- ✅ Maintains individual agent error handling
- ⚠️ Slightly more complex error handling (per-thread exceptions)
- ⚠️ Requires thread-safe logging and error handling
- ⚠️ Can be disabled via configuration if issues arise

---

### ADR-002: Agent Selection Strategy

**Date:** 2025-11-29
**Status:** Accepted

**Context:**
Choice Agent needs a strategy to select best content from three options.

**Decision:**
Use rule-based scoring system with configurable weights.

**Rationale:**
- Transparent and explainable decisions
- No ML training required
- Configurable for different user preferences
- Adequate for MVP

**Scoring Criteria:**
- Relevance to location (keyword matching)
- Content quality indicators (views, ratings)
- Content freshness
- Content type preference weights

**Consequences:**
- May not be optimal for all scenarios
- Future enhancement: ML-based personalization

---

### ADR-003: Using Claude CLI for Agent Implementation

**Date:** 2025-11-29
**Status:** Accepted

**Context:**
Agents need to discover and recommend content (videos, music, information). Options included:
1. Direct API calls to YouTube, Spotify, Wikipedia APIs
2. Using Claude CLI to handle all agent logic
3. Hybrid approach

**Decision:**
Implement all agents using Claude CLI calls via subprocess.

**Rationale:**
- Leverages Claude's knowledge and reasoning for content discovery
- No need to manage multiple API keys and rate limits (YouTube, Spotify, etc.)
- Claude can provide contextual, relevant recommendations
- Simpler architecture with single external dependency (Claude + Google Maps)
- Claude can explain reasoning for recommendations
- More flexible - Claude can adapt search strategies
- Better alignment with educational/research context

**Implementation:**
- Each agent constructs a specific prompt for Claude
- Use subprocess to call `claude` CLI command
- Parse Claude's response to extract recommendations
- Handle Claude CLI errors gracefully

**Consequences:**
- Dependency on Claude CLI availability and user's Claude account
- Processing time depends on Claude response time
- Need to carefully craft prompts for each agent type
- Simpler than managing multiple API integrations
- May have cost implications depending on Claude usage limits

---

### ADR-004: Python as Implementation Language

**Date:** 2025-11-29
**Status:** Accepted

**Context:**
Choice between Python, JavaScript/Node.js, Java, Go.

**Decision:**
Use Python 3.8+

**Rationale:**
- Excellent API integration libraries (requests)
- Rapid development and prototyping
- Rich ecosystem for data processing
- Academic/research context familiarity
- Good testing frameworks (pytest)

**Consequences:**
- Slower execution than compiled languages (acceptable for I/O-bound tasks)
- Requires Python runtime
- Excellent for MVP, may consider Go for production scaling

---

### ADR-005: Configuration Management

**Date:** 2025-11-29
**Status:** Accepted

**Context:**
Need secure, flexible configuration for API keys and parameters.

**Decision:**
Use combination of .env files (secrets) and YAML files (configuration).

**Rationale:**
- .env is standard for secrets management
- YAML is human-readable for configurations
- Clear separation between secrets and settings
- Easy to gitignore .env while versioning config.yaml

**Consequences:**
- Users must create .env from example
- Two configuration sources to maintain

---

### ADR-006: Waypoint Extraction from Google Maps

**Date:** 2025-11-29
**Status:** Accepted

**Context:**
Google Maps returns detailed step-by-step directions. Need to decide which points become waypoints.

**Decision:**
Extract waypoints at:
1. Major junctions (highway exits, merges)
2. Significant maneuvers (turns on major roads)
3. City/town entries
4. Limit to max 20 waypoints per route

**Rationale:**
- Balance between detail and processing time
- Focus on significant locations
- Avoid overwhelming user with content

**Consequences:**
- Some interesting locations may be skipped
- Heuristic-based extraction may need tuning

---

### ADR-007: Error Handling Philosophy

**Date:** 2025-11-29
**Status:** Accepted

**Context:**
External APIs may fail, agents may return no results.

**Decision:**
Implement graceful degradation - continue processing even if individual agents fail.

**Rationale:**
- Partial results better than no results
- Transient failures shouldn't abort entire route
- User gets maximum available information

**Strategy:**
- If agent fails: log error, return "No content found" result
- If all agents fail for a waypoint: include waypoint with no recommendation
- If route retrieval fails: abort (critical failure)

**Consequences:**
- More complex error handling logic
- Better user experience
- Need clear communication about missing content

---

### ADR-008: Output Format

**Date:** 2025-11-29
**Status:** Accepted

**Context:**
Need to decide output format (JSON, XML, plain text, interactive).

**Decision:**
Primary output: JSON
Secondary: Human-readable formatted text

**Rationale:**
- JSON is machine-readable, enables integration
- Structured format matches specification
- Easy to validate against schema
- Can be consumed by future UI/mobile app

**Consequences:**
- Need JSON formatter for CLI output
- Consider adding pretty-print option for humans

---

## 9. Quality Attributes

### 9.1 ISO 25010 Mapping

| Quality Attribute | Architecture Support |
|------------------|---------------------|
| **Functional Suitability** | Complete implementation of all required agents and route processing |
| **Performance Efficiency** | Async-ready architecture, configurable timeouts, caching capability |
| **Compatibility** | Standard JSON output, RESTful API integration, cross-platform Python |
| **Usability** | Clear CLI interface, comprehensive error messages, documentation |
| **Reliability** | Retry logic, graceful degradation, error handling at all levels |
| **Security** | Environment variable secrets, input validation, HTTPS-only APIs |
| **Maintainability** | Modular design, clear interfaces, comprehensive tests, documentation |
| **Portability** | Python 3.8+ compatibility, minimal dependencies, containerizable |

### 9.2 Design Principles Applied

1. **Single Responsibility:** Each agent handles one content type
2. **Open/Closed:** Easy to add new agents without modifying core
3. **Dependency Inversion:** Orchestrator depends on agent abstractions
4. **Interface Segregation:** Minimal, focused interfaces
5. **DRY:** Shared utilities, base agent class
6. **KISS:** Simple, straightforward implementation

---

## 10. Trade-offs & Constraints

### 10.1 Key Trade-offs

| Decision | Trade-off | Chosen Direction | Rationale |
|----------|-----------|------------------|-----------|
| Sequential vs Parallel | Speed vs Complexity | Sequential | Simpler MVP, easier debugging |
| Rule-based vs ML Selection | Simplicity vs Accuracy | Rule-based | Transparent, no training needed |
| Monolith vs Microservices | Simplicity vs Scalability | Monolith | Appropriate for MVP scale |
| Sync vs Async | Simplicity vs Performance | Sync | Adequate for MVP, easier to implement |
| Local vs Cloud | Deployment vs Cost | Local | Academic project, no hosting costs |

### 10.2 Technical Constraints

- **API Rate Limits:** Must implement throttling and respect quotas
- **Internet Dependency:** No offline mode in MVP
- **Processing Time:** 30-60 seconds for typical routes (acceptable for MVP)
- **Language Support:** English only for MVP
- **Platform:** Requires Python 3.8+ runtime

### 10.3 Future Enhancements

1. **Parallel agent execution** for improved performance
2. **Caching layer** for repeated routes/locations
3. **ML-based content selection** for personalization
4. **Web API** for remote access
5. **Mobile application** with real-time navigation
6. **User preference learning** and recommendations
7. **Multi-language support**
8. **Offline mode** with pre-cached content

---

## 11. Security Considerations

### 11.1 Threat Model

| Threat | Mitigation |
|--------|-----------|
| API key exposure | Store in .env, gitignore, environment variables only |
| Injection attacks | Input validation, parameterized API calls |
| Data leakage | No logging of sensitive data, redact API keys in logs |
| API abuse | Rate limiting, request throttling |
| Dependency vulnerabilities | Regular updates, security scanning |

### 11.2 Security Best Practices

- Use HTTPS for all external API calls
- Validate and sanitize all user inputs
- Follow principle of least privilege for API access
- No storage of user data (stateless)
- Security-focused code reviews

---

## 12. Testing Strategy

### 12.1 Test Architecture

```
tests/
├── unit/
│   ├── test_agents/
│   │   ├── test_video_agent.py
│   │   ├── test_music_agent.py
│   │   ├── test_info_agent.py
│   │   └── test_choice_agent.py
│   ├── test_route_service.py
│   ├── test_orchestrator.py
│   └── test_utils/
├── integration/
│   ├── test_api_integration.py
│   └── test_end_to_end.py
└── fixtures/
    ├── mock_api_responses.json
    └── test_routes.json
```

### 12.2 Testing Approach

- **Unit Tests:** 70%+ coverage, mock external APIs
- **Integration Tests:** Test with real APIs (limited)
- **Contract Tests:** Validate API response schemas
- **Error Tests:** Test failure scenarios and recovery

---

## 13. Appendix

### 13.1 Glossary

- **Waypoint:** A significant location along the route
- **Agent:** A specialized module for content discovery
- **Orchestrator:** Main coordinator of agent execution
- **Choice Agent:** Meta-agent that selects best recommendation

### 13.2 References

- Google Maps Platform: https://developers.google.com/maps
- C4 Model: https://c4model.com/
- ISO/IEC 25010: Software Quality Model
- Clean Architecture (Robert C. Martin)
- Design Patterns (Gang of Four)

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-29 | Architecture Team | Initial architecture document |

---

**Document Approval:**
- Technical Lead: [Pending]
- Senior Architect: [Pending]
- Security Review: [Pending]
