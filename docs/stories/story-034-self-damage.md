# Story 034: Self-Damage Implementation

**Epic:** [Epic 005: Advanced Torpedo & Blast Zone System](../epic-005-torpedo-blast-zones.md)
**Status:** ✅ COMPLETED
**Size:** Small (~1 hour)
**Priority:** P0

---

## User Story

**As a** tactical decision maker
**I want** my own torpedoes to damage me if I'm in the blast zone
**So that** close-range torpedo use has meaningful risk/reward trade-offs

## Context

Currently (from Story 033), blast damage applies to all ships in blast zones. However, the game spec explicitly requires that ships can be damaged by their **own** torpedoes, creating tactical risk:
- Launching torpedoes at close range is dangerous
- Must plan escape route before detonation
- Adds depth to torpedo tactics (not just "fire and forget")

This story validates that self-damage works and adds specific tests to ensure it's functioning correctly.

## Acceptance Criteria

- [ ] Ships take damage from blast zones created by their own torpedoes
- [ ] Ship A's torpedoes damage Ship A (if in blast zone)
- [ ] Ship B's torpedoes damage Ship B (if in blast zone)
- [ ] Opponent ships still take damage normally (existing behavior)
- [ ] Both ships in same blast zone both take damage
- [ ] Damage amount same regardless of ownership
- [ ] Self-damage events recorded correctly
- [ ] All existing tests still pass
- [ ] New tests validate self-damage scenarios

## Technical Requirements

### Validation

**Current implementation (from Story 033) should already work:**
```python
def _apply_blast_damage(self, state: GameState, dt: float) -> List[Event]:
    """Apply damage to ALL ships in blast zones, regardless of ownership."""
    events = []

    for zone in state.blast_zones:
        damage_per_second = zone.base_damage / 15.0
        damage_this_substep = damage_per_second * dt

        # Check BOTH ships - no ownership check
        for ship_id, ship in [("ship_a", state.ship_a), ("ship_b", state.ship_b)]:
            distance = ship.position.distance_to(zone.position)
            if distance < zone.current_radius:
                ship.shields -= damage_this_substep  # Damage applied regardless of zone.owner
                # ... record event ...

    return events
```

**Key insight:** Self-damage should already work because Story 033 doesn't check zone ownership. This story is primarily **validation and testing** to ensure it works correctly.

### Tests

**Create tests/test_self_damage.py:**
- Test Ship A takes damage from own torpedo blast
- Test Ship B takes damage from own torpedo blast
- Test ship takes damage when inside own blast zone
- Test ship does NOT take damage when outside own blast zone
- Test both ships take damage when in same blast zone
- Test damage amount identical for owner and non-owner
- Test self-damage event recorded correctly (shows ship damaged by own torpedo)
- Test tactical scenario: ship launches torpedo at close range, must escape
- Test multiple own torpedoes overlapping (damage stacks from own zones)

**Integration test scenarios:**
- **Scenario 1: Close-range detonation**
  - Ship A launches torpedo at close range
  - Torpedo detonates after 2 seconds
  - Ship A has only moved 6 units (not enough to escape 15-unit blast)
  - Ship A takes self-damage

- **Scenario 2: Successful escape**
  - Ship A launches torpedo and immediately retreats
  - Torpedo detonates after 10 seconds
  - Ship A has moved 30 units (outside 15-unit blast)
  - Ship A takes no self-damage

- **Scenario 3: Both ships in same blast**
  - Ship A launches torpedo between both ships
  - Torpedo detonates
  - Both Ship A and Ship B in blast zone
  - Both take identical damage

## Deliverables

- [ ] `tests/test_self_damage.py` - Self-damage validation tests (~9-10 tests)
- [ ] Integration test scenarios demonstrating self-damage tactics

## Definition of Done

- [ ] Self-damage confirmed working (ships damaged by own torpedoes)
- [ ] Tests cover owner and non-owner damage
- [ ] Tactical scenarios validated (close-range risk, escape success)
- [ ] All tests pass
- [ ] Documentation updated to highlight self-damage mechanic
- [ ] No bugs found in self-damage implementation

