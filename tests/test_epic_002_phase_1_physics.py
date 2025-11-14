"""
Comprehensive physics tests for Epic 002 Phase 1: Independent Movement & Rotation.

Tests Stories 004-007:
- Story 004: Data Model Foundation
- Story 005: Movement Direction System
- Story 006: Independent Rotation System
- Story 007: Combined AE Cost System
"""

import pytest
import numpy as np
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import (
    GameState, ShipState, Orders, Vec2D,
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


def create_test_state(
    ship_a_position=None,
    ship_a_heading=0.0,
    ship_a_ae=100,
    ship_b_position=None,
    ship_b_heading=0.0,
    ship_b_ae=100
):
    """Helper to create test game state."""
    ship_a = ShipState(
        position=ship_a_position or Vec2D(100, 100),
        velocity=Vec2D(0, 0),
        heading=ship_a_heading,
        shields=100,
        ae=ship_a_ae,
        phaser_config=PhaserConfig.WIDE
    )
    ship_b = ShipState(
        position=ship_b_position or Vec2D(500, 100),
        velocity=Vec2D(0, 0),
        heading=ship_b_heading,
        shields=100,
        ae=ship_b_ae,
        phaser_config=PhaserConfig.WIDE
    )
    return GameState(turn=0, ship_a=ship_a, ship_b=ship_b, torpedoes=[])


def default_orders_b():
    """Default orders for ship B (stationary)."""
    return Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )


# =============================================================================
# Story 005: Movement Direction System Tests
# =============================================================================

class TestMovementDirections:
    """Test all 9 movement directions work correctly."""

    def test_movement_forward_maintains_heading(self, engine, config):
        """FORWARD movement should not change heading."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0
        # Velocity should be east (heading direction)
        assert new_state.ship_a.velocity.x > 0
        assert abs(new_state.ship_a.velocity.y) < 0.001

    def test_movement_left_perpendicular(self, engine, config):
        """LEFT movement should move perpendicular to heading."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.LEFT,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0
        # Velocity should be north (perpendicular left)
        assert abs(new_state.ship_a.velocity.x) < 0.001
        assert new_state.ship_a.velocity.y > 0
        # Position should move north
        assert new_state.ship_a.position.y > state.ship_a.position.y

    def test_movement_right_perpendicular(self, engine, config):
        """RIGHT movement should move perpendicular to heading."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.RIGHT,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0
        # Velocity should be south (perpendicular right)
        assert abs(new_state.ship_a.velocity.x) < 0.001
        assert new_state.ship_a.velocity.y < 0
        # Position should move south
        assert new_state.ship_a.position.y < state.ship_a.position.y

    def test_movement_backward_reverses(self, engine, config):
        """BACKWARD movement should move opposite to heading."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.BACKWARD,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0
        # Velocity should be west (opposite of heading)
        assert new_state.ship_a.velocity.x < 0
        assert abs(new_state.ship_a.velocity.y) < 0.001
        # Position should move west
        assert new_state.ship_a.position.x < state.ship_a.position.x

    def test_movement_stop_zeroes_velocity(self, engine, config):
        """STOP movement should set velocity to zero."""
        state = create_test_state(ship_a_heading=0.0)
        # Set initial velocity
        state.ship_a.velocity = Vec2D(3.0, 0.0)
        initial_position = Vec2D(state.ship_a.position.x, state.ship_a.position.y)

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Velocity should be zero
        assert new_state.ship_a.velocity.x == 0.0
        assert new_state.ship_a.velocity.y == 0.0
        # Position should not change (no movement during turn)
        assert new_state.ship_a.position.x == initial_position.x
        assert new_state.ship_a.position.y == initial_position.y

    def test_movement_forward_left_diagonal(self, engine, config):
        """FORWARD_LEFT should move at 45° from heading."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.FORWARD_LEFT,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0
        # Velocity should be northeast (45° from east)
        assert new_state.ship_a.velocity.x > 0
        assert new_state.ship_a.velocity.y > 0
        # Should be equal magnitude (45° angle)
        assert abs(new_state.ship_a.velocity.x - new_state.ship_a.velocity.y) < 0.001

    def test_movement_forward_right_diagonal(self, engine, config):
        """FORWARD_RIGHT should move at -45° from heading."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.FORWARD_RIGHT,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0
        # Velocity should be southeast (45° from east)
        assert new_state.ship_a.velocity.x > 0
        assert new_state.ship_a.velocity.y < 0
        # Should be equal magnitude (45° angle)
        assert abs(abs(new_state.ship_a.velocity.x) - abs(new_state.ship_a.velocity.y)) < 0.001

    def test_movement_backward_left_diagonal(self, engine, config):
        """BACKWARD_LEFT should move at 135° from heading."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.BACKWARD_LEFT,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0
        # Velocity should be northwest (135° from east = -135°)
        assert new_state.ship_a.velocity.x < 0
        assert new_state.ship_a.velocity.y > 0
        # Should be equal magnitude (45° from axes)
        assert abs(abs(new_state.ship_a.velocity.x) - abs(new_state.ship_a.velocity.y)) < 0.001

    def test_movement_backward_right_diagonal(self, engine, config):
        """BACKWARD_RIGHT should move at -135° from heading."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.BACKWARD_RIGHT,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0
        # Velocity should be southwest (-135° from east)
        assert new_state.ship_a.velocity.x < 0
        assert new_state.ship_a.velocity.y < 0
        # Should be equal magnitude (45° from axes)
        assert abs(abs(new_state.ship_a.velocity.x) - abs(new_state.ship_a.velocity.y)) < 0.001


