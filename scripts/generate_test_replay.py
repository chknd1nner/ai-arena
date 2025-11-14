#!/usr/bin/env python3
"""
Generate a mock replay JSON file for testing the canvas viewer.
This creates a simple match with one ship strafing around the other.
"""

import json
import math
from pathlib import Path
from datetime import datetime
import uuid

def generate_strafing_maneuver_replay():
    """Generate a replay showing a ship performing a strafing run."""

    match_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    replay = {
        "match_id": match_id,
        "timestamp": timestamp,
        "model_a": "test-ship-a",
        "model_b": "test-ship-b",
        "winner": "a",
        "turns": []
    }

    # Generate 20 turns showing Ship A strafing right while rotating left
    # Ship B stays mostly still
    for turn in range(20):
        t = turn / 20.0  # Normalize to [0, 1]

        # Ship A: Strafing maneuver (move right, rotate left)
        angle = t * 2 * math.pi  # Full circle
        radius = 150
        ship_a_x = radius * math.cos(angle)
        ship_a_y = radius * math.sin(angle)

        # Heading points toward center (faces Ship B)
        ship_a_heading = angle + math.pi

        # Velocity is tangent to circle (perpendicular to heading)
        vel_angle = angle + math.pi / 2
        ship_a_vel_x = 10 * math.cos(vel_angle)
        ship_a_vel_y = 10 * math.sin(vel_angle)

        # Ship B: Center, stationary
        ship_b_x = 0
        ship_b_y = 0
        ship_b_heading = angle  # Slowly rotates to track Ship A

        turn_data = {
            "turn": turn,
            "state": {
                "ship_a": {
                    "position": {"x": ship_a_x, "y": ship_a_y},
                    "velocity": {"x": ship_a_vel_x, "y": ship_a_vel_y},
                    "heading": ship_a_heading,
                    "shields": 100 - turn * 2,  # Gradual damage
                    "ae": 80 + (turn % 10) - 5,  # Oscillating AE
                    "phaser_config": "WIDE"
                },
                "ship_b": {
                    "position": {"x": ship_b_x, "y": ship_b_y},
                    "velocity": {"x": 0, "y": 0},
                    "heading": ship_b_heading,
                    "shields": 100 - turn * 3,
                    "ae": 75,
                    "phaser_config": "FOCUSED"
                },
                "torpedoes": []
            },
            "events": []
        }

        # Add some phaser hit events
        if turn % 3 == 0:
            turn_data["events"].append({
                "type": "phaser_hit",
                "attacker": "a",
                "target": "b",
                "damage": 15,
                "timestamp": turn * 15.0
            })

        replay["turns"].append(turn_data)

    return replay

