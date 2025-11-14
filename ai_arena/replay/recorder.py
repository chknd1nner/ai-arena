import json
import os
from datetime import datetime
from pathlib import Path
from typing import List
import copy

from ai_arena.game_engine.data_models import GameState, Orders, Event, ShipState, TorpedoState, Vec2D, MovementType, PhaserConfig

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
            "weapon_action": orders.weapon_action,
            "torpedo_orders": {
                tid: move.value 
                for tid, move in orders.torpedo_orders.items()
            }
        }
    
    def _serialize_event(self, event: Event) -> dict:
        # A simple way to serialize dataclasses that might contain other non-serializable types
        e = copy.deepcopy(event)
        e.data = self._serialize_dict(e.data)
        return e.__dict__

    def _serialize_dict(self, data: dict) -> dict:
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return data


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
        for replay_file in sorted(replay_dir.glob("*.json"), key=os.path.getmtime, reverse=True):
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
        
        return matches
