"""Tests for blast zone data models (Story 028).

Validates the BlastZonePhase enum, BlastZone dataclass,
GameState.blast_zones field, and TorpedoState.detonation_timer field.
"""

import pytest
from dataclasses import asdict
from ai_arena.game_engine.data_models import (
    BlastZone,
    BlastZonePhase,
    GameState,
    TorpedoState,
    Vec2D,
    ShipState,
    PhaserConfig
)
from ai_arena.config.loader import ConfigLoader


class TestBlastZonePhaseEnum:
    """Test BlastZonePhase enum values and properties."""

    def test_all_phases_exist(self):
        """Verify all 3 blast zone phases exist."""
        assert BlastZonePhase.EXPANSION
        assert BlastZonePhase.PERSISTENCE
        assert BlastZonePhase.DISSIPATION

    def test_phase_values(self):
        """Verify blast zone phase enum values are correct strings."""
        assert BlastZonePhase.EXPANSION.value == "expansion"
        assert BlastZonePhase.PERSISTENCE.value == "persistence"
        assert BlastZonePhase.DISSIPATION.value == "dissipation"

    def test_phase_count(self):
        """Verify there are exactly 3 blast zone phases."""
        assert len(BlastZonePhase) == 3


class TestBlastZoneDataclass:
    """Test BlastZone dataclass creation and properties."""

    def test_blast_zone_creation(self):
        """Test BlastZone can be created with all required fields."""
        zone = BlastZone(
            id="ship_a_torp_1_blast",
            position=Vec2D(100.0, 150.0),
            base_damage=45.0,
            phase=BlastZonePhase.EXPANSION,
            age=0.0,
            current_radius=0.0,
            owner="ship_a"
        )
        assert zone.id == "ship_a_torp_1_blast"
        assert zone.position.x == 100.0
        assert zone.position.y == 150.0
        assert zone.base_damage == 45.0
        assert zone.phase == BlastZonePhase.EXPANSION
        assert zone.age == 0.0
        assert zone.current_radius == 0.0
        assert zone.owner == "ship_a"

    def test_blast_zone_different_phases(self):
        """Test BlastZone can be created in each phase."""
        # Expansion phase
        zone_expansion = BlastZone(
            id="test_blast_1",
            position=Vec2D(0.0, 0.0),
            base_damage=60.0,
            phase=BlastZonePhase.EXPANSION,
            age=2.5,
            current_radius=7.5,
            owner="ship_b"
        )
        assert zone_expansion.phase == BlastZonePhase.EXPANSION
        assert zone_expansion.age == 2.5
        assert zone_expansion.current_radius == 7.5

        # Persistence phase
        zone_persistence = BlastZone(
            id="test_blast_2",
            position=Vec2D(0.0, 0.0),
            base_damage=60.0,
            phase=BlastZonePhase.PERSISTENCE,
            age=30.0,
            current_radius=15.0,
            owner="ship_a"
        )
        assert zone_persistence.phase == BlastZonePhase.PERSISTENCE
        assert zone_persistence.age == 30.0
        assert zone_persistence.current_radius == 15.0

        # Dissipation phase
        zone_dissipation = BlastZone(
            id="test_blast_3",
            position=Vec2D(0.0, 0.0),
            base_damage=60.0,
            phase=BlastZonePhase.DISSIPATION,
            age=68.0,
            current_radius=6.0,
            owner="ship_b"
        )
        assert zone_dissipation.phase == BlastZonePhase.DISSIPATION
        assert zone_dissipation.age == 68.0
        assert zone_dissipation.current_radius == 6.0

    def test_blast_zone_serialization(self):
        """Test BlastZone can be serialized to dict/JSON."""
        zone = BlastZone(
            id="ship_a_torp_1_blast",
            position=Vec2D(100.0, 150.0),
            base_damage=45.0,
            phase=BlastZonePhase.EXPANSION,
            age=2.5,
            current_radius=7.5,
            owner="ship_a"
        )

        # Test that the dataclass can be converted to dict
        zone_dict = asdict(zone)
        assert 'id' in zone_dict
        assert 'position' in zone_dict
        assert 'base_damage' in zone_dict
        assert 'phase' in zone_dict
        assert 'age' in zone_dict
        assert 'current_radius' in zone_dict
        assert 'owner' in zone_dict
        assert zone_dict['id'] == "ship_a_torp_1_blast"
        assert zone_dict['base_damage'] == 45.0