def generate_epic_002_tactical_showcase():
    """
    Generate a comprehensive replay showcasing all 4 Epic 002 tactical maneuvers:
    1. Strafing Run (0-8 turns)
    2. Retreat with Coverage (9-16 turns)
    3. Aggressive Reposition (17-24 turns)
    4. The Drift (25-32 turns)
    """

    match_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    replay = {
        "match_id": match_id,
        "timestamp": timestamp,
        "model_a": "tactical-demo-a",
        "model_b": "tactical-demo-b",
        "winner": "a",
        "turns": []
    }

    # Maneuver 1: Strafing Run (turns 0-8)
    # Ship A moves RIGHT while rotating LEFT to keep guns on Ship B
    for turn in range(9):
        progress = turn / 8.0
        ship_a_x = -200 + progress * 100
        ship_a_y = -100 + progress * 200  # Moving right (south to north)
        ship_a_heading = progress * math.pi / 2  # Rotating left (0° to 90°)
        ship_a_vel_angle = math.pi / 2  # Velocity points north (perpendicular)

        turn_data = {
            "turn": turn,
            "state": {
                "ship_a": {
                    "position": {"x": ship_a_x, "y": ship_a_y},
                    "velocity": {
                        "x": 10 * math.cos(ship_a_vel_angle),
                        "y": 10 * math.sin(ship_a_vel_angle)
                    },
                    "heading": ship_a_heading,  # Facing toward center
                    "shields": 100 - turn,
                    "ae": 75,
                    "phaser_config": "WIDE"
                },
                "ship_b": {
                    "position": {"x": 0, "y": 0},
                    "velocity": {"x": 0, "y": 0},
                    "heading": math.pi,
                    "shields": 100 - turn * 2,
                    "ae": 80,
                    "phaser_config": "FOCUSED"
                },
                "torpedoes": []
            },
            "events": [
                {"type": "phaser_hit", "attacker": "a", "target": "b", "damage": 15}
            ] if turn % 2 == 0 else []
        }
        replay["turns"].append(turn_data)

    # Maneuver 2: Retreat with Coverage (turns 9-16)
    # Ship A moves BACKWARD while maintaining FORWARD facing
    for turn in range(9, 17):
        progress = (turn - 9) / 7.0
        ship_a_x = -100 - progress * 200  # Moving west (backing up)
        ship_a_y = 100  # Constant Y
        ship_a_heading = 0  # Facing east (forward)
        ship_a_vel_x = -25  # Velocity west (backward)

        ship_b_x = 0 - progress * 50  # Slowly following

        turn_data = {
            "turn": turn,
            "state": {
                "ship_a": {
                    "position": {"x": ship_a_x, "y": ship_a_y},
                    "velocity": {"x": ship_a_vel_x, "y": 0},
                    "heading": ship_a_heading,
                    "shields": 91 - turn,
                    "ae": 60 + progress * 10,
                    "phaser_config": "WIDE"
                },
                "ship_b": {
                    "position": {"x": ship_b_x, "y": 0},
                    "velocity": {"x": -5, "y": 0},
                    "heading": math.pi,
                    "shields": 82 - turn * 2,
                    "ae": 75,
                    "phaser_config": "FOCUSED"
                },
                "torpedoes": []
            },
            "events": [
                {"type": "phaser_hit", "attacker": "a", "target": "b", "damage": 15}
            ] if turn % 3 == 0 else []
        }
        replay["turns"].append(turn_data)

    # Maneuver 3: Aggressive Reposition (turns 17-24)
    # Ship A moves FORWARD while rotating HARD_RIGHT
    for turn in range(17, 25):
        progress = (turn - 17) / 7.0
        ship_a_x = -300 + progress * 300  # Moving east (forward)
        ship_a_y = 100 - progress * 100  # Also moving slightly south
        ship_a_heading = progress * math.pi / 2 + math.pi / 4  # Rotating right
        ship_a_vel_angle = progress * math.pi / 4  # Velocity mostly east

        ship_b_x = -50

        turn_data = {
            "turn": turn,
            "state": {
                "ship_a": {
                    "position": {"x": ship_a_x, "y": ship_a_y},
                    "velocity": {
                        "x": 15 * math.cos(ship_a_vel_angle),
                        "y": 15 * math.sin(ship_a_vel_angle)
                    },
                    "heading": ship_a_heading,
                    "shields": 74 - (turn - 17),
                    "ae": 70 + progress * 15,
                    "phaser_config": "FOCUSED"
                },
                "ship_b": {
                    "position": {"x": ship_b_x, "y": 0},
                    "velocity": {"x": 0, "y": 0},
                    "heading": math.pi,
                    "shields": 48 - (turn - 17) * 3,
                    "ae": 70,
                    "phaser_config": "WIDE"
                },
                "torpedoes": []
            },
            "events": [
                {"type": "phaser_hit", "attacker": "a", "target": "b", "damage": 35}
            ] if turn % 2 == 0 else []
        }
        replay["turns"].append(turn_data)

    # Maneuver 4: The Drift (turns 25-32)
    # Ship A moves LEFT while slowly rotating LEFT (tracking target)
    for turn in range(25, 33):
        progress = (turn - 25) / 7.0
        ship_a_x = 0 - progress * 50  # Slight west
        ship_a_y = 20 + progress * 150  # Moving north (left)
        ship_a_heading = math.pi / 2 + progress * math.pi / 8  # Slowly rotating
        ship_a_vel_angle = math.pi / 2  # Velocity north

        turn_data = {
            "turn": turn,
            "state": {
                "ship_a": {
                    "position": {"x": ship_a_x, "y": ship_a_y},
                    "velocity": {
                        "x": 8 * math.cos(ship_a_vel_angle),
                        "y": 8 * math.sin(ship_a_vel_angle)
                    },
                    "heading": ship_a_heading,
                    "shields": 66 - (turn - 25),
                    "ae": 85 - progress * 10,
                    "phaser_config": "WIDE"
                },
                "ship_b": {
                    "position": {"x": -50, "y": 0},
                    "velocity": {"x": 0, "y": 0},
                    "heading": math.pi,
                    "shields": 24 - (turn - 25) * 3,
                    "ae": 60,
                    "phaser_config": "FOCUSED"
                },
                "torpedoes": []
            },
            "events": [
                {"type": "phaser_hit", "attacker": "a", "target": "b", "damage": 15}
            ] if turn % 2 == 1 else []
        }
        replay["turns"].append(turn_data)

    return replay

