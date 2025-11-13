# Story 011: Tactical Validation

**Epic:** [Epic 002: Independent Movement & Rotation System](../epic-002-independent-movement-rotation.md)
**Status:** Ready for Development
**Size:** Small
**Priority:** P1

---

## User Story

**As a** game developer
**I want** to validate that all 4 tactical maneuvers work correctly
**So that** I know the independent movement/rotation system delivers the promised tactical depth

## Context

This story validates the four key tactical maneuvers described in the game spec:
1. **Strafing Run** - Move perpendicular while rotating to maintain phaser lock
2. **Retreat with Coverage** - Move backward while facing forward
3. **Aggressive Reposition** - Advance while rotating for better firing arc
4. **The Drift** - Slide laterally while slowly tracking target

These tests verify the entire system works end-to-end for real tactical scenarios.

## Acceptance Criteria

- [ ] Strafing run test verifies ship circles while maintaining facing
- [ ] Retreat with coverage test verifies backward movement with forward facing
- [ ] Aggressive reposition test verifies forward movement with rotation
- [ ] Drift test verifies perpendicular movement with gradual rotation
- [ ] All maneuvers verified with actual physics simulation
- [ ] Tests verify position, heading, and velocity after each maneuver
- [ ] Tests optionally include phaser firing to verify arc coverage

## Test Requirements

**`tests/test_tactical_maneuvers.py` (new file)**

