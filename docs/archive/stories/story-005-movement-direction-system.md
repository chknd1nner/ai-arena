# Story 005: Movement Direction System

**Epic:** [Epic 002: Independent Movement & Rotation System](../epic-002-independent-movement-rotation.md)
**Status:** ✅ COMPLETED - All Tests Passing
**Size:** Medium
**Priority:** P0

---

## QA Agent Review

**Reviewed By:** task-completion-validator
**Date:** 2025-11-14
**Verdict:** ✅ APPROVED - Fully Implemented

**Implementation Verified:**
- ✅ `MOVEMENT_DIRECTION_OFFSETS` dictionary created (physics.py:44-54)
- ✅ `_update_ship_physics()` refactored - velocity independent of heading (physics.py:262-292)
- ✅ `_get_movement_ae_cost()` method implemented (physics.py:185-198)
- ✅ Heading never changes during movement (rotation decoupled)
- ✅ All 9 movement directions tested and working

**Test Results:** 9/9 movement direction tests passing
- FORWARD maintains heading ✓
- LEFT perpendicular movement ✓
- RIGHT perpendicular movement ✓
- BACKWARD reverses direction ✓
- STOP zeroes velocity ✓
- All 4 diagonal directions tested ✓

**Quality Assessment:**
- Clean separation between velocity calculation and heading changes
- Movement offsets correctly calculate angles relative to heading
- STOP properly special-cased for zero velocity

**Code References:**
- ai_arena/game_engine/physics.py:44-54 - Movement direction offsets
- ai_arena/game_engine/physics.py:262-292 - Refactored ship physics
- ai_arena/game_engine/physics.py:185-198 - Movement AE cost method
- tests/test_epic_002_phase_1_physics.py:15-183 - Movement tests

---

## User Story

**As a** game physics engine
**I want** to calculate ship velocity based on movement direction independent of rotation
**So that** ships can move in one direction while facing another

## Context

Currently, `_update_ship_physics()` uses movement commands to control both velocity AND rotation. The `movement_params` dictionary maps each MovementType to a rotation angle, which changes the ship's heading. Velocity is then set based on the new heading.

**Current flow:**
1. Movement command → Rotation amount
2. Apply rotation to heading
3. Set velocity based on new heading
4. Result: Ship faces where it's moving

**Target flow:**
1. Movement command → Velocity direction (relative to current heading)
2. Calculate velocity vector from (heading + movement offset)
3. Heading remains unchanged (rotation handled separately)
4. Result: Ship can move in any direction while facing any direction

## Acceptance Criteria

- [ ] Movement directions calculate velocity independent of heading changes
- [ ] Each MovementDirection maps to an angle offset from current heading
- [ ] Velocity vector calculated correctly for all 9 movement directions
- [ ] STOP movement sets velocity to zero
- [ ] Ship heading is NOT modified by movement commands
- [ ] Movement uses config values for speed and AE costs
- [ ] All existing physics tests still pass (with updated movement types)
- [ ] Physics remains deterministic (same inputs = same outputs)

## Technical Details

### Files to Modify

- `ai_arena/game_engine/physics.py` - Refactor `_update_ship_physics()`
- `ai_arena/config/loader.py` - May need to update movement config structure
- `config.json` - Update movement configuration
- `tests/test_physics.py` - Update tests for new movement system

### Implementation Approach

**1. Define Movement Direction Offsets:**

Add to PhysicsEngine class:

```python
# Movement direction offsets (relative to current heading)
MOVEMENT_DIRECTION_OFFSETS = {
    MovementDirection.FORWARD: 0.0,              # 0° - Straight ahead
    MovementDirection.FORWARD_LEFT: -np.pi/4,    # -45° - Diagonal left
    MovementDirection.FORWARD_RIGHT: np.pi/4,    # +45° - Diagonal right
    MovementDirection.LEFT: -np.pi/2,            # -90° - Perpendicular left
    MovementDirection.RIGHT: np.pi/2,            # +90° - Perpendicular right
    MovementDirection.BACKWARD: np.pi,           # 180° - Reverse
    MovementDirection.BACKWARD_LEFT: -3*np.pi/4, # -135° - Diagonal back-left
    MovementDirection.BACKWARD_RIGHT: 3*np.pi/4, # +135° - Diagonal back-right
    MovementDirection.STOP: 0.0,                 # Special case: zero velocity
}
```

**2. Refactor `_update_ship_physics()`:**

Old implementation:
```python
def _update_ship_physics(self, ship: ShipState, orders: Orders, dt: float):
    if orders.movement == MovementType.STOP:
        ship.velocity = Vec2D(0, 0)
        return

    # Movement controls rotation (WRONG)
    rotation_per_dt = self.movement_params[orders.movement]["rotation"] * dt / self.action_phase_duration
    ship.heading += rotation_per_dt
    ship.heading = ship.heading % (2 * np.pi)

    # Velocity based on heading
    ship.velocity = Vec2D(
        np.cos(ship.heading) * self.ship_speed,
        np.sin(ship.heading) * self.ship_speed
    )
    ship.position = ship.position + (ship.velocity * dt)
```

