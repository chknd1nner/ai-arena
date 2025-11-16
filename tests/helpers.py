"""
Shared helper functions for AI Arena test suite.

This module provides common utility functions used across multiple test files.
Unlike fixtures in conftest.py, these are regular functions that can be imported.
"""

import numpy as np
from ai_arena.game_engine.data_models import (
    GameState, ShipState, Orders, Vec2D,
    MovementDirection, RotationCommand, PhaserConfig
)


def create_test_state(
    ship_a_position=None,
    ship_a_velocity=None,
    ship_a_heading=0.0,
    ship_a_shields=100,
    ship_a_ae=100,
    ship_a_phaser_config=PhaserConfig.WIDE,
    ship_a_cooldown=0.0,
    ship_b_position=None,
    ship_b_velocity=None,
    ship_b_heading=3.14159,
    ship_b_shields=100,
    ship_b_ae=100,
    ship_b_phaser_config=PhaserConfig.WIDE,
    ship_b_cooldown=0.0,
    torpedoes=None
):
    """Helper to create test game states with customizable parameters.

    Provides sensible defaults for all fields while allowing selective customization.

    Args:
        ship_a_position: Ship A position (default: Vec2D(100, 100))
        ship_a_velocity: Ship A velocity (default: Vec2D(0, 0))
        ship_a_heading: Ship A heading in radians (default: 0.0 = east)
        ship_a_shields: Ship A shields (default: 100)
        ship_a_ae: Ship A available energy (default: 100)
        ship_a_phaser_config: Ship A phaser configuration (default: WIDE)
        ship_a_cooldown: Ship A phaser cooldown remaining (default: 0.0)
        ship_b_position: Ship B position (default: Vec2D(200, 200))
        ship_b_velocity: Ship B velocity (default: Vec2D(0, 0))
        ship_b_heading: Ship B heading in radians (default: π = west)
        ship_b_shields: Ship B shields (default: 100)
        ship_b_ae: Ship B available energy (default: 100)
        ship_b_phaser_config: Ship B phaser configuration (default: WIDE)
        ship_b_cooldown: Ship B phaser cooldown remaining (default: 0.0)
        torpedoes: List of torpedoes (default: [])

    Returns:
        GameState with specified parameters
    """
    ship_a = ShipState(
        position=ship_a_position or Vec2D(100, 100),
        velocity=ship_a_velocity or Vec2D(0, 0),
        heading=ship_a_heading,
        shields=ship_a_shields,
        ae=ship_a_ae,
        phaser_config=ship_a_phaser_config,
        phaser_cooldown_remaining=ship_a_cooldown
    )

    ship_b = ShipState(
        position=ship_b_position or Vec2D(200, 200),
        velocity=ship_b_velocity or Vec2D(0, 0),
        heading=ship_b_heading,
        shields=ship_b_shields,
        ae=ship_b_ae,
        phaser_config=ship_b_phaser_config,
        phaser_cooldown_remaining=ship_b_cooldown
    )

    return GameState(
        turn=0,
        ship_a=ship_a,
        ship_b=ship_b,
        torpedoes=torpedoes or []
    )


def default_orders_b():
    """Create default stationary orders for ship B.

    Useful when testing ship A's behavior in isolation.

    Returns:
        Orders with STOP movement and MAINTAIN_CONFIG weapon action
    """
    return Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )


def get_default_orders_b():
    """Alias for default_orders_b() for backward compatibility."""
    return default_orders_b()
