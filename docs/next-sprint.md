# Next Sprint: Epic 005 - Blast Zone Lifecycle Implementation

**Sprint Goal:** Implement complete 70-second blast zone lifecycle (creation → expansion → persistence → dissipation → removal)

**Stories in This Sprint:**
1. [Story 029: Timed Torpedo Detonation](stories/story-029-timed-detonation.md) (Medium, 2-3 hours)
2. [Story 030: Blast Zone Expansion Phase](stories/story-030-expansion-phase.md) (Small-Medium, 2 hours)
3. [Story 031: Blast Zone Persistence System](stories/story-031-persistence-system.md) (Small, 1 hour)
4. [Story 032: Blast Zone Dissipation Phase](stories/story-032-dissipation-phase.md) (Small-Medium, 1-2 hours)

**Estimated Duration:** 6-8 hours (one 200k token session)

**Branch:** `claude/plan-next-sprint-01WzdPTYfSd94DJKWszKHGmV`

---

## Sprint Overview

This sprint continues **Epic 005: Advanced Torpedo & Blast Zone System** by implementing the complete blast zone lifecycle. This builds on Story 028 (data models) and prepares for damage mechanics (Stories 033-035).

### What Was Completed Last Sprint

**Story 028: Blast Zone Data Models** ✅ **COMPLETED & QA PASSED**

Successfully implemented all foundational data structures:
- Added `BlastZonePhase` enum with 3 lifecycle phases (EXPANSION, PERSISTENCE, DISSIPATION)
- Created `BlastZone` dataclass with 7 fields tracking position, damage, phase, age, radius, and owner
- Updated `GameState` to track blast zones via `blast_zones: List[BlastZone]`
- Updated `TorpedoState` to support timed detonation via `detonation_timer: Optional[float]`
- Added blast zone configuration to config.json
- All 166 tests passing (17 new + 149 existing, 0 regressions)

### Why These 4 Stories Together?

These stories form a natural unit that implements the complete blast zone lifecycle:
- **Story 029** creates blast zones when torpedoes detonate (timed or auto)
- **Story 030** makes them expand from 0→15 units over 5 seconds
- **Story 031** makes them persist at 15 units for 60 seconds
- **Story 032** makes them dissipate from 15→0 units over 5 seconds and get removed

After this sprint, blast zones will have complete visible behavior (lifecycle) but won't damage ships yet. Damage mechanics (Stories 033-035) will be the next sprint.

### Game Specification Reference

From `docs/game_spec_revised.md` (lines 348-395):

**Blast Zone Lifecycle (70 seconds total):**
- **Expansion (5s):** Radius grows from 0→15 units at 3.0 units/second
- **Persistence (60s):** Radius holds at 15 units for ~4 decision intervals
- **Dissipation (5s):** Radius shrinks from 15→0 units at 3.0 units/second, then zone removed

**Timed Detonation:**
- Format: `{"torpedo_id": "torp_1", "action": "detonate_after", "delay": 5.2}`
- Delay range: 0.0 to 15.0 seconds
- Creates blast zone at torpedo's position when timer expires

---

## Sprint Implementation Instructions

### Development Workflow

**IMPORTANT: Work sequentially through the stories in order:**
1. Complete Story 029 (timed detonation) first
2. Then Story 030 (expansion phase)
3. Then Story 031 (persistence system)
4. Finally Story 032 (dissipation phase)

Each story builds on the previous one, so sequential implementation is required.

**After completing each story:**
1. Run the full test suite: `pytest tests/ -v`
2. Verify no regressions (all existing tests still pass)
3. Update the story's Dev Agent Record with implementation details
4. Move to the next story

---

## Story 029: Timed Torpedo Detonation

**Goal:** Enable LLMs to command torpedoes to detonate after a specified delay (0.0-15.0 seconds)

**Read the full story:** [`docs/stories/story-029-timed-detonation.md`](stories/story-029-timed-detonation.md)

**Key Implementation Points:**

1. **LLM Order Parsing** (`ai_arena/llm_adapter/adapter.py`):
   - Add `_parse_torpedo_action()` method to parse `"detonate_after:X"` commands
   - Extract action type and delay from command string
   - Validate delay is in range [0.0, 15.0]
   - Return tuple: (action_type, delay) where delay is None for movement commands

2. **Apply Detonation Timer** (in `resolve_turn()` when processing orders):
   - When torpedo order has action="detonate_after", set `torpedo.detonation_timer = delay`
   - Movement commands don't set timer (remains None)

