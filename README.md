# AI Arena: 1v1 Space Duel

AI Arena is a 1v1 space combat simulation where two large language models pilot starships in real-time tactical battles. Watch AIs reason, predict, and battle in transparent, entertaining matches.

## Quick Start

### Prerequisites

- Python 3.11+
- API keys for LLM providers (OpenAI, Anthropic, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/chknd1nner/ai-arena.git
cd ai-arena

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Running the Application

**Backend (Python 3.11+):**
```bash
# On macOS, use python3 explicitly
python3 main.py
```

The backend API will start on `http://localhost:8000`.

**Frontend (React):**
```bash
# IMPORTANT: Must run from frontend/ directory
cd frontend
npm install  # First time only
npm start    # Runs on http://localhost:3000
```

**Both Servers (for full app):**

Open two terminal windows:

Terminal 1:
```bash
python3 main.py
```

Terminal 2:
```bash
cd frontend
npm start
```

Then visit `http://localhost:3000` in your browser.

### API Usage

**Start a match:**
```bash
curl -X POST http://localhost:8000/api/match/start \
  -H "Content-Type: application/json" \
  -d '{
    "model_a": "gpt-4",
    "model_b": "anthropic/claude-3-haiku-20240307",
    "max_turns": 20
  }'
```

**Check match status:**
```bash
curl http://localhost:8000/api/match/{match_id}
```

**Get replay:**
```bash
curl http://localhost:8000/api/match/{match_id}/replay
```

**List all matches:**
```bash
curl http://localhost:8000/api/matches
```

## Features

### 🧠 Transparent AI Reasoning

Watch both AIs think in real-time! AI Arena displays thinking tokens side-by-side, showing you exactly how each model makes tactical decisions.

**Key Features:**
- **Split-screen layout** showing both AIs' reasoning simultaneously
- **Color-coded by ship** (Ship A: blue, Ship B: red) for easy tracking
- **Toggle visibility** with one click or press 'T' to hide/show
- **Beautiful typography** with monospace font for maximum readability
- **Updates in real-time** as you navigate through match turns
- **Match summary** at the end showing winner and final thoughts

**Why it matters:**

AI Arena isn't just about watching ships move — it's about understanding how AIs think. See competing strategies unfold, spot brilliant predictions, witness tactical miscalculations, and understand the reasoning behind every decision.

This transparent reasoning is what makes AI Arena compelling for spectators, content creators, and AI researchers alike. The tactical simulation is the stage; the AI reasoning is the show.

**Usage:**
- Thinking tokens display automatically when viewing replays
- Press **T** to toggle thinking panel visibility
- Navigate turns with arrow keys to see how AI reasoning evolves
- Match summary appears automatically at the end of each match

## Project Structure

```
ai-arena/
├── ai_arena/              # Python backend source
│   ├── game_engine/       # Physics simulation
│   ├── llm_adapter/       # LLM integration via LiteLLM
│   ├── orchestrator/      # Match coordination
│   ├── replay/            # Match recording and loading
│   └── web_server/        # FastAPI REST API
├── frontend/              # React frontend (MUST cd here to run npm)
│   ├── src/
│   │   ├── components/    # React components (CanvasRenderer, etc.)
│   │   └── utils/         # Utilities (coordinate transforms)
│   └── package.json
├── docs/                  # Architecture and game spec
├── replays/               # Saved match replays (JSON)
├── config.json            # Game balance parameters
├── main.py                # Backend entry point
└── requirements.txt       # Python dependencies
```

## How It Works

1. **Match Orchestrator** coordinates the battle lifecycle
2. **LLM Adapter** calls both AI models in parallel for orders
3. **Game Engine** simulates 60 seconds of real-time physics per turn
4. **Replay System** records every turn for deterministic playback
5. **Web Server** provides REST API for match control

## Game Mechanics

- **Ships**: Each has shields, AE (energy), phasers, and torpedoes
- **Phasers**: Auto-firing energy weapons (WIDE or FOCUSED configs)
- **Torpedoes**: Controlled projectiles with independent movement
- **Movement**: 9 types (STRAIGHT, HARD_LEFT, REVERSE, etc.)
- **Physics**: Deterministic 60 Hz simulation for replay consistency

## Documentation

- **[CLAUDE.md](CLAUDE.md)** - Development guide for AI assistants
- **[docs/architecture.md](docs/architecture.md)** - Complete system architecture
- **[docs/game_spec_revised.md](docs/game_spec_revised.md)** - Detailed game mechanics

## Development

See [CLAUDE.md](CLAUDE.md) for comprehensive development guidance.

## License

MIT

## Author

Martin Kuek (martin.kuek@gmail.com)
