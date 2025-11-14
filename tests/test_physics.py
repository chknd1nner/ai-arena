"""
Tests for physics engine.
"""
import pytest
import copy
import numpy as np
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import (
    GameState, ShipState, Orders, Vec2D, MovementType,
    MovementDirection, RotationCommand, PhaserConfig
)
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
    orders = Orders(movement=MovementDirection.FORWARD, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

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
    orders = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

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
    orders_a = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="LAUNCH_TORPEDO", torpedo_orders={})
    orders_b = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Should have one torpedo
    assert len(new_state.torpedoes) == 1
    assert new_state.torpedoes[0].owner == "ship_a"
    # Check AE: start - launch_cost + regen
    # 100 - 20 + int(0.333 * 15) = 84
    ae_regen = int(config.ship.ae_regen_per_second * config.simulation.decision_interval_seconds)
    expected_ae = 100 - config.torpedo.launch_cost_ae + ae_regen
    assert new_state.ship_a.ae == expected_ae


# Helper function for creating test states
def create_test_state(ship_a_position=None, ship_a_velocity=None, ship_a_heading=0.0,
                     ship_a_shields=100, ship_a_ae=100,
                     ship_b_position=None, ship_b_velocity=None, ship_b_heading=3.14159):
    """Helper to create test game states with sensible defaults."""
    return GameState(
        turn=0,
        ship_a=ShipState(
            position=ship_a_position or Vec2D(100, 100),
            velocity=ship_a_velocity or Vec2D(0, 0),
            heading=ship_a_heading,
            shields=ship_a_shields,
            ae=ship_a_ae,
            phaser_config=PhaserConfig.WIDE
        ),
        ship_b=ShipState(
            position=ship_b_position or Vec2D(200, 200),
            velocity=ship_b_velocity or Vec2D(0, 0),
            heading=ship_b_heading,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        torpedoes=[]
    )


# Default orders for ship B (stationary)
def get_default_orders_b():
    return Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )


# Story 010: Physics Testing Suite - Comprehensive Tests

def test_all_movement_directions(engine):
    """Test all 9 movement directions work correctly."""
    base_state = create_test_state(ship_a_heading=0.0)  # Facing east
    default_orders_b = get_default_orders_b()

    test_cases = [
        (MovementDirection.FORWARD, 0.0, "east"),
        (MovementDirection.LEFT, np.pi/2, "north"),
        (MovementDirection.RIGHT, -np.pi/2, "south"),
        (MovementDirection.BACKWARD, np.pi, "west"),
        (MovementDirection.FORWARD_LEFT, np.pi/4, "northeast"),
        (MovementDirection.FORWARD_RIGHT, -np.pi/4, "southeast"),
        (MovementDirection.BACKWARD_LEFT, 3*np.pi/4, "northwest"),
        (MovementDirection.BACKWARD_RIGHT, -3*np.pi/4, "southwest"),
    ]

    for movement, expected_angle, description in test_cases:
        state = copy.deepcopy(base_state)
        orders = Orders(
            movement=movement,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        new_state, _ = engine.resolve_turn(state, orders, default_orders_b)

        # Verify velocity direction
        actual_angle = np.arctan2(new_state.ship_a.velocity.y, new_state.ship_a.velocity.x)
        # Normalize angles for comparison
        angle_diff = np.abs(np.arctan2(np.sin(actual_angle - expected_angle), np.cos(actual_angle - expected_angle)))
        assert angle_diff < 0.01, f"{description} velocity wrong: expected {expected_angle:.3f}, got {actual_angle:.3f}"


def test_stop_zeroes_velocity(engine):
    """STOP should set velocity to zero."""
    state = create_test_state(ship_a_velocity=Vec2D(3.0, 3.0))
    orders = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )
    default_orders_b = get_default_orders_b()

    new_state, _ = engine.resolve_turn(state, orders, default_orders_b)

    assert new_state.ship_a.velocity.x == 0.0
    assert new_state.ship_a.velocity.y == 0.0


def test_all_rotation_commands(engine):
    """Test all 5 rotation commands work correctly."""
    base_state = create_test_state(ship_a_heading=0.0)
    default_orders_b = get_default_orders_b()

    test_cases = [
        (RotationCommand.NONE, 0.0, "no rotation"),
        (RotationCommand.SOFT_LEFT, np.radians(15.0), "15° left"),
        (RotationCommand.SOFT_RIGHT, -np.radians(15.0), "15° right"),
        (RotationCommand.HARD_LEFT, np.radians(45.0), "45° left"),
        (RotationCommand.HARD_RIGHT, -np.radians(45.0), "45° right"),
    ]

    for rotation, expected_change, description in test_cases:
        state = copy.deepcopy(base_state)
        orders = Orders(
            movement=MovementDirection.FORWARD,
            rotation=rotation,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        new_state, _ = engine.resolve_turn(state, orders, default_orders_b)

        actual_change = new_state.ship_a.heading - state.ship_a.heading
        # Normalize angle difference
        actual_change = np.arctan2(np.sin(actual_change), np.cos(actual_change))
        assert abs(actual_change - expected_change) < 0.01, f"{description} wrong: expected {expected_change:.3f}, got {actual_change:.3f}"


def test_movement_does_not_affect_rotation(engine):
    """Changing movement should not affect rotation rate."""
    base_state = create_test_state(ship_a_heading=0.0)
    default_orders_b = get_default_orders_b()

    # Test 1: FORWARD + HARD_LEFT
    state1 = copy.deepcopy(base_state)
    orders1 = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.HARD_LEFT,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )
    new_state1, _ = engine.resolve_turn(state1, orders1, default_orders_b)

    # Test 2: BACKWARD + HARD_LEFT (different movement, same rotation)
    state2 = copy.deepcopy(base_state)
    orders2 = Orders(
        movement=MovementDirection.BACKWARD,
        rotation=RotationCommand.HARD_LEFT,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )
    new_state2, _ = engine.resolve_turn(state2, orders2, default_orders_b)

    # Heading change should be identical
    assert abs(new_state1.ship_a.heading - new_state2.ship_a.heading) < 0.001


