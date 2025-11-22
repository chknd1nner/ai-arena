"""
Tests for replay serialization to ensure all state fields are properly captured.

Story 044: Match Orchestrator & Replay Cleanup
Epic 007: Technical Debt Reduction & Code Quality
"""

import pytest
import json
from pathlib import Path
from ai_arena.replay.recorder import ReplayRecorder
from ai_arena.game_engine.data_models import (
    GameState, ShipState, TorpedoState, BlastZone, Vec2D,
    Orders, Event, PhaserConfig, BlastZonePhase, MovementDirection, RotationCommand
)


class TestTorpedoSerialization:
    """Test that torpedo state is fully serialized including detonation_timer."""

    def test_serialize_torpedo_without_timer(self):
        """Torpedo without detonation timer should serialize timer as None."""
        recorder = ReplayRecorder("model_a", "model_b")

        torpedo = TorpedoState(
            id="ship_a_torp_1",
            position=Vec2D(100.0, 50.0),
            velocity=Vec2D(10.0, 0.0),
            heading=0.0,
            ae_remaining=100,
            owner="ship_a",
            just_launched=False,
            detonation_timer=None
        )

        serialized = recorder._serialize_torpedo(torpedo)

        assert "detonation_timer" in serialized
        assert serialized["detonation_timer"] is None
        assert serialized["id"] == "ship_a_torp_1"
        assert serialized["position"] == [100.0, 50.0]
        assert serialized["ae_remaining"] == 100

    def test_serialize_torpedo_with_timer(self):
        """Torpedo with detonation timer should serialize the timer value."""
        recorder = ReplayRecorder("model_a", "model_b")

        torpedo = TorpedoState(
            id="ship_b_torp_2",
            position=Vec2D(200.0, 150.0),
            velocity=Vec2D(-5.0, 3.0),
            heading=2.5,
            ae_remaining=75,
            owner="ship_b",
            just_launched=True,
            detonation_timer=3.5
        )

        serialized = recorder._serialize_torpedo(torpedo)

        assert "detonation_timer" in serialized
        assert serialized["detonation_timer"] == 3.5
        assert serialized["id"] == "ship_b_torp_2"
        assert serialized["just_launched"] is True

    def test_serialize_torpedo_with_zero_timer(self):
        """Torpedo with zero timer (about to detonate) should serialize correctly."""
        recorder = ReplayRecorder("model_a", "model_b")

        torpedo = TorpedoState(
            id="ship_a_torp_3",
            position=Vec2D(50.0, 50.0),
            velocity=Vec2D(0.0, 0.0),
            heading=1.57,
            ae_remaining=50,
            owner="ship_a",
            just_launched=False,
            detonation_timer=0.0
        )

        serialized = recorder._serialize_torpedo(torpedo)

        assert "detonation_timer" in serialized
        assert serialized["detonation_timer"] == 0.0


