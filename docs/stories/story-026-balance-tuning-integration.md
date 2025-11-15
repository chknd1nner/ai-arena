# Story 026: Balance Tuning & Integration Testing

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Not Started
**Size:** Small-Medium (~1.5-2 hours)
**Priority:** P1

---

## User Story

**As a** game designer
**I want** to tune phaser cooldown and energy costs based on playtesting
**So that** the game remains balanced with continuous physics

## Context

Continuous physics changes game balance significantly:
- Phasers can now fire ~4 times per turn (vs 1 time previously)
- Energy economy is more granular
- Need to validate balance and tune parameters

This is the final story of Epic 004 - the "polish and tune" phase.

## Acceptance Criteria

- [ ] Run at least 3 full LLM vs LLM matches
- [ ] Analyze match outcomes and energy patterns
- [ ] Tune phaser cooldown if needed (adjust config.json)
- [ ] Document balance changes and rationale
- [ ] Verify tuned parameters feel balanced
- [ ] Update game documentation with new mechanics

## Technical Requirements

### Playtesting Protocol

1. **Run baseline matches:**
   - 3 matches: Claude vs Claude
   - 3 matches: GPT-4 vs GPT-4
   - 3 matches: Claude vs GPT-4

2. **Analyze metrics:**
   - Total phaser shots per match
   - Average AE over time
   - Win rates
   - Match duration

3. **Identify issues:**
   - Are phasers too strong? (too many shots?)
   - Are phasers too weak? (cooldown too long?)
   - Is energy economy broken? (ships always depleted or always full?)

4. **Tune parameters:**
   - Adjust `cooldown_seconds` in config.json
   - Adjust AE rates if needed
   - Re-test with new values

### Balance Tuning Options

**If phasers too strong:**
- Increase cooldown: 3.5s → 5.0s or 7.5s
- Reduce damage: 35 → 30 (focused), 15 → 12 (wide)

**If phasers too weak:**
- Decrease cooldown: 3.5s → 2.5s
- Increase damage slightly

**If energy economy broken:**
- Adjust AE rates in config.json
- Increase/decrease regeneration rate

## Deliverables

- [ ] Balance analysis document (`docs/epic-004-balance-analysis.md`)
- [ ] Updated config.json with tuned parameters
- [ ] Updated architecture.md with continuous physics description

## Definition of Done

- [ ] At least 9 matches completed
- [ ] Balance analysis documented
- [ ] Parameters tuned (if needed)
- [ ] Game feels balanced and fun
- [ ] Documentation updated

## Files Changed

- Modify: `config.json` (potentially)
- Create: `docs/epic-004-balance-analysis.md`
- Modify: `docs/architecture.md` (document continuous physics)

## Dependencies

- Story 025: Integration testing complete

---

## Dev Agent Record

**Implementation Date:** [To be filled in by Dev Agent]
**Agent:** [To be filled in by Dev Agent]
**Status:** [To be filled in by Dev Agent]

---

## QA Agent Record

**Validation Date:** [To be filled in by QA Agent]
**Validator:** [To be filled in by QA Agent]
**Verdict:** [To be filled in by QA Agent]

---

**Story Status:** Ready for Development
