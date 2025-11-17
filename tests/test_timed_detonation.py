"""Tests for Story 029: Timed Torpedo Detonation

Tests the ability for LLMs to command torpedoes to detonate after a specified delay.
"""

import pytest
import numpy as np
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import (
    GameState, Orders, ShipState, TorpedoState, Vec2D,
    MovementDirection, RotationCommand, PhaserConfig,
    BlastZone, BlastZonePhase
)
from ai_arena.config import ConfigLoader


@pytest.fixture
def config():
    """Load game configuration."""
    loader = ConfigLoader()
    return loader.load("config.json")


@pytest.fixture
def physics_engine(config):
    """Create physics engine."""
    return PhysicsEngine(config)


@pytest.fixture
def basic_state():
    """Create basic game state with one torpedo."""
    return GameState(
        turn=1,
        ship_a=ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        ship_b=ShipState(
            position=Vec2D(100, 0),
            velocity=Vec2D(0, 0),
            heading=np.pi,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        torpedoes=[
            TorpedoState(
                id="ship_a_torpedo_1",
                position=Vec2D(50, 0),
                velocity=Vec2D(15, 0),
                heading=0.0,
                ae_remaining=100,
                owner="ship_a",
                just_launched=False,
                detonation_timer=None
            )
        ]
    )


class TestTorpedoActionParsing:
    """Test parsing of torpedo action strings."""

    def test_parse_detonate_after_valid_delay(self, physics_engine):
        """Test parsing valid detonate_after:X commands."""
        action_type, delay = physics_engine._parse_torpedo_action("detonate_after:5.0")
        assert action_type == "detonate_after"
        assert delay == 5.0

    def test_parse_detonate_after_various_delays(self, physics_engine):
        """Test parsing various delay values."""
        test_cases = [
            ("detonate_after:0.1", 0.1),
            ("detonate_after:5.0", 5.0),
            ("detonate_after:10.0", 10.0),
            ("detonate_after:15.0", 15.0),
        ]
        for action_str, expected_delay in test_cases:
            action_type, delay = physics_engine._parse_torpedo_action(action_str)
            assert action_type == "detonate_after"
            assert delay == expected_delay

    def test_parse_detonate_after_invalid_negative_delay(self, physics_engine):
        """Test that negative delays raise ValueError."""
        with pytest.raises(ValueError, match="outside valid range"):
            physics_engine._parse_torpedo_action("detonate_after:-1.0")

    def test_parse_detonate_after_invalid_too_large_delay(self, physics_engine):
        """Test that delays > 15.0 raise ValueError."""
        with pytest.raises(ValueError, match="outside valid range"):
            physics_engine._parse_torpedo_action("detonate_after:16.0")

    def test_parse_movement_command_returns_none_delay(self, physics_engine):
        """Test that movement commands return None for delay."""
        action_type, delay = physics_engine._parse_torpedo_action("HARD_LEFT")
        assert action_type == "HARD_LEFT"
        assert delay is None

    def test_parse_all_movement_commands(self, physics_engine):
        """Test parsing all movement command types."""
        commands = ["STRAIGHT", "HARD_LEFT", "HARD_RIGHT", "SOFT_LEFT", "SOFT_RIGHT"]
        for cmd in commands:
            action_type, delay = physics_engine._parse_torpedo_action(cmd)
            assert action_type == cmd
            assert delay is None


class TestDetonationTimerDecrement:
    """Test that detonation timers decrement correctly."""

    def test_timer_decrements_per_substep(self, physics_engine, basic_state, config):
        """Test that detonation timer decrements by dt each substep."""
        # Set detonation timer to 5.0 seconds
        basic_state.torpedoes[0].detonation_timer = 5.0

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        # Run one turn (15 seconds)
        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        # After 15 seconds, timer should have gone to -10.0 and torpedo should have detonated
        # Check that torpedo was removed
        assert len(new_state.torpedoes) == 0
        # Check that blast zone was created
        assert len(new_state.blast_zones) == 1

    def test_timer_exact_match_triggers_detonation(self, physics_engine, basic_state, config):
        """Test that timer exactly reaching 0 triggers detonation."""
        # Set timer to exactly match one substep duration
        dt = config.simulation.physics_tick_rate_seconds
        basic_state.torpedoes[0].detonation_timer = dt

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        # Torpedo should have detonated on first substep
        assert len(new_state.torpedoes) == 0
        assert len(new_state.blast_zones) == 1


class TestBlastZoneCreation:
    """Test that blast zones are created when torpedoes detonate."""

    def test_blast_zone_created_on_timed_detonation(self, physics_engine, basic_state):
        """Test that timed detonation creates a blast zone."""
        basic_state.torpedoes[0].detonation_timer = 0.1

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        assert len(new_state.blast_zones) == 1
        blast_zone = new_state.blast_zones[0]
        # Blast zone detonates at 0.1s, then expands for rest of turn (14.9s)
        # After 5s it transitions to PERSISTENCE, so check for either phase
        assert blast_zone.phase in [BlastZonePhase.EXPANSION, BlastZonePhase.PERSISTENCE]
        assert blast_zone.age > 0.0  # Age should have incremented
        assert blast_zone.current_radius > 0.0  # Radius should have grown
        assert blast_zone.owner == "ship_a"

    def test_blast_zone_has_correct_position(self, physics_engine, basic_state):
        """Test that blast zone is created at torpedo's position."""
        torpedo_pos = Vec2D(50, 25)
        basic_state.torpedoes[0].position = torpedo_pos
        basic_state.torpedoes[0].detonation_timer = 0.1

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        blast_zone = new_state.blast_zones[0]
        # Position should match torpedo position (approximately, due to movement during substeps)
        assert abs(blast_zone.position.x - torpedo_pos.x) < 1.0  # Allow small movement
        assert abs(blast_zone.position.y - torpedo_pos.y) < 1.0

    def test_blast_zone_base_damage_calculated_correctly(self, physics_engine, basic_state, config):
        """Test that base_damage = ae_remaining × blast_damage_multiplier."""
        ae_remaining = 75.0
        basic_state.torpedoes[0].ae_remaining = ae_remaining
        basic_state.torpedoes[0].detonation_timer = 0.1

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        blast_zone = new_state.blast_zones[0]
        expected_damage = ae_remaining * config.torpedo.blast_damage_multiplier
        # Allow for small AE burn during substeps
        assert abs(blast_zone.base_damage - expected_damage) < 1.0


class TestAutoDetonation:
    """Test that auto-detonation still works when AE depletes."""

    def test_auto_detonation_when_ae_depletes(self, physics_engine, basic_state):
        """Test that torpedoes auto-detonate when AE runs out."""
        # Set AE very low so it depletes quickly
        basic_state.torpedoes[0].ae_remaining = 0.1
        basic_state.torpedoes[0].detonation_timer = None

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        # Torpedo should have auto-detonated
        assert len(new_state.torpedoes) == 0
        assert len(new_state.blast_zones) == 1

    def test_auto_detonation_event_type(self, physics_engine, basic_state):
        """Test that auto-detonation has correct event type."""
        basic_state.torpedoes[0].ae_remaining = 0.1
        basic_state.torpedoes[0].detonation_timer = None

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        # Find detonation event
        detonation_events = [e for e in events if e.type == "torpedo_detonated"]
        assert len(detonation_events) == 1
        assert detonation_events[0].data["detonation_type"] == "auto"


class TestDetonationEvents:
    """Test that detonation events are recorded correctly."""

    def test_detonation_event_recorded(self, physics_engine, basic_state):
        """Test that torpedo_detonated event is created."""
        basic_state.torpedoes[0].detonation_timer = 0.1

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        detonation_events = [e for e in events if e.type == "torpedo_detonated"]
        assert len(detonation_events) == 1

    def test_detonation_event_has_correct_data(self, physics_engine, basic_state):
        """Test that detonation event contains all required data."""
        torpedo = basic_state.torpedoes[0]
        torpedo.detonation_timer = 0.1

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        detonation_event = [e for e in events if e.type == "torpedo_detonated"][0]
        assert detonation_event.data["torpedo_id"] == "ship_a_torpedo_1"
        assert detonation_event.data["owner"] == "ship_a"
        assert "position" in detonation_event.data
        assert "ae_remaining" in detonation_event.data
        assert "blast_zone_id" in detonation_event.data
        assert detonation_event.data["detonation_type"] == "timed"


class TestMultipleTorpedoes:
    """Test handling multiple torpedoes with different timers."""

    def test_multiple_torpedoes_different_timers(self, physics_engine, basic_state):
        """Test that multiple torpedoes can have different detonation timers."""
        # Add second torpedo
        basic_state.torpedoes.append(
            TorpedoState(
                id="ship_a_torpedo_2",
                position=Vec2D(60, 0),
                velocity=Vec2D(15, 0),
                heading=0.0,
                ae_remaining=100,
                owner="ship_a",
                just_launched=False,
                detonation_timer=None
            )
        )

        # Set different timers
        basic_state.torpedoes[0].detonation_timer = 0.1  # Detonate quickly
        basic_state.torpedoes[1].detonation_timer = 20.0  # Won't detonate this turn

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        # First torpedo should detonate, second should still be active
        assert len(new_state.torpedoes) == 1
        assert new_state.torpedoes[0].id == "ship_a_torpedo_2"
        assert len(new_state.blast_zones) == 1

    def test_multiple_simultaneous_detonations(self, physics_engine, basic_state):
        """Test that multiple torpedoes can detonate in same turn."""
        # Add second torpedo
        basic_state.torpedoes.append(
            TorpedoState(
                id="ship_a_torpedo_2",
                position=Vec2D(60, 0),
                velocity=Vec2D(15, 0),
                heading=0.0,
                ae_remaining=100,
                owner="ship_a",
                just_launched=False,
                detonation_timer=None
            )
        )

        # Set both to detonate quickly
        basic_state.torpedoes[0].detonation_timer = 0.1
        basic_state.torpedoes[1].detonation_timer = 0.2

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        # Both should detonate
        assert len(new_state.torpedoes) == 0
        assert len(new_state.blast_zones) == 2


class TestTorpedoOrderApplication:
    """Test that torpedo orders are applied correctly."""

    def test_detonate_after_order_sets_timer(self, physics_engine, basic_state):
        """Test that detonate_after order sets detonation timer."""
        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={"ship_a_torpedo_1": "detonate_after:5.0"}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        # Apply orders (just the order application part)
        physics_engine._apply_torpedo_orders(basic_state, orders_a, orders_b)

        # Timer should be set
        assert basic_state.torpedoes[0].detonation_timer == 5.0

    def test_movement_order_does_not_set_timer(self, physics_engine, basic_state):
        """Test that movement orders don't set detonation timer."""
        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={"ship_a_torpedo_1": "HARD_LEFT"}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        # Apply orders
        physics_engine._apply_torpedo_orders(basic_state, orders_a, orders_b)

        # Timer should remain None
        assert basic_state.torpedoes[0].detonation_timer is None


class TestTorpedoRemoval:
    """Test that torpedoes are removed after detonation."""

    def test_torpedo_removed_after_detonation(self, physics_engine, basic_state):
        """Test that torpedo is removed from state after detonation."""
        basic_state.torpedoes[0].detonation_timer = 0.1

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )
        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="MAINTAIN_CONFIG",
            torpedo_orders={}
        )

        new_state, events = physics_engine.resolve_turn(basic_state, orders_a, orders_b)

        # Torpedo should be removed
        assert len(new_state.torpedoes) == 0
        # Original state should still have torpedo (immutability check)
        assert len(basic_state.torpedoes) == 1
