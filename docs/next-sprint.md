# Next Sprint: Epic 005 Completion - Blast Zone Damage & Integration

**Sprint Goal:** Complete Epic 005 by implementing blast zone damage mechanics, self-damage validation, and full system integration with balance tuning.

**Stories in This Sprint:**
1. [Story 033: Continuous Blast Damage](stories/story-033-continuous-damage.md) (Medium, 2-3 hours)
2. [Story 034: Self-Damage Implementation](stories/story-034-self-damage.md) (Small, ~1 hour)
3. [Story 035: Blast Zone Integration & Balance](stories/story-035-integration-balance.md) (Medium-Large, 3-4 hours)

**Estimated Duration:** 6-7 hours (one 200k token session)

**Branch:** `claude/plan-next-sprint-01RYmYuSJaW8s9AbnTCaxVk6`

---

## Sprint Overview

This sprint **completes Epic 005: Advanced Torpedo & Blast Zone System** by implementing damage mechanics and full integration. This is the final phase of the blast zone lifecycle epic.

### What Was Completed Last Sprint

**Stories 029-032: Blast Zone Lifecycle** ✅ **ALL COMPLETED & QA PASSED**

Successfully implemented complete 70-second blast zone lifecycle:
- **Story 029:** Timed torpedo detonation with `detonate_after:X` commands (0.0-15.0s range)
- **Story 030:** Blast zone expansion from 0→15 units over 5 seconds at 3.0 units/second
- **Story 031:** Blast zone persistence at 15 units for 60 seconds (~4 decision intervals)
- **Story 032:** Blast zone dissipation from 15→0 units over 5 seconds, then removal
- **Story 032a (Bugfix):** Fixed critical canvas rendering bug (blast zones now display correctly)

**Current State:**
- All 226 tests passing (no regressions)
- Blast zones have complete visual lifecycle (expansion → persistence → dissipation → removal)
- Torpedoes can detonate on timer or AE depletion
- Frontend can display blast zones correctly

**What's Missing:**
- Blast zones don't damage ships yet (Stories 033-034)
- LLM prompts don't include blast zone documentation (Story 035)
- No integration testing or balance tuning (Story 035)

### Why These 3 Stories Together?

These stories complete Epic 005 as a natural unit:
- **Story 033** implements the core damage mechanic (ships take damage while in blast zones)
- **Story 034** validates self-damage works (ships can hurt themselves with own torpedoes)
- **Story 035** integrates everything, updates LLM prompts, tunes balance, and validates production readiness

After this sprint, Epic 005 will be **100% complete and production-ready**.

### Game Specification Reference

From `docs/game_spec_revised.md` (lines 377-387):

**Blast Damage Model:**
- Base damage = (Torpedo AE at detonation) × 1.5
- Damage rate = Base damage ÷ 15.0 = damage per second in zone
- Example: 30 AE torpedo → 45 base damage → 3.0 damage/second
- Ship in zone for 2.3 seconds → 2.3 × 3.0 = 6.9 damage
- Continuous damage applied every 0.1 second substep
- Multiple overlapping zones stack damage
- **Self-damage:** Ships CAN be damaged by their own torpedoes

---

## Sprint Implementation Instructions

### Development Workflow

**IMPORTANT: Work sequentially through the stories in order:**
1. Complete Story 033 (continuous blast damage) first
2. Then Story 034 (self-damage validation)
3. Finally Story 035 (integration & balance)

Each story builds on the previous one, so sequential implementation is required.

**After completing each story:**
1. Run the full test suite: `pytest tests/ -v`
2. Verify no regressions (all existing tests still pass)
3. Update the story's Dev Agent Record with implementation details
4. Update the story's YAML status to "Ready for QA"
5. Move to the next story

---

## Story 033: Continuous Blast Damage

**Goal:** Ships take continuous damage while inside blast zone radius

**Read the full story:** [`docs/stories/story-033-continuous-damage.md`](stories/story-033-continuous-damage.md)

**Key Implementation Points:**

1. **Damage Application Method** (`ai_arena/game_engine/physics.py`):
   - Create `_apply_blast_damage()` method
   - Calculate damage_per_second = zone.base_damage / 15.0
   - Calculate damage_this_substep = damage_per_second × dt
   - Check distance from each ship to zone center
   - Apply damage if distance < zone.current_radius
   - Record "blast_damage" events for replay
   - Damage applies to **ALL ships** (no ownership check - enables self-damage)

2. **Integrate into Substep Loop**:
   ```python
   for substep in range(self.substeps):
       # ... existing updates ...
       self._update_blast_zones(new_state.blast_zones, dt)
       self._handle_torpedo_detonations(new_state, events, dt)

       # NEW: Apply blast damage to ships in zones
       blast_damage_events = self._apply_blast_damage(new_state, dt)
       events.extend(blast_damage_events)

       # Check phaser hits
       phaser_events = self._check_phaser_hits(new_state)
       events.extend(phaser_events)
   ```

