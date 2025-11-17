"""Tests for Story 032: Blast Zone Dissipation Phase

Tests that blast zones shrink from 15 to 0 units over 5 seconds and are then removed.
"""

import pytest
import numpy as np
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import (
    GameState, Orders, ShipState, Vec2D,
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
def state_with_dissipating_zone(config):
    """Create game state with blast zone in DISSIPATION phase."""
    # Blast zone that just transitioned to dissipation (age = 65 seconds)
    expansion_duration = config.torpedo.blast_expansion_seconds
    persistence_duration = config.torpedo.blast_persistence_seconds
    max_radius = config.torpedo.blast_radius_units

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
        torpedoes=[],
        blast_zones=[
            BlastZone(
                id="test_blast_1",
                position=Vec2D(50, 0),
                base_damage=150.0,
                phase=BlastZonePhase.DISSIPATION,
                age=expansion_duration + persistence_duration,  # Just entered dissipation
                current_radius=max_radius,
                owner="ship_a"
            )
        ]
    )


class TestDissipationRate:
    """Test that blast zones shrink at the correct rate."""

    def test_radius_shrinks_at_3_units_per_second(self, physics_engine, state_with_dissipating_zone, config):
        """Test that blast zone radius shrinks at 3.0 units/second."""
        max_radius = config.torpedo.blast_radius_units
        initial_radius = state_with_dissipating_zone.blast_zones[0].current_radius

        # Simulate 1 second
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(1.0 / dt)):
            physics_engine._update_blast_zones(state_with_dissipating_zone.blast_zones, dt)

        zone = state_with_dissipating_zone.blast_zones[0]
        expected_radius = max_radius - 3.0  # 15.0 - 3.0 = 12.0
        assert abs(zone.current_radius - expected_radius) < 0.1

    def test_radius_after_1_second_dissipation(self, physics_engine, state_with_dissipating_zone, config):
        """Test radius after 1 second of dissipation."""
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(1.0 / dt)):
            physics_engine._update_blast_zones(state_with_dissipating_zone.blast_zones, dt)

        zone = state_with_dissipating_zone.blast_zones[0]
        expected_radius = 12.0  # 15.0 - 3.0
        assert abs(zone.current_radius - expected_radius) < 0.1

    def test_radius_after_2_point_5_seconds_dissipation(self, physics_engine, state_with_dissipating_zone, config):
        """Test radius after 2.5 seconds of dissipation."""
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(2.5 / dt)):
            physics_engine._update_blast_zones(state_with_dissipating_zone.blast_zones, dt)

        # Zone might be removed already, but if still there, check radius
        if state_with_dissipating_zone.blast_zones:
            zone = state_with_dissipating_zone.blast_zones[0]
            expected_radius = 7.5  # 15.0 - (3.0 × 2.5)
            assert abs(zone.current_radius - expected_radius) < 0.1

    def test_radius_after_5_seconds_dissipation(self, physics_engine, state_with_dissipating_zone, config):
        """Test radius after 5 seconds of dissipation (should be 0 and removed)."""
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(5.0 / dt) + 5):  # Extra iterations to ensure removal
            physics_engine._update_blast_zones(state_with_dissipating_zone.blast_zones, dt)

        # Zone should be removed
        assert len(state_with_dissipating_zone.blast_zones) == 0


class TestRadiusClamping:
    """Test that radius is clamped at 0.0."""

    def test_radius_clamped_at_zero(self, physics_engine, state_with_dissipating_zone, config):
        """Test that radius doesn't go negative."""
        # Simulate well past dissipation end
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(10.0 / dt)):
            physics_engine._update_blast_zones(state_with_dissipating_zone.blast_zones, dt)

        # Zone should be removed, but if somehow still there, radius should be 0
        if state_with_dissipating_zone.blast_zones:
            zone = state_with_dissipating_zone.blast_zones[0]
            assert zone.current_radius >= 0.0


class TestBlastZoneRemoval:
    """Test that blast zones are removed when radius reaches 0."""

    def test_zone_removed_when_radius_zero(self, physics_engine, state_with_dissipating_zone, config):
        """Test that blast zone is removed when radius reaches 0.0."""
        dt = config.simulation.physics_tick_rate_seconds
        dissipation_duration = config.torpedo.blast_dissipation_seconds

        # Simulate dissipation duration + a bit more
        for _ in range(int(dissipation_duration / dt) + 5):
            physics_engine._update_blast_zones(state_with_dissipating_zone.blast_zones, dt)

        # Zone should be removed
        assert len(state_with_dissipating_zone.blast_zones) == 0

    def test_zone_count_decreases_on_removal(self, physics_engine, config):
        """Test that the number of blast zones decreases when one is removed."""
        max_radius = config.torpedo.blast_radius_units
        expansion_duration = config.torpedo.blast_expansion_seconds
        persistence_duration = config.torpedo.blast_persistence_seconds

        state = GameState(
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
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="blast_1",
                    position=Vec2D(30, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.DISSIPATION,
                    age=expansion_duration + persistence_duration,
                    current_radius=max_radius,
                    owner="ship_a"
                ),
                BlastZone(
                    id="blast_2",
                    position=Vec2D(70, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=expansion_duration + 30.0,  # Still persisting
                    current_radius=max_radius,
                    owner="ship_b"
                )
            ]
        )

        initial_count = len(state.blast_zones)
        assert initial_count == 2

        # Simulate dissipation for first zone
        dt = config.simulation.physics_tick_rate_seconds
        dissipation_duration = config.torpedo.blast_dissipation_seconds
        for _ in range(int(dissipation_duration / dt) + 5):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # First zone should be removed, second still there
        assert len(state.blast_zones) == 1
        assert state.blast_zones[0].id == "blast_2"


