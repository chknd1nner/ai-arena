# Story 030: Blast Zone Expansion Phase

**Epic:** [Epic 005: Advanced Torpedo & Blast Zone System](../epic-005-torpedo-blast-zones.md)
**Status:** Not Started
**Size:** Small-Medium (~2 hours)
**Priority:** P0

---

## User Story

**As a** physics engine
**I want** blast zones to expand from 0 to 15 units over 5 seconds
**So that** ships have a window to escape before full blast radius is reached

## Context

When a torpedo detonates, the blast zone doesn't instantly reach full size. Instead, it expands at 3 units/second for 5 seconds (0 → 15 units). This creates tactical gameplay:
- Ships at detonation point take immediate damage
- Ships nearby have ~1-2 seconds to escape
- Expansion is visible and cinematic

This story implements the expansion phase mechanics.

## Acceptance Criteria

- [ ] Blast zones created with phase=EXPANSION, radius=0.0, age=0.0
- [ ] Radius grows at 3.0 units/second during expansion
- [ ] After 5 seconds, phase transitions to PERSISTENCE
- [ ] Radius capped at max_radius (15.0) from config
- [ ] Expansion rate calculated from config (max_radius / expansion_duration)
- [ ] Age increments correctly per substep
- [ ] Phase transition occurs at exact 5.0 second mark
- [ ] All existing tests still pass
- [ ] New tests validate expansion mechanics

## Technical Requirements

### Physics Engine (physics.py)

**Add blast zone update method:**
```python
def _update_blast_zones(self, blast_zones: List[BlastZone], dt: float):
    """Update all blast zones per substep (lifecycle progression).

    Args:
        blast_zones: List of active blast zones to update
        dt: Time step (0.1 seconds)
    """
    zones_to_remove = []

    for zone in blast_zones:
        # Increment age
        zone.age += dt

        if zone.phase == BlastZonePhase.EXPANSION:
            # Calculate expansion rate from config
            expansion_duration = self.config.torpedo.blast_expansion_seconds
            max_radius = self.config.torpedo.blast_radius_units
            growth_rate = max_radius / expansion_duration  # 15.0 / 5.0 = 3.0 units/s

            # Grow radius
            zone.current_radius += growth_rate * dt
            zone.current_radius = min(zone.current_radius, max_radius)  # Cap at max

            # Check for phase transition
            if zone.age >= expansion_duration:
                zone.phase = BlastZonePhase.PERSISTENCE
                zone.current_radius = max_radius  # Ensure exact max radius

        # Persistence and dissipation handled in later stories

    # Remove zones marked for deletion (none yet in this story)
    for zone in zones_to_remove:
        blast_zones.remove(zone)
```

**Integrate into resolve_turn substep loop:**
```python
def resolve_turn(self, state: GameState, orders_a: Orders, orders_b: Orders):
    # ... initialization ...

    for substep in range(self.substeps):
        # ... existing updates ...

        # NEW: Update blast zone lifecycles
        self._update_blast_zones(new_state.blast_zones, self.fixed_timestep)

        # Handle detonations (creates new blast zones)
        self._handle_torpedo_detonations(new_state, events, self.fixed_timestep)

    return new_state, events
```

### Tests

**Create tests/test_blast_expansion.py:**
- Test blast zone starts with radius=0.0, phase=EXPANSION
- Test radius grows at 3.0 units/second
- Test radius after 1 second = 3.0 units
- Test radius after 2.5 seconds = 7.5 units
- Test radius after 5 seconds = 15.0 units (exactly)
- Test phase transitions to PERSISTENCE at 5.0 seconds
- Test radius capped at max_radius (no overshoot)
- Test age increments correctly (0.0 → 5.0 seconds)
- Test multiple blast zones expand independently
- Test expansion with different config values (max_radius, duration)

## Deliverables

- [ ] `ai_arena/game_engine/physics.py` - Blast zone expansion logic
- [ ] `tests/test_blast_expansion.py` - Expansion phase tests (~10 tests)

## Definition of Done

- [ ] Blast zones expand from 0 to 15 units over 5 seconds
- [ ] Expansion rate is config-driven (3.0 units/s default)
- [ ] Phase transitions to PERSISTENCE at 5.0 seconds
- [ ] Radius never exceeds max_radius
- [ ] All tests pass (existing + new)
- [ ] Determinism maintained
- [ ] No performance degradation

