"""
Tests for physics engine.
"""
import pytest
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import GameState, ShipState, Orders, Vec2D, MovementType, PhaserConfig


def test_ship_movement_straight():
    """Test that STRAIGHT movement works correctly."""
    engine = PhysicsEngine()

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

    # After 60 seconds at 10 units/second, ship should move 600 units
    assert new_state.ship_a.position.x > 0
    assert new_state.turn == 1


def test_phaser_hit_detection():
    """Test that phaser hits are detected correctly."""
    engine = PhysicsEngine()

    # Ship A facing ship B at close range
    ship_a = ShipState(
        position=Vec2D(0, 0),
        velocity=Vec2D(0, 0),
        heading=0.0,  # Facing right
        shields=100,
        ae=100,
        phaser_config=PhaserConfig.WIDE
    )

    ship_b = ShipState(
        position=Vec2D(20, 0),  # 20 units to the right, within WIDE range (30)
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


def test_torpedo_launch():
    """Test that torpedoes launch correctly."""
    engine = PhysicsEngine()

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
    assert new_state.ship_a.ae == 80  # 100 - 20 for launch


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
