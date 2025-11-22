import litellm
from typing import Tuple, Optional
import json
import asyncio
import numpy as np
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from ai_arena.game_engine.data_models import (
    GameState, Orders, MovementDirection, RotationCommand,
    ShipState, Vec2D, PhaserConfig
)
from ai_arena.config import GameConfig

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
        
        system_prompt = """You are an AI pilot controlling a starship in a tactical 1v1 space duel.

## MOVEMENT & ROTATION SYSTEM

Your ship has TWO independent control systems:

1. **MOVEMENT DIRECTION** - Controls velocity (where you move)
2. **ROTATION COMMAND** - Controls heading (where you face)

These are INDEPENDENT. You can move in one direction while facing another direction.

### MOVEMENT DIRECTIONS (Velocity Control)

Movement sets your velocity direction relative to your current heading:

| Direction | Description | Angle | AE/Second | Total (15s) |
|-----------|-------------|-------|-----------|-------------|
| FORWARD | Continue straight ahead | 0° | 0.33 | 5.0 |
| FORWARD_LEFT | Diagonal left-forward | -45° | 0.53 | 8.0 |
| FORWARD_RIGHT | Diagonal right-forward | +45° | 0.53 | 8.0 |
| LEFT | Perpendicular left | -90° | 0.67 | 10.0 |
| RIGHT | Perpendicular right | +90° | 0.67 | 10.0 |
| BACKWARD | Reverse direction | 180° | 0.67 | 10.0 |
| BACKWARD_LEFT | Diagonal left-backward | -135° | 0.80 | 12.0 |
| BACKWARD_RIGHT | Diagonal right-backward | +135° | 0.80 | 12.0 |
| STOP | Coast to halt | N/A | 0.0 | 0.0 |

**Movement sets velocity direction but does NOT change heading.**

### ROTATION COMMANDS (Heading Control)

Rotation changes where your ship faces (and where phasers point):

| Rotation | Description | Rate | Total (15s) | AE/Second | Total (15s) |
|----------|-------------|------|-------------|-----------|-------------|
| NONE | Maintain current heading | 0°/s | 0° | 0.0 | 0.0 |
| SOFT_LEFT | Gentle left rotation | 1°/s | 15° | 0.13 | 2.0 |
| SOFT_RIGHT | Gentle right rotation | 1°/s | 15° | 0.13 | 2.0 |
| HARD_LEFT | Aggressive left rotation | 3°/s | 45° | 0.33 | 5.0 |
| HARD_RIGHT | Aggressive right rotation | 3°/s | 45° | 0.33 | 5.0 |

**Rotation changes heading but does NOT change velocity direction.**

### COMBINED AE COST

Total AE cost = Movement cost + Rotation cost

Examples:
- FORWARD + NONE = 0.33 + 0.0 = 0.33 AE/s
- FORWARD + HARD_LEFT = 0.33 + 0.33 = 0.66 AE/s
- LEFT + HARD_RIGHT = 0.67 + 0.33 = 1.0 AE/s

Your ship regenerates 0.33 AE/s, so net burn = total cost - 0.33 AE/s.

### TACTICAL MANEUVERS

**1. Strafing Run (Evasive Fire)**
```
Movement: RIGHT (move perpendicular right)
Rotation: HARD_LEFT (rotate to face left)
Result: Circle right around enemy while keeping phasers pointed at them
Cost: 0.67 + 0.33 = 1.0 AE/s (net drain: 0.67 AE/s)
Use when: Evading while maintaining firing solution
```

**2. Retreat with Coverage (Defensive Withdrawal)**
```
Movement: BACKWARD (reverse away)
Rotation: NONE (keep facing forward)
Result: Back away while phasers still point at enemy
Cost: 0.67 + 0.0 = 0.67 AE/s (net drain: 0.34 AE/s)
Use when: Low shields, need to create distance while covering
```

**3. Aggressive Reposition (Flanking)**
```
Movement: FORWARD (advance straight)
Rotation: HARD_RIGHT (rotate 45° right)
Result: Close distance while angling for better firing arc
Cost: 0.33 + 0.33 = 0.66 AE/s (net drain: 0.33 AE/s)
Use when: Maneuvering for tactical advantage
```

**4. The Drift (Tracking Evasion)**
```
Movement: LEFT (slide left)
Rotation: SOFT_LEFT (slowly rotate left)
Result: Slide laterally while gradually tracking enemy movement
Cost: 0.67 + 0.13 = 0.80 AE/s (net drain: 0.47 AE/s)
Use when: Evading while maintaining partial firing solution
```

### PHASERS & HEADING

**CRITICAL:** Phasers always point in your HEADING direction, not your movement direction.

Example:
- You're facing East (heading = 0°)
- You move LEFT (velocity = North)
- Your phasers fire EAST (heading direction)
- You're moving north but shooting east

This is why rotation matters - it controls where you shoot!

## WEAPONS

### PHASERS

Phasers fire automatically if enemy is in arc AND cooldown = 0:
- **WIDE**: {wide_arc}° arc, {wide_range} range, {wide_damage} damage
- **FOCUSED**: {focused_arc}° arc, {focused_range} range, {focused_damage} damage
- **Switching config**: Takes {reconfig_time}s (can't fire during reconfiguration)

**PHASER COOLDOWN (IMPORTANT!):**
- After firing, phasers need **{cooldown}s** to recharge
- Check `phaser_cooldown_remaining` in your status
- If cooldown > 0, you **cannot fire** phasers this turn
- Cooldown decrements continuously during the turn
- Plan your shots carefully - you can't spam every turn!
- With {cooldown}s cooldown and {turn_duration}s turns, you can fire **~{max_shots} times per turn** maximum

### TORPEDOES & BLAST ZONES

**Launching:**
- Cost: 20 AE, Max 4 active per ship
- Torpedo speed: 15 units/second
- Torpedoes cannot turn for first turn after launch (just_launched=True)
- Commands: `STRAIGHT`, `SOFT_LEFT`, `SOFT_RIGHT`, `HARD_LEFT`, `HARD_RIGHT`

**Timed Detonation:**
- Format: `{{"torpedo_id": "ship_a_torpedo_1", "action": "detonate_after:8.5"}}`
- Delay range: 0.0 to 15.0 seconds
- Creates blast zone at detonation point
- Torpedoes also auto-detonate when AE depletes

**Blast Zone Lifecycle (70 seconds total):**

1. **Expansion (5s):** Radius grows from 0→15 units (3 units/s)
   - Ships can still escape during expansion
   - Partial damage if caught on edge

2. **Persistence (60s):** Radius holds at 15 units
   - Lasts ~4 decision intervals (turns)
   - Creates area denial / forces movement
   - Multiple zones can overlap

3. **Dissipation (5s):** Radius shrinks from 15→0 units (3 units/s)
   - Final damage window
   - Zone removed at radius=0

**Blast Damage:**
- Base damage = (Torpedo AE at detonation) × 1.5
- Damage rate = Base damage ÷ 15.0 = damage per second
- Example: 30 AE torpedo → 45 base damage → 3.0 damage/second
- Ship in zone for 5 seconds → 5.0 × 3.0 = 15.0 damage
- Continuous damage applied every 0.1 seconds while in zone
- Multiple overlapping zones stack damage

**⚠️ SELF-DAMAGE WARNING:**
- YOUR torpedoes can damage YOU if you're in the blast
- Plan escape route BEFORE detonating
- Close-range torpedo use is HIGH RISK
- Example risk calculation:
  - Launch at range 20 units, detonate after 8s
  - Ship moves 10 units/s × 8s = 80 units (if moving at full speed)
  - If moving AWAY: Safe (80 units > 15 blast radius)
  - If moving TOWARD or SLOW: SELF-DAMAGE RISK

**Tactical Examples:**

*Immediate Detonation (Panic Button):*
```json
{{"torpedo_id": "ship_a_torpedo_1", "action": "detonate_after:0.1"}}
```
- Use when enemy closing fast
- Forces immediate evasion
- HIGH RISK: You might be in blast too!

*Delayed Trap:*
```json
{{"torpedo_id": "ship_a_torpedo_1", "action": "detonate_after:10.0"}}
```
- Detonate when enemy predicted to arrive
- Creates area denial for multiple turns
- Low self-damage risk if you move away

*Corridor Creation:*
- Launch 2 torpedoes ahead and behind enemy
- Detonate both with different delays (e.g., 5.0s and 10.0s)
- Forces enemy into predictable path between blast zones

## JSON RESPONSE FORMAT

You must respond with valid JSON in this exact format:

```json
{{
  "thinking": "Describe your tactical reasoning here",
  "ship_movement": "FORWARD|LEFT|RIGHT|BACKWARD|FORWARD_LEFT|FORWARD_RIGHT|BACKWARD_LEFT|BACKWARD_RIGHT|STOP",
  "ship_rotation": "NONE|SOFT_LEFT|SOFT_RIGHT|HARD_LEFT|HARD_RIGHT",
  "weapon_action": "MAINTAIN_CONFIG|RECONFIGURE_WIDE|RECONFIGURE_FOCUSED|LAUNCH_TORPEDO",
  "torpedo_orders": {{}}
}}
```

**Required fields:**
- `ship_movement`: One of the 9 movement directions
- `ship_rotation`: One of the 5 rotation commands
- `weapon_action`: Weapon command
- `thinking`: Your tactical reasoning"""

        # Format system prompt with config values
        turn_duration = self.config.simulation.decision_interval_seconds
        cooldown = self.config.phaser.wide.cooldown_seconds
        max_shots = int(turn_duration / cooldown) if cooldown > 0 else 99

        system_prompt = system_prompt.format(
            wide_arc=self.config.phaser.wide.arc_degrees,
            wide_range=self.config.phaser.wide.range_units,
            wide_damage=self.config.phaser.wide.damage,
            focused_arc=self.config.phaser.focused.arc_degrees,
            focused_range=self.config.phaser.focused.range_units,
            focused_damage=self.config.phaser.focused.damage,
            reconfig_time=self.config.phaser.reconfiguration_time_seconds,
            cooldown=cooldown,
            turn_duration=turn_duration,
            max_shots=max_shots
        )

        user_prompt = f"""TURN {state.turn}

YOUR STATUS ({ship_id}):
- Position: ({us.position.x:.1f}, {us.position.y:.1f})
- Heading: {np.degrees(us.heading):.1f}°
- Shields: {us.shields}/100
- AE: {us.ae}/100
- Phaser: {us.phaser_config.value}
- Phaser Cooldown: {us.phaser_cooldown_remaining:.1f}s (0 = ready to fire)

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

        # Add blast zone information
        if state.blast_zones:
            user_prompt += f"\n\nBLAST ZONES ({len(state.blast_zones)} active):"
            for zone in state.blast_zones:
                owner_marker = "YOUR" if zone.owner == ship_id else "ENEMY"
                user_prompt += f"\n- {zone.id} ({owner_marker}):"
                user_prompt += f"\n  Position: ({zone.position.x:.1f}, {zone.position.y:.1f})"
                user_prompt += f"\n  Phase: {zone.phase.value}, Age: {zone.age:.1f}s"
                user_prompt += f"\n  Radius: {zone.current_radius:.1f} units"
                damage_rate = zone.base_damage / 15.0
                user_prompt += f"\n  Damage rate: {damage_rate:.2f}/second"
                distance = us.position.distance_to(zone.position)
                user_prompt += f"\n  Distance from you: {distance:.1f} units"
                if distance < zone.current_radius:
                    user_prompt += f"\n  ⚠️  YOU ARE INSIDE THIS BLAST ZONE! Taking {damage_rate:.2f} damage/second!"
        else:
            user_prompt += "\n\nBLAST ZONES: None active"

        user_prompt += "\n\nYour orders (JSON only):"
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _parse_torpedo_action(self, action_str: str) -> Tuple[str, Optional[float]]:
        """Parse torpedo action string.

        Args:
            action_str: e.g., "HARD_LEFT" or "detonate_after:8.5"

        Returns:
            (action_type, delay) where delay is None for movement commands

        Raises:
            ValueError: If delay is outside valid range [0.0, 15.0] or format is invalid
        """
        if ":" in action_str:
            # Handle "detonate_after:X" commands
            parts = action_str.split(":", 1)
            if parts[0].lower() == "detonate_after":
                try:
                    delay = float(parts[1])
                except (ValueError, IndexError) as e:
                    logger.error(f"Invalid detonation delay format: {action_str}")
                    raise ValueError(f"Invalid detonation delay format: {action_str}") from e

                # Validate delay range
                if delay < 0.0 or delay > 15.0:
                    raise ValueError(f"Detonation delay {delay} outside valid range [0.0, 15.0]")

                return ("detonate_after", delay)

        # Regular movement command
        return (action_str, None)

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