class TestGameStateWithBlastZones:
    """Test GameState with blast_zones field."""

    def test_game_state_has_blast_zones_field(self):
        """Test GameState can hold blast zones."""
        # Create game state with empty blast zones
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(100.0, 100.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[]
        )
        assert hasattr(state, 'blast_zones')
        assert state.blast_zones == []

    def test_game_state_with_blast_zones(self):
        """Test GameState can hold multiple blast zones."""
        # Create blast zones
        zone1 = BlastZone(
            id="ship_a_torp_1_blast",
            position=Vec2D(50.0, 50.0),
            base_damage=45.0,
            phase=BlastZonePhase.EXPANSION,
            age=2.0,
            current_radius=6.0,
            owner="ship_a"
        )
        zone2 = BlastZone(
            id="ship_b_torp_1_blast",
            position=Vec2D(150.0, 150.0),
            base_damage=60.0,
            phase=BlastZonePhase.PERSISTENCE,
            age=30.0,
            current_radius=15.0,
            owner="ship_b"
        )

        # Create game state with blast zones
        state = GameState(
            turn=5,
            ship_a=ShipState(
                position=Vec2D(0.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=80,
                ae=70,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(100.0, 100.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=75,
                ae=65,
                phaser_config=PhaserConfig.WIDE
            ),
            torpedoes=[],
            blast_zones=[zone1, zone2]
        )

        assert len(state.blast_zones) == 2
        assert state.blast_zones[0].id == "ship_a_torp_1_blast"
        assert state.blast_zones[1].id == "ship_b_torp_1_blast"
        assert state.blast_zones[0].phase == BlastZonePhase.EXPANSION
        assert state.blast_zones[1].phase == BlastZonePhase.PERSISTENCE

    def test_game_state_blast_zones_default_empty(self):
        """Test GameState blast_zones defaults to empty list."""
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(100.0, 100.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            )
        )
        assert state.blast_zones == []

    def test_game_state_serialization_with_blast_zones(self):
        """Test GameState with blast_zones can be serialized."""
        zone = BlastZone(
            id="ship_a_torp_1_blast",
            position=Vec2D(50.0, 50.0),
            base_damage=45.0,
            phase=BlastZonePhase.EXPANSION,
            age=2.0,
            current_radius=6.0,
            owner="ship_a"
        )

        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(100.0, 100.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            blast_zones=[zone]
        )

        # Test serialization
        state_dict = asdict(state)
        assert 'blast_zones' in state_dict
        assert len(state_dict['blast_zones']) == 1
        assert state_dict['blast_zones'][0]['id'] == "ship_a_torp_1_blast"


class TestTorpedoStateWithDetonationTimer:
    """Test TorpedoState with detonation_timer field."""

    def test_torpedo_state_has_detonation_timer_field(self):
        """Test TorpedoState has optional detonation_timer field."""
        # Torpedo without timer (auto-detonate on collision)
        torp1 = TorpedoState(
            id="ship_a_torp_1",
            position=Vec2D(10.0, 10.0),
            velocity=Vec2D(4.0, 0.0),
            heading=0.0,
            ae_remaining=30,
            owner="ship_a",
            just_launched=False,
            detonation_timer=None
        )
        assert hasattr(torp1, 'detonation_timer')
        assert torp1.detonation_timer is None

    def test_torpedo_state_with_detonation_timer(self):
        """Test TorpedoState with timed detonation."""
        # Torpedo with timer (timed detonation)
        torp = TorpedoState(
            id="ship_a_torp_2",
            position=Vec2D(20.0, 20.0),
            velocity=Vec2D(4.0, 0.0),
            heading=0.0,
            ae_remaining=35,
            owner="ship_a",
            just_launched=False,
            detonation_timer=8.5
        )
        assert torp.detonation_timer == 8.5

    def test_torpedo_state_detonation_timer_default_none(self):
        """Test TorpedoState detonation_timer defaults to None."""
        torp = TorpedoState(
            id="ship_a_torp_1",
            position=Vec2D(10.0, 10.0),
            velocity=Vec2D(4.0, 0.0),
            heading=0.0,
            ae_remaining=30,
            owner="ship_a"
        )
        assert torp.detonation_timer is None

    def test_torpedo_state_serialization_with_timer(self):
        """Test TorpedoState serialization includes detonation_timer."""
        torp = TorpedoState(
            id="ship_a_torp_1",
            position=Vec2D(10.0, 10.0),
            velocity=Vec2D(4.0, 0.0),
            heading=0.0,
            ae_remaining=30,
            owner="ship_a",
            detonation_timer=5.0
        )

        torp_dict = asdict(torp)
        assert 'detonation_timer' in torp_dict
        assert torp_dict['detonation_timer'] == 5.0


class TestConfigLoadingBlastZoneParams:
    """Test config.json loading with blast zone parameters."""

    def test_config_loads_blast_zone_params(self):
        """Test config.json loads with blast zone parameters."""
        config = ConfigLoader().load("config.json")

        # Verify all blast zone parameters exist
        assert hasattr(config.torpedo, 'blast_expansion_seconds')
        assert hasattr(config.torpedo, 'blast_persistence_seconds')
        assert hasattr(config.torpedo, 'blast_dissipation_seconds')
        assert hasattr(config.torpedo, 'blast_radius_units')
        assert hasattr(config.torpedo, 'blast_damage_multiplier')

    def test_config_blast_zone_param_values(self):
        """Test config.json blast zone parameters have expected values."""
        config = ConfigLoader().load("config.json")

        # Verify values match config.json
        assert config.torpedo.blast_expansion_seconds == 5.0
        assert config.torpedo.blast_persistence_seconds == 60.0
        assert config.torpedo.blast_dissipation_seconds == 5.0
        assert config.torpedo.blast_radius_units == 15.0
        assert config.torpedo.blast_damage_multiplier == 1.5

    def test_config_blast_zone_param_types(self):
        """Test config.json blast zone parameters are correct types."""
        config = ConfigLoader().load("config.json")

        # Verify types
        assert isinstance(config.torpedo.blast_expansion_seconds, float)
        assert isinstance(config.torpedo.blast_persistence_seconds, float)
        assert isinstance(config.torpedo.blast_dissipation_seconds, float)
        assert isinstance(config.torpedo.blast_radius_units, float)
        assert isinstance(config.torpedo.blast_damage_multiplier, float)
