# Story 035: Blast Zone Integration & Balance

**Epic:** [Epic 005: Advanced Torpedo & Blast Zone System](../epic-005-torpedo-blast-zones.md)
**Status:** Not Started
**Size:** Medium-Large (~3-4 hours)
**Priority:** P0

---

## User Story

**As a** game designer
**I want** blast zones fully integrated and balanced
**So that** matches are fun, strategic, and ready for production

## Context

This is the final story of Epic 005. All blast zone mechanics are implemented (Stories 028-034). This story:
- Integrates everything together
- Runs comprehensive tests with real LLM usage
- Tunes blast zone parameters for balance
- Updates documentation and prompts
- Validates production readiness

## Acceptance Criteria

- [ ] All Epic 005 stories (028-034) complete and merged
- [ ] Full test suite passes (unit + integration + e2e)
- [ ] At least 3 full matches with blast zone tactics
- [ ] LLM prompts updated with complete blast zone documentation
- [ ] LLM observation format includes blast zone information
- [ ] Config parameters tuned based on playtesting
- [ ] Replay system correctly records blast zones
- [ ] Frontend can display blast zones (if canvas updated)
- [ ] Documentation updated (CLAUDE.md, architecture.md)
- [ ] Balance analysis document created
- [ ] Determinism validated (byte-identical replays)
- [ ] Performance acceptable (<10% overhead from blast zones)

## Technical Requirements

### LLM Adapter Updates (adapter.py)

**Enhanced system prompt:**
```
**TORPEDOES & BLAST ZONES:**

**Launching:**
- Cost: 20 AE, Max 4 active per ship
- Torpedo speed: 4.0 units/second
- Torpedoes fly straight for first 15 seconds after launch
- Commands: `straight`, `soft_left`, `hard_right`, `soft_right`, `hard_left`

**Timed Detonation:**
- Format: `{"torpedo_id": "ship_a_torp_1", "action": "detonate_after:8.5"}`
- Delay range: 0.0 to 15.0 seconds
- Creates blast zone at detonation point

**Blast Zone Lifecycle (70 seconds total):**
1. **Expansion (5s):** Radius grows from 0→15 units (3 units/s)
   - Ships can still escape during expansion
   - Partial damage if caught on edge

2. **Persistence (60s):** Radius holds at 15 units
   - Lasts ~4 decision intervals
   - Creates area denial / forces movement
   - Multiple zones can overlap

3. **Dissipation (5s):** Radius shrinks from 15→0 units (3 units/s)
   - Final damage window
   - Zone removed at radius=0

**Blast Damage:**
- Damage rate = (Torpedo AE at detonation × 1.5) ÷ 15.0 = damage per second
- Example: 30 AE torpedo → 45 base damage → 3.0 damage/second
- Continuous damage while in zone (every 0.1 seconds)
- Multiple zones stack damage

**⚠️ SELF-DAMAGE WARNING:**
- YOUR torpedoes can damage YOU if you're in the blast
- Plan escape route before detonating
- Close-range torpedo use is HIGH RISK
- Example risk: Launch at 20 units, detonate at 8s, ship moves 24 units
  - If moving away: Safe (24 units > 15 blast radius)
  - If moving toward: SELF-DAMAGE (still within 15 unit blast)

**Tactical Examples:**

*Immediate Detonation (Panic Button):*
`{"torpedo_id": "ship_a_torp_1", "action": "detonate_after:0.1"}`
- Use when enemy closing fast
- Forces enemy evasion
- Risk: You might be in blast too!

*Delayed Trap:*
`{"torpedo_id": "ship_a_torp_1", "action": "detonate_after:10.0"}`
- Detonate when enemy predicted to arrive
- Creates area denial for next turn
- Low self-damage risk if you move away

*Corridor Creation:*
- Launch 2 torpedoes ahead and behind enemy
- Detonate both with different delays
- Forces enemy into predictable path
```

**Observation format with blast zones:**
```python
def _serialize_state_for_prompt(self, state: GameState, ship_id: str) -> str:
    # ... existing state ...

    # Add blast zone information
    if state.blast_zones:
        obs += f"\n**BLAST ZONES:** {len(state.blast_zones)} active\n"
        for zone in state.blast_zones:
            owner_marker = "YOUR" if zone.owner == ship_id else "ENEMY"
            obs += f"  - {zone.id} ({owner_marker}):\n"
            obs += f"    Position: ({zone.position.x:.1f}, {zone.position.y:.1f})\n"
            obs += f"    Phase: {zone.phase.value}, Age: {zone.age:.1f}s\n"
            obs += f"    Radius: {zone.current_radius:.1f} units\n"
            obs += f"    Damage rate: {(zone.base_damage / 15.0):.2f}/second\n"
            distance = your_ship.position.distance_to(zone.position)
            obs += f"    Distance from you: {distance:.1f} units\n"
            if distance < zone.current_radius:
                obs += f"    ⚠️  YOU ARE INSIDE THIS BLAST ZONE!\n"
    else:
        obs += "\n**BLAST ZONES:** None active\n"

    return obs
```