# =============================================================================
# Story 006: Independent Rotation System Tests
# =============================================================================

class TestRotationCommands:
    """Test all 5 rotation commands work correctly."""

    def test_rotation_none_maintains_heading(self, engine, config):
        """NONE rotation should not change heading."""
        state = create_test_state(ship_a_heading=0.0)
        orders_a = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        assert new_state.ship_a.heading == 0.0

    def test_rotation_soft_left_rotates_15_degrees(self, engine, config):
        """SOFT_LEFT should rotate 15° over 15s turn."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.SOFT_LEFT,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # 1.0°/s × 15s = 15° = 0.2618 radians
        expected_heading = np.radians(15.0)
        assert abs(new_state.ship_a.heading - expected_heading) < 0.001

    def test_rotation_soft_right_rotates_minus_15_degrees(self, engine, config):
        """SOFT_RIGHT should rotate -15° over 15s turn."""
        state = create_test_state(ship_a_heading=np.pi/2)  # Facing north
        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.SOFT_RIGHT,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # -1.0°/s × 15s = -15° from north
        expected_heading = np.pi/2 - np.radians(15.0)
        assert abs(new_state.ship_a.heading - expected_heading) < 0.001

    def test_rotation_hard_left_rotates_45_degrees(self, engine, config):
        """HARD_LEFT should rotate 45° over 15s turn."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.HARD_LEFT,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # 3.0°/s × 15s = 45° = 0.7854 radians
        expected_heading = np.radians(45.0)
        assert abs(new_state.ship_a.heading - expected_heading) < 0.001

    def test_rotation_hard_right_rotates_minus_45_degrees(self, engine, config):
        """HARD_RIGHT should rotate -45° over 15s turn."""
        state = create_test_state(ship_a_heading=np.pi/2)  # Facing north
        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.HARD_RIGHT,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # -3.0°/s × 15s = -45° from north = 45° (northeast)
        expected_heading = np.pi/2 - np.radians(45.0)
        assert abs(new_state.ship_a.heading - expected_heading) < 0.001

    def test_rotation_wraps_correctly(self, engine, config):
        """Heading should wrap from 2π to 0."""
        state = create_test_state(ship_a_heading=6.0)  # Near 2π (6.28)
        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.SOFT_LEFT,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Should wrap to small positive value
        assert 0.0 <= new_state.ship_a.heading < 2 * np.pi


# =============================================================================
# Story 005-006: Independent Movement and Rotation Tests
# =============================================================================

