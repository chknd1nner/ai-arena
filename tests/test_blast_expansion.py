"""Tests for Story 030: Blast Zone Expansion Phase

Tests that blast zones expand from 0 to 15 units over 5 seconds at 3.0 units/second.
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
def state_with_blast_zone():
    """Create game state with one expanding blast zone."""
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
                phase=BlastZonePhase.EXPANSION,
                age=0.0,
                current_radius=0.0,
                owner="ship_a"
            )
        ]
    )


@pytest.fixture
def default_orders():
    """Default orders for testing (ships stationary)."""
    return Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )


class TestInitialBlastZoneState:
    """Test that blast zones start with correct initial values."""

    def test_blast_zone_starts_with_zero_radius(self, state_with_blast_zone):
        """Test that newly created blast zones have radius=0.0."""
        zone = state_with_blast_zone.blast_zones[0]
        assert zone.current_radius == 0.0

    def test_blast_zone_starts_in_expansion_phase(self, state_with_blast_zone):
        """Test that newly created blast zones start in EXPANSION phase."""
        zone = state_with_blast_zone.blast_zones[0]
        assert zone.phase == BlastZonePhase.EXPANSION

    def test_blast_zone_starts_with_zero_age(self, state_with_blast_zone):
        """Test that newly created blast zones have age=0.0."""
        zone = state_with_blast_zone.blast_zones[0]
        assert zone.age == 0.0


class TestExpansionRate:
    """Test that blast zones expand at the correct rate."""

    def test_radius_grows_at_3_units_per_second(self, physics_engine, state_with_blast_zone, default_orders, config):
        """Test that blast zone radius grows at 3.0 units/second."""
        # Run for 1 second (10 substeps at 0.1s each)
        dt = config.simulation.physics_tick_rate_seconds
        substeps_per_second = int(1.0 / dt)

        for _ in range(substeps_per_second):
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        expected_radius = 3.0  # 3.0 units/s × 1.0s
        assert abs(zone.current_radius - expected_radius) < 0.01

    def test_radius_after_1_second(self, physics_engine, state_with_blast_zone, default_orders, config):
        """Test radius after 1 second of expansion."""
        # Simulate 1 second
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(1.0 / dt)):
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        assert abs(zone.current_radius - 3.0) < 0.01

    def test_radius_after_2_point_5_seconds(self, physics_engine, state_with_blast_zone, default_orders, config):
        """Test radius after 2.5 seconds of expansion."""
        # Simulate 2.5 seconds
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(2.5 / dt)):
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        expected_radius = 7.5  # 3.0 units/s × 2.5s
        assert abs(zone.current_radius - expected_radius) < 0.01

    def test_radius_after_5_seconds(self, physics_engine, state_with_blast_zone, default_orders, config):
        """Test radius after 5 seconds (full expansion)."""
        # Simulate 5 seconds
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(5.0 / dt)):
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        max_radius = config.torpedo.blast_radius_units
        assert abs(zone.current_radius - max_radius) < 0.01


class TestPhaseTransition:
    """Test that blast zones transition from EXPANSION to PERSISTENCE."""

    def test_phase_transitions_at_5_seconds(self, physics_engine, state_with_blast_zone, config):
        """Test that phase changes to PERSISTENCE after 5 seconds."""
        # Simulate 5 seconds (add 1 extra iteration to account for floating point precision)
        dt = config.simulation.physics_tick_rate_seconds
        expansion_duration = config.torpedo.blast_expansion_seconds

        for _ in range(int(expansion_duration / dt) + 1):
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        assert zone.phase == BlastZonePhase.PERSISTENCE

    def test_phase_remains_expansion_before_5_seconds(self, physics_engine, state_with_blast_zone, config):
        """Test that phase stays EXPANSION before 5 seconds."""
        # Simulate 4.9 seconds (just before transition)
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(4.9 / dt)):
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        assert zone.phase == BlastZonePhase.EXPANSION

    def test_radius_set_to_exact_max_on_transition(self, physics_engine, state_with_blast_zone, config):
        """Test that radius is set to exact max_radius when transitioning."""
        # Simulate past transition
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(5.0 / dt) + 5):  # A bit past 5 seconds
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        max_radius = config.torpedo.blast_radius_units
        assert zone.current_radius == max_radius  # Exact equality, not approximate


class TestRadiusCapping:
    """Test that radius never exceeds max_radius."""

    def test_radius_capped_at_max_radius(self, physics_engine, state_with_blast_zone, config):
        """Test that radius doesn't exceed max_radius due to floating point overshoot."""
        # Simulate well past expansion duration
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(10.0 / dt)):  # 10 seconds
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        max_radius = config.torpedo.blast_radius_units
        assert zone.current_radius <= max_radius

    def test_radius_does_not_overshoot_max(self, physics_engine, state_with_blast_zone, config):
        """Test that clamping prevents overshoot."""
        # Manually set radius close to max and update once
        max_radius = config.torpedo.blast_radius_units
        state_with_blast_zone.blast_zones[0].current_radius = max_radius - 0.01
        state_with_blast_zone.blast_zones[0].age = 4.99

        dt = config.simulation.physics_tick_rate_seconds
        physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        assert zone.current_radius <= max_radius


