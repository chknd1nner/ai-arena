"""
Mock LLM Adapter for testing matches without API calls.

Provides deterministic, scripted orders for testing match orchestration,
physics interactions, and replay systems without burning API credits.
"""

from typing import Optional, List, Tuple, Callable
from enum import Enum
import numpy as np

from ai_arena.game_engine.data_models import (
    GameState, Orders, ShipState,
    MovementDirection, RotationCommand, PhaserConfig
)
from ai_arena.config import GameConfig


class TacticalStrategy(Enum):
    """Pre-defined tactical strategies for mock matches."""

    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    TORPEDO_SPAM = "torpedo_spam"
    FOCUSED_PHASER = "focused_phaser"
    STRAFE_MASTER = "strafe_master"
    DRIFT_SPECIALIST = "drift_specialist"


class MockLLMAdapter:
    """Mock LLM adapter for deterministic testing without API calls.

    Supports two modes:
    1. Script mode: Pre-defined list of orders per ship
    2. Strategy mode: Named tactical strategies that adapt to game state

    Examples:
        # Script mode - exact orders for each turn
        script_a = [
            Orders(MovementDirection.FORWARD, RotationCommand.NONE, "MAINTAIN_CONFIG"),
            Orders(MovementDirection.LEFT, RotationCommand.HARD_LEFT, "MAINTAIN_CONFIG"),
        ]
        adapter = MockLLMAdapter(config, script_a=script_a)

        # Strategy mode - adaptive behaviors
        adapter = MockLLMAdapter(
            config,
            strategy_a=TacticalStrategy.AGGRESSIVE,
            strategy_b=TacticalStrategy.DEFENSIVE
        )

        # Mixed mode - one scripted, one strategy-based
        adapter = MockLLMAdapter(
            config,
            script_a=script_a,
            strategy_b=TacticalStrategy.BALANCED
        )
    """

    def __init__(
        self,
        config: GameConfig,
        script_a: Optional[List[Orders]] = None,
        script_b: Optional[List[Orders]] = None,
        strategy_a: TacticalStrategy = TacticalStrategy.BALANCED,
        strategy_b: TacticalStrategy = TacticalStrategy.BALANCED,
        custom_strategy_a: Optional[Callable[[GameState, ShipState, ShipState], Orders]] = None,
        custom_strategy_b: Optional[Callable[[GameState, ShipState, ShipState], Orders]] = None
    ):
        """Initialize mock adapter with scripts or strategies.

        Args:
            config: Game configuration
            script_a: Optional pre-defined orders for ship A (overrides strategy)
            script_b: Optional pre-defined orders for ship B (overrides strategy)
            strategy_a: Tactical strategy for ship A (used if no script)
            strategy_b: Tactical strategy for ship B (used if no script)
            custom_strategy_a: Optional custom strategy function for ship A
            custom_strategy_b: Optional custom strategy function for ship B
        """
        self.config = config
        self.script_a = script_a or []
        self.script_b = script_b or []
        self.strategy_a = strategy_a
        self.strategy_b = strategy_b
        self.custom_strategy_a = custom_strategy_a
        self.custom_strategy_b = custom_strategy_b
        self.turn = 0

        # Initialize strategy implementations
        self._strategy_funcs = {
            TacticalStrategy.AGGRESSIVE: self._aggressive_strategy,
            TacticalStrategy.DEFENSIVE: self._defensive_strategy,
            TacticalStrategy.BALANCED: self._balanced_strategy,
            TacticalStrategy.TORPEDO_SPAM: self._torpedo_spam_strategy,
            TacticalStrategy.FOCUSED_PHASER: self._focused_phaser_strategy,
            TacticalStrategy.STRAFE_MASTER: self._strafe_master_strategy,
            TacticalStrategy.DRIFT_SPECIALIST: self._drift_specialist_strategy,
        }

    async def get_orders_for_both_ships(
        self,
        state: GameState
    ) -> Tuple[Orders, str, Orders, str]:
        """Get orders from both ships (synchronous, deterministic).

        Returns:
            Tuple of (orders_a, thinking_a, orders_b, thinking_b)
        """
        # Ship A orders
        if self.turn < len(self.script_a):
            orders_a = self.script_a[self.turn]
            thinking_a = f"[SCRIPTED] Turn {self.turn + 1}: Following pre-defined orders"
        elif self.custom_strategy_a:
            orders_a = self.custom_strategy_a(state, state.ship_a, state.ship_b)
            thinking_a = f"[CUSTOM STRATEGY] Turn {self.turn + 1}"
        else:
            strategy_func = self._strategy_funcs[self.strategy_a]
            orders_a = strategy_func(state, state.ship_a, state.ship_b)
            thinking_a = f"[{self.strategy_a.value.upper()}] Turn {self.turn + 1}: Adaptive tactical decision"

        # Ship B orders
        if self.turn < len(self.script_b):
            orders_b = self.script_b[self.turn]
            thinking_b = f"[SCRIPTED] Turn {self.turn + 1}: Following pre-defined orders"
        elif self.custom_strategy_b:
            orders_b = self.custom_strategy_b(state, state.ship_b, state.ship_a)
            thinking_b = f"[CUSTOM STRATEGY] Turn {self.turn + 1}"
        else:
            strategy_func = self._strategy_funcs[self.strategy_b]
            orders_b = strategy_func(state, state.ship_b, state.ship_a)
            thinking_b = f"[{self.strategy_b.value.upper()}] Turn {self.turn + 1}: Adaptive tactical decision"

        self.turn += 1
        return orders_a, thinking_a, orders_b, thinking_b

    # ========================================================================
    # Strategy Implementations
    # ========================================================================

    def _aggressive_strategy(
        self,
        state: GameState,
        my_ship: ShipState,
        enemy_ship: ShipState
    ) -> Orders:
        """Aggressive strategy: Close distance and engage with phasers.

        Behavior:
        - Move forward when distant
        - Strafe (perpendicular movement) when close
        - Rotate to track enemy
        - Maintain WIDE phasers for easier hits
        """
        distance = my_ship.position.distance_to(enemy_ship.position)

        # Calculate angle to enemy
        dx = enemy_ship.position.x - my_ship.position.x
        dy = enemy_ship.position.y - my_ship.position.y
        angle_to_enemy = np.arctan2(dy, dx)

        # Normalize angle difference
        angle_diff = angle_to_enemy - my_ship.heading
        angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))

        # Decide rotation based on angle to enemy
        if abs(angle_diff) < 0.1:  # Already facing enemy
            rotation = RotationCommand.NONE
        elif angle_diff > 0:
            rotation = RotationCommand.HARD_LEFT if abs(angle_diff) > 0.5 else RotationCommand.SOFT_LEFT
        else:
            rotation = RotationCommand.HARD_RIGHT if abs(angle_diff) > 0.5 else RotationCommand.SOFT_RIGHT

        # Decide movement based on distance
        if distance > 150:
            # Far away: Move forward to close distance
            movement = MovementDirection.FORWARD
        elif distance > 80:
            # Medium range: Strafe right while rotating to track
            movement = MovementDirection.RIGHT
        else:
            # Close range: Strafe left to circle
            movement = MovementDirection.LEFT

        # Low shields: Consider retreating
        if my_ship.shields < 30:
            movement = MovementDirection.BACKWARD

        return Orders(
            movement=movement,
            rotation=rotation,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

    def _defensive_strategy(
        self,
        state: GameState,
        my_ship: ShipState,
        enemy_ship: ShipState
    ) -> Orders:
        """Defensive strategy: Maintain distance and cover retreat.

        Behavior:
        - Keep distance from enemy
        - Face enemy while retreating (covering fire)
        - Switch to FOCUSED for long-range accuracy
        - Launch torpedoes when enemy closes
        """
        distance = my_ship.position.distance_to(enemy_ship.position)

        # Calculate angle to enemy
        dx = enemy_ship.position.x - my_ship.position.x
        dy = enemy_ship.position.y - my_ship.position.y
        angle_to_enemy = np.arctan2(dy, dx)

        # Normalize angle difference
        angle_diff = angle_to_enemy - my_ship.heading
        angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))

        # Always try to face enemy
        if abs(angle_diff) < 0.1:
            rotation = RotationCommand.NONE
        elif angle_diff > 0:
            rotation = RotationCommand.SOFT_LEFT
        else:
            rotation = RotationCommand.SOFT_RIGHT

        # Movement: Maintain safe distance
        if distance < 100:
            # Too close: retreat while facing enemy
            movement = MovementDirection.BACKWARD
        elif distance < 150:
            # Medium distance: strafe to maintain range
            movement = MovementDirection.LEFT if state.turn % 2 == 0 else MovementDirection.RIGHT
        else:
            # Far enough: stop and aim
            movement = MovementDirection.STOP

        # Weapon action: Use FOCUSED for range
        if my_ship.phaser_config == PhaserConfig.WIDE and not my_ship.reconfiguring_phaser:
            weapon_action = "RECONFIGURE_FOCUSED"
        else:
            weapon_action = "MAINTAIN_CONFIG"

        return Orders(
            movement=movement,
            rotation=rotation,
            weapon_action=weapon_action,
            torpedo_orders={}
        )

    def _balanced_strategy(
        self,
        state: GameState,
        my_ship: ShipState,
        enemy_ship: ShipState
    ) -> Orders:
        """Balanced strategy: Adapt based on situation.

        Behavior:
        - Aggressive when shields high
        - Defensive when shields low
        - Manage energy carefully
        """
        # Switch between aggressive and defensive based on shields
        if my_ship.shields > 60:
            return self._aggressive_strategy(state, my_ship, enemy_ship)
        elif my_ship.shields < 40:
            return self._defensive_strategy(state, my_ship, enemy_ship)
        else:
            # Medium shields: cautious engagement
            distance = my_ship.position.distance_to(enemy_ship.position)

            if distance > 120:
                movement = MovementDirection.FORWARD
            else:
                movement = MovementDirection.LEFT  # Strafe

            # Minimal rotation to conserve energy
            dx = enemy_ship.position.x - my_ship.position.x
            dy = enemy_ship.position.y - my_ship.position.y
            angle_to_enemy = np.arctan2(dy, dx)
            angle_diff = angle_to_enemy - my_ship.heading
            angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))

            if abs(angle_diff) < 0.2:
                rotation = RotationCommand.NONE
            elif angle_diff > 0:
                rotation = RotationCommand.SOFT_LEFT
            else:
                rotation = RotationCommand.SOFT_RIGHT

            return Orders(
                movement=movement,
                rotation=rotation,
                weapon_action="MAINTAIN_CONFIG",
                torpedo_orders={}
            )

    def _torpedo_spam_strategy(
        self,
        state: GameState,
        my_ship: ShipState,
        enemy_ship: ShipState
    ) -> Orders:
        """Torpedo spam strategy: Focus on torpedo attacks.

        Behavior:
        - Launch torpedoes when AE is high
        - Maintain distance for torpedo effectiveness
        - Guide torpedoes toward enemy
        """
        distance = my_ship.position.distance_to(enemy_ship.position)

        # Count active torpedoes
        my_torpedoes = [t for t in state.torpedoes if t.owner == ("ship_a" if my_ship == state.ship_a else "ship_b")]

        # Weapon action: Launch torpedo if we can
        if my_ship.ae >= self.config.torpedo.launch_cost_ae and len(my_torpedoes) < 4:
            weapon_action = "LAUNCH_TORPEDO"
        else:
            weapon_action = "MAINTAIN_CONFIG"

        # Movement: Maintain medium range
        if distance < 100:
            movement = MovementDirection.BACKWARD
        elif distance > 200:
            movement = MovementDirection.FORWARD
        else:
            movement = MovementDirection.STOP  # Conserve energy for torpedoes

        # Minimal rotation
        rotation = RotationCommand.NONE

        return Orders(
            movement=movement,
            rotation=rotation,
            weapon_action=weapon_action,
            torpedo_orders={}
        )

    def _focused_phaser_strategy(
        self,
        state: GameState,
        my_ship: ShipState,
        enemy_ship: ShipState
    ) -> Orders:
        """Focused phaser strategy: Use FOCUSED phasers for precision.

        Behavior:
        - Reconfigure to FOCUSED if needed
        - Maintain long range
        - Precise aiming
        """
        # Ensure FOCUSED configuration
        if my_ship.phaser_config == PhaserConfig.WIDE and not my_ship.reconfiguring_phaser:
            weapon_action = "RECONFIGURE_FOCUSED"
        else:
            weapon_action = "MAINTAIN_CONFIG"

        distance = my_ship.position.distance_to(enemy_ship.position)

        # Stay at optimal FOCUSED range (longer than WIDE)
        if distance < 120:
            movement = MovementDirection.BACKWARD
        elif distance > 180:
            movement = MovementDirection.FORWARD
        else:
            movement = MovementDirection.STOP

        # Precise rotation to track enemy
        dx = enemy_ship.position.x - my_ship.position.x
        dy = enemy_ship.position.y - my_ship.position.y
        angle_to_enemy = np.arctan2(dy, dx)
        angle_diff = angle_to_enemy - my_ship.heading
        angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))

        if abs(angle_diff) < 0.05:
            rotation = RotationCommand.NONE
        elif angle_diff > 0:
            rotation = RotationCommand.SOFT_LEFT
        else:
            rotation = RotationCommand.SOFT_RIGHT

        return Orders(
            movement=movement,
            rotation=rotation,
            weapon_action=weapon_action,
            torpedo_orders={}
        )

    def _strafe_master_strategy(
        self,
        state: GameState,
        my_ship: ShipState,
        enemy_ship: ShipState
    ) -> Orders:
        """Strafe master strategy: Constant perpendicular movement with hard rotation.

        Behavior:
        - Always strafing (LEFT or RIGHT movement)
        - Hard rotation to track enemy
        - Demonstrates independent movement/rotation
        """
        # Alternate strafe direction
        movement = MovementDirection.RIGHT if state.turn % 2 == 0 else MovementDirection.LEFT

        # Always hard rotate to track enemy
        dx = enemy_ship.position.x - my_ship.position.x
        dy = enemy_ship.position.y - my_ship.position.y
        angle_to_enemy = np.arctan2(dy, dx)
        angle_diff = angle_to_enemy - my_ship.heading
        angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))

        if abs(angle_diff) < 0.1:
            rotation = RotationCommand.NONE
        elif angle_diff > 0:
            rotation = RotationCommand.HARD_LEFT
        else:
            rotation = RotationCommand.HARD_RIGHT

        return Orders(
            movement=movement,
            rotation=rotation,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

    def _drift_specialist_strategy(
        self,
        state: GameState,
        my_ship: ShipState,
        enemy_ship: ShipState
    ) -> Orders:
        """Drift specialist strategy: Perpendicular movement with soft rotation.

        Behavior:
        - Drift (LEFT movement with SOFT rotation)
        - Gradual enemy tracking
        - Energy efficient
        """
        # Always drift left
        movement = MovementDirection.LEFT

        # Soft rotation to gradually track enemy
        dx = enemy_ship.position.x - my_ship.position.x
        dy = enemy_ship.position.y - my_ship.position.y
        angle_to_enemy = np.arctan2(dy, dx)
        angle_diff = angle_to_enemy - my_ship.heading
        angle_diff = np.arctan2(np.sin(angle_diff), np.cos(angle_diff))

        if abs(angle_diff) < 0.2:
            rotation = RotationCommand.NONE
        elif angle_diff > 0:
            rotation = RotationCommand.SOFT_LEFT
        else:
            rotation = RotationCommand.SOFT_RIGHT

        return Orders(
            movement=movement,
            rotation=rotation,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )


def create_scripted_orders(movements: List[str], rotations: List[str] = None, weapons: List[str] = None) -> List[Orders]:
    """Helper to quickly create scripted orders from string lists.

    Args:
        movements: List of movement direction strings (e.g., ["FORWARD", "LEFT"])
        rotations: List of rotation command strings (default: all NONE)
        weapons: List of weapon action strings (default: all MAINTAIN_CONFIG)

    Returns:
        List of Orders objects

    Example:
        >>> orders = create_scripted_orders(
        ...     ["FORWARD", "RIGHT", "BACKWARD"],
        ...     ["HARD_LEFT", "NONE", "SOFT_RIGHT"],
        ...     ["MAINTAIN_CONFIG", "LAUNCH_TORPEDO", "MAINTAIN_CONFIG"]
        ... )
    """
    rotations = rotations or ["NONE"] * len(movements)
    weapons = weapons or ["MAINTAIN_CONFIG"] * len(movements)

    if not (len(movements) == len(rotations) == len(weapons)):
        raise ValueError("movements, rotations, and weapons must have same length")

    orders_list = []
    for mov, rot, weap in zip(movements, rotations, weapons):
        orders_list.append(Orders(
            movement=MovementDirection[mov],
            rotation=RotationCommand[rot],
            weapon_action=weap,
            torpedo_orders={}
        ))

    return orders_list
