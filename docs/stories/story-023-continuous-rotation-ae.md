# Story 023: Continuous Rotation AE Application

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Ready for QA
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
