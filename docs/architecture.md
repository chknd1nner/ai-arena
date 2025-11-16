# AI Arena: 1v1 Space Duel - Architecture Document

**Version:** 1.0  
**Date:** 2025-11-13  
**Author:** Architecture Workflow  
**Status:** Ready for Implementation

---

## Executive Summary

AI Arena is a 1v1 space combat simulation where two large language models pilot starships in real-time tactical battles. The architecture is designed as a **modular monolith** with clear boundaries that enable future extraction to microservices. The system prioritizes **deterministic physics** for reliable replay, **clean separation of concerns** for maintainability, and **LLM provider flexibility** through unified API abstraction.

**Key Architectural Decisions:**
- Modular monolith architecture with interface-based component boundaries
- Python game engine with fixed-timestep physics (10 Hz) for determinism
- LiteLLM for unified multi-provider LLM integration
- FastAPI web server with React + Canvas 2D visualization
- JSON-based replay system for complete match reproduction

**Technology Stack:**
- Game Engine: Python 3.11+ with NumPy
- LLM Integration: LiteLLM
- Web Framework: FastAPI 0.100+
- Frontend: React 18 + Canvas 2D API
- Deployment: Local-first, cloud-ready

---

## Table of Contents

1. [System Context](#system-context)
2. [Architectural Drivers](#architectural-drivers)
3. [Architecture Overview](#architecture-overview)
4. [Component Architecture](#component-architecture)
5. [Data Architecture](#data-architecture)
6. [API Design](#api-design)
7. [Deployment Architecture](#deployment-architecture)
8. [Implementation Patterns](#implementation-patterns)
9. [Architecture Decision Records](#architecture-decision-records)
10. [Risks & Mitigation](#risks--mitigation)

---

## System Context

### Problem Statement

Create an entertaining AI benchmark where two LLMs pilot starships in simultaneous 1v1 combat, producing watchable AI competition with transparent reasoning (thinking tokens) visible to spectators. The system must be deterministic for reliable replay and flexible enough to support multiple LLM providers.

### Scope

**In Scope:**
- Single match orchestration (MVP)
- Python game engine with custom 2D physics
- LLM integration supporting multiple providers (Claude, GPT-4, Grok, etc.)
- Web-based visualization with React + Canvas
- Complete match recording and replay system
- Thinking token display for spectators

**Out of Scope (Future Phases):**
- Tournament mode with multiple matches
- Live streaming integration with WebSocket
- Multi-user spectating
- Advanced analytics and statistics
- Mobile applications

### Stakeholders

| Stakeholder | Role | Concerns |
|-------------|------|----------|
| Developer (You) | Creator | Maintainability, extensibility, clean architecture |
| AI Enthusiasts | Audience | Entertainment value, understanding AI decisions |
| Content Creators | Streamers | Watchability, spectator features |

### Success Criteria

1. Match runs start-to-finish without crashes
2. Physics is deterministic (same inputs → same outputs)
3. Match is fully reproducible from JSON replay
4. Orders parse correctly and reflect sensible AI decisions
5. At least one moment per match feels genuinely surprising
6. Spectator can watch and understand what happened

### Constraints

- **Technology preference:** Python for game engine
- **LLM flexibility:** Must support multiple providers without code changes
- **Entertainment focus:** Thinking tokens must be visible
- **Timeline:** No rush, personal side project
- **Deployment:** Local-first, then cloud

### Assumptions

- LLM API calls are the primary bottleneck (1-3 seconds per turn)
- Physics simulation is lightweight (<10ms per turn)
- Matches will be 10-30 turns typically
- Users have modern browsers (ES6+, Canvas API support)

---

## Architectural Drivers

### Quality Attributes (Prioritized)

#### 1. Maintainability ⭐⭐⭐ (Critical)
- **Target:** Clean separation allows independent evolution of components
- **Importance:** Critical
- **Rationale:** As a side project, you want to iterate quickly without creating technical debt
- **Implementation:** 
  - Interface-based component boundaries
  - Modular monolith with extraction-ready design
  - Clear ownership of concerns

#### 2. Determinism/Reproducibility ⭐⭐⭐ (Critical)
- **Target:** Same inputs → same outputs, every time
- **Importance:** Critical
- **Rationale:** Physics must be 100% deterministic for replay system and debugging
- **Implementation:**
  - Fixed timestep physics (10 Hz)
  - Pure functions for game engine
  - Avoid floating point non-determinism

#### 3. Testability ⭐⭐⭐ (Critical)
- **Target:** Each component can be tested independently
- **Importance:** Critical
- **Rationale:** Complex game logic (movement, weapons, collisions, AE economy) needs confidence
- **Implementation:**
  - Stateless components where possible
  - Dependency injection
  - Mock-friendly interfaces

### Business Drivers

- **Entertainment value:** Spectators must find matches engaging
- **AI transparency:** Thinking tokens provide insight into AI decision-making
- **Flexibility:** Support multiple LLM providers for competition/comparison
- **Iteration speed:** Architecture should not slow down feature development

### Technical Constraints

- **Python required:** Game engine must be Python (your preference, good for math)
- **Multiple LLM providers:** Cannot be locked to one provider
- **Browser-based visualization:** Must work in modern web browsers
- **JSON serialization:** All game state must be serializable for replay

---

## Architecture Overview

### Architecture Style

**Chosen Style:** Modular Monolith

**Rationale:**

The modular monolith approach is optimal for the MVP phase because:

1. **Simplicity:** Single codebase, easier to develop and debug
2. **Clear boundaries:** Module interfaces designed for future extraction
3. **Fast iteration:** No network overhead, simpler deployment
4. **Extraction-ready:** Components communicate through interfaces that can become HTTP/RPC

Alternative considered:
- **Microservices:** Too much operational complexity for MVP; no scaling needs yet
- **Pure monolith:** Would create coupling issues and make future extraction harder

The architecture is designed with **interface contracts** so components can be extracted to separate services without rewriting logic. Each module has:
- Clear input/output contracts
- No shared mutable state
- Communication via message passing (even if local function calls initially)

### High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────┐
│         Match Orchestrator (Coordinator)          │
│  - Turn loop management                           │
│  - Win condition detection                        │
│  - Component coordination                         │
└─────┬────────────┬──────────────┬────────────────┘
      │            │              │
      │ (1)        │ (2)          │ (3)
      ▼            ▼              ▼
┌────────────┐ ┌──────────┐ ┌──────────────┐
│    LLM     │ │   Game   │ │    Replay    │
│  Adapter   │ │  Engine  │ │    System    │
│            │ │          │ │              │
│  LiteLLM   │ │ Physics  │ │ JSON Writer  │
└────────────┘ └──────────┘ └──────┬───────┘
                                   │ (4)
                                   ▼
                            ┌──────────────┐
                            │  Web Server  │
                            │   FastAPI    │
                            └──────┬───────┘
                                   │ (5)
                                   ▼
                            ┌──────────────┐
                            │    React     │
                            │   Frontend   │
                            │  Canvas 2D   │
                            └──────────────┘
```

### Key Architectural Patterns

1. **Interface Segregation** - Components communicate through well-defined interfaces
2. **Pure Functions** - Game engine is stateless (state + orders → new state)
3. **Dependency Injection** - Components receive dependencies, making them swappable
4. **Fixed Timestep** - Guarantees deterministic physics simulation
5. **Event Sourcing (Light)** - Record all events for replay without re-simulation

### Technology Stack Summary

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Game Engine | Python | 3.11+ | Great for math/logic, your preference, clean syntax |
| Vector Math | NumPy | Latest | Fast vector operations, no heavy physics engine needed |
| LLM Integration | LiteLLM | Latest | Unified API for 100+ LLM providers, handles fallbacks |
| Web Framework | FastAPI | 0.100+ | Modern, async, excellent docs, WebSocket support for Phase 3 |
| Frontend | React | 18.x | Component-based UI, excellent Canvas integration patterns |
| Visualization | Canvas 2D | Native | Perfect for 2D rendering, no WebGL complexity needed |
| Serialization | JSON | Native | Human-readable, excellent tooling, works everywhere |

---

## Component Architecture

### Component Overview

The system consists of six major components:

1. **Match Orchestrator** - Coordinates the match lifecycle
2. **Game Engine** - Physics simulation and rule enforcement
3. **LLM Adapter** - LLM provider abstraction
4. **Replay System** - Match recording and replay loading
5. **Web Server** - API and static file serving
6. **React Frontend** - Visualization and UI

```
Component Dependencies (arrows = depends on):

Match Orchestrator
    ├─> LLM Adapter
    ├─> Game Engine
    └─> Replay System

Web Server
    └─> Replay System

React Frontend
    └─> Web Server (HTTP)
```

---

### Component 1: Match Orchestrator

**Purpose:** Coordinates the entire match lifecycle from initialization to completion

**Responsibilities:**
- Initialize match with starting positions
- Execute turn loop (get orders → resolve physics → record state)
- Coordinate between LLM Adapter and Game Engine
- Detect win conditions
- Trigger replay recording

**Technology:** Python class

**Interfaces:**

Input:
```python
class MatchConfig:
    model_a: str  # "anthropic/claude-sonnet-4"
    model_b: str  # "openai/gpt-4"
    max_turns: int = 50
    initial_ae: int = 100
    initial_shields: int = 100
```

Output:
```python
class MatchResult:
    match_id: str
    winner: str  # "ship_a", "ship_b", or "tie"
    total_turns: int
    replay_path: str
    final_state: GameState
```

**Key Methods:**
```python
async def run_match(config: MatchConfig) -> MatchResult
def _initialize_match() -> GameState
def _check_win_condition(state: GameState) -> Optional[str]
```

**Scaling Strategy:** 
- Stateless - can run multiple matches in parallel
- Each match is independent
- Future: Extract to "Match Scheduler" microservice

**Interface Contract (for future extraction):**
```python
class IMatchOrchestrator(Protocol):
    async def run_match(self, config: MatchConfig) -> MatchResult:
        """Run a complete match and return results."""
        pass
```

---

### Component 2: Game Engine

**Purpose:** Pure physics simulation and game rule enforcement

**Responsibilities:**
- Resolve 15-second action phases with a fixed timestep (continuous real-time simulation)
- Movement physics (ships and torpedoes) based on independent direction and rotation
- Collision detection (torpedoes hitting ships, blast zones)
- Weapon mechanics (continuous phaser firing, torpedo detonation)
- AE economy calculations (continuous resource burn/regeneration)
- Deterministic behavior (same input = same output, always)

**Technology:** Python with NumPy for vector math

**Interfaces:**

Input:
```python
@dataclass
class GameState:
    turn: int
    ship_a: ShipState
    ship_b: ShipState
    torpedoes: List[TorpedoState]

@dataclass
class TorpedoAction:
    torpedo_id: str
    # e.g., "hard_left", "detonate_after:5.2"
    action: str

@dataclass
class Orders:
    # e.g., "forward", "backward_left"
    ship_movement: str
    # e.g., "none", "hard_left"
    ship_rotation: str
    # e.g., "reconfigure_to_focused", "no_change"
    phaser_action: str
    # Orders for existing torpedoes
    torpedo_actions: List[TorpedoAction]
    # Whether to launch a new torpedo this turn
    launch_torpedo: bool
```

Output:
```python
Tuple[GameState, List[Event]]
# Returns: (new_state, events)
```

**Core Function:**
```python
def resolve_turn(
    state: GameState, 
    orders_a: Orders, 
    orders_b: Orders
) -> Tuple[GameState, List[Event]]:
    """
    Pure function: takes current state and orders,
    returns new state and events.
    No side effects.
    """
    pass
```

**Physics Constants:**
```python
FIXED_TIMESTEP = 0.1  # 10 Hz
ACTION_PHASE_DURATION = 15.0  # seconds
SUBSTEPS = 150  # 15 seconds / 0.1s timestep

SHIP_SPEED = 3.0  # units/second
TORPEDO_SPEED = 4.0  # units/second

# Phaser Configuration (from config.json)
PHASER_WIDE_ARC = 90.0  # degrees
PHASER_WIDE_RANGE = 30.0  # units
PHASER_WIDE_DAMAGE = 15.0
PHASER_WIDE_COOLDOWN = 3.5  # seconds between shots

PHASER_FOCUSED_ARC = 10.0  # degrees
PHASER_FOCUSED_RANGE = 50.0  # units
PHASER_FOCUSED_DAMAGE = 35.0
PHASER_FOCUSED_COOLDOWN = 3.5  # seconds between shots

PHASER_RECONFIGURATION_TIME = 15.0  # seconds (blocks firing)

# Energy Economy (continuous)
AE_REGEN_PER_SECOND = 0.333  # 5.0 AE per 15s turn
MAX_AE = 100.0
MOVEMENT_COSTS = {  # AE per second
    "FORWARD": 0.33,
    "DIAGONAL": 0.53,
    "PERPENDICULAR": 0.67,
    "BACKWARD": 0.67,
    "BACKWARD_DIAGONAL": 0.80,
    "STOP": 0.0
}
ROTATION_COSTS = {  # AE per second
    "NONE": 0.0,
    "SOFT_TURN": 0.13,
    "HARD_TURN": 0.33
}

TORPEDO_BLAST_RADIUS = 15.0
```

**Continuous Physics System (Epic 004):**

The game uses a **continuous physics model** with per-substep updates:

1. **Phaser Cooldown (3.5s)**
   - Phasers fire automatically when enemy enters arc
   - Cooldown timer decrements each substep (0.1s)
   - Ships can fire ~4 times per 15s decision interval if continuously in arc
   - Reconfiguring phaser blocks firing for 15 seconds (1 full turn)
   - Cooldown prevents overwhelming damage spam

2. **Continuous AE Economy**
   - Energy regenerates every substep: +0.333 AE/s
   - Movement costs applied per substep based on movement type
   - Rotation costs applied per substep based on rotation rate
   - Forward movement (0.33 AE/s) nearly balances regeneration (0.333 AE/s)
   - Aggressive maneuvering depletes energy, forcing strategic decisions
   - Ships manage energy continuously, not per-turn

3. **Energy Management Patterns**
   - Aggressive play: 45-85 AE fluctuation (observed in testing)
   - Conservative play: 70-95 AE range
   - Energy depletion risk exists for overly aggressive tactics
   - Torpedo launches (20 AE) are significant energy investments

**Scaling Strategy:**
- Completely stateless
- Pure function - perfect for extraction
- Could become "Physics Service" with HTTP endpoint: `POST /resolve-turn`

**Critical Design Notes:**
- Combat style emerges naturally from weapon ranges and continuous physics.
- All floating point operations use consistent precision.
- Fixed timestep prevents non-determinism.
- No randomness anywhere in engine.
- **Phaser cooldown enforced at substep level** - prevents multiple shots per substep.
- **Energy economy calculated per substep** - smooth, continuous resource management.

---

### Component 3: LLM Adapter

**Purpose:** Abstract away LLM provider complexity and manage prompts/responses

**Responsibilities:**
- Construct prompts from game state
- Call LiteLLM with correct model string
- Parse responses into structured `Orders` objects
- Extract thinking tokens for display
- Handle timeouts, retries, and errors
- Support multiple providers (Claude, GPT-4, Grok, etc.)

**Technology:** Python with LiteLLM library

**Interfaces:**

Input:
```python
GameState + model configuration
```

Output:
```python
Tuple[Orders, str, Orders, str]
# (orders_a, thinking_a, orders_b, thinking_b)
```

**Key Methods:**
```python
async def get_orders_for_both_ships(
    state: GameState
) -> Tuple[Orders, str, Orders, str]:
    """Get orders from both models in parallel."""
    pass

async def _get_orders_for_ship(
    state: GameState, 
    ship_id: str, 
    model: str
) -> Tuple[Orders, str]:
    """Get orders from single model."""
    pass
```

**Prompt Structure:**
- System prompt: Game rules, weapon mechanics, response format
- User prompt: Current state (positions, shields, AE, torpedoes)
- Response format: JSON with thinking, movement, weapon, torpedo controls

**Error Handling:**
- LLM timeout: Return safe default orders (STOP movement)
- Parse error: Return safe default orders
- API error: Log and return defaults
- Invalid orders: Validate and default to legal alternatives

**Scaling Strategy:**
- Async calls to both models (parallel)
- Could add caching layer for similar states
- Future: Extract to "LLM Gateway" microservice with rate limiting

**Interface Contract:**
```python
class ILLMAdapter(Protocol):
    async def get_orders_for_both_ships(
        self, 
        state: GameState
    ) -> Tuple[Orders, str, Orders, str]:
        pass
```

---

### Component 4: Replay System

**Purpose:** Record and reload complete match state

**Responsibilities:**
- Save every turn's state to JSON file
- Record events (hits, detonations, phase changes)
- Store thinking tokens for each ship
- Load replay files for visualization
- Provide deterministic replay (no re-simulation)

**Technology:** Python JSON serialization

**Interfaces:**

Recording:
```python
def record_turn(
    turn: int,
    state: GameState,
    orders_a: Orders,
    orders_b: Orders,
    thinking_a: str,
    thinking_b: str,
    events: List[Event]
) -> None
```

Loading:
```python
def load_replay(match_id: str) -> ReplayData
```

**Data Format:**
```json
{
  "match_id": "claude_vs_gpt_2025_11_13_001",
  "models": {
    "ship_a": "anthropic/claude-sonnet-4",
    "ship_b": "openai/gpt-4"
  },
  "winner": "ship_a",
  "total_turns": 18,
  "turns": [
    {
      "turn": 1,
      "state": {
        "ship_a": {
          "position": [100.0, 250.0],
          "velocity": [10.0, 0.0],
          "heading": 0.0,
          "shields": 100,
          "ae": 95,
          "phaser_config": "wide",
          "reconfiguring_phaser": false
        },
        "ship_b": { ... },
        "torpedoes": [
          {
            "id": "ship_a_torpedo_1",
            "position": [120.0, 250.0],
            "velocity": [15.0, 0.0],
            "heading": 0.0,
            "ae_remaining": 38,
            "owner": "ship_a"
          }
        ]
      },
      "orders_a": {
        "ship_movement": "forward",
        "ship_rotation": "none",
        "phaser_action": "no_change",
        "launch_torpedo": true,
        "torpedo_actions": []
      },
      "orders_b": { ... },
      "thinking_a": "Enemy is northeast. I'll launch torpedo...",
      "thinking_b": "I see incoming threat. Will evade...",
      "events": [
        {
          "type": "torpedo_launched",
          "data": {
            "ship": "ship_a",
            "torpedo_id": "ship_a_torpedo_1"
          }
        }
      ]
    },
    { ... turn 2 ... }
  ]
}
```

**Scaling Strategy:**
- Filesystem storage for MVP
- Future: S3/cloud storage for Phase 2+
- Compression (gzip) for large replays
- Indexing for fast match queries

---

### Component 5: Web Server

**Purpose:** Serve React app and provide match data API

**Responsibilities:**
- Serve static React frontend
- Provide REST API for match data
- Replay endpoint for loading matches
- Health check endpoints
- (Future) WebSocket for live match streaming

**Technology:** FastAPI (Python)

**Endpoints:**

```python
# Match Management
POST   /api/match/start          # Start new match
GET    /api/match/{id}           # Get match status
GET    /api/matches              # List available matches

# Replay
GET    /api/match/{id}/replay    # Get full replay JSON

# Health
GET    /health                   # Health check

# Future: Live Streaming
WS     /api/match/{id}/live      # WebSocket live updates
```

**Example Responses:**

Start Match:
```json
POST /api/match/start
{
  "model_a": "anthropic/claude-sonnet-4",
  "model_b": "openai/gpt-4",
  "max_turns": 50
}

Response 202 Accepted:
{
  "match_id": "claude_vs_gpt_2025_11_13_001",
  "status": "running"
}
```

Get Replay:
```json
GET /api/match/claude_vs_gpt_2025_11_13_001/replay

Response 200 OK:
{
  "match_id": "...",
  "models": {...},
  "turns": [...]
}
```

**Scaling Strategy:**
- Stateless API server
- Can run multiple instances behind load balancer
- Static files served via CDN in production

---

### Component 6: React Frontend

**Purpose:** Visualize matches and display thinking tokens

**Responsibilities:**
- Render 2D canvas with ships, torpedoes, phasers
- Display thinking tokens side-by-side
- Replay controls (play/pause, scrub, speed)
- Camera controls (zoom, follow)
- Match selection UI

**Technology:** React 18 + Canvas 2D API

**Component Structure:**
```
src/
  components/
    GameCanvas.jsx          # Main canvas renderer
    ThinkingPanel.jsx       # Display LLM reasoning
    ReplayControls.jsx      # Timeline, play/pause
    MatchList.jsx           # Browse available matches
    ShipSprite.jsx          # Ship rendering logic
    TorpedoSprite.jsx       # Torpedo rendering
  hooks/
    useGameState.js         # Load replay JSON
    useCanvas.js            # Canvas animation loop
    usePlayback.js          # Playback control logic
  utils/
    rendering.js            # Canvas drawing helpers
    geometry.js             # Vector math helpers
```

**Key Rendering Loop:**
```javascript
// useCanvas.js
useEffect(() => {
  const canvas = canvasRef.current;
  const ctx = canvas.getContext('2d');
  
  let animationFrameId;
  
  const render = () => {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background/grid
    drawBackground(ctx);
    
    // Draw ships at current turn position
    const currentState = turns[currentTurn];
    drawShip(ctx, currentState.ship_a, 'blue');
    drawShip(ctx, currentState.ship_b, 'red');
    
    // Draw torpedoes
    currentState.torpedoes.forEach(t => drawTorpedo(ctx, t));
    
    // Draw phaser arcs if firing
    const phaserEvents = currentState.events.filter(e => e.type === 'phaser_hit');
    phaserEvents.forEach(e => drawPhaserArc(ctx, e));
    
    animationFrameId = requestAnimationFrame(render);
  };
  
  render();
  
  return () => cancelAnimationFrame(animationFrameId);
}, [currentTurn, turns]);
```

**Scaling Strategy:**
- Static files hosted on CDN
- Client-side rendering only
- Progressive loading for large replays

---

## Data Architecture

### Core Data Models

All data models use Python dataclasses for type safety and JSON serialization.

#### GameState

```python
@dataclass
class GameState:
    """Complete game state at a single point in time."""
    turn: int
    ship_a: ShipState
    ship_b: ShipState
    torpedoes: List[TorpedoState]
```

#### ShipState

```python
@dataclass
class ShipState:
    """Complete state for one ship."""
    position: Vec2D           # (x, y) coordinates
    velocity: Vec2D           # (vx, vy) velocity vector
    heading: float            # radians, 0 = East
    shields: int              # 0-100
    ae: int                   # 0-100
    phaser_config: PhaserConfig  # WIDE or FOCUSED
    phaser_cooldown: float    # seconds until phaser can fire again
    reconfiguring_phaser: bool   # true during reconfiguration turn
```

#### TorpedoState

```python
@dataclass
class TorpedoState:
    """Complete state for one torpedo."""
    id: str                   # "ship_a_torpedo_1"
    position: Vec2D
    velocity: Vec2D
    heading: float            # radians
    ae_remaining: int         # fuel remaining
    owner: str                # "ship_a" or "ship_b"
    just_launched: bool       # can't turn on launch turn
```

#### Orders

```python
@dataclass
class TorpedoAction:
    """Command for a single torpedo."""
    torpedo_id: str
    # e.g., "hard_left", "detonate_after:5.2"
    action: str

@dataclass
class Orders:
    """Commands from LLM for one ship for one decision interval."""
    # e.g., "forward", "backward_left"
    ship_movement: str
    # e.g., "none", "hard_left"
    ship_rotation: str
    # e.g., "reconfigure_to_focused", "no_change"
    phaser_action: str
    # Orders for existing torpedoes
    torpedo_actions: List[TorpedoAction]
    # Whether to launch a new torpedo this turn
    launch_torpedo: bool
```

#### Event

```python
@dataclass
class Event:
    """Something that happened during a turn."""
    type: str                 # "torpedo_launched", "phaser_hit", etc.
    turn: int
    data: dict                # Event-specific data
```

### Data Flow

```
Turn N State → LLM Adapter → Orders
                ↓
Turn N State + Orders → Game Engine → Turn N+1 State + Events
                                          ↓
                                    Replay System → JSON File
                                          ↓
                                     Web Server → React Frontend
```

### Data Serialization

**JSON Format:**
- All game objects are JSON-serializable
- Vec2D serializes as `[x, y]` tuple
- Enums serialize as strings
- Timestamps in ISO 8601 format

**Serialization Strategy:**
```python
def serialize_state(state: GameState) -> dict:
    """Convert GameState to JSON-compatible dict."""
    return {
        "turn": state.turn,
        "ship_a": serialize_ship(state.ship_a),
        "ship_b": serialize_ship(state.ship_b),
        "torpedoes": [serialize_torpedo(t) for t in state.torpedoes]
    }
```

**Determinism Guarantee:**
- All serialization is order-preserving
- No floating point rounding during serialization
- Replay can reconstruct exact state without re-simulation

---

## API Design

### REST API

**Base URL:** `http://localhost:8000/api`

#### Match Endpoints

**Start Match**
```http
POST /api/match/start
Content-Type: application/json

{
  "model_a": "anthropic/claude-sonnet-4",
  "model_b": "openai/gpt-4",
  "max_turns": 50,
  "initial_shields": 100,
  "initial_ae": 100
}

Response 202 Accepted:
{
  "match_id": "claude_vs_gpt_2025_11_13_001",
  "status": "running",
  "estimated_duration_seconds": 90
}
```

**Get Match Status**
```http
GET /api/match/{match_id}

Response 200 OK:
{
  "match_id": "claude_vs_gpt_2025_11_13_001",
  "status": "completed",  // "running", "completed", "error"
  "winner": "ship_a",
  "current_turn": 18,
  "total_turns": 18
}
```

**List Matches**
```http
GET /api/matches?limit=20&offset=0

Response 200 OK:
{
  "matches": [
    {
      "match_id": "claude_vs_gpt_2025_11_13_001",
      "models": {
        "ship_a": "anthropic/claude-sonnet-4",
        "ship_b": "openai/gpt-4"
      },
      "winner": "ship_a",
      "total_turns": 18,
      "created_at": "2025-11-13T10:30:00Z"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

**Get Replay**
```http
GET /api/match/{match_id}/replay

Response 200 OK:
{
  "match_id": "claude_vs_gpt_2025_11_13_001",
  "models": { ... },
  "winner": "ship_a",
  "total_turns": 18,
  "turns": [ ... ]  // Full turn-by-turn data
}
```

#### Error Responses

```json
{
  "error": {
    "code": "MATCH_NOT_FOUND",
    "message": "Match with ID 'invalid_id' not found",
    "details": {}
  }
}
```

**Error Codes:**
- `MATCH_NOT_FOUND` (404)
- `INVALID_REQUEST` (400)
- `LLM_ERROR` (500)
- `INTERNAL_ERROR` (500)

### Rate Limiting

**MVP:** No rate limiting

**Future (Phase 2+):**
- 60 requests/minute per IP
- 10 concurrent matches per user
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

---

## Deployment Architecture

### MVP Deployment (Local)

```
┌─────────────────────────────────────┐
│       Local Machine                  │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  Python Application           │   │
│  │  - Match Orchestrator         │   │
│  │  - Game Engine                │   │
│  │  - LLM Adapter                │   │
│  │  - Replay System              │   │
│  │  - FastAPI Server             │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  React Build (Static Files)   │   │
│  │  Served by FastAPI            │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  Replay Files (JSON)          │   │
│  │  /replays/*.json              │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
         │
         ├─> LLM APIs (Anthropic, OpenAI, etc.)
         └─> Browser (localhost:8000)
```

**Running Locally:**
```bash
# Terminal 1: Start backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python main.py

# Terminal 2: Start frontend (dev mode)
cd frontend
npm install
npm start

# Access: http://localhost:3000
```

### Phase 2 Deployment (Cloud)

```
┌─────────────────────────────────────────────┐
│              AWS / Cloud Provider            │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  Load Balancer (ALB)                  │   │
│  └────────────┬─────────────────────────┘   │
│               │                              │
│  ┌────────────▼─────────────────────────┐   │
│  │  Container (ECS/Fargate)              │   │
│  │  - Python Backend (FastAPI)           │   │
│  │  - Serves React static files          │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  S3 Bucket                             │   │
│  │  - Replay files (JSON)                 │   │
│  │  - Static assets (images, fonts)       │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │  CloudWatch                            │   │
│  │  - Logs and metrics                    │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │
         ├─> LLM APIs (external)
         └─> Users (browsers)
```

### Monitoring & Observability

**Logging:**
- Tool: Python `logging` module → CloudWatch in production
- Log levels: ERROR, WARN, INFO, DEBUG
- Structured logging (JSON format)

**Key Metrics:**
- Match duration (seconds)
- Turn resolution time (ms)
- LLM API latency (ms)
- Error rate (%)
- Matches completed per hour

**Alerting (Future):**
- LLM API failures > 10%
- Match duration > 5 minutes
- Error rate > 5%

---

## Implementation Patterns

These patterns are **critical for AI agent implementation**. Each includes detailed code examples for consistent, production-ready implementation.

### Pattern 1: Game Engine - Physics Resolution

**Framework:** Pure Python with NumPy

**File:** `game_engine/physics.py`

```python
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import numpy as np
from enum import Enum

# ============= Data Structures =============

@dataclass
class Vec2D:
    """2D vector for positions and velocities."""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other): return Vec2D(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Vec2D(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar): return Vec2D(self.x * scalar, self.y * scalar)
    def magnitude(self) -> float: return np.sqrt(self.x**2 + self.y**2)
    
    def normalized(self) -> 'Vec2D':
        mag = self.magnitude()
        return Vec2D(self.x / mag, self.y / mag) if mag != 0 else Vec2D()
    
    def distance_to(self, other: 'Vec2D') -> float:
        return (self - other).magnitude()

# New enums for decoupled movement and rotation
class MovementDirection(Enum):
    FORWARD = "forward"
    FORWARD_LEFT = "forward_left"
    FORWARD_RIGHT = "forward_right"
    LEFT = "left"
    RIGHT = "right"
    BACKWARD = "backward"
    BACKWARD_LEFT = "backward_left"
    BACKWARD_RIGHT = "backward_right"
    STOP = "stop"

class RotationCommand(Enum):
    NONE = "none"
    SOFT_LEFT = "soft_left"
    SOFT_RIGHT = "soft_right"
    HARD_LEFT = "hard_left"
    HARD_RIGHT = "hard_right"

class PhaserConfig(Enum):
    WIDE = "wide"
    FOCUSED = "focused"

@dataclass
class ShipState:
    position: Vec2D
    velocity: Vec2D = field(default_factory=Vec2D)
    heading: float = 0.0
    shields: float = 100.0
    ae: float = 100.0
    phaser_config: PhaserConfig = PhaserConfig.WIDE
    phaser_cooldown: float = 0.0
    reconfiguring_phaser: bool = False

# ============= Physics Constants =============

FIXED_TIMESTEP = 0.1  # 10 Hz simulation
ACTION_PHASE_DURATION = 15.0  # 15 simulated seconds per turn
SUBSTEPS = int(ACTION_PHASE_DURATION / FIXED_TIMESTEP)  # 150

SHIP_BASE_SPEED = 3.0  # units per second
TORPEDO_SPEED = 4.0  # units per second
AE_PASSIVE_REGEN_RATE = 0.333 # AE per second

# AE Burn Rates (per second)
MOVEMENT_AE_COSTS = {
    MovementDirection.FORWARD: 0.33,
    MovementDirection.FORWARD_LEFT: 0.53,
    MovementDirection.FORWARD_RIGHT: 0.53,
    MovementDirection.LEFT: 0.67,
    MovementDirection.RIGHT: 0.67,
    MovementDirection.BACKWARD: 0.67,
    MovementDirection.BACKWARD_LEFT: 0.80,
    MovementDirection.BACKWARD_RIGHT: 0.80,
    MovementDirection.STOP: 0.0,
}
ROTATION_AE_COSTS = {
    RotationCommand.NONE: 0.0,
    RotationCommand.SOFT_LEFT: 0.13,
    RotationCommand.SOFT_RIGHT: 0.13,
    RotationCommand.HARD_LEFT: 0.33,
    RotationCommand.HARD_RIGHT: 0.33,
}

# Rotation rates (degrees per second)
ROTATION_RATES = {
    RotationCommand.NONE: 0.0,
    RotationCommand.SOFT_LEFT: 1.0,
    RotationCommand.SOFT_RIGHT: -1.0,
    RotationCommand.HARD_LEFT: 3.0,
    RotationCommand.HARD_RIGHT: -3.0,
}

# ============= Core Engine =============

class PhysicsEngine:
    """
    Stateless physics engine - pure function.
    Input: GameState + Orders -> Output: New GameState + Events
    """
    
    def resolve_turn(
        self, 
        state: GameState, 
        orders_a: Orders, 
        orders_b: Orders
    ) -> Tuple[GameState, List[Event]]:
        """
        Resolve one complete turn (15 simulated seconds).
        Uses fixed timestep for determinism.
        """
        events = []
        new_state = self._copy_state(state)
        new_state.turn += 1
        
        # 1. Handle discrete start-of-turn actions (launching, reconfiguring)
        # ... (validation and application logic for orders) ...
        
        # 2. Simulate 15 seconds with fixed timestep
        for _ in range(SUBSTEPS):
            # Update cooldowns and AE continuously
            self._update_resources(new_state.ship_a, orders_a, FIXED_TIMESTEP)
            self._update_resources(new_state.ship_b, orders_b, FIXED_TIMESTEP)

            # Update physics for all objects
            self._update_ship_physics(new_state.ship_a, orders_a, FIXED_TIMESTEP)
            self._update_ship_physics(new_state.ship_b, orders_b, FIXED_TIMESTEP)
            
            # ... (update torpedo physics) ...

            # Continuous checks (phasers, collisions)
            phaser_events = self._check_phaser_hits(new_state, FIXED_TIMESTEP)
            events.extend(phaser_events)
            
            # ... (check torpedo collisions and blast zones) ...
        
        # 3. Clear turn-based flags
        new_state.ship_a.reconfiguring_phaser = False
        new_state.ship_b.reconfiguring_phaser = False
        
        return new_state, events

    def _update_resources(self, ship: ShipState, orders: Orders, dt: float):
        """Update AE and cooldowns for one timestep."""
        # Decrement phaser cooldown
        ship.phaser_cooldown = max(0, ship.phaser_cooldown - dt)
        
        # Calculate AE burn rate for this step
        move_cost_rate = MOVEMENT_AE_COSTS.get(orders.ship_movement, 0)
        rot_cost_rate = ROTATION_AE_COSTS.get(orders.ship_rotation, 0)
        total_burn_rate = move_cost_rate + rot_cost_rate
        
        # Apply net AE change
        net_ae_change = (AE_PASSIVE_REGEN_RATE - total_burn_rate) * dt
        ship.ae = max(0, min(100, ship.ae + net_ae_change))

    def _update_ship_physics(self, ship: ShipState, orders: Orders, dt: float):
        """Update ship position and heading for one timestep, with decoupled movement."""
        if orders.ship_movement == MovementDirection.STOP:
            ship.velocity = Vec2D(0, 0) # Or some coasting logic
        
        # Apply rotation
        rotation_rate_dps = ROTATION_RATES.get(orders.ship_rotation, 0)
        ship.heading += np.radians(rotation_rate_dps) * dt
        ship.heading %= (2 * np.pi)
        
        # Apply movement (simplified for this example)
        # A real implementation would use the movement direction (e.g., 'forward_left')
        # to calculate a target velocity vector relative to the ship's current heading,
        # and then smoothly turn the ship's actual velocity towards that target.
        # For now, we'll just move in the direction of the current heading.
        if orders.ship_movement != MovementDirection.STOP:
             ship.velocity = Vec2D(
                np.cos(ship.heading) * SHIP_BASE_SPEED,
                np.sin(ship.heading) * SHIP_BASE_SPEED
            )
        
        # Update position
        ship.position = ship.position + (ship.velocity * dt)
    
    def _check_phaser_hits(self, state: GameState, dt: float) -> List[Event]:
        """Check if either ship's phaser hit opponent during this timestep."""
        events = []
        
        hit_a = self._check_single_phaser_hit(
            state.ship_a, state.ship_b, "ship_a", "ship_b"
        )
        if hit_a:
            events.append(hit_a)
        
        hit_b = self._check_single_phaser_hit(
            state.ship_b, state.ship_a, "ship_b", "ship_a"
        )
        if hit_b:
            events.append(hit_b)
        
        return events
    
    def _check_single_phaser_hit(
        self, 
        attacker: ShipState, 
        target: ShipState, 
        attacker_id: str, 
        target_id: str
    ) -> Optional[Event]:
        """Check if attacker's phaser hits target, considering cooldown."""
        # Can't fire if reconfiguring or on cooldown
        if attacker.reconfiguring_phaser or attacker.phaser_cooldown > 0:
            return None

        distance = attacker.position.distance_to(target.position)
        
        if attacker.phaser_config == PhaserConfig.WIDE:
            arc, max_range, damage, cooldown = np.radians(90), 30.0, 15.0, 3.5
        else:  # FOCUSED
            arc, max_range, damage, cooldown = np.radians(10), 50.0, 35.0, 3.5
        
        if distance > max_range:
            return None
        
        delta = target.position - attacker.position
        angle_to_target = np.arctan2(delta.y, delta.x)
        angle_diff = (angle_to_target - attacker.heading) % (2 * np.pi)
        if angle_diff > np.pi: angle_diff -= 2 * np.pi
        
        if abs(angle_diff) <= arc / 2:
            # HIT! Apply damage and set cooldown.
            target.shields = max(0, target.shields - damage)
            attacker.phaser_cooldown = cooldown
            
            return Event(
                type="phaser_hit",
                turn=0, # turn number would be properly set
                data={
                    "attacker": attacker_id, "target": target_id,
                    "damage": damage, "config": attacker.phaser_config.value,
                    "distance": distance
                }
            )
        
        return None
    
    # ... (Additional methods: _check_torpedo_collisions, 
    #      _apply_weapon_action, _validate_orders, etc.)
```

**Key Implementation Notes:**
- **Continuous Simulation:** All checks and resource updates now happen inside the `SUBSTEPS` loop for a real-time feel.
- **Decoupled Movement:** `_update_ship_physics` now handles rotation and movement direction independently, enabling "face move" tactics.
- **AE Burn Rate:** `_update_resources` calculates a continuous AE burn based on chosen maneuvers, reflecting the new spec.
- **Phaser Cooldown:** `_check_single_phaser_hit` now checks and sets the `phaser_cooldown` on the `ShipState`, preventing rapid-fire exploits.
- All angles in radians for consistency.
- Vector operations use NumPy for performance.

---

### Pattern 2: LLM Integration with LiteLLM

**Framework:** LiteLLM library

**File:** `llm_adapter/adapter.py`

```python
import litellm
from typing import Tuple, List
import json
import asyncio

# Assuming Orders, MovementDirection, etc. are defined as in Pattern 1
# from game_engine.physics import Orders, TorpedoAction, ...

class LLMAdapter:
    """
    Abstracts LLM provider complexity.
    Constructs prompts, parses responses, handles errors.
    """
    
    def __init__(self, model_a: str, model_b: str):
        self.model_a = model_a
        self.model_b = model_b
    
    async def get_orders_for_both_ships(
        self, 
        state: GameState
    ) -> Tuple[Orders, str, Orders, str]:
        """
        Get orders from both models in parallel.
        Returns: (orders_a, thinking_a, orders_b, thinking_b)
        """
        results = await asyncio.gather(
            self._get_orders_for_ship(state, "ship_a", self.model_a),
            self._get_orders_for_ship(state, "ship_b", self.model_b),
            return_exceptions=True
        )
        
        orders_a, thinking_a = self._handle_result(results[0])
        orders_b, thinking_b = self._handle_result(results[1])
        
        return orders_a, thinking_a, orders_b, thinking_b
    
    def _handle_result(self, result):
        """Handle potential exceptions from gather."""
        if isinstance(result, Exception):
            print(f"LLM error: {result}")
            return self._default_orders(), f"ERROR: {str(result)}"
        return result
    
    async def _get_orders_for_ship(
        self, 
        state: GameState, 
        ship_id: str, 
        model: str
    ) -> Tuple[Orders, str]:
        """Get orders from a single model."""
        prompt = self._build_prompt(state, ship_id)
        
        try:
            response = await litellm.acompletion(
                model=model, messages=prompt,
                max_tokens=1000, temperature=0.7, timeout=30.0
            )
            response_text = response.choices[0].message.content
            orders = self._parse_orders(response_text)
            thinking = json.loads(response_text.strip()).get("reasoning", "")
            
            return orders, thinking
            
        except Exception as e:
            print(f"LLM error for {ship_id}: {e}")
            return self._default_orders(), f"ERROR: {str(e)}"
    
    def _build_prompt(self, state: GameState, ship_id: str) -> list:
        """Build prompt with game state and rules."""
        # ... (logic to get us, enemy, our_torpedoes, etc.) ...
        
        system_prompt = """You are piloting a starship in a real-time 1v1 duel. The game runs in 15-second intervals.

**MOVEMENT & ROTATION (AE/sec cost):**
Your movement direction and rotation are independent.
- MOVEMENT: `forward`(0.33), `forward_left`(0.53), `forward_right`(0.53), `left`(0.67), `right`(0.67), `backward`(0.67), `backward_left`(0.80), `backward_right`(0.80), `stop`(0.0).
- ROTATION: `hard_left`(0.33), `hard_right`(0.33), `soft_left`(0.13), `soft_right`(0.13), `none`(0.0).
- AE regenerates at 0.333 AE/sec.

**PHASERS (Automatic Firing):**
Phasers fire automatically when an enemy enters the arc and cooldown is 0.
- WIDE: 90° arc, 30 range, 15 damage, 3.5s cooldown.
- FOCUSED: 10° arc, 50 range, 35 damage, 3.5s cooldown.
- Reconfiguring (`reconfigure_to_...`) takes one 15s interval (no firing).

**TORPEDOES (Controlled Projectiles):**
- Launch Cost: 20 AE. Max 4 active.
- Damage = (AE at detonation) * 1.5. Blast Radius: 15 units.
- Torpedoes fly straight for the first 15s after launch.
- Commands: `straight`, `soft_left`, `hard_right`, etc.
- Timed Detonation: `detonate_after:X` where X is seconds from 0.0 to 15.0.

**RESPONSE FORMAT (JSON ONLY):**
{
  "reasoning": "Your tactical analysis here.",
  "ship_movement": "forward",
  "ship_rotation": "hard_left",
  "phaser_action": "no_change",
  "launch_torpedo": true,
  "torpedo_actions": [
    {"torpedo_id": "ship_a_torp_1", "action": "hard_right"},
    {"torpedo_id": "ship_a_torp_2", "action": "detonate_after:8.5"}
  ]
}"""
        
        user_prompt = f"""TURN {state.turn} - Your ship is '{ship_id}'
{self._serialize_state_for_prompt(state, ship_id)}

Your orders (JSON only):"""
        
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    def _parse_orders(self, response_text: str) -> Orders:
        """Parse LLM response into Orders object."""
        try:
            text = response_text.strip()
            if text.startswith("```json"): text = text[7:-3].strip()
            
            parsed = json.loads(text)
            
            # Extract and validate ship movement and rotation
            mov = MovementDirection[parsed.get("ship_movement", "stop").upper()]
            rot = RotationCommand[parsed.get("ship_rotation", "none").upper()]
            
            phaser_action = parsed.get("phaser_action", "no_change")
            launch_torpedo = parsed.get("launch_torpedo", False)
            
            # Extract torpedo actions
            torpedo_actions = []
            for ta in parsed.get("torpedo_actions", []):
                torpedo_actions.append(TorpedoAction(
                    torpedo_id=ta.get("torpedo_id"),
                    action=ta.get("action")
                ))

            return Orders(
                ship_movement=mov,
                ship_rotation=rot,
                phaser_action=phaser_action,
                launch_torpedo=launch_torpedo,
                torpedo_actions=torpedo_actions
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"LLM parse error: {e}. Response: {response_text[:200]}")
            return self._default_orders()

    def _default_orders(self) -> Orders:
        """Safe default orders when parsing fails."""
        return Orders(
            ship_movement=MovementDirection.STOP,
            ship_rotation=RotationCommand.NONE,
            phaser_action="no_change",
            launch_torpedo=False,
            torpedo_actions=[]
        )

    def _serialize_state_for_prompt(self, state: GameState, ship_id: str) -> str:
        # Helper to create the user prompt part of the message.
        # This would serialize the ship, enemy, torpedoes, and blast zones.
        return "..." # Placeholder for detailed state summary
```

**Key Implementation Notes:**
- **Revised Prompt:** The system prompt is completely overhauled to teach the LLM the new real-time mechanics, continuous AE model, and independent movement/rotation.
- **New JSON Format:** The prompt and parsing logic now use the new detailed JSON structure, including `ship_movement`, `ship_rotation`, and a list of `torpedo_actions`.
- **Robust Parsing:** `_parse_orders` is updated to safely extract the new fields, with validation against the new Enums.
- **Updated Defaults:** `_default_orders` and error handling in `_handle_result` now correctly instantiate the new `Orders` object, ensuring safe failure modes.

---

### Pattern 3: Replay System

**File:** `replay/recorder.py`

```python
import json
from datetime import datetime
from pathlib import Path
from typing import List

class ReplayRecorder:
    """Records match data for deterministic replay."""
    
    def __init__(self, model_a: str, model_b: str):
        self.model_a = model_a
        self.model_b = model_b
        self.turns = []
        self.match_id = self._generate_match_id()
    
    def record_turn(
        self,
        turn: int,
        state: GameState,
        orders_a: Orders,
        orders_b: Orders,
        thinking_a: str,
        thinking_b: str,
        events: List[Event]
    ):
        """Record one turn's complete data."""
        turn_data = {
            "turn": turn,
            "state": self._serialize_state(state),
            "orders_a": self._serialize_orders(orders_a),
            "orders_b": self._serialize_orders(orders_b),
            "thinking_a": thinking_a,
            "thinking_b": thinking_b,
            "events": [self._serialize_event(e) for e in events]
        }
        self.turns.append(turn_data)
    
    def finalize(self, winner: str, total_turns: int) -> dict:
        """Finalize match and save to file."""
        match_data = {
            "match_id": self.match_id,
            "models": {
                "ship_a": self.model_a,
                "ship_b": self.model_b
            },
            "winner": winner,
            "total_turns": total_turns,
            "created_at": datetime.utcnow().isoformat(),
            "turns": self.turns
        }
        
        # Save to file
        replay_path = Path("replays") / f"{self.match_id}.json"
        replay_path.parent.mkdir(exist_ok=True)
        
        with open(replay_path, 'w') as f:
            json.dump(match_data, f, indent=2)
        
        print(f"Replay saved: {replay_path}")
        return match_data
    
    def _generate_match_id(self) -> str:
        """Generate unique match ID."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_a_short = self.model_a.split("/")[-1][:10]
        model_b_short = self.model_b.split("/")[-1][:10]
        return f"{model_a_short}_vs_{model_b_short}_{timestamp}"
    
    def _serialize_state(self, state: GameState) -> dict:
        """Convert GameState to JSON-compatible dict."""
        return {
            "turn": state.turn,
            "ship_a": self._serialize_ship(state.ship_a),
            "ship_b": self._serialize_ship(state.ship_b),
            "torpedoes": [self._serialize_torpedo(t) for t in state.torpedoes]
        }
    
    def _serialize_ship(self, ship: ShipState) -> dict:
        return {
            "position": [ship.position.x, ship.position.y],
            "velocity": [ship.velocity.x, ship.velocity.y],
            "heading": ship.heading,
            "shields": ship.shields,
            "ae": ship.ae,
            "phaser_config": ship.phaser_config.value,
            "reconfiguring_phaser": ship.reconfiguring_phaser
        }
    
    def _serialize_torpedo(self, torpedo: TorpedoState) -> dict:
        return {
            "id": torpedo.id,
            "position": [torpedo.position.x, torpedo.position.y],
            "velocity": [torpedo.velocity.x, torpedo.velocity.y],
            "heading": torpedo.heading,
            "ae_remaining": torpedo.ae_remaining,
            "owner": torpedo.owner,
            "just_launched": torpedo.just_launched
        }
    
    def _serialize_orders(self, orders: Orders) -> dict:
        return {
            "movement": orders.movement.value,
            "weapon": orders.weapon_action,
            "torpedo_orders": {
                tid: move.value 
                for tid, move in orders.torpedo_orders.items()
            }
        }
    
    def _serialize_event(self, event: Event) -> dict:
        return {
            "type": event.type,
            "turn": event.turn,
            "data": event.data
        }

class ReplayLoader:
    """Loads replay files for visualization."""
    
    @staticmethod
    def load(match_id: str) -> dict:
        """Load replay from file."""
        replay_path = Path("replays") / f"{match_id}.json"
        
        if not replay_path.exists():
            raise FileNotFoundError(f"Replay not found: {match_id}")
        
        with open(replay_path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def list_matches() -> List[dict]:
        """List all available replays."""
        replay_dir = Path("replays")
        if not replay_dir.exists():
            return []
        
        matches = []
        for replay_file in replay_dir.glob("*.json"):
            try:
                with open(replay_file, 'r') as f:
                    data = json.load(f)
                matches.append({
                    "match_id": data["match_id"],
                    "models": data["models"],
                    "winner": data["winner"],
                    "total_turns": data["total_turns"],
                    "created_at": data["created_at"]
                })
            except Exception as e:
                print(f"Error loading {replay_file}: {e}")
        
        return sorted(matches, key=lambda m: m["created_at"], reverse=True)
```

---

### Pattern 4: FastAPI Web Server

**File:** `web_server/main.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

from orchestrator.match_orchestrator import MatchOrchestrator
from replay.recorder import ReplayLoader

app = FastAPI(title="AI Arena API")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class StartMatchRequest(BaseModel):
    model_a: str
    model_b: str
    max_turns: int = 50

class StartMatchResponse(BaseModel):
    match_id: str
    status: str

# In-memory match tracking (MVP - use database in production)
active_matches = {}

@app.post("/api/match/start", response_model=StartMatchResponse)
async def start_match(request: StartMatchRequest):
    """Start a new match."""
    orchestrator = MatchOrchestrator(request.model_a, request.model_b)
    
    # Run match in background
    task = asyncio.create_task(orchestrator.run_match(request.max_turns))
    match_id = f"temp_{len(active_matches)}"  # Simplified
    active_matches[match_id] = {"task": task, "status": "running"}
    
    return StartMatchResponse(match_id=match_id, status="running")

@app.get("/api/match/{match_id}")
async def get_match_status(match_id: str):
    """Get match status."""
    if match_id not in active_matches:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match_info = active_matches[match_id]
    
    if match_info["task"].done():
        result = match_info["task"].result()
        return {
            "match_id": result["match_id"],
            "status": "completed",
            "winner": result["winner"],
            "total_turns": result["total_turns"]
        }
    
    return {"match_id": match_id, "status": "running"}

@app.get("/api/matches")
async def list_matches(limit: int = 20, offset: int = 0):
    """List available replays."""
    matches = ReplayLoader.list_matches()
    total = len(matches)
    paginated = matches[offset:offset + limit]
    
    return {
        "matches": paginated,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.get("/api/match/{match_id}/replay")
async def get_replay(match_id: str):
    """Get full replay data."""
    try:
        replay_data = ReplayLoader.load(match_id)
        return replay_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Replay not found")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Serve React static files in production
# app.mount("/", StaticFiles(directory="frontend/build", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### Pattern 5: React Canvas Rendering

**File:** `frontend/src/hooks/useCanvas.js`

```javascript
import { useRef, useEffect } from 'react';

/**
 * Canvas animation loop hook
 */
export const useCanvas = (draw, currentTurn, turns) => {
  const canvasRef = useRef(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    
    const render = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Call draw function with current turn data
      if (turns && turns[currentTurn]) {
        draw(ctx, turns[currentTurn], canvas);
      }
      
      animationFrameId = requestAnimationFrame(render);
    };
    
    render();
    
    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [draw, currentTurn, turns]);
  
  return canvasRef;
};
```

**File:** `frontend/src/components/GameCanvas.jsx`

```javascript
import React from 'react';
import { useCanvas } from '../hooks/useCanvas';

const GameCanvas = ({ turns, currentTurn }) => {
  
  const draw = (ctx, turnData, canvas) => {
    // Draw background
    ctx.fillStyle = '#000814';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid
    drawGrid(ctx, canvas);
    
    // Draw ships
    drawShip(ctx, turnData.state.ship_a, '#00b4d8');
    drawShip(ctx, turnData.state.ship_b, '#e63946');
    
    // Draw torpedoes
    turnData.state.torpedoes.forEach(torpedo => {
      drawTorpedo(ctx, torpedo);
    });
    
    // Draw phaser arcs for hits this turn
    const phaserHits = turnData.events.filter(e => e.type === 'phaser_hit');
    phaserHits.forEach(hit => {
      drawPhaserArc(ctx, hit, turnData.state);
    });
  };
  
  const drawGrid = (ctx, canvas) => {
    ctx.strokeStyle = '#1d3557';
    ctx.lineWidth = 1;
    
    // Vertical lines
    for (let x = 0; x < canvas.width; x += 50) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    
    // Horizontal lines
    for (let y = 0; y < canvas.height; y += 50) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }
  };
  
  const drawShip = (ctx, ship, color) => {
    const [x, y] = ship.position;
    
    // Draw ship body (triangle pointing in heading direction)
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(ship.heading);
    
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(15, 0);
    ctx.lineTo(-10, -8);
    ctx.lineTo(-10, 8);
    ctx.closePath();
    ctx.fill();
    
    // Draw phaser arc (semi-transparent)
    const arc = ship.phaser_config === 'wide' ? Math.PI / 2 : Math.PI / 18;
    const range = ship.phaser_config === 'wide' ? 30 : 50;
    
    ctx.fillStyle = color + '20';  // 20 = low opacity
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, range, -arc/2, arc/2);
    ctx.closePath();
    ctx.fill();
    
    ctx.restore();
    
    // Draw shield indicator
    const shieldPercent = ship.shields / 100;
    ctx.strokeStyle = shieldPercent > 0.5 ? '#06ffa5' : '#ff006e';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(x, y, 20, 0, Math.PI * 2 * shieldPercent);
    ctx.stroke();
    
    // Draw AE indicator
    ctx.fillStyle = '#ffd60a';
    ctx.fillRect(x - 15, y - 30, 30 * (ship.ae / 100), 3);
  };
  
  const drawTorpedo = (ctx, torpedo) => {
    const [x, y] = torpedo.position;
    
    ctx.fillStyle = torpedo.owner === 'ship_a' ? '#00b4d8' : '#e63946';
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw trail
    ctx.strokeStyle = ctx.fillStyle + '40';
    ctx.lineWidth = 2;
    ctx.beginPath();
    const trailLength = 20;
    ctx.moveTo(x, y);
    ctx.lineTo(
      x - Math.cos(torpedo.heading) * trailLength,
      y - Math.sin(torpedo.heading) * trailLength
    );
    ctx.stroke();
  };
  
  const drawPhaserArc = (ctx, hit, state) => {
    // Get attacker position
    const attacker = hit.data.attacker === 'ship_a' ? state.ship_a : state.ship_b;
    const [x, y] = attacker.position;
    
    // Draw beam effect
    ctx.strokeStyle = hit.data.attacker === 'ship_a' ? '#00b4d8' : '#e63946';
    ctx.lineWidth = 3;
    ctx.globalAlpha = 0.7;
    
    const arc = hit.data.config === 'wide' ? Math.PI / 2 : Math.PI / 18;
    const range = hit.data.distance;
    
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(attacker.heading);
    
    ctx.beginPath();
    ctx.arc(0, 0, range, -arc/2, arc/2);
    ctx.stroke();
    
    ctx.restore();
    ctx.globalAlpha = 1.0;
  };
  
  const canvasRef = useCanvas(draw, currentTurn, turns);
  
  return (
    <canvas
      ref={canvasRef}
      width={1000}
      height={500}
      style={{
        border: '2px solid #1d3557',
        backgroundColor: '#000814'
      }}
    />
  );
};

export default GameCanvas;
```

**File:** `frontend/src/components/ReplayViewer.jsx`

```javascript
import React, { useState, useEffect } from 'react';
import GameCanvas from './GameCanvas';
import ThinkingPanel from './ThinkingPanel';
import ReplayControls from './ReplayControls';

const ReplayViewer = ({ matchId }) => {
  const [replayData, setReplayData] = useState(null);
  const [currentTurn, setCurrentTurn] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  
  useEffect(() => {
    // Load replay data
    fetch(`http://localhost:8000/api/match/${matchId}/replay`)
      .then(res => res.json())
      .then(data => {
        setReplayData(data);
      })
      .catch(err => console.error('Error loading replay:', err));
  }, [matchId]);
  
  useEffect(() => {
    if (!isPlaying || !replayData) return;
    
    const interval = setInterval(() => {
      setCurrentTurn(prev => {
        if (prev >= replayData.turns.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 1000 / playbackSpeed);
    
    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed, replayData]);
  
  if (!replayData) {
    return <div>Loading replay...</div>;
  }
  
  const currentTurnData = replayData.turns[currentTurn];
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', gap: '20px' }}>
        <GameCanvas 
          turns={replayData.turns} 
          currentTurn={currentTurn}
        />
        <ThinkingPanel
          thinkingA={currentTurnData.thinking_a}
          thinkingB={currentTurnData.thinking_b}
          modelA={replayData.models.ship_a}
          modelB={replayData.models.ship_b}
        />
      </div>
      
      <ReplayControls
        currentTurn={currentTurn}
        totalTurns={replayData.turns.length}
        isPlaying={isPlaying}
        playbackSpeed={playbackSpeed}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onSeek={(turn) => setCurrentTurn(turn)}
        onSpeedChange={(speed) => setPlaybackSpeed(speed)}
      />
    </div>
  );
};

export default ReplayViewer;
```

---

### Pattern 6: Error Handling

**Centralized Error Handling Strategy:**

```python
# errors.py

class GameError(Exception):
    """Base exception for all game errors."""
    pass

class PhysicsError(GameError):
    """Physics simulation error."""
    pass

class LLMError(GameError):
    """LLM integration error."""
    pass

class ReplayError(GameError):
    """Replay system error."""
    pass

# Error handler decorator
def handle_errors(default_return=None):
    """Decorator for graceful error handling."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except LLMError as e:
                print(f"LLM error in {func.__name__}: {e}")
                return default_return
            except PhysicsError as e:
                print(f"Physics error in {func.__name__}: {e}")
                raise  # Physics errors should crash - they indicate bugs
            except Exception as e:
                print(f"Unexpected error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator

# Usage example
@handle_errors(default_return=(Orders(MovementType.STOP, "NONE", {}), "ERROR"))
async def get_orders_with_retry(adapter, state, ship_id, model):
    """Get orders with automatic retry on transient failures."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return await adapter._get_orders_for_ship(state, ship_id, model)
        except LLMError as e:
            if attempt == max_retries - 1:
                raise
            print(f"Retry {attempt + 1}/{max_retries} after error: {e}")
            await asyncio.sleep(1)
```

---

## Architecture Decision Records

### ADR Template

```markdown
### ADR-XXX: [Decision Title]

**Date:** YYYY-MM-DD
**Status:** [Proposed / Accepted / Deprecated / Superseded]

**Context:**
[What problem are we solving? What constraints exist?]

**Decision:**
[What did we decide?]

**Rationale:**
[Why did we choose this option?]

**Consequences:**

Positive:
- [Benefit 1]
- [Benefit 2]

Negative:
- [Trade-off 1]
- [Trade-off 2]

**Alternatives Considered:**
- [Alternative 1]: [Why rejected]
- [Alternative 2]: [Why rejected]
```

---

### ADR-001: Modular Monolith Architecture

**Date:** 2025-11-13  
**Status:** Accepted

**Context:**

We need to choose an architecture style for AI Arena MVP. The system has multiple distinct concerns (game engine, LLM integration, visualization) that could be separate services, but we want to move quickly while keeping options open for future scaling.

**Decision:**

Use a modular monolith with clear component boundaries and interface-based communication.

**Rationale:**

1. **Simplicity:** Single codebase is easier to develop, test, and debug during MVP
2. **Speed:** No network overhead or distributed system complexity
3. **Extraction-ready:** Components designed with interfaces can be extracted later
4. **Low operational overhead:** Single deployment, easier to run locally

**Consequences:**

Positive:
- Faster development velocity during MVP
- Simpler debugging (single process, stack traces work normally)
- Easy to run locally for development
- No network latency between components
- Single deployment artifact

Negative:
- Cannot scale components independently
- Single point of failure (entire app goes down together)
- Shared memory space (potential for unintended coupling)
- Must be disciplined about maintaining boundaries

**Alternatives Considered:**

- **Microservices:** Too much operational complexity for MVP; no proven scaling needs yet; would slow down development
- **Pure Monolith:** Would create tight coupling; hard to extract later; no clear boundaries

**Migration Path:**

When ready for microservices:
1. Wrap Game Engine in HTTP API: `POST /resolve-turn`
2. Wrap LLM Adapter in HTTP API: `POST /get-orders`
3. Replace function calls with HTTP clients
4. No game logic changes needed

---

### ADR-002: LiteLLM for Multi-Provider Support

**Date:** 2025-11-13  
**Status:** Accepted

**Context:**

We need to support multiple LLM providers (Claude, GPT-4, Grok, etc.) without writing provider-specific code. Each provider has different APIs, authentication, and response formats.

**Decision:**

Use LiteLLM library for unified LLM provider abstraction.

**Rationale:**

1. **Unified API:** Single interface for 100+ providers
2. **Proven library:** Well-maintained, active development
3. **Built-in features:** Fallbacks, retries, cost tracking
4. **Easy provider switching:** Change model string without code changes
5. **Async support:** Built-in async methods for parallel calls

**Consequences:**

Positive:
- Support multiple providers with minimal code
- Easy to compare different models in matches
- Built-in error handling and retries
- Can add new providers without code changes
- Cost tracking for analytics

Negative:
- Dependency on external library
- Abstraction layer adds small overhead
- Must follow LiteLLM's conventions
- Breaking changes in LiteLLM could affect us

**Alternatives Considered:**

- **OpenAI SDK only:** Would lock us to OpenAI; can't compare models; missing the core value proposition
- **Direct HTTP calls:** Would require implementing retry logic, auth, error handling for each provider; maintenance burden too high
- **Multiple SDKs:** Would need provider-specific code paths; violates DRY; hard to maintain

---

### ADR-003: Fixed Timestep Physics (60 Hz)

**Date:** 2025-11-13  
**Status:** Accepted

**Context:**

Physics simulation must be deterministic for replay system. Variable timesteps can cause non-deterministic behavior due to floating-point precision differences.

**Decision:**

Use fixed timestep physics at 60 Hz (1/60 second per substep).

**Rationale:**

1. **Determinism:** Same timestep every frame = same results every time
2. **Industry standard:** 60 Hz is common in games
3. **Replay-friendly:** No need to store physics substeps, just final state
4. **Predictable:** LLMs can reason about physics knowing it's consistent
5. **Testable:** Easy to write unit tests with known outcomes

**Consequences:**

Positive:
- Complete determinism: same inputs = same outputs, always
- Replay system works without re-simulation
- Easy to test and debug
- LLMs can learn consistent physics behavior
- No floating-point accumulation errors

Negative:
- Fixed 60 seconds per turn (3600 substeps) is inflexible
- If physics gets too complex, might need optimization
- Cannot speed up/slow down simulation dynamically

**Alternatives Considered:**

- **Variable timestep:** Would cause non-deterministic physics; replay would be unreliable; rejected
- **Larger timestep (30 Hz):** Less accurate physics; rejected
- **Smaller timestep (120 Hz):** More CPU for marginal accuracy gain; overkill for this game

**Implementation Note:**

Use "Fix Your Timestep" pattern (Gaffer on Games):
- Accumulator pattern for frame-independent simulation
- Always step physics at fixed 1/60 second increments
- Handle remainder time properly

---

### ADR-004: React + Canvas 2D for Visualization

**Date:** 2025-11-13  
**Status:** Accepted

**Context:**

Need web-based visualization for matches and replays. Must render 2D game state (ships, torpedoes, phasers) with good performance and be browser-compatible.

**Decision:**

Use React for UI structure with Canvas 2D API for game rendering.

**Rationale:**

1. **Canvas 2D is perfect fit:** Simple 2D graphics, no need for WebGL complexity
2. **React for UI:** Component-based architecture for controls, thinking panels
3. **Well-documented:** Excellent resources for React + Canvas integration
4. **Performance:** Canvas 2D easily handles 60 fps for simple 2D rendering
5. **Browser support:** Canvas 2D works everywhere, no special requirements

**Consequences:**

Positive:
- Clean separation: React for UI, Canvas for game rendering
- Easy to add controls (play/pause, timeline, speed)
- Canvas is performant enough for needs
- No heavy dependencies (Three.js, Babylon.js)
- Simple to debug

Negative:
- Canvas state management in React can be tricky
- No declarative rendering (must use imperative Canvas API)
- Animation loop in `useEffect` requires care

**Alternatives Considered:**

- **SVG:** Too slow for animation; rejected
- **WebGL/Three.js:** Overkill for 2D game; adds complexity; rejected
- **Pixi.js:** Good 2D library but adds dependency; Canvas 2D is sufficient
- **Plain HTML/CSS:** Cannot render complex shapes efficiently; rejected

**Implementation Pattern:**

- Use `useRef` for canvas element
- Use `useEffect` with `requestAnimationFrame` for render loop
- Keep game state in React state, read from Canvas render function
- Separate rendering logic into pure functions for testability

---

### ADR-005: JSON for Replay Storage

**Date:** 2025-11-13  
**Status:** Accepted

**Context:**

Need to store complete match data for replay. Must be human-readable, debuggable, and easy to work with.

**Decision:**

Use JSON format for replay storage.

**Rationale:**

1. **Human-readable:** Easy to inspect and debug
2. **Universal support:** Every language/platform has JSON libraries
3. **Structured:** Schema is self-documenting
4. **Lightweight:** Reasonable file sizes for 20-30 turn matches
5. **Web-friendly:** JSON is native to JavaScript for frontend

**Consequences:**

Positive:
- Easy to debug (can open file and read it)
- Universal compatibility
- Can edit manually if needed
- Easy to process/analyze with scripts
- No special tools required

Negative:
- Larger file sizes than binary formats
- No built-in compression (can add gzip)
- No schema enforcement (can add JSON Schema)
- Text parsing is slower than binary

**Alternatives Considered:**

- **Binary format (Protocol Buffers, MessagePack):** Smaller files but not human-readable; harder to debug; rejected for MVP
- **SQLite database:** Good for queries but overkill for simple replay; rejected
- **Plain text:** Unstructured; hard to parse; rejected

**Future Enhancement:**

- Add gzip compression for large replays
- Consider binary format if file sizes become problematic

---

## Risks & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation | Status |
|------|------------|--------|------------|--------|
| **LLM API rate limits** | High | High | Implement exponential backoff, queue requests, cache responses | Open |
| **LLM response parsing failures** | Medium | Medium | Robust JSON extraction, default to safe orders, extensive testing | Open |
| **Non-deterministic physics** | Low | Critical | Fixed timestep, unit tests, replay validation | Mitigated |
| **Floating point accumulation** | Medium | Medium | Use consistent precision, avoid iterative operations | Open |
| **Canvas rendering performance** | Low | Low | Optimize draw calls, skip off-screen elements | Open |
| **Large replay file sizes** | Medium | Low | Implement gzip compression, pagination for loading | Open |

### Operational Risks

| Risk | Probability | Impact | Mitigation | Status |
|------|------------|--------|------------|--------|
| **LLM API downtime** | Medium | High | Implement fallback providers, queue matches, user notifications | Open |
| **Match takes too long** | Low | Medium | Implement max turn limit, timeout safeguards | Mitigated |
| **Infinite loops in physics** | Low | Critical | Add turn limits, sanity checks, emergency stop button | Open |

### Business Risks

| Risk | Probability | Impact | Mitigation | Status |
|------|------------|--------|------------|--------|
| **LLM costs too high** | Medium | Medium | Monitor spending, implement usage limits, cache responses | Open |
| **Matches not entertaining** | Medium | High | Playtest extensively, tune game parameters, collect feedback | Open |
| **AI makes bad decisions** | High | Low | This is part of the entertainment! Document it as feature | Accepted |

---

## Appendices

### Glossary

| Term | Definition |
|------|------------|
| **AE (Anti-Entropy)** | Resource consumed by all actions in the game |
| **Fixed Timestep** | Physics simulation with constant time increment per step |
| **Deterministic Physics** | Same inputs always produce same outputs |
| **LiteLLM** | Library for unified LLM provider access |
| **Thinking Tokens** | LLM's reasoning displayed to spectators |
| **Replay** | Complete recorded match data for visualization |
| **Substep** | Single physics update in fixed timestep simulation |

### References

- [Fix Your Timestep (Gaffer on Games)](https://gafferongames.com/post/fix_your_timestep/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Canvas Patterns](https://blog.openreplay.com/2D-sketches-with-react-and-the-canvas-api/)
- [Game Architecture Patterns](https://gameprogrammingpatterns.com/)

### Future Considerations

**Phase 2 Enhancements:**
- Tournament mode with bracket system
- Player ELO ratings
- Advanced analytics and statistics
- Match prediction system

**Phase 3 Features:**
- Live streaming with WebSocket
- Multi-user spectating
- Chat integration
- Automated highlight clips

**Technical Debt to Address:**
- Add comprehensive unit tests
- Implement integration tests
- Add performance benchmarks
- Create deployment automation

---

## Project Structure

```
ai-arena/
├── backend/
│   ├── game_engine/
│   │   ├── __init__.py
│   │   ├── physics.py          # PhysicsEngine, Vec2D, GameState
│   │   └── constants.py        # Game constants
│   ├── llm_adapter/
│   │   ├── __init__.py
│   │   └── adapter.py          # LLMAdapter, prompt building
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── match_orchestrator.py  # MatchOrchestrator
│   ├── replay/
│   │   ├── __init__.py
│   │   ├── recorder.py         # ReplayRecorder
│   │   └── loader.py           # ReplayLoader
│   ├── web_server/
│   │   ├── __init__.py
│   │   └── main.py             # FastAPI app
│   ├── tests/
│   │   ├── test_physics.py
│   │   ├── test_llm_adapter.py
│   │   └── test_orchestrator.py
│   ├── requirements.txt
│   └── main.py                 # Entry point
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── GameCanvas.jsx
│   │   │   ├── ThinkingPanel.jsx
│   │   │   ├── ReplayControls.jsx
│   │   │   └── MatchList.jsx
│   │   ├── hooks/
│   │   │   ├── useCanvas.js
│   │   │   ├── useGameState.js
│   │   │   └── usePlayback.js
│   │   ├── utils/
│   │   │   ├── rendering.js
│   │   │   └── geometry.js
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── README.md
├── replays/                    # Generated replay files
│   └── *.json
├── docs/
│   ├── architecture.md         # This document
│   └── api.md
└── README.md
```

---

**Document History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-13 | Architecture Workflow | Initial complete version |

---

**End of Architecture Document**

This document provides a complete, production-ready architecture for AI Arena. All components are designed with clear boundaries for future microservices extraction while maintaining simplicity for the MVP. The implementation patterns are detailed enough for AI agent implementation.