def generate_retreat_with_coverage_replay():
    """Generate a replay showing a ship retreating while maintaining facing."""

    match_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()

    replay = {
        "match_id": match_id,
        "timestamp": timestamp,
        "model_a": "test-retreat-a",
        "model_b": "test-advance-b",
        "winner": "b",
        "turns": []
    }

    # Ship A retreats west while facing east
    # Ship B advances east
    for turn in range(15):
        ship_a_x = -50 - turn * 20  # Moving west (backing up)
        ship_a_heading = 0  # Facing east (forward)

        ship_b_x = 100 - turn * 15  # Moving west (advancing toward A)
        ship_b_heading = math.pi  # Facing west (toward A)

        turn_data = {
            "turn": turn,
            "state": {
                "ship_a": {
                    "position": {"x": ship_a_x, "y": 0},
                    "velocity": {"x": -20, "y": 0},  # Moving west
                    "heading": ship_a_heading,  # Facing east
                    "shields": 50 - turn * 3,
                    "ae": 70,
                    "phaser_config": "WIDE"
                },
                "ship_b": {
                    "position": {"x": ship_b_x, "y": 0},
                    "velocity": {"x": -15, "y": 0},
                    "heading": ship_b_heading,
                    "shields": 85 - turn * 2,
                    "ae": 75,
                    "phaser_config": "FOCUSED"
                },
                "torpedoes": []
            },
            "events": []
        }

        if turn % 2 == 0:
            turn_data["events"].append({
                "type": "phaser_hit",
                "attacker": "b",
                "target": "a",
                "damage": 20,
                "timestamp": turn * 15.0
            })

        replay["turns"].append(turn_data)

    return replay

def save_replay(replay, filename):
    """Save replay to replays directory."""
    replays_dir = Path(__file__).parent.parent / "replays"
    replays_dir.mkdir(exist_ok=True)

    filepath = replays_dir / filename
    with open(filepath, 'w') as f:
        json.dump(replay, f, indent=2)

    print(f"✅ Generated test replay: {filepath}")
    print(f"   Match ID: {replay['match_id']}")
    print(f"   Turns: {len(replay['turns'])}")
    return filepath

if __name__ == "__main__":
    print("Generating test replays for Epic 003 canvas viewer...")
    print()

    # Generate Epic 002 tactical showcase (ALL 4 maneuvers!)
    tactical_replay = generate_epic_002_tactical_showcase()
    tactical_file = save_replay(tactical_replay, "test_epic002_tactical_showcase.json")
    print(f"   🎯 Showcases all 4 Epic 002 maneuvers:")
    print(f"      - Turns 0-8:   Strafing Run")
    print(f"      - Turns 9-16:  Retreat with Coverage")
    print(f"      - Turns 17-24: Aggressive Reposition")
    print(f"      - Turns 25-32: The Drift")
    print()

    # Generate strafing maneuver replay
    strafing_replay = generate_strafing_maneuver_replay()
    strafing_file = save_replay(strafing_replay, "test_strafing_maneuver.json")

    # Generate retreat with coverage replay
    retreat_replay = generate_retreat_with_coverage_replay()
    retreat_file = save_replay(retreat_replay, "test_retreat_coverage.json")

    print()
    print("✅ Test replays generated successfully!")
    print()
    print("To view in canvas:")
    print("  1. Start frontend: cd frontend && npm start")
    print("  2. Load replay in canvas viewer")
    print("  3. Watch the tactical maneuvers!")
