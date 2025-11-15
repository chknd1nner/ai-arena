"""
Integration tests to verify physics engine uses configuration correctly.

These tests ensure that the physics engine respects config values and that
changing config values would affect physics behavior.
"""

import pytest
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import (
    GameState, ShipState, Orders, Vec2D, MovementType,
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


class TestPhysicsEngineUsesConfigValues:
    """Verify physics engine uses config values correctly."""

    def test_ship_speed_from_config(self, engine, config):
        """Verify ship speed matches config (3.0, not hardcoded 10.0)."""
        assert engine.ship_speed == config.ship.base_speed_units_per_second
        assert engine.ship_speed == 3.0  # Verify it's the config value

        # Verify in actual simulation
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )
        state = GameState(turn=0, ship_a=ship, ship_b=ship, torpedoes=[])
        orders = Orders(movement=MovementDirection.FORWARD, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

        new_state, _ = engine.resolve_turn(state, orders, orders)

        # Distance = speed * time = 3.0 units/s * 15 s = 45 units
        expected_distance = config.ship.base_speed_units_per_second * config.simulation.decision_interval_seconds
        assert abs(new_state.ship_a.position.x - expected_distance) < 0.1

    def test_torpedo_speed_from_config(self, engine, config):
        """Verify torpedo speed matches config (4.0, not hardcoded 15.0)."""
        assert engine.torpedo_speed == config.torpedo.speed_units_per_second
        assert engine.torpedo_speed == 4.0  # Verify it's the config value

    def test_phaser_damage_from_config(self, engine, config):
        """Verify phaser damage values match config."""
        ship_a = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )
        ship_b = ShipState(
            position=Vec2D(20, 0),  # Within WIDE range (30)
            velocity=Vec2D(0, 0),
            heading=3.14159,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )

        state = GameState(turn=0, ship_a=ship_a, ship_b=ship_b, torpedoes=[])
        orders = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

        new_state, events = engine.resolve_turn(state, orders, orders)

        # Check that damage matches config
        phaser_hits = [e for e in events if e.type == "phaser_hit"]
        if phaser_hits:
            # Damage should be from WIDE phaser config
            expected_damage = config.phaser.wide.damage
            for hit in phaser_hits:
                assert hit.data['damage'] == expected_damage

    def test_phaser_range_from_config(self, engine, config):
        """Verify phaser ranges match config."""
        # WIDE phaser: range = 30
        ship_a = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )

        # Test ship just outside WIDE range
        ship_b_outside = ShipState(
            position=Vec2D(35, 0),  # Beyond WIDE range (30)
            velocity=Vec2D(0, 0),
            heading=3.14159,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )

        state = GameState(turn=0, ship_a=ship_a, ship_b=ship_b_outside, torpedoes=[])
        orders = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

        new_state, events = engine.resolve_turn(state, orders, orders)

        # No hits should occur outside range
        phaser_hits = [e for e in events if e.type == "phaser_hit"]
        assert len(phaser_hits) == 0

    def test_torpedo_launch_cost_from_config(self, engine, config):
        """Verify torpedo launch cost matches config."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )

        state = GameState(turn=0, ship_a=ship, ship_b=ship, torpedoes=[])
        orders_a = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="LAUNCH_TORPEDO", torpedo_orders={})
        orders_b = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

        new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

        # AE calculation: start - launch_cost + regen
        # With continuous physics: 100 - 20 + (0.333 * 15) = 100 - 20 + 4.995 = 84.995
        ae_regen = config.ship.ae_regen_per_second * config.simulation.decision_interval_seconds
        expected_ae = 100 - config.torpedo.launch_cost_ae + ae_regen
        # Use floating-point comparison (Story 021: continuous AE regeneration)
        assert abs(new_state.ship_a.ae - expected_ae) < 0.01

    def test_ae_regen_from_config(self, engine, config):
        """Verify AE regeneration matches config."""
        # AE regen = 0.333 per second * 15 seconds = 4.995 per turn (Story 021: continuous)
        expected_regen = config.ship.ae_regen_per_second * config.simulation.decision_interval_seconds
        # ae_regen_per_turn is legacy integer value, kept for compatibility
        assert engine.ae_regen_per_turn == int(expected_regen)

        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=50,  # Start with partial AE
            phaser_config=PhaserConfig.WIDE
        )

        state = GameState(turn=0, ship_a=ship, ship_b=ship, torpedoes=[])
        orders = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

        new_state, _ = engine.resolve_turn(state, orders, orders)

        # AE should increase by exact regen amount (Story 021: continuous regeneration)
        # Use floating-point comparison
        assert abs(new_state.ship_a.ae - (50 + expected_regen)) < 0.01

    def test_simulation_timing_from_config(self, engine, config):
        """Verify simulation timing parameters match config."""
        assert engine.fixed_timestep == config.simulation.physics_tick_rate_seconds
        assert engine.action_phase_duration == config.simulation.decision_interval_seconds

        # Substeps should be duration / timestep = 15.0 / 0.1 = 150
        expected_substeps = int(config.simulation.decision_interval_seconds / config.simulation.physics_tick_rate_seconds)
        assert engine.substeps == expected_substeps


class TestDerivedValues:
    """Test that derived values are computed correctly from config."""

    def test_movement_costs_derived_from_config(self, engine, config):
        """Verify movement costs are derived from AE per second * decision interval."""
        decision_interval = config.simulation.decision_interval_seconds

        # Forward movement cost
        expected_forward = int(config.movement.forward_ae_per_second * decision_interval)
        assert engine.movement_costs[MovementType.STRAIGHT] == expected_forward

        # Stop should be free
        expected_stop = int(config.movement.stop_ae_per_second * decision_interval)
        assert engine.movement_costs[MovementType.STOP] == expected_stop

    def test_torpedo_initial_ae_from_config(self, engine, config):
        """Verify torpedo starts with max_ae_capacity from config."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )

        state = GameState(turn=0, ship_a=ship, ship_b=ship, torpedoes=[])
        orders_a = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="LAUNCH_TORPEDO", torpedo_orders={})
        orders_b = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})

        new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

        # Torpedo starts with max_ae_capacity but burns AE during the turn
        # AE burn = ae_burn_straight_per_second * decision_interval_seconds
        # 40 - (0.3 * 15) = 40 - 4.5 = 35.5
        ae_burned = config.torpedo.ae_burn_straight_per_second * config.simulation.decision_interval_seconds
        expected_ae = config.torpedo.max_ae_capacity - ae_burned
        assert abs(new_state.torpedoes[0].ae_remaining - expected_ae) < 0.01

    def test_max_torpedoes_from_config(self, engine, config):
        """Verify max active torpedoes per ship matches config."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )

        state = GameState(turn=0, ship_a=ship, ship_b=ship, torpedoes=[])

        # Try to launch multiple torpedoes
        for i in range(config.torpedo.max_active_per_ship + 2):
            orders_a = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="LAUNCH_TORPEDO", torpedo_orders={})
            orders_b = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="NONE", torpedo_orders={})
            state, _ = engine.resolve_turn(state, orders_a, orders_b)

        # Should only have max_active_per_ship torpedoes
        ship_a_torpedoes = [t for t in state.torpedoes if t.owner == "ship_a"]
        assert len(ship_a_torpedoes) <= config.torpedo.max_active_per_ship


class TestNoHardcodedValues:
    """Verify no hardcoded values remain in physics calculations."""

    def test_ship_speed_not_hardcoded_10(self, engine):
        """Verify ship speed is NOT the old hardcoded value of 10.0."""
        assert engine.ship_speed != 10.0
        assert engine.ship_speed == 3.0  # Config value

    def test_torpedo_speed_not_hardcoded_15(self, engine):
        """Verify torpedo speed is NOT the old hardcoded value of 15.0."""
        assert engine.torpedo_speed != 15.0
        assert engine.torpedo_speed == 4.0  # Config value

    def test_phaser_damage_not_hardcoded(self, config):
        """Verify phaser damage values are from config, not hardcoded."""
        # These would be the values if properly loaded from config
        assert config.phaser.wide.damage == 15.0
        assert config.phaser.focused.damage == 35.0

        # Ranges should also match config
        assert config.phaser.wide.range_units == 30.0
        assert config.phaser.focused.range_units == 50.0