```python
import pytest
import numpy as np
from ai_arena.game_engine.physics import PhysicsEngine
from ai_arena.game_engine.data_models import *
from ai_arena.config.loader import ConfigLoader

@pytest.fixture
def engine():
    config = ConfigLoader().load("config.json")
    return PhysicsEngine(config)

def test_strafing_run_maneuver(engine):
    """Strafing Run: Move RIGHT while rotating HARD_LEFT.

    Expected behavior:
    - Ship moves perpendicular to the right
    - Ship rotates 45° left
    - Phasers maintain coverage on left side
    - Net result: Circle right around enemy while shooting left
    """
    initial_heading = 0.0  # Facing east
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(0, 0),
            heading=initial_heading,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        ship_b=ShipState(  # Enemy to the north
            position=Vec2D(100, 150),
            velocity=Vec2D(0, 0),
            heading=np.pi,  # Facing west
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )
    )

    orders_a = Orders(
        movement=MovementDirection.RIGHT,    # Move perpendicular right (south)
        rotation=RotationCommand.HARD_LEFT,  # Rotate 45° left (toward north)
        weapon_action="MAINTAIN_CONFIG"
    )
    orders_b = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Verify ship moved right (south)
    assert new_state.ship_a.position.y < state.ship_a.position.y, "Should move south (right)"

    # Verify ship rotated left (toward north)
    expected_heading = np.radians(45.0)  # 45° from east = northeast
    assert abs(new_state.ship_a.heading - expected_heading) < 0.01, "Should rotate 45° left"

    # Verify heading points toward enemy (north) while position moved away (south)
    # This is the strafing effect!
    assert new_state.ship_a.heading > initial_heading, "Heading should rotate toward enemy"
    assert new_state.ship_a.position.y < state.ship_a.position.y, "Position should move away"

def test_retreat_with_coverage_maneuver(engine):
    """Retreat with Coverage: Move BACKWARD while rotation NONE.

    Expected behavior:
    - Ship moves backward (away from enemy)
    - Ship maintains forward facing (phasers still point at enemy)
    - Defensive maneuver: create distance while covering retreat
    """
    initial_heading = 0.0  # Facing east
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(0, 0),
            heading=initial_heading,
            shields=30,  # Low shields, retreating
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        ship_b=ShipState(  # Enemy to the east
            position=Vec2D(150, 100),
            velocity=Vec2D(0, 0),
            heading=np.pi,  # Facing west
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )
    )

    orders_a = Orders(
        movement=MovementDirection.BACKWARD,  # Move backward (west)
        rotation=RotationCommand.NONE,        # Maintain heading (east)
        weapon_action="MAINTAIN_CONFIG"
    )
    orders_b = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Verify ship moved backward (west, away from enemy)
    assert new_state.ship_a.position.x < state.ship_a.position.x, "Should move west (away)"

    # Verify heading maintained (still facing east, toward enemy)
    assert abs(new_state.ship_a.heading - initial_heading) < 0.01, "Heading should not change"

    # Verify increased distance from enemy
    initial_distance = state.ship_a.position.distance_to(state.ship_b.position)
    final_distance = new_state.ship_a.position.distance_to(new_state.ship_b.position)
    assert final_distance > initial_distance, "Distance from enemy should increase"

def test_aggressive_reposition_maneuver(engine):
    """Aggressive Reposition: Move FORWARD while rotating HARD_RIGHT.

    Expected behavior:
    - Ship advances forward (closes distance)
    - Ship rotates 45° right (angles for better firing solution)
    - Offensive maneuver: close while maneuvering for advantage
    """
    initial_heading = 0.0  # Facing east
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(0, 0),
            heading=initial_heading,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        ship_b=ShipState(  # Enemy to the east
            position=Vec2D(200, 100),
            velocity=Vec2D(0, 0),
            heading=np.pi,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )
    )

    orders_a = Orders(
        movement=MovementDirection.FORWARD,   # Advance forward (east)
        rotation=RotationCommand.HARD_RIGHT,  # Rotate 45° right (southeast)
        weapon_action="MAINTAIN_CONFIG"
    )
    orders_b = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Verify ship moved forward (east, toward enemy)
    assert new_state.ship_a.position.x > state.ship_a.position.x, "Should move east (toward)"

    # Verify ship rotated right (clockwise)
    expected_heading = 2*np.pi - np.radians(45.0)  # -45° = 315° = southeast
    assert abs(new_state.ship_a.heading - expected_heading) < 0.01, "Should rotate 45° right"

    # Verify decreased distance to enemy
    initial_distance = state.ship_a.position.distance_to(state.ship_b.position)
    final_distance = new_state.ship_a.position.distance_to(new_state.ship_b.position)
    assert final_distance < initial_distance, "Distance to enemy should decrease"

def test_drift_maneuver(engine):
    """The Drift: Move LEFT while rotating SOFT_LEFT.

    Expected behavior:
    - Ship slides perpendicular left
    - Ship slowly rotates left (15° over 15s)
    - Balanced maneuver: evade while gradually tracking target
    """
    initial_heading = 0.0  # Facing east
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(0, 0),
            heading=initial_heading,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        ship_b=ShipState(  # Enemy to the northeast
            position=Vec2D(150, 150),
            velocity=Vec2D(0, 0),
            heading=np.pi * 0.75,  # Facing southwest
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        )
    )

    orders_a = Orders(
        movement=MovementDirection.LEFT,      # Slide left (north)
        rotation=RotationCommand.SOFT_LEFT,   # Slowly rotate left (15°)
        weapon_action="MAINTAIN_CONFIG"
    )
    orders_b = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Verify ship moved left (north)
    assert new_state.ship_a.position.y > state.ship_a.position.y, "Should move north (left)"

    # Verify ship rotated left slightly (15°)
    expected_heading = np.radians(15.0)  # 15° counterclockwise from east
    assert abs(new_state.ship_a.heading - expected_heading) < 0.01, "Should rotate 15° left"

    # Verify gradual tracking (heading moved toward enemy)
    enemy_bearing = np.arctan2(
        state.ship_b.position.y - state.ship_a.position.y,
        state.ship_b.position.x - state.ship_a.position.x
    )  # ~45° (northeast)
    # After rotation, heading should be closer to enemy bearing
    assert abs(new_state.ship_a.heading - enemy_bearing) < abs(initial_heading - enemy_bearing)

def test_maneuver_ae_consumption():
    """Verify all maneuvers consume AE as expected."""
    config = ConfigLoader().load("config.json")
    engine = PhysicsEngine(config)

    maneuvers = [
        ("Strafing", MovementDirection.RIGHT, RotationCommand.HARD_LEFT, 0.67 + 0.33),
        ("Retreat", MovementDirection.BACKWARD, RotationCommand.NONE, 0.67 + 0.0),
        ("Reposition", MovementDirection.FORWARD, RotationCommand.HARD_RIGHT, 0.33 + 0.33),
        ("Drift", MovementDirection.LEFT, RotationCommand.SOFT_LEFT, 0.67 + 0.13),
    ]

    for name, movement, rotation, expected_rate in maneuvers:
        state = GameState(
            turn=0,
            ship_a=ShipState(
                position=Vec2D(100, 100),
                velocity=Vec2D(0, 0),
                heading=0.0,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            ),
            ship_b=ShipState(
                position=Vec2D(200, 200),
                velocity=Vec2D(0, 0),
                heading=np.pi,
                shields=100,
                ae=100,
                phaser_config=PhaserConfig.WIDE
            )
        )

        orders_a = Orders(movement=movement, rotation=rotation, weapon_action="MAINTAIN_CONFIG")
        orders_b = Orders(movement=MovementDirection.STOP, rotation=RotationCommand.NONE, weapon_action="MAINTAIN_CONFIG")

        new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

        # Calculate expected net AE cost
        expected_total_cost = expected_rate * 15.0  # 15s action phase
        expected_regen = 0.33 * 15.0
        expected_net = expected_total_cost - expected_regen

        actual_cost = 100 - new_state.ship_a.ae
        assert abs(actual_cost - expected_net) < 1.5, f"{name} maneuver AE cost wrong"
```

## Implementation Checklist

- [ ] Write strafing run test
- [ ] Write retreat with coverage test
- [ ] Write aggressive reposition test
- [ ] Write drift maneuver test
- [ ] Write AE consumption test for all maneuvers
- [ ] Verify all tests pass
- [ ] Optional: Add visualization output for debugging

## Definition of Done

- [ ] All 4 tactical maneuvers validated
- [ ] Tests verify position, heading, and velocity correctly
- [ ] Tests verify AE costs for each maneuver
- [ ] All tests pass
- [ ] Maneuvers work as specified in game spec

## Files Changed

- Create: `tests/test_tactical_maneuvers.py`

## Dependencies

- **Requires:** Stories 004-007 (physics implementation complete)

## Notes

**Why These Tests Matter:**

These aren't just unit tests - they validate the *entire point* of Epic 002. If these tests pass, we've successfully implemented the "face move" system and unlocked tactical depth.

**Debugging Tips:**

If a maneuver test fails:
1. Check heading calculation (is rotation working?)
2. Check velocity direction (is movement working?)
3. Check AE costs (are both movement + rotation deducted?)
4. Visualize the trajectory (print positions over time)

**Future Enhancements:**

Consider adding:
- Phaser hit detection during maneuvers
- Multi-turn maneuver sequences
- Enemy response patterns
- Tournament mode with maneuver statistics
