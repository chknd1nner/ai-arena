"""Tests for data model foundation (Story 004).

Validates the new MovementDirection and RotationCommand enums,
and verifies that Orders dataclass works correctly with the new fields.
"""

import pytest
from ai_arena.game_engine.data_models import (
    MovementDirection,
    RotationCommand,
    Orders,
    MovementType
)


class TestMovementDirectionEnum:
    """Test MovementDirection enum values and properties."""

    def test_all_movement_directions_exist(self):
        """Verify all 9 movement directions exist."""
        assert MovementDirection.FORWARD
        assert MovementDirection.LEFT
        assert MovementDirection.RIGHT
        assert MovementDirection.BACKWARD
        assert MovementDirection.FORWARD_LEFT
        assert MovementDirection.FORWARD_RIGHT
        assert MovementDirection.BACKWARD_LEFT
        assert MovementDirection.BACKWARD_RIGHT
        assert MovementDirection.STOP

    def test_movement_direction_values(self):
        """Verify movement direction enum values are correct strings."""
        assert MovementDirection.FORWARD.value == "FORWARD"
        assert MovementDirection.LEFT.value == "LEFT"
        assert MovementDirection.RIGHT.value == "RIGHT"
        assert MovementDirection.BACKWARD.value == "BACKWARD"
        assert MovementDirection.FORWARD_LEFT.value == "FORWARD_LEFT"
        assert MovementDirection.FORWARD_RIGHT.value == "FORWARD_RIGHT"
        assert MovementDirection.BACKWARD_LEFT.value == "BACKWARD_LEFT"
        assert MovementDirection.BACKWARD_RIGHT.value == "BACKWARD_RIGHT"
        assert MovementDirection.STOP.value == "STOP"

    def test_movement_direction_count(self):
        """Verify there are exactly 9 movement directions."""
        assert len(MovementDirection) == 9


class TestRotationCommandEnum:
    """Test RotationCommand enum values and properties."""

    def test_all_rotation_commands_exist(self):
        """Verify all 5 rotation commands exist."""
        assert RotationCommand.NONE
        assert RotationCommand.SOFT_LEFT
        assert RotationCommand.SOFT_RIGHT
        assert RotationCommand.HARD_LEFT
        assert RotationCommand.HARD_RIGHT

    def test_rotation_command_values(self):
        """Verify rotation command enum values are correct strings."""
        assert RotationCommand.NONE.value == "NONE"
        assert RotationCommand.SOFT_LEFT.value == "SOFT_LEFT"
        assert RotationCommand.SOFT_RIGHT.value == "SOFT_RIGHT"
        assert RotationCommand.HARD_LEFT.value == "HARD_LEFT"
        assert RotationCommand.HARD_RIGHT.value == "HARD_RIGHT"

    def test_rotation_command_count(self):
        """Verify there are exactly 5 rotation commands."""
        assert len(RotationCommand) == 5


class TestOrdersDataclass:
    """Test Orders dataclass with new movement and rotation fields."""

    def test_orders_has_rotation_field(self):
        """Verify Orders dataclass has rotation field."""
        orders = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG"
        )
        assert orders.movement == MovementDirection.FORWARD
        assert orders.rotation == RotationCommand.NONE
        assert orders.weapon_action == "MAINTAIN_CONFIG"

    def test_orders_with_different_movement_and_rotation(self):
        """Verify movement and rotation are independent."""
        orders = Orders(
            movement=MovementDirection.LEFT,
            rotation=RotationCommand.HARD_RIGHT,
            weapon_action="MAINTAIN_CONFIG"
        )
        assert orders.movement == MovementDirection.LEFT
        assert orders.rotation == RotationCommand.HARD_RIGHT

    def test_orders_serialization(self):
        """Verify Orders can be serialized to dict (for replay system)."""
        orders = Orders(
            movement=MovementDirection.LEFT,
            rotation=RotationCommand.HARD_RIGHT,
            weapon_action="MAINTAIN_CONFIG"
        )
        # Should be able to access enum values for serialization
        assert orders.movement.value == "LEFT"
        assert orders.rotation.value == "HARD_RIGHT"

    def test_orders_with_all_movement_directions(self):
        """Test creating orders with each movement direction."""
        for movement in MovementDirection:
            orders = Orders(
                movement=movement,
                rotation=RotationCommand.NONE,
                weapon_action="MAINTAIN_CONFIG"
            )
            assert orders.movement == movement

    def test_orders_with_all_rotation_commands(self):
        """Test creating orders with each rotation command."""
        for rotation in RotationCommand:
            orders = Orders(
                movement=MovementDirection.FORWARD,
                rotation=rotation,
                weapon_action="MAINTAIN_CONFIG"
            )
            assert orders.rotation == rotation

    def test_orders_with_torpedo_orders(self):
        """Verify torpedo orders still use MovementType (legacy system)."""
        orders = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={
                "torpedo_1": MovementType.HARD_LEFT,
                "torpedo_2": MovementType.STRAIGHT
            }
        )
        assert orders.torpedo_orders["torpedo_1"] == MovementType.HARD_LEFT
        assert orders.torpedo_orders["torpedo_2"] == MovementType.STRAIGHT


class TestBackwardCompatibility:
    """Test that legacy MovementType enum still exists for torpedoes."""

    def test_movement_type_still_exists(self):
        """Verify MovementType enum still exists for torpedo compatibility."""
        assert MovementType.STRAIGHT
        assert MovementType.HARD_LEFT
        assert MovementType.HARD_RIGHT
        assert MovementType.SOFT_LEFT
        assert MovementType.SOFT_RIGHT
        assert MovementType.REVERSE
        assert MovementType.REVERSE_LEFT
        assert MovementType.REVERSE_RIGHT
        assert MovementType.STOP

    def test_movement_type_count(self):
        """Verify MovementType has 9 values."""
        assert len(MovementType) == 9