3. **Detonation Handler** (`ai_arena/game_engine/physics.py`):
   - Create `_handle_torpedo_detonations()` method
   - Called each substep in the substep loop
   - For each torpedo:
     - If `detonation_timer is not None`: decrement by dt, check if <= 0
     - If `ae_remaining <= 0`: auto-detonate (existing behavior)
   - When detonation triggered:
     - Create BlastZone at torpedo's position
     - Set phase=EXPANSION, age=0.0, current_radius=0.0
     - Calculate base_damage = ae_remaining × blast_damage_multiplier
     - Set owner = torpedo.owner
     - Append to state.blast_zones
     - Record "torpedo_detonated" event
     - Remove torpedo from state.torpedoes

4. **Testing** (`tests/test_timed_detonation.py`):
   - Test parsing various delay values (0.1, 5.0, 10.0, 15.0)
   - Test invalid delays raise errors (< 0, > 15)
   - Test timer decrements correctly per substep
   - Test blast zone created when timer reaches 0
   - Test auto-detonation when AE depletes
   - Test multiple torpedoes with different timers

**Deliverables:**
- Modified: `ai_arena/llm_adapter/adapter.py`
- Modified: `ai_arena/game_engine/physics.py`
- Created: `tests/test_timed_detonation.py` (~10-12 tests)

---

## Story 030: Blast Zone Expansion Phase

**Goal:** Blast zones expand from 0 to 15 units over 5 seconds at 3.0 units/second

**Read the full story:** [`docs/stories/story-030-expansion-phase.md`](stories/story-030-expansion-phase.md)

**Key Implementation Points:**

1. **Blast Zone Update Method** (`ai_arena/game_engine/physics.py`):
   - Create `_update_blast_zones()` method
   - Called each substep in the substep loop (BEFORE _handle_torpedo_detonations)
   - For each blast zone, increment `zone.age += dt`
   - If phase == EXPANSION:
     - Calculate growth_rate = max_radius / expansion_duration (from config)
     - Increment radius: `zone.current_radius += growth_rate * dt`
     - Clamp radius at max_radius
     - Check transition: if `zone.age >= expansion_duration`, set phase = PERSISTENCE

2. **Integration into Substep Loop**:
   ```python
   for substep in range(self.substeps):
       # ... existing updates ...

       # NEW: Update blast zones FIRST (before new zones created)
       self._update_blast_zones(new_state.blast_zones, self.fixed_timestep)

       # Handle detonations (creates new blast zones)
       self._handle_torpedo_detonations(new_state, events, self.fixed_timestep)
   ```

3. **Testing** (`tests/test_blast_expansion.py`):
   - Test radius grows at 3.0 units/second
   - Test radius at various time points (1s=3.0, 2.5s=7.5, 5s=15.0)
   - Test phase transitions to PERSISTENCE at 5.0 seconds
   - Test radius clamped at max_radius

**Deliverables:**
- Modified: `ai_arena/game_engine/physics.py`
- Created: `tests/test_blast_expansion.py` (~10 tests)

---

## Story 031: Blast Zone Persistence System

**Goal:** Blast zones persist at full radius for 60 seconds after expansion

**Read the full story:** [`docs/stories/story-031-persistence-system.md`](stories/story-031-persistence-system.md)

**Key Implementation Points:**

1. **Extend `_update_blast_zones()`** with persistence logic:
   - Add case for `phase == PERSISTENCE`:
     - Calculate persistence_end = expansion_duration + persistence_duration
     - Check if `zone.age >= persistence_end`
     - If yes, transition to `zone.phase = BlastZonePhase.DISSIPATION`
     - No radius changes (stays at max_radius)

2. **Testing** (`tests/test_blast_persistence.py`):
   - Test zone maintains radius=15.0 during persistence
   - Test phase transitions at 65 seconds (5 expansion + 60 persistence)
   - Test age increments correctly

**Deliverables:**
- Modified: `ai_arena/game_engine/physics.py`
- Created: `tests/test_blast_persistence.py` (~7-8 tests)

---

## Story 032: Blast Zone Dissipation Phase

**Goal:** Blast zones shrink from 15 to 0 units over 5 seconds, then are removed

**Read the full story:** [`docs/stories/story-032-dissipation-phase.md`](stories/story-032-dissipation-phase.md)

**Key Implementation Points:**

1. **Complete `_update_blast_zones()`** with dissipation:
   - Add case for `phase == DISSIPATION`:
     - Calculate shrink_rate = max_radius / dissipation_duration
     - Decrement radius: `zone.current_radius -= shrink_rate * dt`
     - Clamp at 0: `zone.current_radius = max(0.0, zone.current_radius)`
     - If radius <= 0.0: append zone to zones_to_remove list
   - After loop: remove all zones in zones_to_remove from blast_zones list