3. **Testing** (`tests/test_blast_damage.py`):
   - Test damage rate calculation (base_damage ÷ 15.0)
   - Test damage applied per substep
   - Test ship inside radius takes damage
   - Test ship outside radius takes no damage
   - Test damage accumulates over multiple substeps
   - Test multiple overlapping zones stack damage
   - Test damage during all phases (expansion, persistence, dissipation)
   - Test damage events recorded correctly

**Deliverables:**
- Modified: `ai_arena/game_engine/physics.py`
- Created: `tests/test_blast_damage.py` (~12-15 tests)

**Expected Test Count:** ~238 tests (226 baseline + 12 new)

---

## Story 034: Self-Damage Implementation

**Goal:** Validate that ships can be damaged by their own torpedoes (self-damage works)

**Read the full story:** [`docs/stories/story-034-self-damage.md`](stories/story-034-self-damage.md)

**Key Implementation Points:**

1. **Validation (Not Implementation)**:
   - Story 033's `_apply_blast_damage()` should already enable self-damage
   - No ownership check = all ships in blast zone take damage (including owner)
   - This story primarily validates through testing

2. **If Self-Damage NOT Working**:
   - Debug `_apply_blast_damage()` to ensure no ownership filtering
   - Verify blast zone owner field is set correctly
   - Fix and document in Dev Agent Record

3. **Testing** (`tests/test_self_damage.py`):
   - Test Ship A takes damage from own torpedo blast
   - Test Ship B takes damage from own torpedo blast
   - Test both ships in same blast zone both take damage
   - Test damage amount identical for owner and non-owner
   - Test tactical scenario: close-range launch with escape
   - Test tactical scenario: close-range launch with self-damage
   - Test self-damage events recorded correctly
   - Test multiple own torpedoes (damage stacks)

4. **Update LLM Prompts**:
   - Add self-damage warning to system prompt
   - Document tactical risk of close-range torpedoes
   - Add escape planning guidance

**Deliverables:**
- Created: `tests/test_self_damage.py` (~9-10 tests)
- Modified: `ai_arena/llm_adapter/adapter.py` (if prompts need updating)

**Expected Test Count:** ~248 tests (238 baseline + 10 new)

---

## Story 035: Blast Zone Integration & Balance

**Goal:** Complete Epic 005 with full integration, LLM prompt updates, balance tuning, and production readiness validation

**Read the full story:** [`docs/stories/story-035-integration-balance.md`](stories/story-035-integration-balance.md)

**Key Implementation Points:**

1. **LLM Adapter Updates** (`ai_arena/llm_adapter/adapter.py`):
   - Update system prompt with complete blast zone documentation
   - Add timed detonation examples (immediate, delayed, trap)
   - Add self-damage warning prominently
   - Update observation format to include blast zone information
   - Show blast zone data: position, phase, radius, age, damage rate, distance from player

2. **Replay System Validation** (`ai_arena/replay/recorder.py`):
   - Verify blast zones are serialized correctly (already done in Story 029)
   - Test replay system includes all blast zone data
   - Validate backward compatibility with old replays

3. **Integration Tests** (`tests/test_blast_zone_integration.py`):
   - Test full match with blast zone tactics
   - Test deterministic replay with blast zones
   - Test performance with 10+ active blast zones
   - Test LLM can issue timed detonation commands
   - Test overlapping blast zones damage ships correctly

4. **Balance Testing**:
   - Run at least 3 test matches with MockLLM strategies
   - Analyze match duration, damage stats, blast zone effectiveness
   - Verify blast zones add tactical depth without being overpowered
   - Document findings in balance analysis document

5. **Documentation Updates**:
   - Update `CLAUDE.md` with blast zone system
   - Update `docs/architecture.md` with BlastZone mechanics
   - Create `docs/epic-005-balance-analysis.md` with balance findings

**Deliverables:**
- Modified: `ai_arena/llm_adapter/adapter.py` (enhanced prompts)
- Modified: `ai_arena/replay/recorder.py` (if needed)
- Created: `tests/test_blast_zone_integration.py` (~8-10 tests)
- Created: `docs/epic-005-balance-analysis.md` (balance report)
- Modified: `CLAUDE.md` (updated docs)
- Modified: `docs/architecture.md` (updated docs)

**Expected Test Count:** ~256-258 tests (248 baseline + 8-10 new)

---

## Critical Implementation Notes

### Determinism Requirements

**CRITICAL:** Physics must remain 100% deterministic for replay system.

