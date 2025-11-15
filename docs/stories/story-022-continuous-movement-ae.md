# Story 022: Continuous Movement AE Application

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Ready for QA
**Size:** Small (~1-1.5 hours)
**Priority:** P0

---

## User Story

**As a** game engine developer
**I want** movement AE costs applied per substep instead of per turn
**So that** energy drain from movement feels continuous

## Context

Currently, movement AE costs are deducted once per 15-second decision interval. With Story 021 adding continuous regeneration, we now need to make movement costs continuous too.

**Current behavior (discrete):**
```python
# Once at start of turn
movement_cost = get_movement_cost_for_turn(orders.movement, config)  # e.g., 10 AE
ship.available_energy -= movement_cost  # Deduct entire turn's cost upfront
```

**Target behavior (continuous):**
```python
# Each 0.1s substep
movement_rate = get_movement_ae_rate(orders.movement, config)  # e.g., 0.67 AE/s
ae_cost_this_substep = movement_rate * dt  # 0.67 * 0.1 = 0.067 AE
ship.available_energy -= ae_cost_this_substep
```

## Acceptance Criteria

- [ ] Movement AE cost applied per substep using `movement_ae_rate * dt`
- [ ] Movement rates come from config (already exist: `forward_ae_per_second`, etc.)
- [ ] All 9 movement directions have correct per-second rates
- [ ] Total AE cost over full turn matches previous per-turn cost
- [ ] AE can go to zero but not negative (clamp at 0.0)
- [ ] Movement physics still work when AE is depleted
- [ ] Tests verify continuous movement costs
- [ ] Determinism preserved

## Technical Requirements

### Movement AE Rate Mapping

**File:** `ai_arena/game_engine/physics.py`

Create helper function to get movement AE rate:

```python
def _get_movement_ae_rate(movement: MovementDirection, config: GameConfig) -> float:
    """Get AE cost rate for movement direction.

    Args:
        movement: Movement direction command
        config: Game configuration

    Returns:
        AE cost in AE per second
    """
    rates = {
        MovementDirection.FORWARD: config.movement.forward_ae_per_second,
        MovementDirection.FORWARD_LEFT: config.movement.diagonal_ae_per_second,
        MovementDirection.FORWARD_RIGHT: config.movement.diagonal_ae_per_second,
        MovementDirection.LEFT: config.movement.perpendicular_ae_per_second,
        MovementDirection.RIGHT: config.movement.perpendicular_ae_per_second,
        MovementDirection.BACKWARD: config.movement.backward_ae_per_second,
        MovementDirection.BACKWARD_LEFT: config.movement.backward_diagonal_ae_per_second,
        MovementDirection.BACKWARD_RIGHT: config.movement.backward_diagonal_ae_per_second,
        MovementDirection.STOP: config.movement.stop_ae_per_second
    }
    return rates[movement]
```

### Apply Movement Cost Per Substep

Update `_update_ship_physics()`:

```python
def _update_ship_physics(ship: ShipState, orders: Orders, config: GameConfig, dt: float) -> None:
    """Apply physics updates for one substep."""

    # Decrement phaser cooldown (from Story 021)
    if ship.phaser_cooldown_remaining > 0.0:
        ship.phaser_cooldown_remaining -= dt
        ship.phaser_cooldown_remaining = max(0.0, ship.phaser_cooldown_remaining)

    # Apply movement AE cost per substep (NEW)
    movement_ae_rate = _get_movement_ae_rate(orders.movement, config)
    ae_cost_this_substep = movement_ae_rate * dt
    ship.available_energy -= ae_cost_this_substep
    ship.available_energy = max(0.0, ship.available_energy)  # Clamp at zero

    # Apply movement physics (unchanged - already works per substep)
    # ... existing movement code ...
```

## Testing & Validation

**File:** `tests/test_continuous_physics.py` (add to existing)

```python
def test_movement_ae_cost_per_substep():
    """Verify movement AE cost applied per substep."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=100.0,
        phaser_cooldown_remaining=0.0
    )

    orders = Orders(
        movement=MovementDirection.PERPENDICULAR,  # 0.67 AE/s
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    dt = config.simulation.physics_tick  # 0.1s
    expected_cost = config.movement.perpendicular_ae_per_second * dt  # 0.067 AE

    initial_ae = ship.available_energy
    _update_ship_physics(ship, orders, config, dt)

    # AE should decrease by movement cost minus regeneration
    regen = config.ship.ae_regeneration_rate * dt
    expected_ae = initial_ae - expected_cost + regen

    assert ship.available_energy == pytest.approx(expected_ae, rel=1e-6)

def test_movement_cost_over_full_turn():
    """Verify continuous movement cost equals total turn cost."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=100.0,
        phaser_cooldown_remaining=0.0
    )

    orders = Orders(
        movement=MovementDirection.FORWARD,  # 0.33 AE/s
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    dt = config.simulation.physics_tick
    decision_interval = config.simulation.decision_interval_seconds
    num_substeps = int(decision_interval / dt)

    for _ in range(num_substeps):
        _apply_ae_regeneration(ship, config, dt)
        movement_rate = _get_movement_ae_rate(orders.movement, config)
        ship.available_energy -= movement_rate * dt
        ship.available_energy = max(0.0, ship.available_energy)

    # Net AE change: regen - movement
    # Regen: 0.33 AE/s * 15s = 4.95 AE
    # Movement: 0.33 AE/s * 15s = 4.95 AE
    # Net: 0.0 AE (energy neutral for FORWARD movement)
    assert ship.available_energy == pytest.approx(100.0, rel=1e-6)

def test_ae_does_not_go_negative():
    """Verify AE is clamped at zero."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=0.05,  # Very low AE
        phaser_cooldown_remaining=0.0
    )

    orders = Orders(
        movement=MovementDirection.PERPENDICULAR,  # High cost: 0.67 AE/s
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    dt = config.simulation.physics_tick
    _update_ship_physics(ship, orders, config, dt)

    # AE should be exactly 0.0, not negative
    assert ship.available_energy >= 0.0
    assert ship.available_energy == 0.0  # Cost exceeds available, should clamp
```

