# Story 006: Independent Rotation System

**Epic:** [Epic 002: Independent Movement & Rotation System](../epic-002-independent-movement-rotation.md)
**Status:** Ready for Development
**Size:** Medium
**Priority:** P0

---

## User Story

**As a** game physics engine
**I want** to rotate ship heading based on rotation commands independent of movement
**So that** ships can face one direction while moving in another

## Context

After Story 005, ships can move in any direction relative to their heading, but heading never changes. This story adds back rotation as an independent system controlled by the `rotation` field in Orders.

**Current state (after Story 005):**
- Movement sets velocity direction
- Heading is frozen (never changes)
- Ships move correctly but can't aim phasers

**Target state (after Story 006):**
- Movement sets velocity direction (unchanged from Story 005)
- Rotation sets heading change (NEW)
- Ships can move + rotate independently

## Acceptance Criteria

- [ ] Rotation commands change ship heading independent of movement
- [ ] Rotation rates loaded from config (degrees per second)
- [ ] NONE rotation maintains current heading (no change)
- [ ] SOFT rotations apply 1.0°/s (15° per 15s turn)
- [ ] HARD rotations apply 3.0°/s (45° per 15s turn)
- [ ] Rotation direction correct (LEFT = counterclockwise, RIGHT = clockwise)
- [ ] Rotation applied continuously during substeps
- [ ] Heading wraps correctly (0-360° or 0-2π radians)
- [ ] Physics remains deterministic

## Technical Details

### Files to Modify

- `ai_arena/game_engine/physics.py` - Add rotation logic to `_update_ship_physics()`
- `tests/test_physics.py` - Add rotation tests

### Implementation Approach

**1. Define Rotation Rates:**

Add to PhysicsEngine class:

```python
# Rotation rates (degrees per second, from config)
ROTATION_RATES = {
    RotationCommand.NONE: 0.0,
    RotationCommand.SOFT_LEFT: 1.0,   # counterclockwise
    RotationCommand.SOFT_RIGHT: -1.0, # clockwise
    RotationCommand.HARD_LEFT: 3.0,   # counterclockwise
    RotationCommand.HARD_RIGHT: -3.0, # clockwise
}
```

**2. Update `_update_ship_physics()`:**

```python
def _update_ship_physics(self, ship: ShipState, orders: Orders, dt: float):
    # 1. Apply rotation (independent of movement)
    rotation_rate_deg_per_sec = self.ROTATION_RATES[orders.rotation]
    rotation_per_dt_rad = np.radians(rotation_rate_deg_per_sec * dt)
    ship.heading += rotation_per_dt_rad
    ship.heading = ship.heading % (2 * np.pi)  # Wrap to [0, 2π)

    # 2. Apply movement (independent of rotation)
    if orders.movement == MovementDirection.STOP:
        ship.velocity = Vec2D(0, 0)
        return

    movement_offset = self.MOVEMENT_DIRECTION_OFFSETS[orders.movement]
    velocity_angle = ship.heading + movement_offset

    ship.velocity = Vec2D(
        np.cos(velocity_angle) * self.ship_speed,
        np.sin(velocity_angle) * self.ship_speed
    )

    # 3. Update position
    ship.position = ship.position + (ship.velocity * dt)
```

**Key insight:** Rotation happens FIRST, then movement velocity is calculated based on the new heading. This ensures smooth rotation during the turn.

**3. Load Rotation Rates from Config:**

```python
def __init__(self, config: GameConfig):
    # ... existing init ...

    # Load rotation rates from config
    self.ROTATION_RATES = {
        RotationCommand.NONE: 0.0,
        RotationCommand.SOFT_LEFT: config.rotation.soft_turn_degrees_per_second,
        RotationCommand.SOFT_RIGHT: -config.rotation.soft_turn_degrees_per_second,
        RotationCommand.HARD_LEFT: config.rotation.hard_turn_degrees_per_second,
        RotationCommand.HARD_RIGHT: -config.rotation.hard_turn_degrees_per_second,
    }
```

## Test Requirements

