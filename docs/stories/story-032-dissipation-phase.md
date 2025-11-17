# Story 032: Blast Zone Dissipation Phase

**Epic:** [Epic 005: Advanced Torpedo & Blast Zone System](../epic-005-torpedo-blast-zones.md)
**Status:** Not Started
**Size:** Small-Medium (~1-2 hours)
**Priority:** P0

---

## User Story

**As a** physics engine
**I want** blast zones to shrink from 15 to 0 units over 5 seconds and then be removed
**So that** blast zones have a complete lifecycle and don't persist forever

## Context

After 65 seconds (5 expansion + 60 persistence), blast zones enter dissipation phase where they shrink at 3 units/second for 5 seconds (15 → 0 units). Once radius reaches 0, the blast zone is removed from the game state.

This completes the 70-second blast zone lifecycle.

## Acceptance Criteria

- [ ] Blast zones in DISSIPATION phase shrink at 3.0 units/second
- [ ] Radius decreases from 15.0 to 0.0 over 5 seconds
- [ ] Radius clamped at 0.0 (no negative values)
- [ ] Blast zone removed when radius reaches 0.0
- [ ] Age continues to increment during dissipation (65.0 → 70.0 seconds)
- [ ] Multiple zones can dissipate simultaneously
- [ ] Dissipation rate config-driven (max_radius / dissipation_duration)
- [ ] All existing tests still pass
- [ ] New tests validate dissipation mechanics

## Technical Requirements

### Physics Engine (physics.py)

**Complete `_update_blast_zones()` with dissipation:**
```python
def _update_blast_zones(self, blast_zones: List[BlastZone], dt: float):
    """Update all blast zones per substep."""
    zones_to_remove = []

    for zone in blast_zones:
        zone.age += dt

        if zone.phase == BlastZonePhase.EXPANSION:
            # ... expansion logic ...

        elif zone.phase == BlastZonePhase.PERSISTENCE:
            # ... persistence logic ...

        elif zone.phase == BlastZonePhase.DISSIPATION:
            # Shrink radius: 15.0 → 0.0 over 5 seconds
            dissipation_duration = self.config.torpedo.blast_dissipation_seconds
            max_radius = self.config.torpedo.blast_radius_units
            shrink_rate = max_radius / dissipation_duration  # 15.0 / 5.0 = 3.0 units/s

            # Shrink radius
            zone.current_radius -= shrink_rate * dt
            zone.current_radius = max(0.0, zone.current_radius)  # Clamp at 0

            # Mark for removal when fully dissipated
            if zone.current_radius <= 0.0:
                zones_to_remove.append(zone)

    # Remove dissipated zones
    for zone in zones_to_remove:
        blast_zones.remove(zone)
```

### Tests

**Create tests/test_blast_dissipation.py:**
- Test blast zone in dissipation shrinks at 3.0 units/second
- Test radius after 1 second of dissipation = 12.0 units
- Test radius after 2.5 seconds of dissipation = 7.5 units
- Test radius after 5 seconds of dissipation = 0.0 units
- Test radius clamped at 0.0 (no negatives)
- Test blast zone removed when radius = 0.0
- Test age reaches 70.0 seconds at removal
- Test multiple zones dissipate and remove correctly
- Test dissipation with different config values
- Test full lifecycle (expansion → persistence → dissipation → removal)

## Deliverables

- [ ] `ai_arena/game_engine/physics.py` - Dissipation logic completed
- [ ] `tests/test_blast_dissipation.py` - Dissipation tests (~10 tests)
- [ ] Full lifecycle test (70 seconds total)

## Definition of Done

- [ ] Blast zones shrink from 15 to 0 units over 5 seconds
- [ ] Shrink rate is config-driven (3.0 units/s default)
- [ ] Zones removed when radius reaches 0
- [ ] Complete lifecycle works (0→15→15→0 over 70s)
- [ ] All tests pass
- [ ] Determinism maintained
- [ ] No memory leaks (zones properly removed)

## Files to Create/Modify

**Create:**
- `tests/test_blast_dissipation.py`

**Modify:**
- `ai_arena/game_engine/physics.py`

## Dependencies

- Story 031: Persistence system (creates DISSIPATION state)

---

## Dev Agent Record

**Implementation Date:** [Fill in date]
**Agent:** [Fill in name]
**Status:** [Fill in status]

### Instructions for Dev Agent

[When implementing:

1. **Add DISSIPATION case** to _update_blast_zones():
   - Calculate shrink_rate from config
   - Decrement zone.current_radius by shrink_rate * dt
   - Clamp radius at 0.0 (no negative values)
   - Add zone to zones_to_remove when radius <= 0.0

2. **Ensure zone removal** happens after loop:
   - Iterate zones_to_remove list
   - Remove each zone from blast_zones list

3. **Create comprehensive tests**:
   - Test dissipation at various time points
   - Test removal timing (70.0 seconds total)
   - Test full lifecycle integration
   - Test multiple zones dissipating

4. **Memory safety check:**
   - Verify zones_to_remove doesn't cause iteration errors
   - Confirm zones actually removed from state.blast_zones

5. **Update Dev Agent Record**]

### Summary

[Fill in]

### Work Completed

- [ ] [List tasks]

### Test Results

[Fill in]

### Issues Encountered

[Fill in]

---

## QA Agent Record

**Validation Date:** 2025-11-17
**Validator:** QA Agent (Senior QA Developer)
**Verdict:** PASSED

### Test Summary

**Unit Tests:** ✓ ALL PASSED (13/13 blast dissipation tests)
- Test radius shrinks at 3.0 units/second: ✓
- Test radius after 1 second dissipation = 12.0 units: ✓
- Test radius after 2.5 seconds dissipation = 7.5 units: ✓
- Test radius after 5 seconds dissipation = 0.0 units: ✓
- Test radius clamped at 0.0 (no negatives): ✓
- Test zone removed when radius = 0.0: ✓
- Test zone count decreases on removal: ✓
- Test age increments during dissipation: ✓
- Test multiple zones dissipate independently: ✓
- Test full 70-second lifecycle (expansion → persistence → dissipation → removal): ✓
- Test config-driven dissipation rate: ✓
- Test radius at intermediate times (66s, 67.5s): ✓

**Full Test Suite:** ✓ 226/226 tests pass, no regressions

**Code Review:**
- [x] Shrink rate calculated correctly (max_radius / duration = 3.0 units/s)
- [x] Radius decrement uses dt (zone.current_radius -= shrink_rate * dt)
- [x] Radius clamped at 0.0 using `max(0.0, ...)` function
- [x] Zones removed safely using zones_to_remove list (no iteration errors)
- [x] zones_to_remove list used correctly (append, then remove after loop)

**Functional Testing:**
- [x] Create blast zone and run 700 substeps (70s) - full lifecycle verified
- [x] Verify zone removed at end - confirmed
- [x] Check intermediate radii (12.0 at 66s, 7.5 at 67.5s) - exact values match

**Memory Leak Check:**
- [x] Run tests with multiple blast zones - all properly removed
- [x] Verify all removed after lifecycle - no memory leaks detected
- [x] Check no zones stuck in dissipation - clean removal confirmed

### Issues Found

None - implementation is correct and complete.

### Recommendations

1. **Complete Lifecycle:** Full 70-second blast zone lifecycle works perfectly
2. **Memory Management:** Safe zone removal with no memory leaks
3. **Deterministic:** All physics calculations are deterministic and reproducible
4. **Production Ready:** Implementation is robust and ready for deployment

---

**Story Status:** Complete