## Implementation Checklist

- [ ] Create `_get_movement_ae_rate()` helper function
- [ ] Apply movement cost per substep in `_update_ship_physics()`
- [ ] Clamp AE at zero (no negative values)
- [ ] Write unit tests for movement costs
- [ ] Verify total turn cost matches expected
- [ ] Verify AE clamping at zero
- [ ] Run full test suite

## Definition of Done

- [ ] Movement AE applied continuously per substep
- [ ] All tests passing
- [ ] No negative AE values
- [ ] Determinism preserved

## Files Changed

- Modify: `ai_arena/game_engine/physics.py`
- Modify: `tests/test_continuous_physics.py`

## Dependencies

- Story 021: Substep AE Tracking

## Blocks

- Story 025: Continuous Physics Testing

---

## Dev Agent Record

**Implementation Date:** 2025-11-15
**Agent Identifier:** Claude (Sonnet 4.5)
**Status:** Completed - Ready for QA

### Implementation Summary

Successfully implemented continuous movement AE cost application per substep. The implementation follows the pattern established in Story 021 for continuous AE regeneration. Movement costs are now applied incrementally every 0.1 seconds (per physics tick) rather than as a single deduction at the start of each turn.

**Key Implementation Details:**
1. Renamed `_get_movement_ae_cost()` to `_get_movement_ae_rate()` for clarity (returns AE per second)
2. Updated `_update_ship_physics()` to apply movement costs per substep
3. Removed old discrete AE deduction from `resolve_turn()`
4. Applied proper ordering: costs → regeneration → clamping
5. AE values are clamped at zero to prevent negative values

### Files Created
None (only modified existing files)

### Files Modified
1. `ai_arena/game_engine/physics.py`:
   - Renamed `_get_movement_ae_cost()` → `_get_movement_ae_rate()` (lines 176-197)
   - Updated `_validate_orders()` to use new function name (line 224)
   - Removed discrete AE deduction from `resolve_turn()` (removed lines 119-129)
   - Updated `_update_ship_physics()` to apply movement cost per substep (lines 306-309)
   - Updated step numbering and comments

2. `tests/test_continuous_physics.py`:
   - Added `TestMovementAECostsPerSubstep` class with 3 test cases (lines 431-522)
   - Tests cover: per-substep costs, full turn totals, and AE clamping

### Testing Notes

All tests passing (131/131):
- `test_movement_ae_cost_per_substep`: Validates cost applied correctly per 0.1s substep
- `test_movement_cost_over_full_turn`: Confirms continuous costs equal discrete costs over full turn
- `test_ae_does_not_go_negative`: Verifies AE clamping at zero
- All existing tests continue to pass (no regressions)

**Test Fix Required:** Initial test used ships at max AE (100.0), causing regeneration capping to interfere with assertions. Fixed by starting ships at 50.0 AE to avoid cap interference.

### Technical Notes

1. **Order of Operations:** Movement cost → rotation cost → regeneration → clamp at zero. This ensures costs are deducted before regeneration happens.

2. **AE Regeneration Capping:** The `_apply_ae_regeneration()` function caps AE at max (100.0), which can interfere with tests if ships start at max AE. Tests now use ships starting at 50.0 AE.

3. **Determinism Preserved:** Fixed timestep and continuous application maintain deterministic behavior required for replay system.

4. **Energy Economy Validation:**
   - FORWARD (0.33 AE/s) + NONE (0.0 AE/s) vs regen (0.333 AE/s) = ~0 net (energy neutral)
   - LEFT (0.67 AE/s) drains faster than regen can offset
   - STOP (0.0 AE/s) + NONE allows maximum regeneration

5. **Pattern Consistency:** Implementation mirrors Story 021's approach for continuous AE regeneration and cooldown decrement.

---

## QA Agent Record

[QA Agent: After dev implementation is complete:
- Validate all acceptance criteria
- Run all tests and verify they pass
- Check code quality and adherence to patterns
- Document any issues found
- If all checks pass, update YAML status to "Completed"
- If issues found, update YAML status to "Remediation needed" and document issues]

**Validation Date:** [To be filled in by QA Agent]
**Validator:** [To be filled in by QA Agent]
**Verdict:** [To be filled in by QA Agent]

### Acceptance Criteria Validation
[To be filled in by QA Agent]

### Test Results
[To be filled in by QA Agent]

### Issues Found
[To be filled in by QA Agent]

---

**Story Status:** Ready for Development