New implementation:
```python
def _update_ship_physics(self, ship: ShipState, orders: Orders, dt: float):
    # Handle STOP as special case
    if orders.movement == MovementDirection.STOP:
        ship.velocity = Vec2D(0, 0)
        return

    # Calculate velocity direction (independent of rotation)
    movement_offset = self.MOVEMENT_DIRECTION_OFFSETS[orders.movement]
    velocity_angle = ship.heading + movement_offset

    # Set velocity based on movement direction
    ship.velocity = Vec2D(
        np.cos(velocity_angle) * self.ship_speed,
        np.sin(velocity_angle) * self.ship_speed
    )

    # Update position
    ship.position = ship.position + (ship.velocity * dt)

    # NOTE: Heading is NOT modified here
    # Rotation is handled separately in Story 006
```

**3. Update Movement AE Costs:**

Update config.json:
```json
"movement": {
  "forward_ae_per_second": 0.33,
  "diagonal_ae_per_second": 0.53,
  "perpendicular_ae_per_second": 0.67,
  "backward_ae_per_second": 0.67,
  "backward_diagonal_ae_per_second": 0.80,
  "stop_ae_per_second": 0.0
}
```

Map movement directions to costs:
```python
def _get_movement_ae_cost(self, movement: MovementDirection) -> float:
    """Get AE cost per second for movement direction."""
    cost_map = {
        MovementDirection.FORWARD: self.config.movement.forward_ae_per_second,
        MovementDirection.FORWARD_LEFT: self.config.movement.diagonal_ae_per_second,
        MovementDirection.FORWARD_RIGHT: self.config.movement.diagonal_ae_per_second,
        MovementDirection.LEFT: self.config.movement.perpendicular_ae_per_second,
        MovementDirection.RIGHT: self.config.movement.perpendicular_ae_per_second,
        MovementDirection.BACKWARD: self.config.movement.backward_ae_per_second,
        MovementDirection.BACKWARD_LEFT: self.config.movement.backward_diagonal_ae_per_second,
        MovementDirection.BACKWARD_RIGHT: self.config.movement.backward_diagonal_ae_per_second,
        MovementDirection.STOP: self.config.movement.stop_ae_per_second,
    }
    return cost_map[movement]
```

**4. Update AE Deduction:**

In `resolve_turn()`, update the movement AE cost calculation:

```python
# Old way (per-turn cost)
movement_cost = self.movement_costs.get(orders_a.movement, 0)
ship_a.ae -= movement_cost

# New way (per-second cost × duration)
movement_ae_per_second = self._get_movement_ae_cost(orders_a.movement)
movement_cost = movement_ae_per_second * self.action_phase_duration
ship_a.ae = max(0, ship_a.ae - movement_cost)
```

### Design Decisions

**Why use offsets from heading instead of absolute angles?**
- More intuitive: "LEFT" means "perpendicular to my facing"
- LLMs don't need to calculate absolute bearings
- Matches naval/aviation conventions ("port" = left of bow)

**Why STOP is special-cased?**
- No velocity means no angle calculation needed
- Clearer logic than checking if angle exists
- Matches game spec (STOP is distinct from other movements)

**Why not implement rotation in this story?**
- Separation of concerns: Movement first, rotation later
- Easier to test: Can verify movement works before adding rotation
- Smaller PRs: Each story is focused and reviewable

## Test Requirements

**`tests/test_physics.py` (update existing tests)**

