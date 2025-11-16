# Next Sprint: Story 024 - Phaser Cooldown Enforcement

## Dev Agent Prompt

You are the **Development Agent** for the AI Arena project. Your task is to implement **Story 024: Phaser Cooldown Enforcement** as part of Epic 004 (Continuous Physics System).

### Context

**What's Been Completed:**
- Stories 020-021: Phaser cooldown tracking infrastructure (cooldown field in ShipState, cooldown decrements per substep)
- Stories 022-023: Continuous AE economy (movement, rotation, and regeneration all work per substep)

**Current State:**
- Ships have `phaser_cooldown_remaining` field that decrements every 0.1s substep
- But phasers **are not yet prevented from firing** when cooldown > 0
- Cooldown is **not yet set** after successful phaser fire
- LLMs **cannot see** cooldown status in their observations

### Your Mission: Story 024

Implement phaser cooldown enforcement so that:
1. Phasers can **only fire** when `ship.phaser_cooldown_remaining == 0.0`
2. After successful fire, cooldown is **set to** `config.weapons.phaser.cooldown_seconds` (3.5s)
3. LLMs can **see cooldown status** in their observations
4. System prompt is **updated** to explain cooldown mechanics to LLMs

### Implementation Requirements

**Read the full specification:** `docs/stories/story-024-phaser-cooldown-enforcement.md`

**Key Files to Modify:**

1. **`ai_arena/game_engine/physics.py`**
   - Locate weapon firing logic (likely in phaser hit detection or weapon action processing)
   - Add cooldown check: `if ship.phaser_cooldown_remaining > 0.0: return False`
   - After successful fire: `ship.phaser_cooldown_remaining = config.weapons.phaser.cooldown_seconds`
   - Return True/False to indicate fire success

2. **`ai_arena/llm_adapter/adapter.py`**
   - Add `phaser_cooldown_remaining` to ship observations sent to LLMs
   - Update system prompt to explain cooldown mechanics
   - Make sure LLMs understand they cannot spam phasers

3. **`config.json`**
   - Verify `weapons.phaser.cooldown_seconds` exists (should be 3.5)
   - If missing, add it

4. **`tests/test_continuous_physics.py`**
   - Add test: `test_phaser_respects_cooldown()` - verify phaser won't fire during cooldown
   - Add test: `test_phaser_fires_when_ready()` - verify phaser fires when cooldown = 0
   - Add test: `test_cooldown_set_after_firing()` - verify cooldown set to 3.5s after fire

### Acceptance Criteria

Your implementation must satisfy ALL of these:
- [ ] Phaser fire only allowed when `ship.phaser_cooldown_remaining == 0.0`
- [ ] After successful fire, cooldown set to `config.weapons.phaser.cooldown_seconds`
- [ ] Weapon action still processed (reconfiguration, etc.), just firing prevented during cooldown
- [ ] LLM observations include `phaser_cooldown_remaining` field
- [ ] LLM system prompt explains cooldown mechanics
- [ ] Tests verify cooldown prevents rapid firing
- [ ] All existing tests still pass (no regressions)
- [ ] At least one test demonstrates cooldown working in multi-turn scenario

### Testing Strategy

1. **Unit Tests**: Add 3-4 targeted tests in `test_continuous_physics.py`
2. **Integration Test**: Run at least one short match (5-10 turns) and verify:
   - Phasers fire when cooldown = 0
   - Phasers blocked when cooldown > 0
   - Cooldown correctly set after each fire
3. **Regression Test**: Run full test suite with `pytest` - all must pass

### Implementation Checklist

Work through these steps systematically:
1. [ ] Read Story 024 specification thoroughly
2. [ ] Understand current phaser firing logic in `physics.py`
3. [ ] Implement cooldown check before firing
4. [ ] Implement cooldown setting after firing
5. [ ] Add cooldown to LLM observations in `adapter.py`
6. [ ] Update LLM system prompt with cooldown explanation
7. [ ] Write 3-4 unit tests for cooldown enforcement
8. [ ] Run `pytest` to ensure all tests pass
9. [ ] Run a short test match to verify behavior
10. [ ] Fill in Dev Agent Record section in Story 024 with your findings

### Dev Agent Record Template

When complete, update `docs/stories/story-024-phaser-cooldown-enforcement.md` with:

```markdown
## Dev Agent Record

**Implementation Date:** [Today's date]
**Agent:** Claude Dev Agent
**Status:** Completed - Ready for QA

### Implementation Summary
[Brief description of what you implemented and approach taken]

### Files Created
[List any new files]

### Files Modified
[List files modified with brief description]

### Testing Notes
[Test results, any edge cases discovered]

### Technical Notes
[Important implementation details, gotchas, notes for future developers]

### Known Issues / Future Work
[Any issues discovered or follow-up work needed]
```

### Success Criteria

Your implementation is complete when:
- ✅ All acceptance criteria met
- ✅ All tests passing (run `pytest`)
- ✅ Dev Agent Record section filled in Story 024
- ✅ Code committed with clear commit message
- ✅ Ready for QA Agent review

### Important Notes

1. **Read the game spec**: Phaser cooldown should enable ~4 shots per 15s turn (not 1 per turn)
2. **Maintain determinism**: Fixed timestep, predictable behavior
3. **Don't break existing features**: All 131 tests must still pass
4. **Follow existing patterns**: Mirror the approach from Stories 021-023

### Questions to Consider

- Where exactly does phaser firing happen in the current code?
- Is there a separate function for weapon actions, or is it inline?
- How do we handle phaser reconfiguration vs firing?
- Should cooldown apply to both WIDE and FOCUSED phasers equally?

**Begin Implementation Now**

Start by reading the current phaser firing logic in `ai_arena/game_engine/physics.py`. Look for functions related to weapon actions, phaser hits, or combat resolution. Then proceed with the implementation following the checklist above.

Good luck! 🚀
