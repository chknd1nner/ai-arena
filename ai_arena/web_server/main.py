from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import asyncio

from ai_arena.orchestrator.match_orchestrator import MatchOrchestrator
from ai_arena.replay.recorder import ReplayLoader

app = FastAPI(title="AI Arena API")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory match tracking (MVP - use database in production)
active_matches: Dict[str, Dict] = {}

# Models
class StartMatchRequest(BaseModel):
    model_a: str = "gpt-4"
    model_b: str = "anthropic/claude-3-haiku-20240307"
    max_turns: int = 20

class StartMatchResponse(BaseModel):
    match_id: str
    status: str

async def run_match_background(orchestrator: MatchOrchestrator, max_turns: int):
    match_id = orchestrator.get_match_id()
    try:
        result = await orchestrator.run_match(max_turns)
        active_matches[match_id]['status'] = 'completed'
        active_matches[match_id]['result'] = result
    except Exception as e:
        print(f"Error running match {match_id}: {e}")
        active_matches[match_id]['status'] = 'error'
        active_matches[match_id]['error'] = str(e)


@app.post("/api/match/start", response_model=StartMatchResponse)
async def start_match(request: StartMatchRequest, background_tasks: BackgroundTasks):
    """Start a new match."""
    orchestrator = MatchOrchestrator(request.model_a, request.model_b)
    match_id = orchestrator.get_match_id()
    
    active_matches[match_id] = {"status": "running", "orchestrator": orchestrator}
    
    background_tasks.add_task(run_match_background, orchestrator, request.max_turns)
    
    return StartMatchResponse(match_id=match_id, status="running")

@app.get("/api/match/{match_id}")
async def get_match_status(match_id: str):
    """Get match status."""
    if match_id not in active_matches:
        # Check if it's a completed match from replay
        try:
            replay = ReplayLoader.load(match_id)
            return {
                "match_id": match_id,
                "status": "completed",
                "winner": replay.get("winner"),
                "total_turns": replay.get("total_turns")
            }
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Match not found")

    
    match_info = active_matches[match_id]
    status = match_info['status']
    
    response = {"match_id": match_id, "status": status}

    if status == 'completed':
        result = match_info.get('result', {})
        response['winner'] = result.get('winner')
        response['total_turns'] = result.get('total_turns')
    elif status == 'error':
        response['error'] = match_info.get('error')

    return response

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
