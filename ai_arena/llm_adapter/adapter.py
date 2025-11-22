import litellm
from typing import Tuple, Optional
import json
import asyncio
import numpy as np
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from ai_arena.game_engine.data_models import (
    GameState, Orders, MovementDirection, RotationCommand,
    ShipState, Vec2D, PhaserConfig
)
from ai_arena.config import GameConfig
from ai_arena.llm_adapter.prompt_formatter import (
    build_user_prompt,
    format_system_prompt_with_config
)

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

    # Cache for loaded system prompt
    _system_prompt_cache: Optional[str] = None

    def __init__(self, model_a: str, model_b: str, config: GameConfig):
        """
        model format: "provider/model"
        Examples: "anthropic/claude-3-haiku-20240307", "gpt-4", "groq/llama3-8b-8192"

        Args:
            model_a: Model identifier for ship A
            model_b: Model identifier for ship B
            config: Game configuration (for dynamic prompt generation)
        """
        self.model_a = model_a
        self.model_b = model_b
        self.config = config
        self._load_system_prompt()
    
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
    
    def _load_system_prompt(self):
        """Load system prompt from file and cache it (class-level cache)."""
        if LLMAdapter._system_prompt_cache is None:
            # Find prompts directory relative to this file
            prompts_dir = Path(__file__).parent.parent / "prompts"
            prompt_file = prompts_dir / "pilot_system_prompt.md"

            if not prompt_file.exists():
                raise FileNotFoundError(
                    f"System prompt file not found: {prompt_file}\n"
                    f"Expected location: ai_arena/prompts/pilot_system_prompt.md"
                )

            with open(prompt_file, 'r') as f:
                LLMAdapter._system_prompt_cache = f.read()

            logger.info(f"Loaded system prompt from {prompt_file}")

    def _build_prompt(self, state: GameState, ship_id: str) -> list:
        """Build prompt with game state and rules.

        Args:
            state: Current game state
            ship_id: "ship_a" or "ship_b"

        Returns:
            List of message dicts for LLM API
        """
        # Get cached system prompt and format with config values
        system_prompt = format_system_prompt_with_config(
            LLMAdapter._system_prompt_cache,
            self.config
        )

        # Build user prompt from game state
        user_prompt = build_user_prompt(state, ship_id)

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
        """Parse LLM response into Orders object.

        Args:
            response_text: Raw JSON string from LLM
            state: Current game state
            ship_id: "ship_a" or "ship_b" for error logging

        Returns:
            Tuple of (Orders object, thinking string)
        """
        try:
            parsed = json.loads(response_text)
            thinking = parsed.get("thinking", "No reasoning provided.")

            # Parse movement direction (NEW)
            movement_str = parsed.get("ship_movement", "STOP").upper()
            try:
                movement = MovementDirection[movement_str]
            except KeyError:
                logger.warning(f"{ship_id} invalid movement '{movement_str}', defaulting to STOP")
                movement = MovementDirection.STOP

            # Parse rotation command (NEW)
            rotation_str = parsed.get("ship_rotation", "NONE").upper()
            try:
                rotation = RotationCommand[rotation_str]
            except KeyError:
                logger.warning(f"{ship_id} invalid rotation '{rotation_str}', defaulting to NONE")
                rotation = RotationCommand.NONE

            # Extract weapon action
            weapon_action = parsed.get("weapon_action", "MAINTAIN_CONFIG")

            # Extract torpedo controls (now stores raw action strings)
            # Supports both movement commands ("HARD_LEFT") and detonation ("detonate_after:8.5")
            torpedo_orders = {}
            if "torpedo_orders" in parsed:
                for tid, action in parsed["torpedo_orders"].items():
                    # Store raw action string - will be parsed in physics engine
                    torpedo_orders[tid] = str(action).strip()

            return Orders(
                movement=movement,
                rotation=rotation,
                weapon_action=weapon_action,
                torpedo_orders=torpedo_orders
            ), thinking

        except json.JSONDecodeError as e:
            logger.error(f"{ship_id} JSON parse error: {e}")
            logger.error(f"Response: {response_text[:200]}")
            return self._default_orders(), "JSON PARSE ERROR"
        except Exception as e:
            logger.error(f"{ship_id} unexpected parse error: {e}")
            return self._default_orders(), "UNEXPECTED PARSE ERROR"
    
    def _default_orders(self) -> Orders:
        """Safe default orders when parsing fails."""
        return Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
