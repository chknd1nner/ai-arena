# Story 023: Continuous Rotation AE Application

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Completed
**Size:** Small (~1 hour)
**Priority:** P0

---

## User Story

**As a** game engine developer
**I want** rotation AE costs applied per substep instead of per turn
**So that** energy drain from rotation feels continuous

## Context

Similar to Story 022, but for rotation. This completes the transition to fully continuous AE economy.

**Target behavior:**
```python
# Each 0.1s substep
rotation_rate = _get_rotation_ae_rate(orders.rotation, config)  # e.g., 0.33 AE/s for HARD
ae_cost_this_substep = rotation_rate * dt  # 0.33 * 0.1 = 0.033 AE
ship.available_energy -= ae_cost_this_substep
```

## Acceptance Criteria

- [ ] Rotation AE cost applied per substep
- [ ] All 5 rotation commands have correct rates
- [ ] Total cost over full turn matches previous per-turn cost
- [ ] Tests verify continuous rotation costs
- [ ] Combined movement + rotation costs work correctly

## Technical Requirements

```python
def _get_rotation_ae_rate(rotation: RotationCommand, config: GameConfig) -> float:
    """Get AE cost rate for rotation command."""
    rates = {
        RotationCommand.NONE: config.rotation.none_ae_per_second,
        RotationCommand.SOFT_LEFT: config.rotation.soft_turn_ae_per_second,
        RotationCommand.SOFT_RIGHT: config.rotation.soft_turn_ae_per_second,
        RotationCommand.HARD_LEFT: config.rotation.hard_turn_ae_per_second,
        RotationCommand.HARD_RIGHT: config.rotation.hard_turn_ae_per_second
    }
    return rates[rotation]
```

## Testing & Validation

```python
def test_rotation_ae_cost_per_substep():
    """Verify rotation AE cost applied per substep."""
    # Similar to test_movement_ae_cost_per_substep but for rotation
    pass

def test_combined_movement_and_rotation_costs():
    """Verify movement + rotation costs combine correctly."""
    # Test aggressive maneuver: PERPENDICULAR + HARD_LEFT
    # Should cost 0.67 + 0.33 = 1.0 AE/s
    # Regen: 0.33 AE/s
    # Net: -0.67 AE/s
    pass
```

## Definition of Done

- [ ] Rotation AE applied continuously
- [ ] All tests passing
- [ ] Combined costs work correctly

## Files Changed

- Modify: `ai_arena/game_engine/physics.py`
- Modify: `tests/test_continuous_physics.py`

## Dependencies

- Story 022: Continuous Movement AE

---

## Dev Agent Record

**Implementation Date:** 2025-11-15
**Agent Identifier:** Claude (Sonnet 4.5)
**Status:** Completed - Ready for QA

### Implementation Summary

Successfully implemented continuous rotation AE cost application per substep, completing the continuous AE economy system. Rotation costs are now applied incrementally every 0.1 seconds (per physics tick) rather than as a single deduction at the start of each turn. This was implemented alongside Story 022 (movement costs) as they share the same pattern.

**Key Implementation Details:**
1. Renamed `_get_rotation_ae_cost()` to `_get_rotation_ae_rate()` for clarity (returns AE per second)
2. Updated `_update_ship_physics()` to apply rotation costs per substep
3. Costs applied in correct order: movement → rotation → regeneration → clamp
4. All 5 rotation commands properly mapped to their AE rates from config

### Files Created
None (only modified existing files)

### Files Modified
1. `ai_arena/game_engine/physics.py`:
   - Renamed `_get_rotation_ae_cost()` → `_get_rotation_ae_rate()` (lines 199-216)
   - Updated `_validate_orders()` to use new function name (line 225)
   - Updated `_update_ship_physics()` to apply rotation cost per substep (lines 311-314)
   - Updated docstrings and comments

2. `tests/test_continuous_physics.py`:
   - Added `TestRotationAECostsPerSubstep` class with 3 test cases (lines 525-627)
   - Tests cover: per-substep costs, combined movement+rotation costs, full turn totals

### Testing Notes

All tests passing (131/131):
- `test_rotation_ae_cost_per_substep`: Validates rotation cost applied correctly per 0.1s substep
- `test_combined_movement_and_rotation_costs`: Confirms movement + rotation costs combine correctly
- `test_rotation_cost_over_full_turn`: Verifies continuous costs equal discrete costs over full turn
- All existing tests continue to pass (no regressions)

