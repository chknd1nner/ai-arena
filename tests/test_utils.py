"""Tests for game engine utilities (Story 043).

Validates shared utility functions in ai_arena/game_engine/utils.py.
"""

import pytest
from ai_arena.game_engine.utils import parse_torpedo_action, deep_copy_game_state
from ai_arena.game_engine.data_models import (
    GameState,
    ShipState,
    TorpedoState,
    BlastZone,
    Vec2D,
    PhaserConfig,
    BlastZonePhase
)


class TestParseTorpedoAction:
    """Test torpedo action parsing utility."""

    def test_parse_movement_command(self):
        """Verify movement commands are parsed correctly."""
        action, delay = parse_torpedo_action("HARD_LEFT")
        assert action == "HARD_LEFT"
        assert delay is None

    def test_parse_detonate_command(self):
        """Verify detonation commands are parsed correctly."""
        action, delay = parse_torpedo_action("detonate_after:8.5")
        assert action == "detonate_after"
        assert delay == 8.5

    def test_parse_detonate_command_case_insensitive(self):
        """Verify detonation commands are case insensitive."""
        action, delay = parse_torpedo_action("DETONATE_AFTER:5.0")
        assert action == "detonate_after"
        assert delay == 5.0

    def test_parse_detonate_zero_delay(self):
        """Verify zero delay detonation is valid."""
        action, delay = parse_torpedo_action("detonate_after:0.0")
        assert action == "detonate_after"
        assert delay == 0.0

    def test_parse_detonate_max_delay(self):
        """Verify max delay (15.0) is valid."""
        action, delay = parse_torpedo_action("detonate_after:15.0")
        assert action == "detonate_after"
        assert delay == 15.0

    def test_parse_detonate_invalid_delay_negative(self):
        """Verify negative delay raises ValueError."""
        with pytest.raises(ValueError, match="outside valid range"):
            parse_torpedo_action("detonate_after:-1.0")

    def test_parse_detonate_invalid_delay_too_large(self):
        """Verify delay > 15.0 raises ValueError."""
        with pytest.raises(ValueError, match="outside valid range"):
            parse_torpedo_action("detonate_after:16.0")

    def test_parse_detonate_invalid_format(self):
        """Verify invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid detonation delay format"):
            parse_torpedo_action("detonate_after:abc")

    def test_parse_detonate_empty_delay(self):
        """Verify empty delay raises ValueError."""
        with pytest.raises(ValueError, match="Invalid detonation delay format"):
            parse_torpedo_action("detonate_after:")

    def test_parse_straight_command(self):
        """Verify STRAIGHT command is parsed correctly."""
        action, delay = parse_torpedo_action("STRAIGHT")
        assert action == "STRAIGHT"
        assert delay is None

    def test_parse_soft_left_command(self):
        """Verify SOFT_LEFT command is parsed correctly."""
        action, delay = parse_torpedo_action("SOFT_LEFT")
        assert action == "SOFT_LEFT"
        assert delay is None

    def test_parse_soft_right_command(self):
        """Verify SOFT_RIGHT command is parsed correctly."""
        action, delay = parse_torpedo_action("SOFT_RIGHT")
        assert action == "SOFT_RIGHT"
        assert delay is None

    def test_parse_hard_right_command(self):
        """Verify HARD_RIGHT command is parsed correctly."""
        action, delay = parse_torpedo_action("HARD_RIGHT")
        assert action == "HARD_RIGHT"
        assert delay is None


class TestDeepCopyGameState:
    """Test deep copy game state utility."""

    def test_deep_copy_basic_state(self):
        """Verify basic game state is copied correctly."""
        original = GameState(
            turn=5,
            ship_a=ShipState(
                position=Vec2D(100.0, 200.0),
                velocity=Vec2D(10.0, 0.0),
                heading=0.0,
                shields=75.0,
                ae=50.0,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=0.0
            ),
            ship_b=ShipState(
                position=Vec2D(300.0, 400.0),
                velocity=Vec2D(-5.0, 0.0),
                heading=3.14,
                shields=90.0,
                ae=60.0,
                phaser_config=PhaserConfig.FOCUSED,
                phaser_cooldown_remaining=2.5
            ),
            torpedoes=[],
            blast_zones=[]
        )

        copied = deep_copy_game_state(original)

        # Verify turn is copied
        assert copied.turn == 5

        # Verify ship_a is copied
        assert copied.ship_a.position.x == 100.0
        assert copied.ship_a.position.y == 200.0
        assert copied.ship_a.shields == 75.0
        assert copied.ship_a.ae == 50.0

        # Verify ship_b is copied
        assert copied.ship_b.position.x == 300.0
        assert copied.ship_b.position.y == 400.0
        assert copied.ship_b.shields == 90.0
        assert copied.ship_b.ae == 60.0

    def test_deep_copy_independence(self):
        """Verify copied state is independent from original."""
        original = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100.0,
                ae=100.0,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=0.0
            ),
            ship_b=ShipState(
                position=Vec2D(100.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100.0,
                ae=100.0,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=0.0
            ),
            torpedoes=[],
            blast_zones=[]
        )

        copied = deep_copy_game_state(original)

        # Modify original
        original.ship_a.shields = 50.0
        original.ship_a.position.x = 999.0

        # Verify copied state is unchanged
        assert copied.ship_a.shields == 100.0
        assert copied.ship_a.position.x == 0.0

    def test_deep_copy_with_torpedoes(self):
        """Verify torpedoes are copied correctly."""
        original = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100.0,
                ae=100.0,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=0.0
            ),
            ship_b=ShipState(
                position=Vec2D(100.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100.0,
                ae=100.0,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=0.0
            ),
            torpedoes=[
                TorpedoState(
                    id="ship_a_torpedo_1",
                    owner="ship_a",
                    position=Vec2D(10.0, 20.0),
                    velocity=Vec2D(15.0, 0.0),
                    heading=0.0,
                    ae_remaining=30.0,
                    just_launched=True
                )
            ],
            blast_zones=[]
        )

        copied = deep_copy_game_state(original)

        # Verify torpedo is copied
        assert len(copied.torpedoes) == 1
        assert copied.torpedoes[0].id == "ship_a_torpedo_1"
        assert copied.torpedoes[0].position.x == 10.0
        assert copied.torpedoes[0].ae_remaining == 30.0

        # Verify independence
        original.torpedoes[0].ae_remaining = 10.0
        assert copied.torpedoes[0].ae_remaining == 30.0

    def test_deep_copy_with_blast_zones(self):
        """Verify blast zones are copied correctly."""
        original = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(0.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100.0,
                ae=100.0,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=0.0
            ),
            ship_b=ShipState(
                position=Vec2D(100.0, 0.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100.0,
                ae=100.0,
                phaser_config=PhaserConfig.WIDE,
                phaser_cooldown_remaining=0.0
            ),
            torpedoes=[],
            blast_zones=[
                BlastZone(
                    id="blast_1",
                    owner="ship_a",
                    position=Vec2D(50.0, 50.0),
                    base_damage=45.0,
                    current_radius=10.0,
                    phase=BlastZonePhase.EXPANSION,
                    age=2.0
                )
            ]
        )

        copied = deep_copy_game_state(original)

        # Verify blast zone is copied
        assert len(copied.blast_zones) == 1
        assert copied.blast_zones[0].id == "blast_1"
        assert copied.blast_zones[0].position.x == 50.0
        assert copied.blast_zones[0].base_damage == 45.0

        # Verify independence
        original.blast_zones[0].current_radius = 15.0
        assert copied.blast_zones[0].current_radius == 10.0
