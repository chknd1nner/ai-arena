"""
Tests for physics engine.
"""
import pytest
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import GameState, ShipState, Orders, Vec2D, MovementType, PhaserConfig
from ai_arena.config import ConfigLoader


@pytest.fixture
def config():
    """Load game configuration for tests."""
    return ConfigLoader().load("config.json")


@pytest.fixture
def engine(config):
    """Create physics engine with config for tests."""
    return PhysicsEngine(config)


def test_ship_movement_straight(engine, config):
    """Test that STRAIGHT movement works correctly."""

    ship = ShipState(
        position=Vec2D(0, 0),
        velocity=Vec2D(0, 0),
        heading=0.0,  # Facing right
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )

    state = GameState(turn=0, ship_a=ship, ship_b=ship, torpedoes=[])
    orders = Orders(movement=MovementType.STRAIGHT, weapon_action="NONE", torpedo_orders={})

    new_state, events = engine.resolve_turn(state, orders, orders)

    # After decision_interval_seconds at base_speed_units_per_second, ship should move
    # 15 seconds * 3.0 units/second = 45 units
    expected_distance = config.simulation.decision_interval_seconds * config.ship.base_speed_units_per_second
    assert new_state.ship_a.position.x > 0
    assert abs(new_state.ship_a.position.x - expected_distance) < 1.0  # Allow small tolerance
    assert new_state.turn == 1


def test_phaser_hit_detection(engine, config):
    """Test that phaser hits are detected correctly."""

    # Ship A facing ship B at close range
    ship_a = ShipState(
        position=Vec2D(0, 0),
        velocity=Vec2D(0, 0),
        heading=0.0,  # Facing right
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )

    # Position ship_b within WIDE phaser range from config
    ship_b = ShipState(
        position=Vec2D(20, 0),  # 20 units to the right, within WIDE range (config: 30)
        velocity=Vec2D(0, 0),
        heading=3.14159,  # Facing left
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )

    state = GameState(turn=0, ship_a=ship_a, ship_b=ship_b, torpedoes=[])
    orders = Orders(movement=MovementType.STOP, weapon_action="NONE", torpedo_orders={})

    new_state, events = engine.resolve_turn(state, orders, orders)

    # Both ships should hit each other
    phaser_events = [e for e in events if e.type == "phaser_hit"]
    assert len(phaser_events) >= 1  # At least one ship should hit


def test_torpedo_launch(engine, config):
    """Test that torpedoes launch correctly."""
    ship = ShipState(
        position=Vec2D(0, 0),
        velocity=Vec2D(0, 0),
        heading=0.0,
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )

    state = GameState(turn=0, ship_a=ship, ship_b=ship, torpedoes=[])
    orders_a = Orders(movement=MovementType.STOP, weapon_action="LAUNCH_TORPEDO", torpedo_orders={})
    orders_b = Orders(movement=MovementType.STOP, weapon_action="NONE", torpedo_orders={})

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Should have one torpedo
    assert len(new_state.torpedoes) == 1
    assert new_state.torpedoes[0].owner == "ship_a"
    # Check AE: start - launch_cost + regen
    # 100 - 20 + int(0.333 * 15) = 84
    ae_regen = int(config.ship.ae_regen_per_second * config.simulation.decision_interval_seconds)
    expected_ae = 100 - config.torpedo.launch_cost_ae + ae_regen
    assert new_state.ship_a.ae == expected_ae


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
