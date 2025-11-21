# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Arena is a 1v1 space combat simulation where two large language models pilot starships in real-time tactical battles. The system is a modular monolith written in Python with FastAPI backend and React frontend for visualization.

## Development Commands

**Important:** This project uses Python 3. On macOS, use `python3` and `pip3` commands instead of `python` and `pip`.

### Running the Application

**Backend:**
```bash
# Start the backend server (runs on http://localhost:8000)
python3 main.py

# Alternative: Direct uvicorn command
uvicorn ai_arena.web_server.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
# From the project root
cd frontend
npm install  # First time only
npm start    # Runs on http://localhost:3000
```

### Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Unix/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

### Environment Configuration

Copy the example file and add your API keys:
```bash
cp .env.example .env
# Edit .env and add your actual API keys
```

`.env` file should contain:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_physics.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=ai_arena
```

### Testing Matches

Start a match via API:
```bash
curl -X POST http://localhost:8000/api/match/start \
  -H "Content-Type: application/json" \
  -d '{"model_a": "gpt-4", "model_b": "anthropic/claude-3-haiku-20240307", "max_turns": 20}'
```

Or use the frontend at `http://localhost:3000` and click "Start New Match".

## Architecture

### High-Level Structure

The system follows a **modular monolith** pattern with clear component boundaries:

```
Match Orchestrator
    ├─> LLM Adapter (LiteLLM)
    ├─> Game Engine (Physics)
    └─> Replay System (JSON)
         └─> Web Server (FastAPI)
```

### Core Components

1. **Match Orchestrator** (`ai_arena/orchestrator/match_orchestrator.py`)
   - Coordinates match lifecycle from initialization to completion
   - Manages turn loop: get orders → resolve physics → record state
   - Detects win conditions (shields ≤ 0)
   - Entry point: `async def run_match(max_turns: int)`

2. **Game Engine** (`ai_arena/game_engine/physics.py`)
   - Pure, stateless physics simulation with fixed timestep (60 Hz)
   - Each turn = 60 simulated seconds split into 3600 substeps
   - Core function: `resolve_turn(state, orders_a, orders_b) -> (new_state, events)`
   - Handles ship movement, phaser firing, torpedo collisions
   - **Critical**: Physics must be deterministic for replay system

3. **LLM Adapter** (`ai_arena/llm_adapter/adapter.py`)
   - Abstracts LLM providers via LiteLLM library
   - Constructs prompts from game state, parses JSON responses
   - Calls both models in parallel using `asyncio.gather()`
   - Handles timeouts, retries, and parsing errors with safe defaults
   - Returns: `(orders_a, thinking_a, orders_b, thinking_b)`

4. **Replay System** (`ai_arena/replay/recorder.py`)
   - Records every turn to JSON for deterministic replay
   - Saves to `replays/` directory with timestamped filenames
   - `ReplayRecorder`: Records turn-by-turn state and events (new format: `"models": {ship_a, ship_b}`)
   - `ReplayLoader`: Loads replays for API endpoints (supports both old and new formats for backward compatibility)

5. **Web Server** (`ai_arena/web_server/main.py`)
   - FastAPI application serving REST API
   - Endpoints: `/api/match/start`, `/api/match/{id}`, `/api/matches`, `/api/match/{id}/replay`
   - Uses background tasks for async match execution
   - CORS enabled for React dev server (port 3000)

6. **Frontend** (`frontend/`)
   - React 18 application for match visualization
   - Simple UI to start matches and view results
   - Proxy configured to backend on port 8000
   - Future: Canvas-based real-time match viewer with replay controls

### Data Models

All core data structures defined in `ai_arena/game_engine/data_models.py`:

- **GameState**: Complete game state (turn, ship_a, ship_b, torpedoes)
- **ShipState**: Position, velocity, heading, shields, AE, phaser config
- **TorpedoState**: Independent projectile with position, velocity, AE, owner
- **Orders**: LLM commands (movement, weapon_action, torpedo_orders)
- **MovementType**: Enum of movement commands (STRAIGHT, HARD_LEFT, etc.)
- **PhaserConfig**: WIDE or FOCUSED (arc, range, and damage values configured in `config.json`)

### Physics Constants

From `ai_arena/game_engine/physics.py`:
- Fixed timestep: 1/60 second (60 Hz)
- Action phase: 60 seconds per turn (3600 substeps)
- Ship speed: 10 units/second
- Torpedo speed: 15 units/second
- Movement costs: STRAIGHT=5, HARD_LEFT/RIGHT=10, STOP=0 AE
- Phaser reconfiguration blocks firing for one turn

## Key Design Patterns