```python
def test_movement_forward_maintains_heading():
    """FORWARD movement should not change heading."""
    engine = PhysicsEngine(config)
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(0, 0),
            heading=0.0,  # Facing east
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        # ... ship_b ...
    )
    orders_a = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Heading should not change
    assert new_state.ship_a.heading == 0.0
    # Velocity should be east (heading direction)
    assert new_state.ship_a.velocity.x > 0
    assert abs(new_state.ship_a.velocity.y) < 0.001

def test_movement_left_perpendicular():
    """LEFT movement should move perpendicular to heading."""
    engine = PhysicsEngine(config)
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(0, 0),
            heading=0.0,  # Facing east
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        # ... ship_b ...
    )
    orders_a = Orders(
        movement=MovementDirection.LEFT,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Heading should not change
    assert new_state.ship_a.heading == 0.0
    # Velocity should be north (perpendicular left)
    assert abs(new_state.ship_a.velocity.x) < 0.001
    assert new_state.ship_a.velocity.y > 0

def test_movement_backward_reverses():
    """BACKWARD movement should move opposite to heading."""
    engine = PhysicsEngine(config)
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(0, 0),
            heading=0.0,  # Facing east
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        # ... ship_b ...
    )
    orders_a = Orders(
        movement=MovementDirection.BACKWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Heading should not change
    assert new_state.ship_a.heading == 0.0
    # Velocity should be west (opposite of heading)
    assert new_state.ship_a.velocity.x < 0
    assert abs(new_state.ship_a.velocity.y) < 0.001

def test_movement_stop_zeroes_velocity():
    """STOP movement should set velocity to zero."""
    engine = PhysicsEngine(config)
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(3.0, 0.0),  # Moving east
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        # ... ship_b ...
    )
    orders_a = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Velocity should be zero
    assert new_state.ship_a.velocity.x == 0.0
    assert new_state.ship_a.velocity.y == 0.0
    # Position should not change (no movement during turn)
    assert new_state.ship_a.position.x == state.ship_a.position.x
    assert new_state.ship_a.position.y == state.ship_a.position.y

def test_movement_diagonal_correct_angle():
    """FORWARD_LEFT should move at 45° from heading."""
    engine = PhysicsEngine(config)
    state = GameState(
        turn=0,
        ship_a=ShipState(
            position=Vec2D(100, 100),
            velocity=Vec2D(0, 0),
            heading=0.0,  # Facing east
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE
        ),
        # ... ship_b ...
    )
    orders_a = Orders(
        movement=MovementDirection.FORWARD_LEFT,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, events = engine.resolve_turn(state, orders_a, orders_b)

    # Heading should not change
    assert new_state.ship_a.heading == 0.0
    # Velocity should be northeast (45° from east)
    assert new_state.ship_a.velocity.x > 0
    assert new_state.ship_a.velocity.y > 0
    # Should be equal magnitude (45° angle)
    assert abs(new_state.ship_a.velocity.x - new_state.ship_a.velocity.y) < 0.001

def test_movement_ae_costs():
    """Movement should deduct correct AE based on direction."""
    engine = PhysicsEngine(config)
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
        # ... ship_b ...
    )

    # Test FORWARD (lowest cost)
    orders_forward = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )
    new_state, _ = engine.resolve_turn(state, orders_forward, orders_b)
    forward_cost = 100 - new_state.ship_a.ae

    # Test LEFT (higher cost)
    orders_left = Orders(
        movement=MovementDirection.LEFT,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )
    new_state, _ = engine.resolve_turn(state, orders_left, orders_b)
    left_cost = 100 - new_state.ship_a.ae

    # LEFT should cost more than FORWARD
    assert left_cost > forward_cost
```

## Implementation Checklist

- [ ] Add `MOVEMENT_DIRECTION_OFFSETS` dictionary to PhysicsEngine
- [ ] Refactor `_update_ship_physics()` to use movement offsets
- [ ] Remove rotation logic from movement (heading no longer changes)
- [ ] Implement `_get_movement_ae_cost()` method
- [ ] Update AE deduction to use per-second costs
- [ ] Update config.json with new movement cost structure
- [ ] Update ConfigLoader if movement config structure changes
- [ ] Write tests for all 9 movement directions
- [ ] Verify heading never changes (rotation removed)
- [ ] Verify physics remains deterministic

## Edge Cases to Handle

1. **STOP movement:** Set velocity to (0, 0), skip angle calculation
2. **Angle wrapping:** Ensure velocity_angle wraps correctly (0-2π)
3. **Zero speed:** If ship_speed = 0, velocity should be (0, 0)
4. **Insufficient AE:** If AE insufficient, validate orders (set to STOP?)

## Performance Considerations

- Angle calculation per substep: Negligible (just trig functions)
- Dictionary lookup for costs: O(1), no impact
- Overall: No performance regression expected

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Movement calculates velocity independent of heading
- [ ] Heading never changes in `_update_ship_physics()`
- [ ] All 9 movement directions tested
- [ ] AE costs correct for each direction
- [ ] Existing physics tests updated and passing
- [ ] Physics remains deterministic

## Files Changed

- Modify: `ai_arena/game_engine/physics.py`
- Modify: `ai_arena/config/loader.py` (if config structure changes)
- Modify: `config.json`
- Modify: `tests/test_physics.py`

## Dependencies

- **Requires:** Story 004 (Data Model Foundation) - MovementDirection enum

## Blocks

- Story 006: Independent Rotation System (rotation will add back heading changes)
- Story 007: Combined AE Cost System (needs movement costs first)

## Notes

**Important:** After this story, ships will move correctly but will NOT rotate at all (heading is frozen). This is expected! Story 006 will add rotation back as an independent system.

**Testing Strategy:**
- Test each movement direction individually
- Verify heading never changes (critical!)
- Test position updates correctly based on velocity
- Test AE costs for each direction

**Migration Path:**
All existing code that creates Orders with MovementType will need to be updated to use MovementDirection + RotationCommand. This includes:
- LLM adapter (Story 008-009)
- Test fixtures
- Default orders fallback

## Developer Notes

**Why this approach is better:**

Old system: `HARD_LEFT` = "rotate 45° left AND move in an arc"
- Can't strafe (move perpendicular without rotating)
- Can't retreat while facing forward
- Phasers always point where ship is going

New system: `LEFT` movement + `NONE` rotation = "strafe left"
- Movement sets velocity direction
- Rotation sets heading (separately)
- Phasers point at heading, not velocity
- Full tactical control!

**Visual example:**

```
Ship facing → (heading = 0°, east)
Movement = LEFT (velocity = north, 90°)
Rotation = NONE (heading stays 0°)

Result:
  →  Ship body points east (heading)
  ↑  Ship moves north (velocity)
 -|  Phasers fire east (heading)
```

This is the "strafing run" maneuver!