### Replay System Validation

**Verify replay format includes blast zones:**
```python
# In recorder.py - _serialize_state()
def _serialize_state(self, state: GameState) -> dict:
    return {
        "turn": state.turn,
        "ship_a": self._serialize_ship(state.ship_a),
        "ship_b": self._serialize_ship(state.ship_b),
        "torpedoes": [self._serialize_torpedo(t) for t in state.torpedoes],
        "blast_zones": [self._serialize_blast_zone(z) for z in state.blast_zones]  # NEW
    }

def _serialize_blast_zone(self, zone: BlastZone) -> dict:
    return {
        "id": zone.id,
        "position": [zone.position.x, zone.position.y],
        "base_damage": zone.base_damage,
        "phase": zone.phase.value,
        "age": zone.age,
        "current_radius": zone.current_radius,
        "owner": zone.owner
    }
```

### Integration Tests

**Create tests/test_blast_zone_integration.py:**
- Test full torpedo lifecycle with blast zone
- Test match with multiple blast zones active
- Test overlapping blast zones damage ships correctly
- Test self-damage in tactical scenario
- Test blast zones persist across multiple turns
- Test deterministic replay with blast zones
- Test performance with 10+ active blast zones
- Test LLM can issue timed detonation commands
- Test blast zone events in replay JSON

### Balance Testing

**Run 3+ test matches:**

1. **Match 1: Aggressive Torpedo Tactics**
   - MockLLM strategy: torpedo_spam vs aggressive
   - Goal: Validate blast zones don't make torpedoes overpowered
   - Expected: Match duration 15-20 turns, winner not always torpedo user

2. **Match 2: Self-Damage Risk**
   - MockLLM strategy: aggressive vs defensive
   - Force close-range torpedo launches
   - Goal: Validate self-damage creates meaningful risk
   - Expected: See self-damage events in replay

3. **Match 3: Area Denial**
   - MockLLM strategy: focused_sniper vs balanced
   - Use delayed detonations to create zones
   - Goal: Validate blast zones affect movement tactics
   - Expected: Ships navigate around blast zones

**Balance parameters to consider:**
- blast_damage_multiplier (currently 1.5)
- blast_radius_units (currently 15.0)
- blast_persistence_seconds (currently 60.0)
- Adjust if matches show imbalance

### Documentation Updates

**Update CLAUDE.md:**
- Document blast zone system in "Key Design Patterns"
- Add timed detonation to command examples
- Update testing section with blast zone scenarios

**Update architecture.md:**
- Document BlastZone data model
- Add blast zone lifecycle to physics description
- Update continuous physics section

**Create docs/epic-005-balance-analysis.md:**
- Match results and statistics
- Balance assessment
- Parameter tuning decisions
- Recommendations for future

## Deliverables

- [ ] `ai_arena/llm_adapter/adapter.py` - Enhanced prompts and observations
- [ ] `ai_arena/replay/recorder.py` - Blast zone serialization
- [ ] `tests/test_blast_zone_integration.py` - Integration tests (~8-10 tests)
- [ ] `docs/epic-005-balance-analysis.md` - Balance analysis document
- [ ] `CLAUDE.md` - Updated with blast zone documentation
- [ ] `docs/architecture.md` - Updated with blast zone system
- [ ] 3+ test match replays demonstrating blast zones

## Definition of Done

- [ ] All Epic 005 stories complete and passing
- [ ] Full test suite passes (150+ tests expected)
- [ ] 3+ matches run with blast zone tactics
- [ ] Balance analysis complete, parameters tuned
- [ ] LLM prompts and observations updated
- [ ] Replay system includes blast zones
- [ ] Documentation updated completely
- [ ] Determinism validated
- [ ] Performance acceptable
- [ ] Epic 005 ready for production

## Files to Create/Modify

**Create:**
- `tests/test_blast_zone_integration.py`
- `docs/epic-005-balance-analysis.md`

**Modify:**
- `ai_arena/llm_adapter/adapter.py`
- `ai_arena/replay/recorder.py`
- `CLAUDE.md`
- `docs/architecture.md`