### 1. Deterministic Physics
- Fixed timestep simulation guarantees same inputs → same outputs
- No randomness in physics engine
- Critical for replay system - replays reconstruct state without re-simulation
- All angles in radians for consistency

### 2. Interface-Based Component Boundaries
- Components communicate through well-defined interfaces
- Stateless where possible (especially physics engine)
- Designed for future extraction to microservices if needed
- Pure functions: `resolve_turn()` takes state + orders, returns new state + events

### 3. LLM Provider Abstraction
- LiteLLM provides unified API for 100+ providers
- Model specified as string: `"gpt-4"`, `"anthropic/claude-3-haiku-20240307"`, `"groq/llama3-8b-8192"`
- Async parallel calls to both models for efficiency
- Graceful degradation: parsing errors return safe default orders (STOP movement)

### 4. Async Match Execution
- Matches run as background tasks (FastAPI BackgroundTasks)
- API returns immediately with match_id and "running" status
- Poll `/api/match/{id}` for completion status
- Prevents LLM API latency from blocking HTTP requests

## Important Implementation Details

### LLM Prompt Structure
- System prompt: Game rules, weapon mechanics, JSON response format
- User prompt: Current state (positions, shields, AE, torpedoes)
- Response format enforced: `response_format={"type": "json_object"}`
- Models receive complete battlefield visibility (no fog of war)

### Order Validation
- Physics engine validates orders before execution in `_validate_orders()`
- Insufficient AE → order changed to STOP
- Invalid movement strings → default to STOP
- Torpedo commands validated against active torpedoes

### Turn Resolution Sequence
1. Parse LLM orders (simultaneous for both ships)
2. Validate orders and deduct movement AE costs
3. Apply weapon actions (torpedo launches, phaser reconfig)
4. Simulate 60 seconds with 3600 physics substeps
5. Check for phaser hits (arc-crossing detection)
6. Check for torpedo collisions (blast radius 15 units)
7. Regenerate 5 AE per ship per turn
8. Record turn to replay system

### Phaser Mechanics
- Phasers fire automatically if enemy enters arc (not manual)
- No cooldown system in current implementation (fires once per turn if in arc)
- Reconfiguring blocks firing for that turn
- Hit detection: range check + arc check using angle difference

### Torpedo Mechanics
- Launch cost: 20 AE, max 4 active per ship
- Damage = AE_remaining × 1.5 on collision
- Torpedoes burn ~1 AE per second while flying
- Just-launched torpedoes cannot turn on first turn
- Auto-detonates when AE reaches 0

## Project Configuration

### Game Balance Parameters

All tunable game parameters are in `config.json`:
- Ship stats (speed, AE regen, starting shields)
- Movement costs and rotation rates
- Phaser configurations (arc, range, damage)
- Torpedo mechanics (speed, AE capacity, blast radius)
- Arena dimensions

Edit these values to balance gameplay without changing code.

## Testing and Development Workflow

### Manual Testing Flow
1. Start backend: `python3 main.py`
2. Start frontend: `cd frontend && npm start`
3. Open `http://localhost:3000` and click "Start New Match"
4. Watch match status update in real-time
5. Inspect replays in `replays/` directory

**Important:** Frontend commands MUST be run from `frontend/` directory, not project root.

### Running Both Servers for Automated Testing

When using Playwright or other automation tools that need both servers running:

**Option 1: Manual Background Processes**
```bash
# From project root
python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

cd frontend && npm start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for servers to be ready
sleep 30

# Run your tests
python3 your_test_script.py

# Clean up
kill $BACKEND_PID $FRONTEND_PID
```

**Option 2: Using Playwright's with_server.py Helper**
```bash
# Requires full paths and directory changes in commands
python3 /path/to/with_server.py \
  --server "python3 main.py" --port 8000 \
  --server "cd frontend && npm start" --port 3000 \
  --timeout 90 \
  -- python3 validate_canvas.py
```

**Common Issue:** `npm start` will fail if run from project root. Always `cd frontend` first.

### API Testing Flow
1. Start server: `python3 main.py`
2. Send POST to `/api/match/start` with model names
3. Poll `/api/match/{match_id}` until status = "completed"
4. Fetch replay JSON from `/api/match/{match_id}/replay`

### Unit Testing
```bash
# Run tests
pytest

# Add new tests in tests/ directory
# Test naming: test_*.py
```

### Adding New Movement Types
1. Add enum to `MovementType` in `data_models.py`
2. Add cost to `MOVEMENT_COSTS` dict in `physics.py`
3. Add rotation parameter to `MOVEMENT_PARAMS` dict
4. Update LLM system prompt in `adapter.py`