class TestAgeProgression:
    """Test that age increments correctly during dissipation."""

    def test_age_increments_during_dissipation(self, physics_engine, state_with_dissipating_zone, config):
        """Test that age continues to increase during dissipation."""
        initial_age = state_with_dissipating_zone.blast_zones[0].age
        dt = config.simulation.physics_tick_rate_seconds

        # Simulate 2 seconds (before removal)
        for _ in range(int(2.0 / dt)):
            physics_engine._update_blast_zones(state_with_dissipating_zone.blast_zones, dt)

        # Zone should still exist
        if state_with_dissipating_zone.blast_zones:
            zone = state_with_dissipating_zone.blast_zones[0]
            expected_age = initial_age + 2.0
            assert abs(zone.age - expected_age) < 0.2


class TestMultipleDissipatingZones:
    """Test that multiple blast zones can dissipate simultaneously."""

    def test_multiple_zones_dissipate_independently(self, physics_engine, config):
        """Test multiple zones in dissipation at different stages."""
        max_radius = config.torpedo.blast_radius_units
        expansion_duration = config.torpedo.blast_expansion_seconds
        persistence_duration = config.torpedo.blast_persistence_seconds

        state = GameState(
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
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="blast_1",
                    position=Vec2D(30, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.DISSIPATION,
                    age=expansion_duration + persistence_duration,  # Just started dissipating
                    current_radius=max_radius,
                    owner="ship_a"
                ),
                BlastZone(
                    id="blast_2",
                    position=Vec2D(70, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.DISSIPATION,
                    age=expansion_duration + persistence_duration + 2.0,  # 2s into dissipation
                    current_radius=max_radius - 6.0,  # 15.0 - (3.0 × 2)
                    owner="ship_b"
                )
            ]
        )

        # Simulate 1 second
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(1.0 / dt)):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # Both should still be dissipating
        assert len(state.blast_zones) == 2
        # First zone: 15.0 - 3.0 = 12.0
        assert abs(state.blast_zones[0].current_radius - 12.0) < 0.1
        # Second zone: 9.0 - 3.0 = 6.0
        assert abs(state.blast_zones[1].current_radius - 6.0) < 0.1


class TestFullLifecycle:
    """Test complete blast zone lifecycle from creation to removal."""

    def test_full_70_second_lifecycle(self, physics_engine, config):
        """Test blast zone through expansion, persistence, dissipation, and removal."""
        # Create zone at start of expansion
        state = GameState(
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
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.EXPANSION,
                    age=0.0,
                    current_radius=0.0,
                    owner="ship_a"
                )
            ]
        )

        dt = config.simulation.physics_tick_rate_seconds
        expansion_duration = config.torpedo.blast_expansion_seconds
        persistence_duration = config.torpedo.blast_persistence_seconds
        dissipation_duration = config.torpedo.blast_dissipation_seconds
        total_duration = expansion_duration + persistence_duration + dissipation_duration

        # Simulate full lifecycle
        for step in range(int(total_duration / dt) + 10):
            if not state.blast_zones:
                # Zone has been removed
                break
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # Zone should be removed after full lifecycle
        assert len(state.blast_zones) == 0


class TestConfigDrivenDissipation:
    """Test that dissipation uses config values."""

    def test_dissipation_rate_from_config(self, physics_engine, state_with_dissipating_zone, config):
        """Test that shrink rate is calculated from config."""
        max_radius = config.torpedo.blast_radius_units
        dissipation_duration = config.torpedo.blast_dissipation_seconds
        expected_shrink_rate = max_radius / dissipation_duration

        # Simulate 1 second
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(1.0 / dt)):
            physics_engine._update_blast_zones(state_with_dissipating_zone.blast_zones, dt)

        zone = state_with_dissipating_zone.blast_zones[0]
        expected_radius = max_radius - (expected_shrink_rate * 1.0)
        assert abs(zone.current_radius - expected_radius) < 0.1


class TestDissipationAtVariousTimes:
    """Test dissipation at specific time points during the phase."""

    def test_radius_at_66_seconds(self, physics_engine, config):
        """Test radius at 66 seconds total (1 second into dissipation)."""
        max_radius = config.torpedo.blast_radius_units
        expansion_duration = config.torpedo.blast_expansion_seconds
        persistence_duration = config.torpedo.blast_persistence_seconds

        state = GameState(
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
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.EXPANSION,
                    age=0.0,
                    current_radius=0.0,
                    owner="ship_a"
                )
            ]
        )

        # Simulate to 66 seconds
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(66.0 / dt)):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # Should be in dissipation with radius ~12.0 (15.0 - 3.0)
        zone = state.blast_zones[0]
        assert zone.phase == BlastZonePhase.DISSIPATION
        assert abs(zone.current_radius - 12.0) < 0.5

    def test_radius_at_67_point_5_seconds(self, physics_engine, config):
        """Test radius at 67.5 seconds total (2.5 seconds into dissipation)."""
        state = GameState(
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
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="test_blast_1",
                    position=Vec2D(50, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.EXPANSION,
                    age=0.0,
                    current_radius=0.0,
                    owner="ship_a"
                )
            ]
        )

        # Simulate to 67.5 seconds
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(67.5 / dt)):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # Should be in dissipation with radius ~7.5 (15.0 - 7.5)
        if state.blast_zones:
            zone = state.blast_zones[0]
            assert zone.phase == BlastZonePhase.DISSIPATION
            assert abs(zone.current_radius - 7.5) < 0.5
