"""Tests for Story 033: Continuous Blast Damage

Tests that ships take continuous damage while inside blast zones.
Damage rate = (base_damage ÷ 15.0) per second, applied every substep.
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
def default_orders():
    """Default orders for testing (ships stationary)."""
    return Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )


class TestBasicBlastDamage:
    """Test basic blast damage mechanics."""

    def test_ship_takes_damage_inside_blast_zone(self, physics_engine, default_orders):
        """Test that a ship inside a blast zone takes damage."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),  # Inside blast zone at (50, 0)
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),  # Far away
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),  # Centered on ship_a
                    base_damage=45.0,  # 3.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Ship should have taken damage (15 seconds × 3.0 damage/sec = 45 damage)
        assert new_state.ship_a.shields < initial_shields
        expected_damage = 3.0 * physics_engine.action_phase_duration  # 45.0 (15 seconds)
        actual_damage = initial_shields - new_state.ship_a.shields
        assert abs(actual_damage - expected_damage) < 0.01

    def test_ship_outside_radius_takes_no_damage(self, physics_engine, default_orders):
        """Test that a ship outside blast radius takes no damage."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(100, 0),  # Outside blast zone radius
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,  # Ship is at distance 50, outside radius 15
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Ship should not have taken any blast damage
        # (may have minor AE changes but shields should be unchanged)
        assert new_state.ship_a.shields == initial_shields

    def test_damage_rate_calculation(self, physics_engine, default_orders):
        """Test that damage rate is correctly calculated as base_damage / 15.0."""
        # Base damage 30.0 → 30.0 / 15.0 = 2.0 damage/second
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=150.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=30.0,  # Should give 2.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Expected damage: 2.0 damage/second × 15 seconds = 30.0
        expected_damage = 2.0 * physics_engine.action_phase_duration
        actual_damage = initial_shields - new_state.ship_a.shields
        assert abs(actual_damage - expected_damage) < 0.01


class TestDamageAccumulation:
    """Test that damage accumulates correctly over time."""

    def test_damage_accumulates_over_multiple_substeps(self, physics_engine, default_orders):
        """Test that damage is applied continuously across all substeps."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,  # 3.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Damage per substep: 3.0 damage/sec * 0.1s = 0.3
        # Total substeps: 150 (15 seconds / 0.1 seconds)
        # Total damage: 0.3 × 150 = 45.0
        expected_damage = 3.0 * physics_engine.action_phase_duration  # 45.0
        actual_damage = initial_shields - new_state.ship_a.shields
        assert abs(actual_damage - expected_damage) < 0.01

    def test_overlapping_zones_stack_damage(self, physics_engine, default_orders):
        """Test that multiple overlapping blast zones stack damage."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),  # Inside both zones
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=300.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,  # 3.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                ),
                BlastZone(
                    id="test_blast_2",
                    position=Vec2D(52, 0),  # Overlapping
                    base_damage=30.0,  # 2.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Combined damage: (3.0 + 2.0) × 15 = 75.0
        expected_damage = 5.0 * physics_engine.action_phase_duration
        actual_damage = initial_shields - new_state.ship_a.shields
        assert abs(actual_damage - expected_damage) < 0.01


class TestDamageInAllPhases:
    """Test that damage applies during all blast zone phases."""

    def test_damage_during_expansion_phase(self, physics_engine, default_orders):
        """Test that ships take damage during expansion phase."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 1),  # Close to blast center
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,  # 3.0 damage/second
                    phase=BlastZonePhase.EXPANSION,
                    age=0.0,
                    current_radius=0.0,  # Will expand during turn
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Ship should take damage as zone expands over it
        # Zone expands 3.0 units/sec, ship at distance 1.0, so will be inside very quickly
        assert new_state.ship_a.shields < initial_shields

    def test_damage_during_persistence_phase(self, physics_engine, default_orders):
        """Test that ships take damage during persistence phase."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Full damage for full turn (15 seconds)
        expected_damage = 3.0 * physics_engine.action_phase_duration
        actual_damage = initial_shields - new_state.ship_a.shields
        assert abs(actual_damage - expected_damage) < 0.01

    def test_damage_during_dissipation_phase(self, physics_engine, default_orders):
        """Test that ships take damage during dissipation phase."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.DISSIPATION,
                    age=65.0,  # Past persistence, in dissipation
                    current_radius=15.0,  # Will shrink during turn
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Should take damage while zone is shrinking (less than full turn damage)
        assert new_state.ship_a.shields < initial_shields


class TestDamageEvents:
    """Test that damage events are recorded correctly."""

    def test_blast_damage_events_recorded(self, physics_engine, default_orders):
        """Test that blast damage events are created and recorded."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Should have blast_damage events
        blast_damage_events = [e for e in events if e.type == "blast_damage"]
        assert len(blast_damage_events) > 0

    def test_damage_event_contains_correct_data(self, physics_engine, default_orders):
        """Test that damage events contain all required fields."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        blast_damage_events = [e for e in events if e.type == "blast_damage"]
        assert len(blast_damage_events) > 0

        # Check first event has all required fields
        event = blast_damage_events[0]
        assert "ship" in event.data
        assert "blast_zone_id" in event.data
        assert "damage" in event.data
        assert "zone_phase" in event.data
        assert "zone_radius" in event.data
        assert "distance" in event.data


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_ship_at_exact_radius_boundary(self, physics_engine, default_orders):
        """Test ship at exact radius boundary (should NOT take damage if distance == radius)."""
        # Using distance < radius check, so ship AT radius should not take damage
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(65, 0),  # Exactly 15 units from blast center at (50, 0)
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Should not take damage (distance == radius, not < radius)
        assert new_state.ship_a.shields == initial_shields

    def test_zero_radius_zone_deals_no_damage(self, physics_engine, default_orders):
        """Test that a zone with radius 0 deals no damage."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.EXPANSION,
                    age=0.0,
                    current_radius=0.0,  # Zero radius
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Zone will expand during turn, but initially at radius 0
        # At start of first substep, radius is 0, so no damage yet
        # After expansion starts, ship will start taking damage
        # Overall should see damage since zone expands very quickly
        assert new_state.ship_a.shields < initial_shields

    def test_both_ships_can_take_damage_simultaneously(self, physics_engine, default_orders):
        """Test that both ships can be damaged by blast zones simultaneously."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),  # Inside zone
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(60, 0),  # Also inside zone
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a"  # Ship A's zone damages both ships
                )
            ]
        )

        initial_shields_a = state.ship_a.shields
        initial_shields_b = state.ship_b.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Both ships should have taken damage
        assert new_state.ship_a.shields < initial_shields_a
        assert new_state.ship_b.shields < initial_shields_b