### Modifying Physics
- All physics in `physics.py`: `resolve_turn()` is entry point
- Keep simulation deterministic - avoid randomness
- Update `FIXED_TIMESTEP`, `ACTION_PHASE_DURATION`, or `SUBSTEPS` together
- Test replay reproduction after changes

### Debugging LLM Issues
- Check console output for "LLM error" or "JSON parse error"
- Inspect `thinking_a` and `thinking_b` in replay JSON
- Verify API keys in `.env` file
- Test with smaller models first (Haiku, GPT-3.5-turbo)
- Use `response_format={"type": "json_object"}` to enforce JSON

## Common Pitfalls

1. **Frontend Working Directory**: `npm start` MUST be run from `frontend/` directory, not project root. Running from root causes "ENOENT: no such file or directory, open 'package.json'" error.
2. **Port Conflicts**: Backend (8000) and frontend (3000) must both be available. Use `lsof -ti:8000 | xargs kill -9` and `lsof -ti:3000 | xargs kill -9` to clear ports.
3. **Async Context**: Match orchestrator methods must be async, use `await` for LLM calls
4. **Replay Directory**: `replays/` directory must exist or will be created automatically
5. **API Key Environment**: LiteLLM reads keys from both `.env` and environment variables
6. **Model String Format**: Some providers need prefix (e.g., `"anthropic/claude-..."`), others don't (e.g., `"gpt-4"`)
7. **Physics Modifications**: Changing SUBSTEPS without updating ACTION_PHASE_DURATION breaks time scaling
8. **JSON Response Format**: LLMs must return exact format expected by `_parse_orders()` or get default STOP orders
9. **Headless Browser Testing**: Playwright runs in headless mode by default - no visible browser window. Screenshots saved to `/tmp/` for validation.
10. **Replay Format Compatibility**: `ReplayLoader.list_matches()` and `ReplayLoader.load()` support both old format (with `model_a`/`model_b` fields) and new format (with `models` object). New replays use the new format; old test replays use the old format. Both work seamlessly via backward compatibility logic.

## Epic 006: Thinking Tokens Visualization (Complete)

**Status:** ✅ Production Ready
**Completion Date:** 2025-11-18

### Overview

The thinking tokens visualization system makes AI reasoning transparent and entertaining - the core value proposition of AI Arena. This epic implemented a production-ready UI for displaying LLM thinking tokens side-by-side with maximum polish.

### Components

**1. ThinkingPanel Component** (`frontend/src/components/ThinkingPanel.jsx`)

Displays AI thinking tokens in a split-screen layout with color theming and excellent readability.

**Component API:**
```javascript
<ThinkingPanel
  thinkingA={string}           // Ship A's thinking tokens
  thinkingB={string}           // Ship B's thinking tokens
  turnNumber={number}          // Current turn (0-indexed)
  modelA={string}              // Model name for Ship A
  modelB={string}              // Model name for Ship B
  isVisible={boolean}          // Toggle visibility
  previousThinkingA={string}   // Previous turn (optional)
  previousThinkingB={string}   // Previous turn (optional)
/>
```

**Key Features:**
- Split-screen layout: Ship A (left, blue) | Ship B (right, red)
- Monospace typography for code-like readability (14px, 1.6 line height)
- Scrollable for long thinking tokens (max-height: 400px)
- Handles edge cases: empty, null, very long thinking
- Memoized with React.memo for performance
- Smooth fade-in animation (300ms)
- Responsive: vertical stacking on screens <1024px

**2. MatchSummary Component** (`frontend/src/components/MatchSummary.jsx`)

Displays compelling end-of-match summary with winner announcement and final thinking tokens.

**Features:**
- Victory announcement with color-coded winner
- Animated trophy icon with bounce effect
- Match statistics (total turns, match ID)
- Final thinking tokens preview (truncated to 300 chars)
- "Watch Again" button (resets to turn 0)
- "Back to Matches" button (reloads page)
- Responsive design with vertical stacking on mobile

**3. Thinking Formatter Utilities** (`frontend/src/utils/thinkingFormatter.js`)

Utility functions for formatting and processing thinking tokens:
- `formatThinking()`: Trims whitespace, handles null/empty
- `hasStructuredFormat()`: Detects JSON, lists, section formatting
- `highlightSyntax()`: Framework for syntax highlighting
- `calculateDiff()`: Framework for diff highlighting
- `truncateThinking()`: Truncates for previews (default: 200 chars)

### Integration

**ReplayViewer Integration:**

