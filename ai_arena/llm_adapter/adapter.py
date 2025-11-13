import litellm
from typing import Tuple
import json
import asyncio
import numpy as np
import os
from dotenv import load_dotenv

from ai_arena.game_engine.data_models import GameState, Orders, MovementType, ShipState, Vec2D, PhaserConfig

load_dotenv()

# Set API keys from environment variables
litellm.api_key = os.getenv("OPENAI_API_KEY")
litellm.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
litellm.groq_api_key = os.getenv("GROQ_API_KEY")


class LLMAdapter:
    """
    Abstracts LLM provider complexity.
    Constructs prompts, parses responses, handles errors.
    """
    
    def __init__(self, model_a: str, model_b: str):
        """
        model format: "provider/model"
        Examples: "anthropic/claude-3-haiku-20240307", "gpt-4", "groq/llama3-8b-8192"
        """
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
            return_exceptions=True  # Don't let one failure kill both
        )
        
        # Handle potential errors
        orders_a, thinking_a = self._handle_result(results[0])
        orders_b, thinking_b = self._handle_result(results[1])
        
        return orders_a, thinking_a, orders_b, thinking_b
    
    def _handle_result(self, result):
        """Handle potential exceptions from gather."""
        if isinstance(result, Exception):
            print(f"LLM error: {result}")
            return (
                self._default_orders(),
                f"ERROR: {str(result)}"
            )
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
                model=model,
                messages=prompt,
                max_tokens=1000,
                temperature=0.7,
                timeout=30.0,
                response_format={ "type": "json_object" }
            )
            
            response_text = response.choices[0].message.content
            orders, thinking = self._parse_orders(response_text, state, ship_id)
            
            return orders, thinking
            
        except litellm.Timeout:
            print(f"LLM timeout for {ship_id}")
            return self._default_orders(), "TIMEOUT"
        except Exception as e:
            print(f"LLM error for {ship_id}: {e}")
            return self._default_orders(), f"ERROR: {str(e)}"
    
    def _build_prompt(self, state: GameState, ship_id: str) -> list:
        """Build prompt with game state and rules."""
        us = state.ship_a if ship_id == "ship_a" else state.ship_b
        enemy = state.ship_b if ship_id == "ship_a" else state.ship_a
        our_torpedoes = [t for t in state.torpedoes if t.owner == ship_id]
        enemy_torpedoes = [t for t in state.torpedoes if t.owner != ship_id]
        
        system_prompt = """You are piloting a starship in 1v1 combat.

WEAPONS:
- Phasers: Fire automatically if enemy in arc
  - WIDE: 90° arc, 30 range, 15 damage
  - FOCUSED: 10° arc, 50 range, 35 damage
  - Switching config takes 1 turn (can't fire)
- Torpedoes: Independent projectiles
  - Launch: 20 AE, max 4 in flight
  - Damage = (AE remaining) × 1.5
  - Blast radius: 15 units

MOVEMENT (AE cost):
- STRAIGHT (5) - Continue heading
- SOFT_LEFT/RIGHT (7) - 15° turn
- HARD_LEFT/RIGHT (10) - 45° turn
- REVERSE (8) - 180° turn
- STOP (0) - No movement

RESPOND WITH JSON ONLY, matching this exact format:
{
  "thinking": "Your reasoning for your chosen actions. Analyze the situation and explain your strategy in 2-3 sentences.",
  "movement": "STRAIGHT",
  "weapon": "NONE",
  "torpedo_controls": {
    "your_torpedo_id_1": "STRAIGHT"
  }
}"""
        
        user_prompt = f"""TURN {state.turn}

YOUR STATUS ({ship_id}):
- Position: ({us.position.x:.1f}, {us.position.y:.1f})
- Heading: {np.degrees(us.heading):.1f}°
- Shields: {us.shields}/100
- AE: {us.ae}/100
- Phaser: {us.phaser_config.value}

ENEMY:
- Position: ({enemy.position.x:.1f}, {enemy.position.y:.1f})
- Shields: {enemy.shields}/100
- Distance: {us.position.distance_to(enemy.position):.1f} units

YOUR TORPEDOES ({len(our_torpedoes)}/4):"""
        
        for t in our_torpedoes:
            user_prompt += f"\n- {t.id}: pos ({t.position.x:.1f}, {t.position.y:.1f}), AE {t.ae_remaining}"
        
        user_prompt += f"\n\nENEMY TORPEDOES ({len(enemy_torpedoes)}):"
        for t in enemy_torpedoes:
            user_prompt += f"\n- {t.id}: pos ({t.position.x:.1f}, {t.position.y:.1f}), AE {t.ae_remaining}"

        user_prompt += "\n\nYour orders (JSON only):"
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _parse_orders(
        self, 
        response_text: str, 
        state: GameState, 
        ship_id: str
    ) -> Tuple[Orders, str]:
        """Parse LLM response into Orders object."""
        try:
            parsed = json.loads(response_text)
            thinking = parsed.get("thinking", "No reasoning provided.")
            
            # Extract and validate movement
            movement_str = parsed.get("movement", "STOP").upper()
            try:
                movement = MovementType[movement_str]
            except KeyError:
                print(f"Invalid movement '{movement_str}', using STOP")
                movement = MovementType.STOP
            
            # Extract weapon action
            weapon = parsed.get("weapon", "NONE").upper()
            
            # Extract torpedo controls
            torpedo_orders = {}
            if "torpedo_controls" in parsed:
                for tid, move in parsed["torpedo_controls"].items():
                    try:
                        torpedo_orders[tid] = MovementType[move.upper()]
                    except KeyError:
                        torpedo_orders[tid] = MovementType.STRAIGHT
            
            return Orders(movement, weapon, torpedo_orders), thinking
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response: {response_text[:200]}")
            return self._default_orders(), "JSON PARSE ERROR"
        except Exception as e:
            print(f"Unexpected parse error: {e}")
            return self._default_orders(), "UNEXPECTED PARSE ERROR"
    
    def _default_orders(self) -> Orders:
        """Safe default orders when parsing fails."""
        return Orders(
            movement=MovementType.STOP,
            weapon_action="NONE",
            torpedo_orders={}
        )
