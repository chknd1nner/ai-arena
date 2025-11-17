# Story 031: Blast Zone Persistence System

**Epic:** [Epic 005: Advanced Torpedo & Blast Zone System](../epic-005-torpedo-blast-zones.md)
**Status:** Not Started
**Size:** Small (~1 hour)
**Priority:** P0

---

## User Story

**As a** game designer
**I want** blast zones to persist at full radius for 60 seconds
**So that** they create meaningful area denial and force multi-turn tactical adjustments

## Context

After expansion (5 seconds), blast zones enter persistence phase where they remain at full 15-unit radius for 60 seconds. This creates:
- Long-term area denial (persists ~4 decision intervals)
- Strategic battlefield shaping
- Multi-turn tactical consequences

This is the simplest phase - blast zones just maintain their current radius while age increments.

## Acceptance Criteria

- [ ] Blast zones in PERSISTENCE phase maintain radius at max_radius
- [ ] Phase remains PERSISTENCE for 60 seconds after expansion
- [ ] After 65 seconds total (5 expansion + 60 persistence), phase transitions to DISSIPATION
- [ ] Age continues to increment during persistence
- [ ] Radius unchanged during persistence (stays at 15.0 units)
- [ ] Multiple blast zones can persist simultaneously
- [ ] All existing tests still pass
- [ ] New tests validate persistence behavior

## Technical Requirements

### Physics Engine (physics.py)

**Extend `_update_blast_zones()` with persistence logic:**
```python
def _update_blast_zones(self, blast_zones: List[BlastZone], dt: float):
    """Update all blast zones per substep."""
    zones_to_remove = []

    for zone in blast_zones:
        zone.age += dt

        if zone.phase == BlastZonePhase.EXPANSION:
            # ... expansion logic from Story 030 ...

        elif zone.phase == BlastZonePhase.PERSISTENCE:
            # Maintain current radius (no changes)
            persistence_start = self.config.torpedo.blast_expansion_seconds
            persistence_end = persistence_start + self.config.torpedo.blast_persistence_seconds

            # Check for phase transition to dissipation
            if zone.age >= persistence_end:
                zone.phase = BlastZonePhase.DISSIPATION

        # Dissipation handled in Story 032

    for zone in zones_to_remove:
        blast_zones.remove(zone)
```

### Tests

**Create tests/test_blast_persistence.py:**
- Test zone maintains radius=15.0 during persistence
- Test phase remains PERSISTENCE for 60 seconds
- Test phase transition occurs at 65 seconds (5 expansion + 60 persistence)
- Test age increments correctly during persistence (5.0 → 65.0 seconds)
- Test multiple zones in persistence simultaneously
- Test config-driven persistence duration
- Test no radius changes during persistence (stable at max_radius)

## Deliverables

- [ ] `ai_arena/game_engine/physics.py` - Persistence logic added
- [ ] `tests/test_blast_persistence.py` - Persistence tests (~7-8 tests)

## Definition of Done

- [ ] Blast zones persist at full radius for 60 seconds
- [ ] Phase transitions to DISSIPATION at 65 seconds total age
- [ ] Radius remains exactly 15.0 units during persistence
- [ ] All tests pass
- [ ] Determinism maintained
- [ ] Config-driven behavior (persistence_duration)

## Files to Create/Modify

**Create:**
- `tests/test_blast_persistence.py`

**Modify:**
- `ai_arena/game_engine/physics.py`

## Dependencies

- Story 030: Expansion phase (required - creates PERSISTENCE state)

---

## Dev Agent Record

**Implementation Date:** [Fill in date]
**Agent:** [Fill in name]
**Status:** [Fill in status]

### Instructions for Dev Agent

[When implementing:

1. **Add PERSISTENCE case** to _update_blast_zones():
   - Calculate persistence_end = expansion_duration + persistence_duration
   - Check if zone.age >= persistence_end
   - Transition to DISSIPATION when threshold reached
   - No radius changes (zone.current_radius remains at max_radius)

2. **Create tests** in test_blast_persistence.py:
   - Test radius stability during persistence
   - Test phase transition timing
   - Test config-driven duration

3. **Integration test:**
   - Create blast zone, step through full expansion + persistence
   - Verify 650 substeps (65 seconds) before dissipation

4. **Update Dev Agent Record**]

### Summary

[Fill in summary]

### Work Completed

- [ ] [List tasks]

### Test Results

[Fill in results]

### Issues Encountered

[Fill in issues]

---

## QA Agent Record

**Validation Date:** [Fill in date]
**Validator:** [Fill in name]
**Verdict:** [Fill in verdict]

### Instructions for QA Agent

[When validating:

1. **Run tests** and verify:
   - test_blast_persistence.py passes
   - No regression

2. **Code review:**
   - [ ] Persistence duration from config
   - [ ] Phase transition at correct time (65s)
   - [ ] Radius unchanged during persistence
   - [ ] Age increments correctly

3. **Functional testing:**
   - [ ] Step blast zone through 650 substeps (65s)
   - [ ] Verify radius = 15.0 throughout persistence
   - [ ] Verify phase = DISSIPATION at end

4. **Update QA Record**]

### Test Summary

[Fill in]

### Issues Found

[Fill in]

### Recommendations

[Fill in]

---

**Story Status:** [Update when complete]