ThinkingPanel is integrated into ReplayViewer with these additions:
- Toggle button in Match Info Header
- Keyboard shortcut: **T key** toggles visibility
- Automatic display at start (default: visible)
- Auto-display MatchSummary 1 second after reaching final turn
- Backward-compatible model name extraction (supports old and new replay formats)

**Data Flow:**
```
Replay JSON → ReplayViewer → ThinkingPanel
  ├─ turns[n].thinking_a
  ├─ turns[n].thinking_b
  ├─ model_a (or models.ship_a)
  └─ model_b (or models.ship_b)
```

### Styling

All styles are in `frontend/src/App.css`:
- **Thinking Panel Styles** (lines 88-262)
- **Syntax Highlighting** (lines 264-306)
- **Match Summary Styles** (lines 308-489)

**Design System:**
- **Colors**: Ship A (#4A90E2 blue), Ship B (#E24A4A red)
- **Background**: #1a1a1a (dark gray)
- **Text**: #e0e0e0 (light gray)
- **Spacing**: 8px grid system
- **Typography**: Monaco, Menlo, Consolas (monospace)
- **Transitions**: 300ms standard duration
- **Shadows**: Subtle (0 4px 6px rgba(0,0,0,0.3))

### Keyboard Shortcuts

Added to ReplayViewer:
- **T**: Toggle thinking panel visibility
- **Space**: Play/Pause (existing)
- **← →**: Previous/Next turn (existing)
- **Home/End**: First/Last turn (existing)

### Usage

**Viewing Thinking Tokens:**
1. Load any replay in ReplayViewer
2. Thinking panel displays automatically above canvas
3. Navigate turns with arrow keys to see reasoning evolution
4. Press T to toggle panel visibility

**Match Summary:**
1. Navigate to final turn of match
2. Wait 1 second (or pause playback)
3. MatchSummary appears automatically
4. Click "Watch Again" to replay from turn 0

### Performance

- **Turn navigation**: <100ms update time (React.memo optimization)
- **Memory usage**: <50MB additional overhead
- **Render performance**: 60 FPS maintained
- **Loading time**: <2s on normal connection

### Edge Cases Handled

1. **Empty thinking tokens**: Displays "(No thinking tokens available for this turn)"
2. **Null/undefined**: Same fallback, no crash
3. **Very long thinking**: Scrollable with custom scrollbar
4. **Special characters**: Preserved with <pre> tag
5. **Narrow screens**: Vertical stacking for mobile
6. **Missing model names**: Falls back to "Unknown Model A/B"

### Files Modified

**Created:**
- `frontend/src/components/ThinkingPanel.jsx` (91 lines)
- `frontend/src/components/MatchSummary.jsx` (96 lines)
- `frontend/src/utils/thinkingFormatter.js` (99 lines)

**Modified:**
- `frontend/src/components/ReplayViewer.jsx` (added ThinkingPanel integration)
- `frontend/src/App.css` (added 445 lines of styles)

### Design Philosophy

> "Thinking tokens are not a side feature — they ARE the feature. The tactical simulation is just the stage. The AI reasoning is the show."

**Principles:**
1. Maximum readability above all else
2. Thinking tokens are the visual centerpiece
3. Polish should feel subtle, not flashy
4. Every pixel counts - sweat the details
5. Production-ready means stream-worthy

### Future Enhancements

**Implemented (v1.0):**
- ✅ Basic thinking token display
- ✅ Split-screen layout
- ✅ Toggle visibility
- ✅ Match summary
- ✅ Responsive design
- ✅ Smooth animations

**Potential Future Work:**
- Full syntax highlighting for structured thinking
- Diff highlighting (changes from previous turn)
- Copy to clipboard button
- Collapsible sections for long thinking
- Searchable thinking history
- Export thinking tokens to file

### Accessibility

- Semantic HTML with proper heading hierarchy
- ARIA labels for screen readers
- Keyboard navigation support (T key toggle)
- Color contrast meets WCAG AA standards (4.5:1 minimum)
- Focus indicators visible on interactive elements

### Browser Compatibility

Tested and working on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Documentation References

- **Full Architecture**: `docs/architecture.md` - Complete system design, ADRs, deployment
- **Game Specification**: `docs/game_spec_revised.md` - Detailed mechanics, real-time physics, combat system
- **Original Design Notes**: `gemini.md` - Project summary and initial structure

## Future Enhancements

The architecture is designed for future extraction to microservices:
- Game Engine → HTTP service: `POST /resolve-turn`
- LLM Adapter → Gateway service with rate limiting
- React frontend for visualization (planned, directory structure exists)
- WebSocket support for live match streaming (Phase 3)
- Tournament mode with multiple matches (Phase 2)
- Always remember to keep the repo tidy. After merging a feature, clean up the redundant branch