## Files to Create/Modify

**Create:**
- `tests/test_self_damage.py`

**Modify:**
- None (validation only - implementation from Story 033 should work)

## Dependencies

- Story 033: Continuous blast damage (provides damage implementation)

---

## Dev Agent Record

**Implementation Date:** 2025-11-18
**Agent:** Claude (Sonnet 4.5)
**Status:** ✅ COMPLETED

### Summary

Validated that self-damage works correctly from Story 033 implementation. Ships can be damaged by their own torpedoes when inside blast zones. Created comprehensive test suite with 10 tests covering basic self-damage, tactical scenarios, and event recording. No code changes required - Story 033's implementation already enables self-damage by not checking zone ownership.

### Work Completed

- ✅ Verified Story 033 implementation enables self-damage
  - Confirmed `_apply_blast_damage()` has no ownership check
  - Damage applies to ALL ships within radius regardless of zone.owner
  - Self-damage works correctly without any modifications

- ✅ Created comprehensive test suite `tests/test_self_damage.py` with 10 tests
  - Basic self-damage (Ship A and Ship B take damage from own zones)
  - Both ships in same blast zone (both damaged equally)
  - Self-damage events recorded correctly
  - Tactical scenarios (close-range detonation, successful escape)
  - Multiple own torpedoes (damage stacks)

- ✅ Tactical scenario validation
  - Close-range detonation: Ship takes self-damage when torpedo detonates nearby
  - Successful escape: Ship avoids self-damage by retreating before detonation
  - Overlapping own zones: Self-damage stacks from multiple own torpedoes

### Test Results

**All 249 tests passing** (239 baseline + 10 new self-damage tests)

- ✅ Ship A takes damage from own blast zones
- ✅ Ship B takes damage from own blast zones
- ✅ Ships outside own blast zones take no self-damage
- ✅ Both ships damaged in same blast zone (owner and non-owner)
- ✅ Damage amount identical for owner and non-owner (same position = same damage)
- ✅ Self-damage events recorded with blast_zone_id allowing identification
- ✅ Tactical scenarios validated (close-range risk, escape success)
- ✅ Multiple own torpedoes stack self-damage correctly
- ✅ No regressions in existing tests

### Issues Encountered

**Test interference from phasers:** Initial tests had ships facing each other at close range, causing phaser hits in addition to blast damage. Fixed by:
- Setting `phaser_cooldown_remaining=99.0` to disable phasers during tests
- Adjusting ship positions to be perpendicular or parallel (non-targeting orientations)
- This isolated blast damage effects for accurate self-damage validation

**No implementation issues:** Self-damage worked perfectly from Story 033 without any code changes required.

---

## QA Agent Record

**Validation Date:** [Fill in date]
**Validator:** [Fill in name]
**Verdict:** [Fill in verdict]

### Instructions for QA Agent

[When validating:

1. **Run test suite:**
   - test_self_damage.py passes all tests
   - Integration scenarios pass
   - No regression

2. **Code review:**
   - [ ] _apply_blast_damage() treats all ships equally
   - [ ] No ownership check prevents self-damage
   - [ ] Events record self-damage correctly

3. **Functional testing:**
   - [ ] Create Ship A torpedo, detonate near Ship A
   - [ ] Verify Ship A shields decreased
   - [ ] Check blast_damage event shows ship_a damaged by ship_a torpedo

4. **Tactical scenario validation:**
   - [ ] Close-range: Ship damaged by own torpedo
   - [ ] Escape: Ship avoids own torpedo blast
   - [ ] Overlap: Both ships damaged in same blast

5. **LLM prompt check:**
   - [ ] Self-damage warning in system prompt
   - [ ] Tactical guidance mentions escape planning

6. **Update QA Record**]

### Test Summary

[Fill in]

### Issues Found

[Fill in]

### Recommendations

[Fill in]

---

**Story Status:** [Update when complete]