2. **Testing** (`tests/test_blast_dissipation.py`):
   - Test blast zone shrinks at 3.0 units/second
   - Test radius at dissipation times (66s=12.0, 67.5s=7.5, 70s=0.0)
   - Test blast zone removed when radius = 0.0
   - Test full lifecycle (expansion → persistence → dissipation → removal)

**Deliverables:**
- Modified: `ai_arena/game_engine/physics.py`
- Created: `tests/test_blast_dissipation.py` (~10 tests)

---

## Critical Implementation Notes

### Determinism Requirements

**CRITICAL:** Physics must remain 100% deterministic for replay system.

- Use exact floating-point arithmetic (same as Epic 004)
- Use config values (don't hardcode 15.0, 5.0, etc.)
- Increment/decrement by `rate * dt` (not hardcoded 0.1)

### Substep Loop Order

**The substep loop should look like this:**

```python
for substep in range(self.substeps):
    # 1. Update resources
    self._update_resources(new_state.ship_a, valid_orders_a, dt)
    self._update_resources(new_state.ship_b, valid_orders_b, dt)

    # 2. Update physics
    self._update_ship_physics(new_state.ship_a, valid_orders_a, dt)
    self._update_ship_physics(new_state.ship_b, valid_orders_b, dt)
    for torpedo in new_state.torpedoes:
        self._update_torpedo_physics(torpedo, ..., dt)

    # 3. NEW: Update blast zones (expansion/persistence/dissipation)
    self._update_blast_zones(new_state.blast_zones, self.fixed_timestep)

    # 4. NEW: Handle torpedo detonations (creates new blast zones)
    self._handle_torpedo_detonations(new_state, events, self.fixed_timestep)

    # 5. Check weapon hits
    phaser_events = self._check_phaser_hits(new_state)
    events.extend(phaser_events)
```

### Config Values

From `config.json`:
- `config.torpedo.blast_expansion_seconds` = 5.0
- `config.torpedo.blast_persistence_seconds` = 60.0
- `config.torpedo.blast_dissipation_seconds` = 5.0
- `config.torpedo.blast_radius_units` = 15.0
- `config.torpedo.blast_damage_multiplier` = 1.5

Never hardcode these values - always use config.

---

## Sprint Success Criteria

**The sprint is DONE when:**

- [ ] All 4 stories (029-032) implemented and tested
- [ ] Full test suite passes (~203 tests expected)
- [ ] Blast zones have complete 70-second lifecycle
- [ ] Torpedoes detonate on timer or AE depletion
- [ ] Blast zones expand, persist, dissipate, and are removed automatically
- [ ] All 4 story Dev Agent Records completed
- [ ] No regressions in existing tests
- [ ] Determinism validated
- [ ] Ready for QA validation

**Expected test count progression:**
- After Story 029: ~176 tests (166 baseline + 10 new)
- After Story 030: ~186 tests (+10 expansion tests)
- After Story 031: ~193 tests (+7 persistence tests)
- After Story 032: ~203 tests (+10 dissipation tests)

---

## What's NOT in This Sprint

**Stories deferred to next sprint:**
- Story 033: Continuous Blast Damage
- Story 034: Self-Damage Implementation
- Story 035: Blast Zone Integration & Balance

**Rationale:** This sprint focuses on blast zone lifecycle mechanics. Damage mechanics and integration are a separate logical unit.

---

## Getting Started

### Pre-Sprint Checklist

1. [ ] Verify Story 028 is complete and merged
2. [ ] Run baseline test: `pytest tests/ -v` (expect 166 passing)
3. [ ] Review `docs/game_spec_revised.md` lines 348-395
4. [ ] Review `docs/epic-005-torpedo-blast-zones.md`
5. [ ] Ensure on branch: `claude/plan-next-sprint-01WzdPTYfSd94DJKWszKHGmV`

### Story Implementation Order

1. **Story 029** (2-3 hours): Implement timed detonation
2. **Story 030** (2 hours): Implement expansion phase
3. **Story 031** (1 hour): Implement persistence phase
4. **Story 032** (1-2 hours): Implement dissipation phase

**Total estimated time:** 6-8 hours

---

## Key References

- **Game Spec:** `docs/game_spec_revised.md` (lines 348-395)
- **Epic 005:** `docs/epic-005-torpedo-blast-zones.md`
- **Stories:** `docs/stories/story-029-*.md` through `story-032-*.md`
- **CLAUDE.md:** Project development guide

---

🚀 **Ready to implement the blast zone lifecycle! Work sequentially, test thoroughly, document completely. Good luck!**