class TestGameStateSerialization:
    """Test that full game state serialization includes torpedo timers."""

    def test_serialize_state_with_torpedo_timers(self):
        """Game state with torpedoes should serialize all torpedo fields."""
        recorder = ReplayRecorder("gpt-4", "claude-3-haiku")

        torpedoes = [
            TorpedoState(
                id="ship_a_torp_1",
                position=Vec2D(100.0, 50.0),
                velocity=Vec2D(10.0, 0.0),
                heading=0.0,
                ae_remaining=100,
                owner="ship_a",
                detonation_timer=5.0
            ),
            TorpedoState(
                id="ship_b_torp_1",
                position=Vec2D(200.0, 150.0),
                velocity=Vec2D(-10.0, 0.0),
                heading=3.14,
                ae_remaining=80,
                owner="ship_b",
                detonation_timer=None
            )
        ]

        state = GameState(
            turn=5,
            ship_a=ShipState(
                position=Vec2D(50.0, 50.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=200,
                phaser_config=PhaserConfig.WIDE,
                reconfiguring_phaser=False
            ),
            ship_b=ShipState(
                position=Vec2D(250.0, 150.0),
                velocity=Vec2D(0.0, 0.0),
                heading=3.14,
                shields=100,
                ae=200,
                phaser_config=PhaserConfig.FOCUSED,
                reconfiguring_phaser=False
            ),
            torpedoes=torpedoes,
            blast_zones=[]
        )

        serialized = recorder._serialize_state(state)

        assert len(serialized["torpedoes"]) == 2
        assert serialized["torpedoes"][0]["detonation_timer"] == 5.0
        assert serialized["torpedoes"][1]["detonation_timer"] is None


class TestFullReplaySerialization:
    """Test that complete replay files include torpedo detonation timers."""

    def test_full_replay_includes_torpedo_timers(self, tmp_path):
        """Full replay recording should preserve torpedo detonation timers."""
        # Create recorder
        recorder = ReplayRecorder("gpt-4", "claude-3-haiku")

        # Create a turn with torpedoes
        torpedo_with_timer = TorpedoState(
            id="ship_a_torp_1",
            position=Vec2D(100.0, 50.0),
            velocity=Vec2D(10.0, 0.0),
            heading=0.0,
            ae_remaining=100,
            owner="ship_a",
            detonation_timer=4.2
        )

        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50.0, 50.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=200,
                phaser_config=PhaserConfig.WIDE,
                reconfiguring_phaser=False
            ),
            ship_b=ShipState(
                position=Vec2D(250.0, 150.0),
                velocity=Vec2D(0.0, 0.0),
                heading=3.14,
                shields=100,
                ae=200,
                phaser_config=PhaserConfig.FOCUSED,
                reconfiguring_phaser=False
            ),
            torpedoes=[torpedo_with_timer],
            blast_zones=[]
        )

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="LAUNCH_TORPEDO",
            torpedo_orders={}
        )

        orders_b = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="HOLD",
            torpedo_orders={}
        )

        # Record turn
        recorder.record_turn(
            turn=1,
            state=state,
            orders_a=orders_a,
            orders_b=orders_b,
            thinking_a="Test thinking A",
            thinking_b="Test thinking B",
            events=[]
        )

        # Finalize and check structure
        match_data = recorder.finalize("ship_a", 1)

        # Verify structure
        assert "turns" in match_data
        assert len(match_data["turns"]) == 1

        turn_data = match_data["turns"][0]
        assert "state" in turn_data
        assert "torpedoes" in turn_data["state"]
        assert len(turn_data["state"]["torpedoes"]) == 1

        # Verify detonation_timer is preserved
        torpedo_data = turn_data["state"]["torpedoes"][0]
        assert "detonation_timer" in torpedo_data
        assert torpedo_data["detonation_timer"] == 4.2

    def test_replay_json_structure_includes_timer(self, tmp_path):
        """Verify replay JSON structure includes detonation_timer field."""
        recorder = ReplayRecorder("model_a", "model_b")

        # Create simple state with torpedo
        state = GameState(
            turn=1,
            ship_a=ShipState(
                position=Vec2D(50.0, 50.0),
                velocity=Vec2D(0.0, 0.0),
                heading=0.0,
                shields=100,
                ae=200,
                phaser_config=PhaserConfig.WIDE,
                reconfiguring_phaser=False
            ),
            ship_b=ShipState(
                position=Vec2D(250.0, 150.0),
                velocity=Vec2D(0.0, 0.0),
                heading=3.14,
                shields=100,
                ae=200,
                phaser_config=PhaserConfig.FOCUSED,
                reconfiguring_phaser=False
            ),
            torpedoes=[
                TorpedoState(
                    id="test_torp",
                    position=Vec2D(100.0, 100.0),
                    velocity=Vec2D(5.0, 5.0),
                    heading=0.78,
                    ae_remaining=100,
                    owner="ship_a",
                    detonation_timer=2.5
                )
            ],
            blast_zones=[]
        )

        orders_a = Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action="HOLD",
            torpedo_orders={}
        )

        recorder.record_turn(1, state, orders_a, orders_a, "thinking", "thinking", [])

        # Get the turn data
        turn_data = recorder.turns[0]

        # Verify JSON structure
        assert turn_data["state"]["torpedoes"][0]["detonation_timer"] == 2.5

        # Verify it can be JSON serialized
        json_str = json.dumps(turn_data)
        parsed = json.loads(json_str)

        assert parsed["state"]["torpedoes"][0]["detonation_timer"] == 2.5


class TestBackwardCompatibility:
    """Test that replays work with or without detonation_timer field."""

    def test_new_replay_format_with_timer(self):
        """New replays should include detonation_timer field."""
        recorder = ReplayRecorder("model_a", "model_b")

        torpedo = TorpedoState(
            id="test",
            position=Vec2D(0.0, 0.0),
            velocity=Vec2D(0.0, 0.0),
            heading=0.0,
            ae_remaining=100,
            owner="ship_a",
            detonation_timer=1.5
        )

        serialized = recorder._serialize_torpedo(torpedo)

        # New format always includes the field
        assert "detonation_timer" in serialized
        assert serialized["detonation_timer"] == 1.5

    def test_serialization_handles_none_timer(self):
        """Serialization should handle None timer (no timed detonation set)."""
        recorder = ReplayRecorder("model_a", "model_b")

        torpedo = TorpedoState(
            id="test",
            position=Vec2D(0.0, 0.0),
            velocity=Vec2D(0.0, 0.0),
            heading=0.0,
            ae_remaining=100,
            owner="ship_a",
            detonation_timer=None
        )

        serialized = recorder._serialize_torpedo(torpedo)

        # Should serialize None explicitly
        assert "detonation_timer" in serialized
        assert serialized["detonation_timer"] is None

        # Should be JSON serializable
        json_str = json.dumps(serialized)
        parsed = json.loads(json_str)
        assert parsed["detonation_timer"] is None