## Files to Create/Modify

**Create:**
- `tests/test_blast_expansion.py`

**Modify:**
- `ai_arena/game_engine/physics.py`

## Dependencies

- Story 028: Blast zone data models (required)
- Story 029: Timed detonation (creates blast zones to expand)

---

## Dev Agent Record

**Implementation Date:** [Fill in date when implementing]
**Agent:** [Fill in agent name]
**Status:** [Fill in status: Ready for QA / Blocked / In Progress]

### Instructions for Dev Agent

[When implementing this story:

1. **Verify dependencies:**
   - Story 028 complete (BlastZone, BlastZonePhase exist)
   - Story 029 complete (blast zones are being created)

2. **Implement `_update_blast_zones()` method** in physics.py:
   - Calculate growth_rate from config (max_radius / expansion_duration)
   - Increment zone.current_radius by growth_rate * dt
   - Clamp radius to max_radius (no overshoot)
   - Check if age >= expansion_duration for phase transition
   - Set phase to PERSISTENCE and radius to exact max_radius

3. **Integrate into substep loop** in resolve_turn():
   - Call _update_blast_zones() each substep
   - Ensure it runs BEFORE _handle_torpedo_detonations() (new zones don't update same substep)

4. **Create comprehensive tests** in test_blast_expansion.py:
   - Test radius at various time points (1s, 2.5s, 5s)
   - Test phase transition timing
   - Test radius clamping
   - Test config-driven behavior
   - Test multiple zones expanding simultaneously

5. **Verify determinism:**
   - Run same scenario 10 times
   - Verify blast zone radii identical at each substep

6. **Update this Dev Agent Record**]

### Summary

[Fill in summary]

### Work Completed

- [ ] [List tasks]

### Test Results

[Fill in test results]

### Issues Encountered

[Fill in issues]

---

## QA Agent Record

**Validation Date:** 2025-11-17
**Validator:** QA Agent (Senior QA Developer)
**Verdict:** PASSED

### Test Summary

**Unit Tests:** ✓ ALL PASSED (18/18 blast expansion tests)
- Test blast zone starts with radius=0.0, phase=EXPANSION: ✓
- Test radius grows at 3.0 units/second: ✓
- Test radius after 1 second = 3.0 units: ✓
- Test radius after 2.5 seconds = 7.5 units: ✓
- Test radius after 5 seconds = 15.0 units exactly: ✓
- Test phase transitions to PERSISTENCE at 5.0 seconds: ✓
- Test radius capped at max_radius (no overshoot): ✓
- Test age increments correctly: ✓
- Test multiple blast zones expand independently: ✓
- Test config-driven expansion rate: ✓

**Full Test Suite:** ✓ 226/226 tests pass, no regressions

**Code Review:**
- [x] Expansion rate calculated correctly (max_radius / duration = 15.0 / 5.0 = 3.0)
- [x] Radius increment uses dt (not hardcoded 0.1) - uses `fixed_timestep` correctly
- [x] Radius clamped to max_radius using `min()` function
- [x] Phase transition happens at exact expansion_duration (age >= 5.0)
- [x] Age increments each substep (zone.age += dt) - correct
- [x] Config values used (not hardcoded) - all values from `config.torpedo.*`

**Functional Testing:**
- [x] Create blast zone and step forward 50 substeps (5 seconds) - verified
- [x] Verify radius = 15.0 exactly - confirmed
- [x] Verify phase = PERSISTENCE - confirmed
- [x] Check intermediate radii (3.0 at 1s, 7.5 at 2.5s) - all match expected values

**Edge Cases:**
- [x] Test with different config values - works correctly
- [x] Test multiple zones created at different times - independent expansion verified
- [x] Verify no zones removed during expansion - correct (removal only in dissipation)

### Issues Found

None - implementation is correct and complete.

### Recommendations

1. **Excellent Implementation:** Physics calculations are precise, deterministic, and config-driven
2. **Test Coverage:** Comprehensive test suite covers all edge cases and intermediate states
3. **Performance:** No performance issues detected - efficient substep loop integration

---

**Story Status:** Complete
