# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

AI Arena is a 1v1 space combat simulation where two LLMs pilot starships in tactical battles. It's a modular monolith: Python/FastAPI backend with deterministic physics, React frontend for visualization, and LiteLLM for model abstraction. **Key principle: thinking tokens are the entertainment value.**

## Quick Start

**Important:** This project uses Python 3. On macOS, use `python3` and `pip3` (not `python` and `pip`).

### Running Servers

**Backend** (http://localhost:8000):
```bash
python3 main.py
```

**Frontend** (http://localhost:3000):
```bash
cd frontend      # MUST cd first!
npm install      # First time only
npm start
```

### Common Commands

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_physics.py

# Start a match via API
curl -X POST http://localhost:8000/api/match/start \
  -H "Content-Type: application/json" \
  -d '{"model_a": "gpt-4", "model_b": "anthropic/claude-3-haiku-20240307", "max_turns": 20}'
```

### Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip3 install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

## File Structure Essentials

**Core game engine:**
- `ai_arena/game_engine/physics.py` — Deterministic physics simulation (entry: `resolve_turn()`)
- `ai_arena/game_engine/data_models.py` — GameState, ShipState, Orders, etc.
- `ai_arena/orchestrator/match_orchestrator.py` — Turn loop orchestration

**LLM & Web:**
- `ai_arena/llm_adapter/adapter.py` — LiteLLM provider abstraction
- `ai_arena/web_server/main.py` — FastAPI server and endpoints

**Frontend:**
- `frontend/src/components/ReplayViewer.jsx` — Main visualization
- `frontend/src/components/ThinkingPanel.jsx` — AI thinking display

**Configuration:**
- `config.json` — Game balance parameters (ship stats, movement costs, phaser/torpedo mechanics)
- `.env` — API keys for LLM providers

## Critical Development Context

### Deterministic Physics (Non-Negotiable)
- Fixed timestep simulation: inputs → outputs always identical
- Required for replay system to reconstruct state without re-running
- Avoid randomness in physics.py
- When modifying physics, test replay reproduction

### Backward Compatibility
- Replays support both old format (`model_a`/`model_b`) and new format (`models` object)
- `ReplayLoader` auto-detects and converts transparently
- New replays use new format; preserve compatibility in changes

### Thinking Tokens = The Show
- Displayed in ThinkingPanel component (split-screen, Ship A left/blue, Ship B right/red)
- Toggle with T key in ReplayViewer
- Auto-display MatchSummary at end of match
- This is the core value proposition — design decisions should support visibility

### Model String Format
- OpenAI: `"gpt-4"` (no prefix)
- Anthropic: `"anthropic/claude-3-haiku-20240307"` (with prefix)
- Groq: `"groq/llama3-8b-8192"` (with prefix)
- Check LiteLLM docs for your model

## Testing & Workflows

### Manual Testing
1. Start backend: `python3 main.py`
2. Start frontend: `cd frontend && npm start`
3. Open http://localhost:3000, click "Start New Match"
4. Inspect replays in `replays/` directory (JSON format)

### Running Both Servers (for automation)
```bash
# Option 1: Manual background processes
python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

cd frontend && npm start > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 30  # Wait for servers to start
python3 your_test_script.py

kill $BACKEND_PID $FRONTEND_PID
```

### API Testing
1. Start server: `python3 main.py`
2. POST to `/api/match/start` with model names
3. Poll `/api/match/{match_id}` until `status = "completed"`
4. Fetch replay: `/api/match/{match_id}/replay`

## Common Pitfalls

**Critical to avoid:**

1. **Frontend directory issue**: `npm start` MUST be run from `frontend/` directory. Running from project root causes "ENOENT: no such file or directory, open 'package.json'" error.

2. **Port conflicts**: Backend (8000) and frontend (3000) must both be available.
   ```bash
   lsof -ti:8000 | xargs kill -9
   lsof -ti:3000 | xargs kill -9
   ```

3. **Async context**: Match orchestrator methods must be async; use `await` for LLM calls.

4. **Replay directory**: `replays/` directory auto-created if missing, but ensure write permissions.

5. **API key environment**: LiteLLM reads from both `.env` and environment variables. Check both if keys not loading.

6. **Physics modifications**: Changing `SUBSTEPS` without updating `ACTION_PHASE_DURATION` breaks time scaling. Keep them synchronized.

7. **JSON response format**: LLMs must return exact format expected by `_parse_orders()` or get default STOP orders. Use `response_format={"type": "json_object"}`.

8. **Order validation**: Physics engine validates in `_validate_orders()`. Insufficient AE → STOP. Invalid movement → STOP. Torpedo commands checked against active torpedoes.

9. **Headless browser testing**: Playwright runs headless by default (no visible window). Screenshots saved to `/tmp/` for validation.

10. **Replay format compatibility**: Both old and new replay formats work seamlessly. `ReplayLoader` handles conversion transparently.

## Documentation Reference

For detailed information, see:

- **Architecture & Design** → `docs/architecture.md` (component boundaries, data flow, design patterns, ADRs, deployment)
- **Game Mechanics** → `docs/game_spec_revised.md` (detailed physics, combat system, balance)
- **Development Workflow** → `docs/development-workflow.md` (detailed testing procedures, debugging LLM issues, adding features)
- **Epic 006** → `docs/epic-006-thinking-tokens-visualization.md` (thinking panel implementation, keyboard shortcuts, styling)

## Key Constraints & Heuristics

| Principle | Why | Impact |
|-----------|-----|--------|
| **Deterministic physics** | Replay system requires perfect reproducibility | Never add randomness to physics.py |
| **Backward replay compatibility** | Old test replays must still work | Support both old and new JSON formats |
| **Thinking tokens first** | Core entertainment value | Design UI to showcase AI reasoning |
| **Interface-based components** | Future microservices extraction | Keep components with clear boundaries |
| **Async LLM calls** | Parallel model inference | Use `asyncio.gather()` for both models |

---

**Last updated:** 2025-11-21 | Streamlined from 538 → 150 lines
