# Story 033: Continuous Blast Damage

**Epic:** [Epic 005: Advanced Torpedo & Blast Zone System](../epic-005-torpedo-blast-zones.md)
**Status:** ✅ COMPLETED
**Size:** Medium (~2-3 hours)
**Priority:** P0

---

## User Story

**As a** ship captain
**I want** to take continuous damage while inside blast zones
**So that** blast zones are dangerous and force me to avoid or escape them

## Context

Blast zones currently expand, persist, and dissipate visually, but don't damage ships yet. This story implements the continuous damage mechanic:
- Damage rate = (base_damage ÷ 15.0) per second
- Applied every substep while ship is in zone
- Damage stacks from multiple overlapping zones
- Damage events recorded for replay

## Acceptance Criteria

- [ ] Ships take damage when inside blast zone radius
- [ ] Damage applied per substep (not per turn)
- [ ] Damage rate = (base_damage ÷ 15.0) per second
- [ ] Multiple overlapping zones stack damage
- [ ] Damage events recorded with zone ID, ship ID, amount
- [ ] Ships outside blast radius take no damage
- [ ] Damage applies during all phases (expansion, persistence, dissipation)
- [ ] All existing tests still pass
- [ ] New tests validate damage mechanics

## Technical Requirements

### Physics Engine (physics.py)

**Add damage application method:**
```python
def _apply_blast_damage(self, state: GameState, dt: float) -> List[Event]:
    """Apply continuous damage to ships in blast zones.

    Damage rate = (base_damage ÷ 15.0) per second
    Damage per substep = damage_rate × dt

    Args:
        state: Current game state
        dt: Time step (0.1 seconds)

    Returns:
        List of blast damage events
    """
    events = []

    for zone in state.blast_zones:
        # Calculate damage for this zone
        damage_per_second = zone.base_damage / 15.0
        damage_this_substep = damage_per_second * dt

        # Check each ship for collision with zone
        for ship_id, ship in [("ship_a", state.ship_a), ("ship_b", state.ship_b)]:
            distance = ship.position.distance_to(zone.position)

            if distance < zone.current_radius:
                # Ship is inside blast zone - apply damage
                ship.shields -= damage_this_substep

                # Record damage event (for replay/debugging)
                events.append(Event(
                    type="blast_damage",
                    turn=state.turn,
                    data={
                        "ship": ship_id,
                        "blast_zone_id": zone.id,
                        "damage": damage_this_substep,
                        "zone_phase": zone.phase.value,
                        "zone_radius": zone.current_radius,
                        "distance": distance
                    }
                ))

    return events
```

**Integrate into substep loop:**
```python
def resolve_turn(self, state: GameState, orders_a: Orders, orders_b: Orders):
    # ... initialization ...

    for substep in range(self.substeps):
        # ... existing substep updates ...

        # Update blast zones (expansion/persistence/dissipation)
        self._update_blast_zones(new_state.blast_zones, self.fixed_timestep)

        # Handle torpedo detonations (creates new zones)
        self._handle_torpedo_detonations(new_state, events, self.fixed_timestep)

        # NEW: Apply blast damage to ships in zones
        blast_damage_events = self._apply_blast_damage(new_state, self.fixed_timestep)
        events.extend(blast_damage_events)

        # Check phaser hits (existing)
        phaser_events = self._check_phaser_hits(new_state)
        events.extend(phaser_events)

    return new_state, events
```

### Damage Calculation Examples

**Example 1: High-damage torpedo**
- Torpedo detonates with 30.0 AE remaining
- Base damage = 30.0 × 1.5 = 45.0
- Damage per second = 45.0 ÷ 15.0 = 3.0
- Damage per substep = 3.0 × 0.1 = 0.3
- Ship in zone for 5 seconds = 5.0 × 3.0 = 15.0 total damage

**Example 2: Low-damage torpedo**
- Torpedo detonates with 10.0 AE remaining
- Base damage = 10.0 × 1.5 = 15.0
- Damage per second = 15.0 ÷ 15.0 = 1.0
- Damage per substep = 1.0 × 0.1 = 0.1
- Ship in zone for 5 seconds = 5.0 × 1.0 = 5.0 total damage

**Example 3: Overlapping zones**
- Zone 1: 3.0 damage/second
- Zone 2: 2.0 damage/second
- Ship in both zones: 5.0 damage/second total
- Ship in both for 3 seconds = 15.0 total damage

### Tests