**Test Adjustments:**
- Tests use ships at 50.0 AE (not max) to avoid regeneration capping interference
- Corrected comment: SOFT_LEFT costs 0.13 AE/s (not 0.17 as originally noted)

### Technical Notes

1. **Combined Cost Application:** Movement and rotation costs are applied sequentially per substep:
   ```python
   ship.ae -= movement_rate * dt  # e.g., 0.67 * 0.1 = 0.067 AE
   ship.ae -= rotation_rate * dt   # e.g., 0.33 * 0.1 = 0.033 AE
   ship.ae += regen_rate * dt      # e.g., 0.333 * 0.1 = 0.0333 AE
   ship.ae = max(0.0, ship.ae)     # Clamp at zero
   ```

2. **Energy Economy Examples (validated in tests):**
   - LEFT (0.67 AE/s) + HARD_LEFT (0.33 AE/s) = 1.0 AE/s total cost
   - With regen (0.333 AE/s), net drain = -0.667 AE/s
   - STOP + NONE = net gain of +0.333 AE/s (recharging)

3. **Rotation Rate Mapping:**
   - NONE: 0.0 AE/s
   - SOFT_LEFT/RIGHT: 0.13 AE/s
   - HARD_LEFT/RIGHT: 0.33 AE/s
   - All values sourced from config.json

4. **Completion of Continuous AE Economy:** With Stories 021, 022, and 023 complete, the entire AE economy is now continuous:
   - ✅ Regeneration per substep (Story 021)
   - ✅ Movement costs per substep (Story 022)
   - ✅ Rotation costs per substep (Story 023)
   - ✅ Cooldown decrement per substep (Story 021)

5. **Determinism:** Continuous application maintains deterministic physics required for replay system.

---

## QA Agent Record

**Validation Date:** 2025-11-16
**Validator:** Senior QA Developer (Claude Code)
**Verdict:** ✅ PASSED WITH MINOR FIX

### Acceptance Criteria Validation

✅ **Rotation AE cost applied per substep** - Verified at physics.py:311-314
✅ **All 5 rotation commands have correct rates** - Mapped correctly in `_get_rotation_ae_rate()` (physics.py:186-203)
✅ **Total cost matches expected** - Test `test_rotation_cost_over_full_turn` confirms continuous = discrete
✅ **Tests verify continuous rotation costs** - 3 dedicated tests all passing
✅ **Combined movement + rotation costs work** - Test `test_combined_movement_and_rotation_costs` validates combined application

### Test Results

**Unit Tests (18/18 PASSED):**
```
TestRotationAECostsPerSubstep::test_rotation_ae_cost_per_substep PASSED
TestRotationAECostsPerSubstep::test_combined_movement_and_rotation_costs PASSED
TestRotationAECostsPerSubstep::test_rotation_cost_over_full_turn PASSED
```

**Integration Tests:**
```
TestContinuousPhysicsIntegration::test_aggressive_maneuver_drains_ae PASSED
  - Validates LEFT (0.67 AE/s) + HARD_LEFT (0.33 AE/s) = net -0.667 AE/s drain
  - Confirms continuous costs combine correctly
```

**Visual Validation:**
- ✅ Screenshots captured: `/screenshots/story-023/`
- ✅ All services operational
- ✅ Continuous physics observable in test replays

### Issues Found

🐛 **Minor Bug - Missing Rotation Field in Replay Serialization** (Same as Story 022)
- **Location:** `ai_arena/replay/recorder.py:107`
- **Issue:** Rotation field was not being serialized to replay JSON
- **Impact:** Rotation commands not visible in replay data
- **Severity:** Low (doesn't affect physics execution)
- **Fix Applied:** Added rotation field to `_serialize_orders()`
- **Verification:** Tests still pass, rotation now appears in new replays

### QA Summary

Excellent implementation that completes the continuous AE economy system started in Story 021. Rotation costs are correctly applied per substep using `ae_cost = rotation_ae_rate × dt`. The combined application of movement and rotation costs works seamlessly.

**Energy Economy Verification:**
- Aggressive maneuver (LEFT + HARD_LEFT) correctly drains -0.667 AE/s net
- Rotation rates properly sourced from config.json
- Costs combine additively as expected
- Clamping at zero prevents negative AE values

The implementation follows the same pattern as Story 022, maintaining code consistency and making the continuous physics system easy to understand and maintain.

**Note:** The rotation field serialization bug affected both Story 022 and 023 equally, since they share the same replay recorder. The fix ensures rotation commands are now properly recorded for future analysis and debugging.

**Recommendation:** APPROVE for merge with fix applied.

---

**Story Status:** ✅ Complete
