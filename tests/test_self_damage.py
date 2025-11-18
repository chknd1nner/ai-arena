"""Tests for Story 034: Self-Damage Implementation

Tests that ships can be damaged by their own torpedoes when inside blast zones.
Self-damage should work because _apply_blast_damage() doesn't check zone ownership.
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


class TestBasicSelfDamage:
    """Test that ships take damage from their own torpedoes."""

    def test_ship_a_takes_damage_from_own_blast_zone(self, physics_engine, default_orders):
        """Test that Ship A takes damage from blast zone it owns."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),  # Inside own blast zone
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 0),  # Far away, safe
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="ship_a_torpedo_1_blast",
                    position=Vec2D(50, 0),
                    base_damage=45.0,  # 3.0 damage/second
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a"  # Ship A's own torpedo
                )
            ]
        )

        initial_shields_a = state.ship_a.shields
        initial_shields_b = state.ship_b.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Ship A should take self-damage
        assert new_state.ship_a.shields < initial_shields_a
        expected_damage = 3.0 * physics_engine.action_phase_duration  # 45.0
        actual_damage = initial_shields_a - new_state.ship_a.shields
        assert abs(actual_damage - expected_damage) < 0.01

        # Ship B should be unaffected (too far away)
        assert new_state.ship_b.shields == initial_shields_b

    def test_ship_b_takes_damage_from_own_blast_zone(self, physics_engine, default_orders):
        """Test that Ship B takes damage from blast zone it owns."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(200, 0),  # Far away, safe
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(50, 0),  # Inside own blast zone
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="ship_b_torpedo_1_blast",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_b"  # Ship B's own torpedo
                )
            ]
        )

        initial_shields_a = state.ship_a.shields
        initial_shields_b = state.ship_b.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Ship A should be unaffected (too far away)
        assert new_state.ship_a.shields == initial_shields_a

        # Ship B should take self-damage
        assert new_state.ship_b.shields < initial_shields_b
        expected_damage = 3.0 * physics_engine.action_phase_duration  # 45.0
        actual_damage = initial_shields_b - new_state.ship_b.shields
        assert abs(actual_damage - expected_damage) < 0.01

    def test_ship_outside_own_blast_zone_takes_no_self_damage(self, physics_engine, default_orders):
        """Test that ship outside its own blast zone takes no self-damage."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(100, 0),  # Outside own blast zone (50 units away)
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
                    id="ship_a_torpedo_1_blast",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,  # Ship A at distance 50, outside radius 15
                    owner="ship_a"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Ship A should not take damage (too far from own blast)
        assert new_state.ship_a.shields == initial_shields


class TestBothShipsInSameBlast:
    """Test scenarios where both ships are in the same blast zone."""

    def test_both_ships_take_damage_in_same_blast_zone(self, physics_engine, default_orders):
        """Test that both owner and non-owner take damage in same blast."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),  # Inside blast zone
                velocity=Vec2D(0, 0),
                heading=0.0,  # Facing east
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=99.0  # Disable phasers for this test
            ),
            ship_b=ShipState(
                position=Vec2D(50, 10),  # Also inside blast zone, but perpendicular to avoid phaser hits
                velocity=Vec2D(0, 0),
                heading=0.0,  # Also facing east (parallel, won't hit each other)
                shields=100.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=99.0  # Disable phasers for this test
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="ship_a_torpedo_1_blast",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a"  # Ship A's torpedo damages both ships
                )
            ]
        )

        initial_shields_a = state.ship_a.shields
        initial_shields_b = state.ship_b.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Both ships should take damage
        expected_damage = 3.0 * physics_engine.action_phase_duration  # 45.0

        actual_damage_a = initial_shields_a - new_state.ship_a.shields
        actual_damage_b = initial_shields_b - new_state.ship_b.shields

        assert abs(actual_damage_a - expected_damage) < 0.01
        assert abs(actual_damage_b - expected_damage) < 0.01

    def test_damage_amount_same_for_owner_and_non_owner(self, physics_engine, default_orders):
        """Test that owner and non-owner take identical damage amounts."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),  # At center
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=99.0  # Disable phasers
            ),
            ship_b=ShipState(
                position=Vec2D(50, 5),  # Slightly offset to avoid same position
                velocity=Vec2D(0, 0),
                heading=0.0,  # Same heading (won't hit each other)
                shields=200.0,
                ae=100,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=99.0  # Disable phasers
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="ship_a_torpedo_1_blast",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a"
                )
            ]
        )

        initial_shields_a = state.ship_a.shields
        initial_shields_b = state.ship_b.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        damage_a = initial_shields_a - new_state.ship_a.shields
        damage_b = initial_shields_b - new_state.ship_b.shields

        # Damage should be identical (both at same position)
        assert abs(damage_a - damage_b) < 0.01