**`tests/test_physics.py`**

```python
def test_rotation_none_maintains_heading():
    """NONE rotation should not change heading."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_heading=0.0)
    orders_a = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    assert new_state.ship_a.heading == 0.0

def test_rotation_soft_left_rotates_15_degrees():
    """SOFT_LEFT should rotate 15° over 15s turn."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_heading=0.0)  # Facing east
    orders_a = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.SOFT_LEFT,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # 1.0°/s × 15s = 15° = 0.2618 radians
    expected_heading = np.radians(15.0)
    assert abs(new_state.ship_a.heading - expected_heading) < 0.001

def test_rotation_hard_right_rotates_45_degrees():
    """HARD_RIGHT should rotate -45° over 15s turn."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_heading=np.pi/2)  # Facing north
    orders_a = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.HARD_RIGHT,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # -3.0°/s × 15s = -45° from north = 45° (northeast)
    expected_heading = np.pi/2 - np.radians(45.0)
    assert abs(new_state.ship_a.heading - expected_heading) < 0.001

def test_rotation_wraps_correctly():
    """Heading should wrap from 2π to 0."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_heading=6.0)  # Near 2π (6.28)
    orders_a = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.SOFT_LEFT,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # Should wrap to small positive value
    assert 0.0 <= new_state.ship_a.heading < 2 * np.pi

def test_independent_movement_and_rotation():
    """Movement and rotation should work independently."""
    engine = PhysicsEngine(config)
    state = create_test_state(
        ship_a_position=Vec2D(100, 100),
        ship_a_heading=0.0  # Facing east
    )

    # Move LEFT (north) while rotating HARD_RIGHT (-45°)
    orders_a = Orders(
        movement=MovementDirection.LEFT,
        rotation=RotationCommand.HARD_RIGHT,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # Heading should rotate right: 0° → -45° (315° or 5.5 rad)
    expected_heading = 2*np.pi - np.radians(45.0)
    assert abs(new_state.ship_a.heading - expected_heading) < 0.001

    # Velocity direction: Start facing east (0°), move LEFT (90°)
    # But heading rotates during turn, so velocity angle changes continuously
    # Final velocity should be based on final heading + LEFT offset
    # This is complex to test precisely, so just verify it moves generally north
    assert new_state.ship_a.position.y > state.ship_a.position.y  # Moved north
```

## Implementation Checklist

- [ ] Add `ROTATION_RATES` dictionary to PhysicsEngine
- [ ] Load rotation rates from config
- [ ] Add rotation logic to `_update_ship_physics()` BEFORE movement
- [ ] Apply rotation per substep (continuous rotation)
- [ ] Wrap heading to [0, 2π) after rotation
- [ ] Write tests for all 5 rotation commands
- [ ] Test rotation + movement combinations
- [ ] Verify heading wrapping
- [ ] Verify determinism

## Edge Cases

1. **Heading wrap:** 2π + ε should become ε
2. **Negative heading:** -0.1 should become 2π - 0.1
3. **Zero rotation:** NONE should be exact (no floating point drift)
4. **Simultaneous movement + rotation:** Order matters (rotate first)

## Definition of Done

- [ ] Rotation changes heading independent of movement
- [ ] Rotation rates match config values
- [ ] Heading wraps correctly
- [ ] All rotation commands tested
- [ ] Movement + rotation combinations work
- [ ] Physics remains deterministic

## Files Changed

- Modify: `ai_arena/game_engine/physics.py`
- Modify: `tests/test_physics.py`

## Dependencies

- **Requires:** Story 005 (Movement Direction System)

## Blocks

- Story 007: Combined AE Cost System (needs both movement and rotation working)

## Notes

**Critical:** Rotation must happen BEFORE calculating velocity direction. Otherwise, the velocity will be based on the old heading, not the new heading.

**Order of operations per substep:**
1. Rotate heading (based on rotation command)
2. Calculate velocity angle (heading + movement offset)
3. Set velocity vector
4. Update position

This ensures smooth, continuous rotation with correct velocity throughout.