def test_rotation_does_not_affect_movement_speed(engine):
    """Changing rotation should not affect velocity magnitude."""
    base_state = create_test_state(ship_a_heading=0.0)
    default_orders_b = get_default_orders_b()

    # Test 1: FORWARD + NONE
    state1 = copy.deepcopy(base_state)
    orders1 = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )
    new_state1, _ = engine.resolve_turn(state1, orders1, default_orders_b)

    # Test 2: FORWARD + HARD_RIGHT (same movement, different rotation)
    state2 = copy.deepcopy(base_state)
    orders2 = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.HARD_RIGHT,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )
    new_state2, _ = engine.resolve_turn(state2, orders2, default_orders_b)

    # Velocity magnitude should be the same
    speed1 = np.sqrt(new_state1.ship_a.velocity.x**2 + new_state1.ship_a.velocity.y**2)
    speed2 = np.sqrt(new_state2.ship_a.velocity.x**2 + new_state2.ship_a.velocity.y**2)
    assert abs(speed1 - speed2) < 0.1, f"Speed should be same: {speed1:.3f} vs {speed2:.3f}"


def test_combined_ae_costs(engine, config):
    """Test AE costs for movement + rotation combinations."""
    default_orders_b = get_default_orders_b()

    test_cases = [
        (MovementDirection.FORWARD, RotationCommand.NONE, 0.33, 0.0),
        (MovementDirection.FORWARD, RotationCommand.HARD_LEFT, 0.33, 0.33),
        (MovementDirection.LEFT, RotationCommand.HARD_RIGHT, 0.67, 0.33),
        (MovementDirection.BACKWARD_LEFT, RotationCommand.SOFT_LEFT, 0.80, 0.13),
    ]

    for movement, rotation, expected_move_cost, expected_rot_cost in test_cases:
        state = create_test_state(ship_a_ae=100)
        orders = Orders(
            movement=movement,
            rotation=rotation,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        new_state, _ = engine.resolve_turn(state, orders, default_orders_b)

        # Calculate expected total cost
        expected_total = (expected_move_cost + expected_rot_cost) * config.simulation.decision_interval_seconds
        expected_regen = config.ship.ae_regen_per_second * config.simulation.decision_interval_seconds
        expected_net = expected_total - expected_regen

        actual_cost = 100 - new_state.ship_a.ae
        assert abs(actual_cost - expected_net) < 1.5, f"AE cost wrong for {movement}+{rotation}: expected {expected_net:.1f}, got {actual_cost:.1f}"

    # Test STOP separately with AE below max to verify regen works
    state = create_test_state(ship_a_ae=50)
    orders = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )
    new_state, _ = engine.resolve_turn(state, orders, default_orders_b)

    # Should only regenerate AE (no costs)
    expected_regen = config.ship.ae_regen_per_second * config.simulation.decision_interval_seconds
    expected_ae = min(100, 50 + expected_regen)  # Cap at max AE
    assert abs(new_state.ship_a.ae - expected_ae) < 1.0, f"STOP should only regenerate AE"


def test_determinism_same_orders(engine):
    """Same inputs should produce identical outputs."""
    state = create_test_state()
    orders_a = Orders(
        movement=MovementDirection.LEFT,
        rotation=RotationCommand.HARD_LEFT,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )
    orders_b = Orders(
        movement=MovementDirection.RIGHT,
        rotation=RotationCommand.HARD_RIGHT,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )

    # Run twice
    new_state1, events1 = engine.resolve_turn(copy.deepcopy(state), orders_a, orders_b)
    new_state2, events2 = engine.resolve_turn(copy.deepcopy(state), orders_a, orders_b)

    # Results should be identical
    assert new_state1.ship_a.position.x == new_state2.ship_a.position.x
    assert new_state1.ship_a.position.y == new_state2.ship_a.position.y
    assert new_state1.ship_a.heading == new_state2.ship_a.heading
    assert new_state1.ship_a.velocity.x == new_state2.ship_a.velocity.x
    assert new_state1.ship_a.velocity.y == new_state2.ship_a.velocity.y


def test_angle_wrapping(engine):
    """Test that heading stays in valid range [0, 2π) after multiple rotations."""
    state = create_test_state(ship_a_heading=0.0)
    default_orders_b = get_default_orders_b()

    # Rotate left multiple times to exceed 2π
    for _ in range(10):  # 10 turns of 45° = 450° total
        orders = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.HARD_LEFT,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        state, _ = engine.resolve_turn(state, orders, default_orders_b)

    # Heading should be wrapped to [0, 2π)
    assert 0.0 <= state.ship_a.heading < 2 * np.pi, f"Heading {state.ship_a.heading} not in [0, 2π)"

    # Rotate right multiple times to go negative
    state = create_test_state(ship_a_heading=0.0)
    for _ in range(10):  # 10 turns of -45° = -450° total
        orders = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.HARD_RIGHT,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        state, _ = engine.resolve_turn(state, orders, default_orders_b)

    # Heading should be wrapped to [0, 2π)
    assert 0.0 <= state.ship_a.heading < 2 * np.pi, f"Heading {state.ship_a.heading} not in [0, 2π)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
