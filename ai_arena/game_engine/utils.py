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
    """
    from ai_arena.game_engine.data_models import GameState, ShipState, TorpedoState, BlastZone

    return GameState(
        turn=state.turn,
        ship_a=ShipState(**state.ship_a.__dict__),
        ship_b=ShipState(**state.ship_b.__dict__),
        torpedoes=[TorpedoState(**t.__dict__) for t in state.torpedoes],
        blast_zones=[BlastZone(**bz.__dict__) for bz in state.blast_zones]
    )
