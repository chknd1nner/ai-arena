"""
Shared game engine utilities.

This module contains shared functions used across the game engine.
"""
from typing import Tuple, Optional
import copy
import logging

logger = logging.getLogger(__name__)


def parse_torpedo_action(action_str: str) -> Tuple[str, Optional[float]]:
    """Parse torpedo action string.

    Args:
        action_str: Action string, e.g., "HARD_LEFT" or "detonate_after:8.5"

    Returns:
        Tuple of (action_type, delay) where delay is None for movement commands

    Raises:
        ValueError: If delay is outside valid range [0.0, 15.0] or format is invalid

    Examples:
        >>> parse_torpedo_action("HARD_LEFT")
        ("HARD_LEFT", None)

        >>> parse_torpedo_action("detonate_after:8.5")
        ("detonate_after", 8.5)
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


def deep_copy_game_state(state):
    """Deep copy a GameState object.

    Creates a new GameState with deep copies of all nested objects.

    Args:
        state: GameState object to copy

    Returns:
        Deep copy of the GameState

    Note:
        Uses dataclass reconstruction to ensure proper copying of all fields.
        Vec2D objects are also deep copied to ensure independence.
    """
    from ai_arena.game_engine.data_models import GameState, ShipState, TorpedoState, BlastZone, Vec2D

    def copy_ship(ship):
        """Deep copy a ShipState including Vec2D objects."""
        return ShipState(
            position=Vec2D(ship.position.x, ship.position.y),
            velocity=Vec2D(ship.velocity.x, ship.velocity.y),
            heading=ship.heading,
            shields=ship.shields,
            ae=ship.ae,
            phaser_config=ship.phaser_config,
            reconfiguring_phaser=ship.reconfiguring_phaser,
            phaser_cooldown_remaining=ship.phaser_cooldown_remaining
        )

    def copy_torpedo(t):
        """Deep copy a TorpedoState including Vec2D objects."""
        return TorpedoState(
            id=t.id,
            owner=t.owner,
            position=Vec2D(t.position.x, t.position.y),
            velocity=Vec2D(t.velocity.x, t.velocity.y),
            heading=t.heading,
            ae_remaining=t.ae_remaining,
            just_launched=t.just_launched,
            detonation_timer=t.detonation_timer
        )

    def copy_blast_zone(bz):
        """Deep copy a BlastZone including Vec2D objects."""
        return BlastZone(
            id=bz.id,
            owner=bz.owner,
            position=Vec2D(bz.position.x, bz.position.y),
            base_damage=bz.base_damage,
            current_radius=bz.current_radius,
            phase=bz.phase,
            age=bz.age
        )

    return GameState(
        turn=state.turn,
        ship_a=copy_ship(state.ship_a),
        ship_b=copy_ship(state.ship_b),
        torpedoes=[copy_torpedo(t) for t in state.torpedoes],
        blast_zones=[copy_blast_zone(bz) for bz in state.blast_zones]
    )
