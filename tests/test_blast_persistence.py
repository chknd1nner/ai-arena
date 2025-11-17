"""Tests for Story 031: Blast Zone Persistence System

Tests that blast zones persist at full radius for 60 seconds after expansion.
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
def state_with_persisting_zone(config):
    """Create game state with blast zone in PERSISTENCE phase."""
    # Blast zone that just transitioned to persistence (age = expansion_duration)
    expansion_duration = config.torpedo.blast_expansion_seconds
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
                phase=BlastZonePhase.PERSISTENCE,
                age=expansion_duration,  # Just entered persistence
                current_radius=max_radius,
                owner="ship_a"
            )
        ]
    )


class TestPersistencePhaseStability:
    """Test that blast zones maintain their radius during persistence."""

    def test_radius_remains_at_max_during_persistence(self, physics_engine, state_with_persisting_zone, config):
        """Test that radius stays at max_radius throughout persistence."""
        max_radius = config.torpedo.blast_radius_units
        initial_radius = state_with_persisting_zone.blast_zones[0].current_radius

        # Simulate 30 seconds of persistence (middle of persistence phase)
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(30.0 / dt)):
            physics_engine._update_blast_zones(state_with_persisting_zone.blast_zones, dt)

        zone = state_with_persisting_zone.blast_zones[0]
        assert zone.current_radius == max_radius
        assert zone.current_radius == initial_radius  # Unchanged

    def test_radius_unchanged_at_various_persistence_times(self, physics_engine, state_with_persisting_zone, config):
        """Test radius at multiple points during persistence phase."""
        max_radius = config.torpedo.blast_radius_units
        dt = config.simulation.physics_tick_rate_seconds

        # Test at 10, 20, 30, 40, 50 seconds into persistence
        test_times = [10.0, 20.0, 30.0, 40.0, 50.0]

        for test_time in test_times:
            # Reset state
            zone = state_with_persisting_zone.blast_zones[0]
            zone.age = config.torpedo.blast_expansion_seconds
            zone.phase = BlastZonePhase.PERSISTENCE
            zone.current_radius = max_radius

            # Simulate to test time
            for _ in range(int(test_time / dt)):
                physics_engine._update_blast_zones(state_with_persisting_zone.blast_zones, dt)

            assert zone.current_radius == max_radius


class TestPersistenceDuration:
    """Test that persistence phase lasts for correct duration."""

    def test_phase_remains_persistence_for_60_seconds(self, physics_engine, state_with_persisting_zone, config):
        """Test that phase stays PERSISTENCE for full 60 seconds."""
        # Simulate 59 seconds (just before transition)
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(59.0 / dt)):
            physics_engine._update_blast_zones(state_with_persisting_zone.blast_zones, dt)

        zone = state_with_persisting_zone.blast_zones[0]
        assert zone.phase == BlastZonePhase.PERSISTENCE

    def test_phase_transitions_to_dissipation_at_65_seconds(self, physics_engine, state_with_persisting_zone, config):
        """Test that phase transitions to DISSIPATION after 65 seconds total (5 expansion + 60 persistence)."""
        expansion_duration = config.torpedo.blast_expansion_seconds
        persistence_duration = config.torpedo.blast_persistence_seconds
        total_duration = expansion_duration + persistence_duration

        # Reset zone to start of persistence
        zone = state_with_persisting_zone.blast_zones[0]
        zone.age = expansion_duration
        zone.phase = BlastZonePhase.PERSISTENCE

        # Simulate persistence duration + a bit more
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(persistence_duration / dt) + 2):
            physics_engine._update_blast_zones(state_with_persisting_zone.blast_zones, dt)

        assert zone.phase == BlastZonePhase.DISSIPATION


class TestAgeProgression:
    """Test that age increments correctly during persistence."""

    def test_age_increments_during_persistence(self, physics_engine, state_with_persisting_zone, config):
        """Test that age continues to increase during persistence."""
        initial_age = state_with_persisting_zone.blast_zones[0].age
        dt = config.simulation.physics_tick_rate_seconds

        # Simulate 10 seconds
        for _ in range(int(10.0 / dt)):
            physics_engine._update_blast_zones(state_with_persisting_zone.blast_zones, dt)

        zone = state_with_persisting_zone.blast_zones[0]
        expected_age = initial_age + 10.0
        assert abs(zone.age - expected_age) < 0.1  # Allow small floating point error

    def test_age_from_expansion_through_persistence(self, physics_engine, config):
        """Test age progression from expansion through full persistence phase."""
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

        # Simulate through expansion and persistence (65 seconds total)
        dt = config.simulation.physics_tick_rate_seconds
        expansion_duration = config.torpedo.blast_expansion_seconds
        persistence_duration = config.torpedo.blast_persistence_seconds
        total_duration = expansion_duration + persistence_duration

        for _ in range(int(total_duration / dt) + 2):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        zone = state.blast_zones[0]
        # Should have transitioned to DISSIPATION
        assert zone.phase == BlastZonePhase.DISSIPATION
        # Age should be approximately 65 seconds
        assert abs(zone.age - total_duration) < 0.5


class TestMultiplePersistingZones:
    """Test that multiple blast zones can persist simultaneously."""

    def test_multiple_zones_persist_independently(self, physics_engine, config):
        """Test multiple zones in persistence at different ages."""
        max_radius = config.torpedo.blast_radius_units
        expansion_duration = config.torpedo.blast_expansion_seconds

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
                    phase=BlastZonePhase.PERSISTENCE,
                    age=expansion_duration + 10.0,  # 10s into persistence
                    current_radius=max_radius,
                    owner="ship_a"
                ),
                BlastZone(
                    id="blast_2",
                    position=Vec2D(70, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=expansion_duration + 30.0,  # 30s into persistence
                    current_radius=max_radius,
                    owner="ship_b"
                )
            ]
        )

        # Simulate 20 seconds
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(20.0 / dt)):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # Both should still be in persistence and at max radius
        assert state.blast_zones[0].phase == BlastZonePhase.PERSISTENCE
        assert state.blast_zones[0].current_radius == max_radius
        assert state.blast_zones[1].phase == BlastZonePhase.PERSISTENCE
        assert state.blast_zones[1].current_radius == max_radius


class TestConfigDrivenPersistence:
    """Test that persistence duration comes from config."""

    def test_persistence_duration_from_config(self, physics_engine, config):
        """Test that persistence uses config value for duration."""
        expansion_duration = config.torpedo.blast_expansion_seconds
        persistence_duration = config.torpedo.blast_persistence_seconds

        # Create zone at start of persistence
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
                    phase=BlastZonePhase.PERSISTENCE,
                    age=expansion_duration,
                    current_radius=config.torpedo.blast_radius_units,
                    owner="ship_a"
                )
            ]
        )

        # Simulate just before persistence_duration ends (account for floating point)
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(persistence_duration / dt) - 1):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # Should still be in persistence
        zone = state.blast_zones[0]
        assert zone.phase == BlastZonePhase.PERSISTENCE

        # Two more updates should trigger transition (due to floating point accumulation)
        physics_engine._update_blast_zones(state.blast_zones, dt)
        physics_engine._update_blast_zones(state.blast_zones, dt)
        assert zone.phase == BlastZonePhase.DISSIPATION


class TestPersistencePhaseTransition:
    """Test transition from persistence to dissipation."""

    def test_transition_occurs_at_correct_time(self, physics_engine, state_with_persisting_zone, config):
        """Test that transition to DISSIPATION happens at persistence_end."""
        expansion_duration = config.torpedo.blast_expansion_seconds
        persistence_duration = config.torpedo.blast_persistence_seconds

        # Start at beginning of persistence
        zone = state_with_persisting_zone.blast_zones[0]
        zone.age = expansion_duration
        zone.phase = BlastZonePhase.PERSISTENCE

        # Simulate just before transition (account for floating point precision)
        dt = config.simulation.physics_tick_rate_seconds
        steps_to_transition = int(persistence_duration / dt) - 1

        for step in range(steps_to_transition):
            physics_engine._update_blast_zones(state_with_persisting_zone.blast_zones, dt)
            # Should still be in persistence
            assert zone.phase == BlastZonePhase.PERSISTENCE

        # Two more steps should trigger transition (due to floating point accumulation)
        physics_engine._update_blast_zones(state_with_persisting_zone.blast_zones, dt)
        physics_engine._update_blast_zones(state_with_persisting_zone.blast_zones, dt)
        assert zone.phase == BlastZonePhase.DISSIPATION