**Create tests/test_blast_damage.py:**
- Test ship takes damage when inside blast radius
- Test damage rate calculation (base_damage ÷ 15.0)
- Test damage applied per substep (0.1s increments)
- Test ship outside radius takes no damage
- Test ship at exact radius boundary (edge case)
- Test damage accumulates over multiple substeps
- Test multiple overlapping zones stack damage
- Test damage during expansion phase
- Test damage during persistence phase
- Test damage during dissipation phase
- Test damage events recorded correctly
- Test shields decrease correctly

## Deliverables

- [ ] `ai_arena/game_engine/physics.py` - Blast damage implementation
- [ ] `tests/test_blast_damage.py` - Damage tests (~12-15 tests)

## Definition of Done

- [ ] Ships take damage when inside blast zones
- [ ] Damage rate = (base_damage ÷ 15.0) per second
- [ ] Damage applied every substep
- [ ] Overlapping zones stack damage correctly
- [ ] Damage events recorded for replay
- [ ] All tests pass
- [ ] Determinism maintained
- [ ] No edge case bugs (radius boundaries, etc.)

## Files to Create/Modify

**Create:**
- `tests/test_blast_damage.py`

**Modify:**
- `ai_arena/game_engine/physics.py`

## Dependencies

- Story 032: Dissipation phase (blast zones have full lifecycle)

---

## Dev Agent Record

**Implementation Date:** 2025-11-18
**Agent:** Claude (Sonnet 4.5)
**Status:** ✅ COMPLETED

### Summary

Successfully implemented continuous blast damage mechanics. Ships now take damage every substep while inside blast zone radius. The implementation correctly calculates damage rate as (base_damage ÷ 15.0) per second and applies it continuously over the decision interval (15 seconds).

### Work Completed

- ✅ Implemented `_apply_blast_damage()` method in `ai_arena/game_engine/physics.py`
  - Calculates damage_per_second = zone.base_damage / 15.0
  - Applies damage_this_substep = damage_per_second * dt to ships within radius
  - Records blast_damage events with zone ID, ship ID, damage, phase, radius, and distance
  - No ownership check (enables self-damage for Story 034)

- ✅ Integrated blast damage into substep loop (lines 153-155)
  - Called after `_handle_torpedo_detonations()` (new zones created)
  - Called before phaser hit checks (outside loop)
  - Events correctly extended with blast damage events

- ✅ Created comprehensive test suite `tests/test_blast_damage.py` with 13 tests
  - Basic damage mechanics (inside/outside radius, damage rate)
  - Damage accumulation over substeps
  - Overlapping zones stack damage correctly
  - Damage applies in all phases (expansion, persistence, dissipation)
  - Event recording validation
  - Edge cases (exact boundary, zero radius, both ships)

### Test Results

**All 239 tests passing** (226 baseline + 13 new blast damage tests)

- ✅ Ships take damage when inside blast zones
- ✅ Damage rate correctly calculated as base_damage / 15.0
- ✅ Damage applied continuously per substep (dt = 0.1s)
- ✅ Multiple overlapping zones stack damage
- ✅ Damage applies during all lifecycle phases
- ✅ Blast damage events recorded correctly
- ✅ No regressions in existing tests

**Key test insight:** Decision interval is 15 seconds (not 60), so total damage per turn = damage_rate × 15.

### Issues Encountered

**Initial test failures:** Tests assumed 60-second decision intervals, but actual config uses 15 seconds. Fixed by using `physics_engine.action_phase_duration` instead of hardcoded values. This ensures tests work correctly regardless of config changes.

---

## QA Agent Record

**Validation Date:** [Fill in date]
**Validator:** [Fill in name]
**Verdict:** [Fill in verdict]

### Instructions for QA Agent

[When validating:

1. **Run tests:**
   - test_blast_damage.py passes all tests
   - Integration test with full match
   - No regression

2. **Code review:**
   - [ ] Damage rate calculation correct (base ÷ 15.0)
   - [ ] Damage applied per substep (× dt)
   - [ ] Distance check correct (< radius, not <=)
   - [ ] Shields decremented properly
   - [ ] Events recorded with all fields

3. **Functional testing:**
   - [ ] Create blast zone with known base damage
   - [ ] Place ship inside for 50 substeps (5s)
   - [ ] Verify shields decreased by expected amount
   - [ ] Test overlapping zones damage stacks

4. **Edge cases:**
   - [ ] Ship at exact radius boundary
   - [ ] Zone radius = 0.0 (no damage)
   - [ ] Negative shields (should clamp at 0?)

5. **Event validation:**
   - [ ] Damage events in replay JSON
   - [ ] Event data complete and accurate

6. **Update QA Record**]

### Test Summary

[Fill in]

### Issues Found

[Fill in]

### Recommendations

[Fill in]

---

**Story Status:** [Update when complete]
