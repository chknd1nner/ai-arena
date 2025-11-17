# Story 021: Substep AE Tracking System

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Ready for dev
**Size:** Medium (~2-2.5 hours)
**Priority:** P0

---

## User Story

**As a** game engine developer
**I want** AE regeneration applied per substep instead of per turn
**So that** energy economy feels continuous and realistic

## Context

Currently, AE regeneration happens once at the end of each 15-second decision interval. This creates a discrete, chunky feel to energy management. The game spec calls for continuous operation where AE regenerates every substep (0.1s).

This story changes AE regeneration from per-turn to per-substep, but does NOT yet change movement/rotation costs (those are Stories 022-023). This allows us to test and validate the substep tracking system independently.

**Current behavior:**
```python
# At end of 15s turn
ship.available_energy += config.ship.ae_regeneration_rate * 15.0  # +4.95 AE once
```

**Target behavior:**
```python
# Each 0.1s substep
ship.available_energy += config.ship.ae_regeneration_rate * dt  # +0.033 AE per substep
# Over 150 substeps = +4.95 AE total (same net result, but continuous)
```

## Acceptance Criteria

- [ ] AE regeneration applied per substep, not per turn
- [ ] Regeneration uses `config.ship.ae_regeneration_rate * dt` formula
- [ ] Physics tick duration `dt` comes from `config.simulation.physics_tick`
- [ ] Regeneration happens during action phase (not decision phase)
- [ ] AE cannot exceed starting maximum (100.0 unless config changes)
- [ ] Tests verify continuous regeneration matches total turn regeneration
- [ ] Determinism preserved (same inputs = same outputs)
- [ ] No NaN or infinity values in AE calculations

## Technical Requirements

### 1. Refactor AE Regeneration in Physics Engine

**File:** `ai_arena/game_engine/physics.py`

**Current implementation (Epic 003 state):**
```python
def _action_phase(game_state: GameState, config: GameConfig) -> None:
    """Execute movement and combat for one decision interval."""

    decision_interval = config.simulation.decision_interval_seconds
    dt = config.simulation.physics_tick

    num_substeps = int(decision_interval / dt)

    for substep in range(num_substeps):
        for ship in game_state.ships.values():
            if ship.shields <= 0:
                continue

            orders = game_state.current_orders.get(ship.id)
            if orders:
                _update_ship_physics(ship, orders, config, dt)

        _update_torpedo_physics(game_state, config, dt)
        _check_collisions(game_state, config)

    # Regenerate AE once at end of turn (CURRENT - DISCRETE)
    for ship in game_state.ships.values():
        if ship.shields > 0:
            regen_amount = config.ship.ae_regeneration_rate * decision_interval
            ship.available_energy += regen_amount
            ship.available_energy = min(ship.available_energy, config.ship.starting_ae)
```

**Target implementation:**
```python
def _action_phase(game_state: GameState, config: GameConfig) -> None:
    """Execute movement and combat for one decision interval."""

    decision_interval = config.simulation.decision_interval_seconds
    dt = config.simulation.physics_tick

    num_substeps = int(decision_interval / dt)

    for substep in range(num_substeps):
        for ship in game_state.ships.values():
            if ship.shields <= 0:
                continue

            orders = game_state.current_orders.get(ship.id)
            if orders:
                _update_ship_physics(ship, orders, config, dt)

            # Regenerate AE per substep (NEW - CONTINUOUS)
            _apply_ae_regeneration(ship, config, dt)

        _update_torpedo_physics(game_state, config, dt)
        _check_collisions(game_state, config)

    # NOTE: No more end-of-turn regeneration - moved to per-substep above
```

**New helper function:**
```python
def _apply_ae_regeneration(ship: ShipState, config: GameConfig, dt: float) -> None:
    """Apply continuous AE regeneration per substep.

    Args:
        ship: Ship state to update
        config: Game configuration
        dt: Time step duration in seconds (typically 0.1s)
    """
    regen_rate = config.ship.ae_regeneration_rate  # AE per second
    regen_amount = regen_rate * dt  # AE for this substep

    ship.available_energy += regen_amount

    # Cap at maximum AE
    max_ae = config.ship.starting_ae
    ship.available_energy = min(ship.available_energy, max_ae)
```

### 2. Update Cooldown Tracking Per Substep

**File:** `ai_arena/game_engine/physics.py`

While we're modifying `_update_ship_physics`, prepare cooldown tracking:

```python
def _update_ship_physics(ship: ShipState, orders: Orders, config: GameConfig, dt: float) -> None:
    """Apply physics updates for one substep.

    Args:
        ship: Ship state to update
        orders: Commands from LLM
        config: Game configuration
        dt: Time step duration in seconds (typically 0.1s)
    """
    # Decrement phaser cooldown (Story 020 added the field, now we update it)
    if ship.phaser_cooldown_remaining > 0.0:
        ship.phaser_cooldown_remaining -= dt
        ship.phaser_cooldown_remaining = max(0.0, ship.phaser_cooldown_remaining)

    # Movement and rotation physics (unchanged for now)
    # ... existing movement/rotation code ...

    # NOTE: Movement/rotation AE costs still applied per-turn (Stories 022-023)
```

## Testing & Validation

### Unit Tests

**File:** `tests/test_continuous_physics.py` (new file)

```python
import pytest
from ai_arena.game_engine.data_models import ShipState, Vec2D, GameState, Orders, MovementDirection, RotationCommand
from ai_arena.game_engine.physics import _apply_ae_regeneration, _action_phase
from ai_arena.config.loader import load_config

def test_ae_regeneration_per_substep():
    """Verify AE regenerates per substep."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=50.0,
        phaser_cooldown_remaining=0.0
    )

    dt = config.simulation.physics_tick  # 0.1s
    expected_regen = config.ship.ae_regeneration_rate * dt  # 0.33 * 0.1 = 0.033

    _apply_ae_regeneration(ship, config, dt)

    assert ship.available_energy == pytest.approx(50.0 + expected_regen, rel=1e-6)

def test_ae_regeneration_caps_at_maximum():
    """Verify AE doesn't exceed starting maximum."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=99.9,  # Just below max
        phaser_cooldown_remaining=0.0
    )

    dt = config.simulation.physics_tick  # 0.1s

    _apply_ae_regeneration(ship, config, dt)

    # Should cap at starting_ae (100.0)
    assert ship.available_energy == config.ship.starting_ae
    assert ship.available_energy == 100.0

def test_ae_regeneration_over_full_turn():
    """Verify continuous regeneration equals total turn regeneration."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=50.0,
        phaser_cooldown_remaining=0.0
    )

    dt = config.simulation.physics_tick  # 0.1s
    decision_interval = config.simulation.decision_interval_seconds  # 15.0s
    num_substeps = int(decision_interval / dt)  # 150

    # Apply regeneration for all substeps
    for _ in range(num_substeps):
        _apply_ae_regeneration(ship, config, dt)

    # Total regeneration should equal: 0.33 AE/s * 15s = 4.95 AE
    expected_total = config.ship.ae_regeneration_rate * decision_interval
    expected_final_ae = min(50.0 + expected_total, config.ship.starting_ae)

    assert ship.available_energy == pytest.approx(expected_final_ae, rel=1e-6)

def test_cooldown_decrements_per_substep():
    """Verify phaser cooldown decrements each substep."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=100.0,
        phaser_cooldown_remaining=3.5
    )

    dt = config.simulation.physics_tick  # 0.1s

    # Mock orders (not used yet, but required by _update_ship_physics)
    orders = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    # Update physics for one substep
    from ai_arena.game_engine.physics import _update_ship_physics
    _update_ship_physics(ship, orders, config, dt)

    # Cooldown should decrease by dt
    assert ship.phaser_cooldown_remaining == pytest.approx(3.4, rel=1e-6)

def test_cooldown_bottoms_out_at_zero():
    """Verify cooldown doesn't go negative."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=100.0,
        phaser_cooldown_remaining=0.05  # Less than dt
    )

    dt = config.simulation.physics_tick  # 0.1s
    orders = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    from ai_arena.game_engine.physics import _update_ship_physics
    _update_ship_physics(ship, orders, config, dt)

    # Cooldown should be exactly 0.0, not negative
    assert ship.phaser_cooldown_remaining == 0.0

def test_no_nan_or_infinity_in_ae():
    """Verify AE calculations don't produce NaN or infinity."""
    config = load_config()
    ship = ShipState(
        id="ship1",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=0.0,  # Edge case: zero AE
        phaser_cooldown_remaining=0.0
    )

    dt = config.simulation.physics_tick

    # Apply regeneration 1000 times
    for _ in range(1000):
        _apply_ae_regeneration(ship, config, dt)

        assert not math.isnan(ship.available_energy)
        assert not math.isinf(ship.available_energy)
        assert ship.available_energy >= 0.0
        assert ship.available_energy <= config.ship.starting_ae
```

### Determinism Test

**File:** `tests/test_continuous_physics.py`