## Dependencies

- Stories 028-034: All blast zone implementation stories

---

## Dev Agent Record

**Implementation Date:** [Fill in date]
**Agent:** [Fill in agent name]
**Status:** [Fill in status: Ready for QA / Blocked / In Progress]

### Instructions for Dev Agent

[When implementing this story:

1. **Verify all dependencies complete:**
   - Stories 028-034 all merged and passing
   - Run full test suite to confirm baseline

2. **Update LLM adapter:**
   - Add comprehensive blast zone documentation to system prompt
   - Update observation format to include blast zone info
   - Add tactical examples for timed detonation

3. **Update replay system:**
   - Add blast zone serialization to recorder.py
   - Test that replays include blast_zones in state
   - Verify backward compatibility with old replays

4. **Create integration tests:**
   - Full match with blast zones
   - Deterministic replay verification
   - Performance testing (10+ zones)

5. **Run balance test matches:**
   - Use MockLLM with different strategies
   - Record match results (duration, winner, damage stats)
   - Analyze if blast zones are balanced

6. **Create balance analysis document:**
   - Document match results
   - Assess balance (too strong? too weak?)
   - Recommend parameter changes if needed
   - Justify keeping current params if balanced

7. **Update documentation:**
   - CLAUDE.md: Add blast zone system
   - architecture.md: Document BlastZone mechanics

8. **Final validation:**
   - Run full test suite (all 150+ tests)
   - Check determinism (same match 10 times)
   - Verify no performance degradation

9. **Update this Dev Agent Record** with comprehensive summary]

### Summary

[Fill in comprehensive summary of Epic 005 completion]

### Work Completed

- [ ] [List all integration tasks completed]

### Test Results

[Fill in full test suite results and balance test results]

### Balance Analysis

[Fill in key findings from balance testing]

### Issues Encountered

[Fill in any issues or decisions made during integration]

### Performance Metrics

[Fill in performance data - test execution time, match simulation time]

---

## QA Agent Record

**Validation Date:** [Fill in date when validating]
**Validator:** [Fill in validator name]
**Verdict:** [Fill in: PASSED / FAILED / NEEDS REVISION]

### Instructions for QA Agent

[When validating this story:

1. **Comprehensive test suite validation:**
   - Run `pytest tests/ -v` and verify all tests pass
   - Expected: 150+ tests (Epic 004: 149 + Epic 005: ~50 new)
   - Check coverage report for blast zone code

2. **Balance test validation:**
   - Review 3+ balance test match replays
   - Verify blast zones appear in replays
   - Check match durations reasonable (15-20 turns)
   - Confirm self-damage events present

3. **Code review:**
   - [ ] LLM prompts comprehensive and clear
   - [ ] Observation format includes all blast zone data
   - [ ] Replay serialization includes blast_zones
   - [ ] Backward compatibility maintained
   - [ ] Type hints correct throughout

4. **Documentation review:**
   - [ ] CLAUDE.md updated with blast zone system
   - [ ] architecture.md documents BlastZone mechanics
   - [ ] Balance analysis document complete and thorough
   - [ ] All Epic 005 stories marked complete

5. **Functional validation:**
   - [ ] Run match with real/mock LLM issuing timed detonations
   - [ ] Verify blast zones visible in replay
   - [ ] Check observation shows blast zone warnings
   - [ ] Validate self-damage occurs in close-range scenarios

6. **Determinism check:**
   - [ ] Run same match 10 times
   - [ ] Compare replays byte-by-byte
   - [ ] Verify identical blast zone ages, radii, phases

7. **Performance validation:**
   - [ ] Test suite completes in reasonable time (<5 seconds)
   - [ ] Match simulation with 10+ blast zones performs well
   - [ ] No memory leaks (zones properly removed)

8. **Balance assessment:**
   - [ ] Review balance analysis document
   - [ ] Verify parameter recommendations justified
   - [ ] Check if blast zones feel balanced in matches

9. **Production readiness:**
   - [ ] All acceptance criteria met
   - [ ] No critical bugs found
   - [ ] Documentation complete
   - [ ] Epic 005 ready for merge

10. **Update this QA Agent Record** with complete findings]

### Test Summary

[Fill in comprehensive test results]

### Balance Assessment

[Fill in QA perspective on balance]

### Issues Found

[Fill in any issues discovered]

### Recommendations

[Fill in recommendations for next steps or improvements]

### Production Readiness Decision

[Fill in: APPROVED FOR PRODUCTION / NEEDS WORK - with justification]

---

**Story Status:** [Update when complete]
