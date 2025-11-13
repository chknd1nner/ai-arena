from typing import Optional, Tuple
from ai_arena.game_engine.data_models import GameState, Orders, MatchConfig, MatchResult, ShipState, Vec2D, PhaserConfig
from ai_arena.llm_adapter.adapter import LLMAdapter
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.replay.recorder import ReplayRecorder

class MatchOrchestrator:
    def __init__(self, model_a: str, model_b: str):
        self.model_a = model_a
        self.model_b = model_b
        self.llm_adapter = LLMAdapter(model_a, model_b)
        self.physics_engine = PhysicsEngine()
        self.replay_recorder = ReplayRecorder(model_a, model_b)

    async def run_match(self, max_turns: int) -> dict:
        """Run a complete match and return results."""
        print(f"Starting match between {self.model_a} and {self.model_b}")
        
        state = self._initialize_match()
        
        for turn in range(1, max_turns + 1):
            print(f"Turn {turn}")
            
            orders_a, thinking_a, orders_b, thinking_b = await self.llm_adapter.get_orders_for_both_ships(state)
            
            # Store state before physics resolution for replay
            state_for_replay = self.physics_engine._copy_state(state)

            new_state, events = self.physics_engine.resolve_turn(state, orders_a, orders_b)
            
            self.replay_recorder.record_turn(turn, state_for_replay, orders_a, orders_b, thinking_a, thinking_b, events)
            
            state = new_state
            
            winner = self._check_win_condition(state)
            if winner:
                print(f"Match over! Winner: {winner}")
                final_data = self.replay_recorder.finalize(winner, turn)
                final_data['status'] = 'completed'
                return final_data

        print("Match ended due to max turns reached.")
        final_data = self.replay_recorder.finalize("tie", max_turns)
        final_data['status'] = 'completed'
        return final_data

    def _initialize_match(self) -> GameState:
        """Initializes the game state."""
        
        ship_a = ShipState(
            position=Vec2D(100.0, 250.0),
            velocity=Vec2D(0.0, 0.0),
            heading=0.0, # Facing right
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE,
            reconfiguring_phaser=False,
        )
        ship_b = ShipState(
            position=Vec2D(900.0, 250.0),
            velocity=Vec2D(0.0, 0.0),
            heading=3.14159, # pi, facing left
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE,
            reconfiguring_phaser=False,
        )
        
        return GameState(turn=0, ship_a=ship_a, ship_b=ship_b, torpedoes=[])

    def _check_win_condition(self, state: GameState) -> Optional[str]:
        """Checks if there is a winner."""
        a_dead = state.ship_a.shields <= 0
        b_dead = state.ship_b.shields <= 0

        if a_dead and b_dead:
            return "tie"
        if a_dead:
            return "ship_b"
        if b_dead:
            return "ship_a"
        return None
    
    def get_match_id(self) -> str:
        return self.replay_recorder.match_id
