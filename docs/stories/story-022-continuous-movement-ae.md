# Story 022: Continuous Movement AE Application

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Not Started
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

**Implementation Date:** [To be filled in by Dev Agent]
**Agent:** [To be filled in by Dev Agent]
**Status:** [To be filled in by Dev Agent]

---

## QA Agent Record

**Validation Date:** [To be filled in by QA Agent]
**Validator:** [To be filled in by QA Agent]
**Verdict:** [To be filled in by QA Agent]

---

**Story Status:** Ready for Development