```python
def test_substep_regeneration_deterministic():
    """Verify continuous regeneration produces deterministic results."""
    config = load_config()

    results = []

    for run in range(5):
        ship = ShipState(
            id="ship1",
            position=Vec2D(0.0, 0.0),
            velocity=Vec2D(0.0, 0.0),
            heading=0.0,
            shields=100.0,
            available_energy=50.0,
            phaser_cooldown_remaining=0.0
        )

        dt = config.simulation.physics_tick
        decision_interval = config.simulation.decision_interval_seconds
        num_substeps = int(decision_interval / dt)

        for _ in range(num_substeps):
            _apply_ae_regeneration(ship, config, dt)

        results.append(ship.available_energy)

    # All runs should produce identical result
    assert len(set(results)) == 1, f"Non-deterministic results: {results}"
```

## Implementation Checklist

- [ ] Create `_apply_ae_regeneration()` helper function
- [ ] Move AE regeneration from end-of-turn to per-substep
- [ ] Add cooldown decrement logic to `_update_ship_physics()`
- [ ] Ensure AE caps at maximum value
- [ ] Ensure cooldown caps at zero (no negative values)
- [ ] Create `tests/test_continuous_physics.py`
- [ ] Write unit tests for regeneration
- [ ] Write unit tests for cooldown decrement
- [ ] Write determinism tests
- [ ] Run full test suite and verify all pass

## Edge Cases to Handle

1. **AE at maximum:** Regeneration should not exceed starting_ae
2. **AE at zero:** Regeneration should still work normally
3. **Cooldown below dt:** Should clamp to 0.0, not go negative
4. **Cooldown at zero:** Should remain at 0.0 (no underflow)
5. **Dead ship (shields = 0):** Should not regenerate AE
6. **Floating-point precision:** Use `pytest.approx()` for comparisons

## Performance Considerations

**Potential concern:** Per-substep regeneration adds 150 operations per turn per ship.

**Mitigation:**
- Regeneration is a simple addition and min() operation
- Cost is negligible compared to existing movement physics
- Profile before/after to verify

**Expected impact:** < 1% performance change

## Definition of Done

- [ ] All acceptance criteria met
- [ ] AE regeneration per substep implemented
- [ ] Cooldown tracking per substep implemented
- [ ] Unit tests written and passing
- [ ] Determinism validated
- [ ] No NaN or infinity values
- [ ] Existing tests still pass
- [ ] Code reviewed and committed

## Files Changed

- Modify: `ai_arena/game_engine/physics.py`
- Create: `tests/test_continuous_physics.py`

## Dependencies

- Story 020: Phaser Cooldown State & Config (needs cooldown field)

## Blocks

- Story 022: Continuous Movement AE (builds on substep tracking)
- Story 023: Continuous Rotation AE (builds on substep tracking)

## Notes

**Important:** This story changes AE regeneration to continuous, but movement/rotation costs remain per-turn. This creates an intermediate state where:
- Regeneration: Continuous ✅
- Movement cost: Discrete (per-turn) ⚠️
- Rotation cost: Discrete (per-turn) ⚠️

This is intentional - Stories 022-023 will make movement/rotation continuous.

**Testing Strategy:** Focus on unit tests for regeneration math. Integration testing will happen in Story 025.

**Why separate from movement/rotation:** Easier to test and debug regeneration in isolation. If something breaks, we know it's the regeneration logic, not movement.

---

## Dev Agent Record

**Implementation Date:** [To be filled in by Dev Agent]
**Agent:** [To be filled in by Dev Agent]
**Status:** [To be filled in by Dev Agent]

### Implementation Summary

[Dev Agent: Summarize what was implemented, any challenges encountered, and decisions made]

### Files Created

[Dev Agent: List any new files created]

### Files Modified

[Dev Agent: List files modified with brief description of changes]

### Testing Notes

[Dev Agent: Describe testing performed, test results, any edge cases discovered]

### Technical Notes

[Dev Agent: Any important implementation details, gotchas, or notes for future developers]

### Known Issues / Future Work

[Dev Agent: Any issues discovered, limitations, or follow-up work needed]

---

## QA Agent Record

**Validation Date:** 2025-11-15
**Validator:** Claude (QA Agent)
**Verdict:** PASS

### Acceptance Criteria Validation

✓ **AE regeneration applied per substep, not per turn**
  - Evidence: `ai_arena/game_engine/physics.py:297` - `self._apply_ae_regeneration(ship, dt)`
  - Moved from end-of-turn batch to per-substep continuous application
  - Test: `tests/test_continuous_physics.py::TestAERegenerationPerSubstep::test_ae_regenerates_continuously`