class TestIndependentMovementAndRotation:
    """Test that movement and rotation work independently."""

    def test_strafing_left_while_rotating_right(self, engine, config):
        """Test ship can move LEFT while rotating HARD_RIGHT (strafing maneuver)."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.LEFT,     # Move north
            rotation=RotationCommand.HARD_RIGHT, # Rotate clockwise
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should rotate right: 0° → -45° (315° or ~5.5 rad)
        expected_heading = 2*np.pi - np.radians(45.0)
        assert abs(new_state.ship_a.heading - expected_heading) < 0.001

        # Position should move generally north (LEFT relative to initial heading)
        # Movement is continuous, so final direction is based on changing heading
        # But overall, ship should have moved in a generally northward direction
        assert new_state.ship_a.position.y > state.ship_a.position.y

    def test_forward_movement_with_rotation(self, engine, config):
        """Test FORWARD movement while rotating creates a curved path."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.HARD_LEFT,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should rotate left: 0° → +45°
        expected_heading = np.radians(45.0)
        assert abs(new_state.ship_a.heading - expected_heading) < 0.001

        # Ship should move in a curved path (northeast overall)
        assert new_state.ship_a.position.x > state.ship_a.position.x
        assert new_state.ship_a.position.y > state.ship_a.position.y

    def test_backward_movement_without_rotation(self, engine, config):
        """Test BACKWARD movement with NONE rotation (retreat maneuver)."""
        state = create_test_state(ship_a_heading=0.0)  # Facing east
        orders_a = Orders(
            movement=MovementDirection.BACKWARD,  # Move west
            rotation=RotationCommand.NONE,        # Keep facing east
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Heading should not change
        assert new_state.ship_a.heading == 0.0

        # Ship should move backward (west)
        assert new_state.ship_a.position.x < state.ship_a.position.x


# =============================================================================
# Story 007: Combined AE Cost System Tests
# =============================================================================

class TestCombinedAECosts:
    """Test combined AE costs for movement + rotation."""

    def test_forward_none_ae_cost(self, engine, config):
        """FORWARD + NONE should cost only movement."""
        state = create_test_state(ship_a_ae=100)
        orders_a = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Movement cost: 0.33 AE/s × 15s = 4.95 AE
        # Rotation cost: 0.0 AE/s × 15s = 0 AE
        # Total cost: 4.95 AE
        # AE regen: 0.333 AE/s × 15s = ~5 AE
        # Net change: ~0 AE (regen cancels cost)
        # Ship should have approximately same AE (within regen tolerance)
        assert 95 <= new_state.ship_a.ae <= 105

    def test_forward_hard_left_ae_cost(self, engine, config):
        """FORWARD + HARD_LEFT should cost movement + rotation."""
        state = create_test_state(ship_a_ae=100)
        orders_a = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.HARD_LEFT,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Movement cost: 0.33 AE/s × 15s = 4.95 AE
        # Rotation cost: 0.33 AE/s × 15s = 4.95 AE
        # Total cost: 9.9 AE
        # AE regen: 0.333 AE/s × 15s = ~5 AE
        # Net change: ~5 AE drain
        # Expected AE: 100 - 9.9 + 5 = ~95
        assert 93 <= new_state.ship_a.ae <= 97

    def test_left_hard_right_ae_cost(self, engine, config):
        """LEFT + HARD_RIGHT should cost perpendicular movement + rotation."""
        state = create_test_state(ship_a_ae=100)
        orders_a = Orders(
            movement=MovementDirection.LEFT,
            rotation=RotationCommand.HARD_RIGHT,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Movement cost: 0.67 AE/s × 15s = 10.05 AE
        # Rotation cost: 0.33 AE/s × 15s = 4.95 AE
        # Total cost: 15 AE
        # AE regen: ~5 AE
        # Net change: ~10 AE drain
        # Expected AE: 100 - 15 + 5 = ~90
        assert 88 <= new_state.ship_a.ae <= 92

    def test_stop_none_ae_cost(self, engine, config):
        """STOP + NONE should cost nothing (only regen)."""
        state = create_test_state(ship_a_ae=50)
        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # No cost, only regen: +~5 AE
        # Expected AE: 50 + 5 = ~55
        assert new_state.ship_a.ae > 50
        assert 53 <= new_state.ship_a.ae <= 57

    def test_insufficient_ae_for_orders(self, engine, config):
        """Ship with insufficient AE should have orders downgraded."""
        state = create_test_state(ship_a_ae=3)  # Very low AE
        orders_a = Orders(
            movement=MovementDirection.BACKWARD_LEFT,  # Expensive (0.80 AE/s)
            rotation=RotationCommand.HARD_LEFT,         # Expensive (0.33 AE/s)
            weapon_action="MAINTAIN_CONFIG"
        )

        new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b())

        # Total cost would be (0.80 + 0.33) × 15 = 16.95 AE
        # Ship only has 3 AE, so orders should be downgraded to STOP + NONE
        # With regen, ship should gain ~5 AE
        # Expected AE: 3 + 5 = ~8
        assert new_state.ship_a.ae >= 0  # No negative AE
        assert new_state.ship_a.ae >= 6  # Should have regened


# =============================================================================
# Determinism Tests
# =============================================================================

class TestPhysicsDeterminism:
    """Test that physics engine is deterministic."""

    def test_same_inputs_same_outputs(self, engine, config):
        """Same initial state and orders should produce same result."""
        state1 = create_test_state(ship_a_heading=np.pi/4)
        state2 = create_test_state(ship_a_heading=np.pi/4)

        orders = Orders(
            movement=MovementDirection.FORWARD_LEFT,
            rotation=RotationCommand.SOFT_RIGHT,
            weapon_action="MAINTAIN_CONFIG"
        )

        result1, _ = engine.resolve_turn(state1, orders, default_orders_b())
        result2, _ = engine.resolve_turn(state2, orders, default_orders_b())

        # Positions should be identical
        assert result1.ship_a.position.x == result2.ship_a.position.x
        assert result1.ship_a.position.y == result2.ship_a.position.y
        # Headings should be identical
        assert result1.ship_a.heading == result2.ship_a.heading
        # AE should be identical
        assert result1.ship_a.ae == result2.ship_a.ae

    def test_multiple_turns_deterministic(self, engine, config):
        """Running multiple turns should be deterministic."""
        state1 = create_test_state()
        state2 = create_test_state()

        orders = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.HARD_LEFT,
            weapon_action="MAINTAIN_CONFIG"
        )

        # Run 3 turns
        for _ in range(3):
            state1, _ = engine.resolve_turn(state1, orders, default_orders_b())
            state2, _ = engine.resolve_turn(state2, orders, default_orders_b())

        # Final states should be identical
        assert state1.ship_a.position.x == state2.ship_a.position.x
        assert state1.ship_a.position.y == state2.ship_a.position.y
        assert state1.ship_a.heading == state2.ship_a.heading
        assert state1.ship_a.ae == state2.ship_a.ae


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
