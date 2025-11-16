"""
Shared fixtures and helpers for AI Arena test suite.

This module provides common fixtures used across multiple test files,
reducing duplication and ensuring consistency.
"""

import pytest
import numpy as np
from ai_arena.config import ConfigLoader
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import (
    GameState, ShipState, Orders, Vec2D,
    MovementDirection, RotationCommand, PhaserConfig
)
from ai_arena.llm_adapter.adapter import LLMAdapter


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def config():
    """Load game configuration for tests.

    Used by most test files that need access to game parameters.
    """
    return ConfigLoader().load("config.json")


# ============================================================================
# Engine Fixtures
# ============================================================================

@pytest.fixture
def engine(config):
    """Create physics engine with configuration.

    Provides a configured PhysicsEngine instance for testing game physics.
    """
    return PhysicsEngine(config)


@pytest.fixture
def physics_engine(config):
    """Alias for engine fixture for backward compatibility.

    Some tests use 'physics_engine' instead of 'engine'.
    """
    return PhysicsEngine(config)


# ============================================================================
# LLM Adapter Fixtures
# ============================================================================

@pytest.fixture
def adapter(config):
    """Create LLM adapter for testing.

    Creates an adapter with default models (gpt-4 vs gpt-4).
    Note: This is for testing prompt generation and parsing, not actual LLM calls.
    """
    return LLMAdapter(model_a="gpt-4", model_b="gpt-4", config=config)


# ============================================================================
# Game State Fixtures
# ============================================================================

@pytest.fixture
def mock_game_state():
    """Create a basic mock game state for testing.

    Provides two ships at standard positions facing each other.
    """
    ship_a = ShipState(
        position=Vec2D(0, 0),
        velocity=Vec2D(0, 0),
        heading=0.0,
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )
    ship_b = ShipState(
        position=Vec2D(100, 100),
        velocity=Vec2D(0, 0),
        heading=0.0,
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )
    return GameState(turn=1, ship_a=ship_a, ship_b=ship_b, torpedoes=[])


@pytest.fixture
def initial_state():
    """Create initial game state for continuous physics tests.

    Ships start at standard arena positions with partial AE to test regeneration.
    """
    return GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 250),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=50,  # Start with half AE to test regeneration
            phaser_config=PhaserConfig.WIDE,
            phaser_cooldown_remaining=0.0
        ),
        ship_b=ShipState(
            position=Vec2D(900, 250),
            velocity=Vec2D(0, 0),
            heading=np.pi,
            shields=100,
            ae=50,
            phaser_config=PhaserConfig.WIDE,
            phaser_cooldown_remaining=0.0
        ),
        torpedoes=[]
    )


# Helper functions are in tests/helpers.py (not conftest.py)
# This allows them to be imported explicitly by test modules
