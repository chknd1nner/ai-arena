# AI Arena: 1v1 Space Duel

This document provides a high-level overview of the AI Arena project for Gemini.

## Project Summary

AI Arena is a 1v1 space combat simulation where two large language models (LLMs) pilot starships. The project aims to be an entertaining AI benchmark, showcasing AI decision-making and strategy. The system is built as a modular monolith, with a Python backend and a React frontend for visualization.

## Technology Stack

-   **Backend**:
    -   Language: Python 3.11+
    -   Web Framework: FastAPI
    -   LLM Integration: LiteLLM
    -   Vector Math: NumPy
-   **Frontend**:
    -   Framework: React 18
    -   Rendering: Canvas 2D API
    -   Package Manager: npm
-   **Database/Storage**:
    -   Replays: JSON files stored on the local filesystem (initially).

## Project Structure

```
.
├── ai_arena/            # Python backend source code
│   ├── game_engine/
│   │   ├── __init__.py
│   │   ├── data_models.py
│   │   └── physics.py
│   ├── llm_adapter/
│   │   ├── __init__.py
│   │   └── adapter.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── match_orchestrator.py
│   ├── replay/
│   │   ├── __init__.py
│   │   └── recorder.py
│   ├── web_server/
│   │   ├── __init__.py
│   │   └── main.py
│   └── __init__.py
├── frontend/            # React frontend source code
│   ├── public/
│   ├── src/
│   └── package.json
├── docs/
│   ├── architecture.md
│   └── game_spec.md
├── replays/             # Directory for match replay files
├── .gitignore
├── main.py              # Main application entrypoint
├── gemini.md
└── requirements.txt
```

## Key Components

-   **Match Orchestrator**: Manages the match lifecycle, from setup to completion.
-   **Game Engine**: A pure, deterministic physics simulation for ship and projectile movement.
-   **LLM Adapter**: Interfaces with various LLM providers via LiteLLM to get ship orders.
-   **Replay System**: Records and loads match data from JSON files.
-   **Web Server (FastAPI)**: Serves the frontend and provides a REST API for match data.
-   **React Frontend**: Visualizes the game, including the 2D battle and the LLMs' "thinking tokens".

## How to Run

### Backend

```bash
# From the project root
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

The backend server will run on `http://localhost:8000`.

### Frontend

```bash
# From the project root
cd frontend
npm install
npm start
```

The frontend development server will run on `http://localhost:3000`.

## Git Repository

The project is version-controlled with Git. The remote repository will be hosted on your GitHub profile.
