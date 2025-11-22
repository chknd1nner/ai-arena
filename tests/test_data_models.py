"""Tests for data model foundation (Story 004).

Validates the new MovementDirection and RotationCommand enums,
and verifies that Orders dataclass works correctly with the new fields.
"""

import pytest
from ai_arena.game_engine.data_models import (
    MovementDirection,
    RotationCommand,
    Orders,
    ShipState,
    Vec2D,
    PhaserConfig
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
        """Verify torpedo orders use simple string commands."""
        orders = Orders(
            movement=MovementDirection.FORWARD,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={
                "torpedo_1": "HARD_LEFT",
                "torpedo_2": "STRAIGHT"
            }
        )
        assert orders.torpedo_orders["torpedo_1"] == "HARD_LEFT"
        assert orders.torpedo_orders["torpedo_2"] == "STRAIGHT"


class TestShipStateCooldown:
    """Test ShipState phaser cooldown field (Story 020)."""

    def test_cooldown_field_exists(self):
        """Verify ShipState has phaser_cooldown_remaining field."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )
        assert hasattr(ship, 'phaser_cooldown_remaining')
        assert ship.phaser_cooldown_remaining == 0.0

    def test_cooldown_default_value(self):
        """Verify phaser_cooldown_remaining defaults to 0.0."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )
        assert ship.phaser_cooldown_remaining == 0.0

    def test_cooldown_can_be_set(self):
        """Verify phaser_cooldown_remaining can be set to valid values."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE,
            phaser_cooldown_remaining=3.5
        )
        assert ship.phaser_cooldown_remaining == 3.5

    def test_cooldown_rejects_negative(self):
        """Verify phaser_cooldown_remaining rejects negative values."""
        with pytest.raises(ValueError) as exc_info:
            ShipState(
                position=Vec2D(0, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=-1.0
            )
        assert "phaser_cooldown_remaining must be >= 0.0" in str(exc_info.value)

    def test_cooldown_accepts_zero(self):
        """Verify phaser_cooldown_remaining accepts 0.0."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE,
            phaser_cooldown_remaining=0.0
        )
        assert ship.phaser_cooldown_remaining == 0.0

    def test_cooldown_accepts_large_values(self):
        """Verify phaser_cooldown_remaining accepts large valid values."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE,
            phaser_cooldown_remaining=100.0
        )
        assert ship.phaser_cooldown_remaining == 100.0

    def test_cooldown_serialization(self):
        """Verify phaser_cooldown_remaining is included in serialization."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE,
            phaser_cooldown_remaining=2.5
        )
        # Test that the field is accessible (replays will serialize via dataclasses.asdict())
        from dataclasses import asdict
        ship_dict = asdict(ship)
        assert 'phaser_cooldown_remaining' in ship_dict
        assert ship_dict['phaser_cooldown_remaining'] == 2.5