- Use exact floating-point arithmetic (same as Epic 004)
- All damage calculations must be reproducible
- Use config values (don't hardcode 15.0, 1.5, etc.)
- Damage applied as `damage_rate * dt` (not hardcoded 0.1)

### Damage Calculation Formula

From game spec (lines 377-387):

```
Base damage = torpedo.ae_remaining × blast_damage_multiplier (1.5)
Damage per second = base_damage ÷ 15.0
Damage per substep = damage_per_second × dt (0.1s)
```

**Example:**
- Torpedo with 30.0 AE remaining detonates
- Base damage = 30.0 × 1.5 = 45.0
- Damage per second = 45.0 ÷ 15.0 = 3.0
- Damage per substep = 3.0 × 0.1 = 0.3
- Ship in zone for 5.0 seconds = 50 substeps × 0.3 = 15.0 total damage

### Config Values

From `config.json`:
- `config.torpedo.blast_damage_multiplier` = 1.5
- `config.torpedo.blast_radius_units` = 15.0
- All other blast zone timing values from Stories 029-032

Never hardcode these values - always use config.

### Self-Damage Implementation

**Key insight:** Self-damage should work automatically if `_apply_blast_damage()` does NOT check `zone.owner`. The method should damage ALL ships within the blast radius, regardless of ownership.

```python
# Correct implementation (enables self-damage):
for ship_id, ship in [("ship_a", state.ship_a), ("ship_b", state.ship_b)]:
    if distance < zone.current_radius:
        ship.shields -= damage_this_substep  # No ownership check!

# Wrong implementation (disables self-damage):
if distance < zone.current_radius and zone.owner != ship_id:  # DON'T DO THIS
    ship.shields -= damage_this_substep
```

---

## Sprint Success Criteria

**The sprint is DONE when:**

- [ ] All 3 stories (033-035) implemented and tested
- [ ] Full test suite passes (~256-258 tests expected)
- [ ] Ships take damage from blast zones (continuous per substep)
- [ ] Self-damage validated and working (ships hurt by own torpedoes)
- [ ] LLM prompts updated with complete blast zone documentation
- [ ] Replay system includes blast zones
- [ ] At least 3 balance test matches run and analyzed
- [ ] Balance analysis document created
- [ ] Documentation updated (CLAUDE.md, architecture.md)
- [ ] All 3 story Dev Agent Records completed
- [ ] No regressions in existing tests
- [ ] Determinism validated
- [ ] Epic 005 complete and production-ready

**Expected test count progression:**
- After Story 033: ~238 tests (226 baseline + 12 blast damage tests)
- After Story 034: ~248 tests (+10 self-damage tests)
- After Story 035: ~256-258 tests (+8-10 integration tests)

---

## What's NOT in This Sprint

**Future Epics (Post-Epic 005):**
- Epic 006: Frontend Polish & Thinking Tokens Visualization
- Epic 007: Tournament & Match Infrastructure
- Epic 008: Live Match Streaming (WebSocket)

**Rationale:** This sprint completes Epic 005. Future epics focus on visualization, scaling, and streaming.

---

## Getting Started

### Pre-Sprint Checklist

1. [ ] Verify Stories 029-032 are complete and merged (all PASSED QA)
2. [ ] Run baseline test: `pytest tests/ -v` (expect 226 passing)
3. [ ] Review `docs/game_spec_revised.md` lines 377-415 (blast damage mechanics)
4. [ ] Review `docs/epic-005-torpedo-blast-zones.md`
5. [ ] Review Story 032a retrospective for E2E UI validation requirements
6. [ ] Ensure on branch: `claude/plan-next-sprint-01RYmYuSJaW8s9AbnTCaxVk6`

### Story Implementation Order

1. **Story 033** (2-3 hours): Implement continuous blast damage
2. **Story 034** (1 hour): Validate self-damage works
3. **Story 035** (3-4 hours): Full integration, balance, documentation

**Total estimated time:** 6-7 hours

---

## Key References

- **Game Spec:** `docs/game_spec_revised.md` (lines 348-415, blast zones & damage)
- **Epic 005:** `docs/epic-005-torpedo-blast-zones.md`
- **Stories:** `docs/stories/story-033-*.md` through `story-035-*.md`
- **CLAUDE.md:** Project development guide
- **Retrospective:** `docs/stories/story-032a-canvas-bugfix.md` (E2E validation requirements)

---

## Important Notes from Story 032a Retrospective

### E2E UI Validation Requirements

**CRITICAL for Story 035 QA validation:**

When validating frontend visualization features, you MUST:

1. Start both servers:
   ```bash
   python3 main.py &
   cd frontend && npm start &
   ```

2. Open http://localhost:3000 in browser

3. For canvas viewer validation:
   - [ ] Load a replay (via dropdown or test replay buttons)
   - [ ] Verify canvas displays all game elements
   - [ ] Step through multiple turns using slider
   - [ ] Take screenshots showing actual gameplay visualization
   - [ ] Save screenshots to evidence directory

4. Evidence requirements:
   - Screenshots showing canvas with visible game elements
   - NOT just match list or unit test output
   - Minimum: 2-3 screenshots showing different game states

**If the canvas shows a black screen or runtime errors, the story FAILS QA.**

This applies especially to Story 035 where we need to validate blast zone visualization in the frontend.

---

🚀 **Ready to complete Epic 005! Work sequentially, test thoroughly, document completely. This sprint will make the blast zone system production-ready. Good luck!**