class TestAgeIncrement:
    """Test that blast zone age increments correctly."""

    def test_age_increments_per_substep(self, physics_engine, state_with_blast_zone, config):
        """Test that age increases by dt each update."""
        dt = config.simulation.physics_tick_rate_seconds
        initial_age = state_with_blast_zone.blast_zones[0].age

        physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        assert abs(zone.age - (initial_age + dt)) < 0.0001

    def test_age_after_5_seconds(self, physics_engine, state_with_blast_zone, config):
        """Test that age equals 5.0 after 5 seconds of updates."""
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(5.0 / dt)):
            physics_engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        assert abs(zone.age - 5.0) < 0.01


class TestMultipleBlastZones:
    """Test that multiple blast zones expand independently."""

    def test_multiple_zones_expand_independently(self, physics_engine, config):
        """Test that multiple blast zones created at different times expand correctly."""
        # Create state with two blast zones at different ages
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
                    phase=BlastZonePhase.EXPANSION,
                    age=0.0,
                    current_radius=0.0,
                    owner="ship_a"
                ),
                BlastZone(
                    id="blast_2",
                    position=Vec2D(70, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.EXPANSION,
                    age=2.0,  # Already 2 seconds old
                    current_radius=6.0,  # 2s × 3.0 units/s
                    owner="ship_b"
                )
            ]
        )

        # Simulate 1 second
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(1.0 / dt)):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # First zone should be at 3.0 units (1 second of growth)
        assert abs(state.blast_zones[0].current_radius - 3.0) < 0.01

        # Second zone should be at 9.0 units (started at 6.0, grew for 1 second)
        assert abs(state.blast_zones[1].current_radius - 9.0) < 0.01

    def test_zones_transition_at_different_times(self, physics_engine, config):
        """Test that zones created at different times transition independently."""
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
                    phase=BlastZonePhase.EXPANSION,
                    age=0.0,
                    current_radius=0.0,
                    owner="ship_a"
                ),
                BlastZone(
                    id="blast_2",
                    position=Vec2D(70, 0),
                    base_damage=150.0,
                    phase=BlastZonePhase.EXPANSION,
                    age=4.0,  # Almost done expanding
                    current_radius=12.0,
                    owner="ship_b"
                )
            ]
        )

        # Simulate 1.5 seconds
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(1.5 / dt)):
            physics_engine._update_blast_zones(state.blast_zones, dt)

        # First zone should still be expanding (age=1.5s)
        assert state.blast_zones[0].phase == BlastZonePhase.EXPANSION

        # Second zone should have transitioned (age=5.5s)
        assert state.blast_zones[1].phase == BlastZonePhase.PERSISTENCE


class TestConfigDrivenBehavior:
    """Test that expansion uses config values, not hardcoded constants."""

    def test_expansion_rate_from_config(self, state_with_blast_zone, config):
        """Test that expansion rate is calculated from config."""
        # Create engine with real config
        engine = PhysicsEngine(config)

        # Calculate expected growth rate
        max_radius = config.torpedo.blast_radius_units
        expansion_duration = config.torpedo.blast_expansion_seconds
        expected_rate = max_radius / expansion_duration

        # Simulate one second
        dt = config.simulation.physics_tick_rate_seconds
        for _ in range(int(1.0 / dt)):
            engine._update_blast_zones(state_with_blast_zone.blast_zones, dt)

        zone = state_with_blast_zone.blast_zones[0]
        expected_radius = expected_rate * 1.0
        assert abs(zone.current_radius - expected_radius) < 0.01


class TestIntegrationWithTorpedoDetonation:
    """Test that blast zones created by detonations expand correctly."""

    def test_detonated_torpedo_creates_expanding_blast_zone(self, physics_engine):
        """Test end-to-end: torpedo detonates and blast zone expands."""
        # Create state with torpedo set to detonate
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
            torpedoes=[
                TorpedoState(
                    id="ship_a_torpedo_1",
                    position=Vec2D(50, 0),
                    velocity=Vec2D(15, 0),
                    heading=0.0,
                    ae_remaining=100,
                    owner="ship_a",
                    just_launched=False,
                    detonation_timer=0.1  # Detonate almost immediately
                )
            ]
        )

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

        # Run one turn
        new_state, events = physics_engine.resolve_turn(state, orders_a, orders_b)

        # Blast zone should be created and have some radius (expanded during turn)
        assert len(new_state.blast_zones) == 1
        zone = new_state.blast_zones[0]
        assert zone.phase == BlastZonePhase.EXPANSION or zone.phase == BlastZonePhase.PERSISTENCE
        assert zone.current_radius > 0.0