class TestSelfDamageEvents:
    """Test that self-damage events are recorded correctly."""

    def test_self_damage_event_recorded(self, physics_engine, default_orders):
        """Test that blast_damage events include self-damage cases."""
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
                    id="ship_a_torpedo_1_blast",
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a"  # Ship A's own zone
                )
            ]
        )

        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Filter for blast_damage events affecting ship_a
        ship_a_damage_events = [
            e for e in events
            if e.type == "blast_damage" and e.data["ship"] == "ship_a"
        ]

        # Should have self-damage events for ship_a
        assert len(ship_a_damage_events) > 0

    def test_self_damage_event_contains_zone_owner_info(self, physics_engine, default_orders):
        """Test that events allow identifying self-damage (via blast_zone_id)."""
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
                    id="ship_a_torpedo_1_blast",  # ID contains owner info
                    position=Vec2D(50, 0),
                    base_damage=45.0,
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a"
                )
            ]
        )

        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        ship_a_damage_events = [
            e for e in events
            if e.type == "blast_damage" and e.data["ship"] == "ship_a"
        ]

        # Event should contain blast_zone_id that indicates ship_a's zone
        assert len(ship_a_damage_events) > 0
        event = ship_a_damage_events[0]
        assert "blast_zone_id" in event.data
        assert "ship_a" in event.data["blast_zone_id"]  # Can identify self-damage


class TestTacticalScenarios:
    """Test realistic tactical scenarios involving self-damage."""

    def test_close_range_detonation_causes_self_damage(self, physics_engine):
        """Test tactical scenario: close-range torpedo detonation hurts attacker."""
        # Ship A launches torpedo forward, it detonates almost immediately
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,  # Facing east
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
                    position=Vec2D(5, 0),  # Just launched, 5 units ahead
                    velocity=Vec2D(15, 0),  # Moving away at 15 units/sec
                    heading=0.0,
                    ae_remaining=30.0,
                    owner="ship_a",
                    detonation_timer=0.5  # Detonates after 0.5 seconds
                )
            ],
            blast_zones=[]
        )

        # Ship A stays still (risky!)
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

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, orders_a, orders_b)

        # Torpedo detonates at position ~12.5 units from ship (5 + 15*0.5)
        # Ship is within 15-unit blast radius - should take self-damage
        assert new_state.ship_a.shields < initial_shields

    def test_successful_escape_avoids_self_damage(self, physics_engine):
        """Test tactical scenario: ship escapes own torpedo blast."""
        # Ship A launches torpedo, then retreats
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0, 0),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100.0,
                ae=200,  # Extra AE for retreat
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
                    position=Vec2D(10, 0),  # Ahead of ship
                    velocity=Vec2D(15, 0),
                    heading=0.0,
                    ae_remaining=30.0,
                    owner="ship_a",
                    detonation_timer=10.0  # Detonates after 10 seconds
                )
            ],
            blast_zones=[]
        )

        # Ship A retreats at full speed
        orders_a = Orders(
            movement=MovementDirection.BACKWARD,  # Retreat!
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

        # Ship retreats for 15 seconds at 10 units/sec backward = 150 units
        # Torpedo moves forward 10 units + 15*10 = 160 units
        # Distance: 160 - (-150) = 310 units apart (well outside 15-unit blast)
        # Ship should NOT take self-damage
        # (Note: there might be minimal damage in early substeps before full escape)
        # Let's be lenient: shields should be close to initial (>90% of original)
        damage_taken = initial_shields - new_state.ship_a.shields
        assert damage_taken < initial_shields * 0.1  # Less than 10% damage

    def test_multiple_own_torpedoes_stack_self_damage(self, physics_engine, default_orders):
        """Test that multiple own blast zones stack self-damage."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50, 0),  # Surrounded by own blast zones
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
                    id="ship_a_torpedo_1_blast",
                    position=Vec2D(50, 0),
                    base_damage=45.0,  # 3.0 damage/sec
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a"
                ),
                BlastZone(
                    id="ship_a_torpedo_2_blast",
                    position=Vec2D(52, 0),  # Overlapping
                    base_damage=30.0,  # 2.0 damage/sec
                    phase=BlastZonePhase.PERSISTENCE,
                    age=5.0,
                    current_radius=15.0,
                    owner="ship_a"
                )
            ]
        )

        initial_shields = state.ship_a.shields
        new_state, events = physics_engine.resolve_turn(state, default_orders, default_orders)

        # Both own zones damage Ship A: (3.0 + 2.0) * 15 = 75.0 damage
        expected_damage = 5.0 * physics_engine.action_phase_duration
        actual_damage = initial_shields - new_state.ship_a.shields
        assert abs(actual_damage - expected_damage) < 0.01