✓ **Regeneration uses `config.ship.ae_regeneration_rate * dt` formula**
  - Evidence: `ai_arena/game_engine/physics.py:263-265`
  - Formula: `regen_amount = self.config.ship.ae_regen_per_second * dt`
  - Test validates correct calculation: `test_total_regeneration_matches_expected`

✓ **Physics tick duration `dt` comes from `config.simulation.physics_tick`**
  - Evidence: `ai_arena/game_engine/physics.py:297` - `dt` parameter passed from substep loop
  - Confirmed: dt = 0.1s from config

✓ **Regeneration happens during action phase (not decision phase)**
  - Evidence: `ai_arena/game_engine/physics.py:294-297` - Inside `_update_ship_physics()` within substep loop
  - Removed old end-of-turn regeneration (lines 156-164 deleted)

✓ **AE cannot exceed starting maximum**
  - Evidence: `ai_arena/game_engine/physics.py:266` - `ship.ae = min(ship.ae, self.config.ship.max_ae)`
  - Test: `tests/test_continuous_physics.py::TestAERegenerationPerSubstep::test_ae_caps_at_maximum`

✓ **Tests verify continuous regeneration matches total turn regeneration**
  - Evidence: `tests/test_continuous_physics.py::TestAERegenerationPerSubstep::test_total_regeneration_matches_expected`
  - Test confirms 150 substeps × 0.033 AE = 4.95 AE total (matches 15s × 0.33 AE/s)

✓ **Determinism preserved (same inputs = same outputs)**
  - Evidence: `tests/test_continuous_physics.py::TestDeterminism::test_identical_runs_produce_identical_results`
  - Test runs same match 10 times, validates byte-identical results

✓ **No NaN or infinity values in AE calculations**
  - Evidence: `tests/test_continuous_physics.py::TestNoInvalidValues::test_no_nan_or_infinity_in_ae`
  - Test applies regeneration 1000× and validates no invalid values

### Test Results

**All tests passing: 125/125**

Story 021-specific tests (12 tests):
- `TestAERegenerationPerSubstep`: 3 tests PASSED
  - `test_ae_regenerates_continuously`
  - `test_ae_caps_at_maximum`
  - `test_total_regeneration_matches_expected`

- `TestCooldownDecrementPerSubstep`: 3 tests PASSED
  - `test_cooldown_decrements_over_turn`
  - `test_cooldown_caps_at_zero`
  - `test_zero_cooldown_stays_zero`

- `TestDeterminism`: 1 test PASSED
  - `test_identical_runs_produce_identical_results`

- `TestNoInvalidValues`: 3 tests PASSED
  - `test_no_nan_or_infinity_in_positions`
  - `test_no_nan_or_infinity_in_ae`
  - `test_no_nan_or_infinity_in_cooldown`

- `TestContinuousPhysicsIntegration`: 2 tests PASSED
  - `test_movement_with_regeneration`
  - `test_aggressive_maneuver_drains_ae`

Full test output saved to: `screenshots/story-020-021/test_results.txt`

### Code Quality Assessment

**Excellent** - Implementation follows best practices:

**Architecture:**
- Clean separation of concerns: `_apply_ae_regeneration()` is a focused helper function
- Follows single responsibility principle
- Per-substep application properly integrated into existing physics loop

**Code Quality:**
- Proper docstring for `_apply_ae_regeneration()` (lines 253-262)
- Clear variable names (`regen_amount`, `max_ae`)
- Consistent with existing physics engine patterns
- Removed old code cleanly (end-of-turn regeneration deleted)

**Physics Correctness:**
- Formula mathematically sound: rate × time = amount
- Proper capping prevents AE overflow
- Cooldown decrement uses same dt (consistent timing)
- Cooldown clamping prevents negative values (lines 300-301)

**Code Diff Evidence:**
- `screenshots/story-020-021/physics_changes.diff`

### Issues Found

**No issues found.**

The implementation is correct and complete:
- AE regeneration works per substep as specified
- Cooldown tracking integrated seamlessly
- All edge cases handled (capping, negative prevention)
- Tests comprehensive and passing
- Code quality high

### Final Verdict

**PASS** - Story 021 implementation is complete and correct.

**Summary:**
- All 8 acceptance criteria met with evidence
- 12 new tests added, all passing
- Physics behaves correctly (continuous regeneration, determinism preserved)
- Code quality excellent
- No regressions (all 125 tests pass)
- Ready for merge

**Evidence Package:**
- Test results: `screenshots/story-020-021/test_results.txt`
- Code changes: `screenshots/story-020-021/physics_changes.diff`
- Test file: `tests/test_continuous_physics.py` (comprehensive coverage)

---

**Story Status:** QA Passed
