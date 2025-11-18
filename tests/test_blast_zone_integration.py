"""Tests for Story 035: Blast Zone Integration & Balance

Integration tests that validate the complete blast zone system working together
with timed detonations, damage, and tactical scenarios.
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


class TestFullTorpedoLifecycle:
    """Test complete torpedo lifecycle with blast zone creation."""

    def test_torpedo_detonation_creates_blast_zone(self, physics_engine):
        """Test that torpedo detonation creates a blast zone with correct properties."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0, 0),
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
            torpedoes=[
                TorpedoState(
                    id="ship_a_torpedo_1",
                    position=Vec2D(50, 0),
                    velocity=Vec2D(15, 0),
                    heading=0.0,
                    ae_remaining=30.0,
                    owner="ship_a",
                    detonation_timer=1.0  # Detonate after 1 second
                )
            ],
            blast_zones=[]
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

        new_state, events = physics_engine.resolve_turn(state, orders_a, orders_b)

        # Torpedo should have detonated and created blast zone
        assert len(new_state.torpedoes) == 0  # Torpedo removed
        assert len(new_state.blast_zones) == 1  # Blast zone created

        zone = new_state.blast_zones[0]
        assert zone.owner == "ship_a"
        # Zone may be in EXPANSION or PERSISTENCE depending on turn duration
        # (detonates at 1s, expansion lasts 5s, turn is 15s, so likely in PERSISTENCE by turn end)
        assert zone.phase in [BlastZonePhase.EXPANSION, BlastZonePhase.PERSISTENCE]
        # Base damage depends on AE remaining at detonation (burns ~1 AE/s while flying)
        # Started with 30 AE, flies for ~1s, so ~29 AE remaining → ~43.5 base damage
        assert zone.base_damage > 40.0 and zone.base_damage < 50.0
        assert zone.current_radius > 0.0  # Expanded from initial 0


class TestOverlappingBlastZones:
    """Test scenarios with multiple overlapping blast zones."""

    def test_overlapping_zones_stack_damage(self, physics_engine, default_orders):
        """Test that multiple overlapping zones cause cumulative damage."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),  # In both zones
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
                    id="zone_1",
                    position=Vec2D(50, 0),
                    base_damage=45.0,  # 3.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                ),
                BlastZone(
                    id="zone_2",
                    position=Vec2D(52, 0),  # Overlapping
                    base_damage=30.0,  # 2.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                ),
                BlastZone(
                    id="zone_3",
                    position=Vec2D(48, 0),  # Also overlapping
                    base_damage=15.0,  # 1.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Ship should take cumulative damage: (3.0 + 2.0 + 1.0) × 15 = 90.0
        expected_damage = 6.0 * physics_engine.action_phase_duration
        actual_damage = initial_shields - new_state.ship_a.shields
        assert abs(actual_damage - expected_damage) < 0.01


class TestBlastZonePersistence:
    """Test that blast zones persist across multiple turns."""

    def test_blast_zone_survives_multiple_turns(self, physics_engine, default_orders):
        """Test that blast zones persist across turns and continue damaging ships."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=200,
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
                    id="persistent_zone",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        # Turn 1
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)
        assert len(new_state.blast_zones) == 1
        damage_turn_1 = 200.0 - new_state.ship_a.shields

        # Turn 2
        new_state2, events2 = physics_engine.resolve_turn(new_state, default_orders, default_orders)
        assert len(new_state2.blast_zones) == 1  # Zone still active
        damage_turn_2 = new_state.ship_a.shields - new_state2.ship_a.shields

        # Both turns should cause similar damage
        assert abs(damage_turn_1 - damage_turn_2) < 1.0  # Similar damage each turn


class TestTacticalScenarios:
    """Test realistic tactical scenarios involving blast zones."""

    def test_ship_escapes_blast_zone_by_moving(self, physics_engine):
        """Test ship can escape blast zone damage by moving away."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 5),  # Near zone edge
                velocity=Vec2D(0, 0),
                heading=np.pi/2,  # Facing north
                shields=100.0,
                ae=200,
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
                    id="danger_zone",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"
                )
            ]
        )

        # Ship A moves forward (north) away from blast zone
        orders_a = Orders(
            movement=MovementDirection.FORWARD,  # Move north
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

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, orders_a, orders_b)

        # Ship moves 10 units/s × 15s = 150 units north
        # Starting at (50, 5), distance from (50, 0) is 5 units (inside 15 unit radius)
        # After moving north 150 units, distance is ~150 units (well outside radius)
        # Should take some damage initially but much less than full turn
        damage = initial_shields - new_state.ship_a.shields
        full_turn_damage = 3.0 * physics_engine.action_phase_duration  # 45.0
        assert damage < full_turn_damage * 0.5  # Less than half damage (escaped early)


class TestDeterminism:
    """Test that blast zone mechanics are deterministic."""

    def test_blast_zone_expansion_deterministic(self, physics_engine, default_orders):
        """Test that blast zone expansion produces identical results."""
        def create_state():
            return GameState(
                turn=1,
                ship_a=ShipState(
                    position=Vec2D(0, 0),
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
                        id="test_zone",
                        position=Vec2D(50, 0),
                        base_damage=45.0,
                        phase=BlastZonePhase.EXPANSION,
                        age=0.0,
                        current_radius=0.0,
                        owner="ship_a"
                    )
                ]
            )

        # Run twice with identical inputs
        state1 = create_state()
        state2 = create_state()

        new_state1, events1 = physics_engine.resolve_turn(state1, default_orders, default_orders)
        new_state2, events2 = physics_engine.resolve_turn(state2, default_orders, default_orders)

        # Results should be identical
        zone1 = new_state1.blast_zones[0]
        zone2 = new_state2.blast_zones[0]

        assert zone1.age == zone2.age
        assert zone1.current_radius == zone2.current_radius
        assert zone1.phase == zone2.phase


class TestPerformance:
    """Test performance with many active blast zones."""

    def test_many_blast_zones_perform_acceptably(self, physics_engine, default_orders):
        """Test that simulation performs well with 10+ blast zones."""
        import time

        # Create state with 12 blast zones
        blast_zones = []
        for i in range(12):
            blast_zones.append(
                BlastZone(
                    id=f"zone_{i}",
                    position=Vec2D(50 + i * 5, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a" if i % 2 == 0 else "ship_b"
                )
            )

        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(75, 0),  # In some zones
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=500.0,
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
            blast_zones=blast_zones
        )

        start_time = time.time()
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)
        elapsed_time = time.time() - start_time

        # Should complete in reasonable time (< 1 second for one turn)
        assert elapsed_time < 1.0
        assert len(new_state.blast_zones) == 12  # All zones still active


class TestBlastZoneEvents:
    """Test that blast zone events are properly recorded."""

    def test_blast_damage_events_in_replay(self, physics_engine, default_orders):
        """Test that blast damage events are recorded for replay."""
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
                    id="event_test_zone",
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
        blast_events = [e for e in events if e.type == "blast_damage"]
        assert len(blast_events) > 0

        # Events should have complete data
        event = blast_events[0]
        assert "ship" in event.data
        assert "blast_zone_id" in event.data
        assert "damage" in event.data
        assert "zone_phase" in event.data
        assert "zone_radius" in event.data
        assert "distance" in event.data
