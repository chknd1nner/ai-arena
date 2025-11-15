# Story 025: Continuous Physics Testing & Validation

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Not Started
**Size:** Medium (~2-2.5 hours)
**Priority:** P0

---

## User Story

**As a** game engine developer
**I want** comprehensive tests validating continuous physics
**So that** I can trust the physics engine is deterministic and correct

## Context

Stories 020-024 implemented continuous physics incrementally. This story adds integration tests to validate everything works together correctly, including determinism validation (critical for replays).

## Acceptance Criteria

- [ ] Full match with continuous physics runs successfully
- [ ] Determinism validated: same inputs produce byte-identical replays
- [ ] Energy economy tests pass (net drain/gain calculations correct)
- [ ] Phaser cooldown works correctly in full match
- [ ] No NaN, infinity, or out-of-bounds values
- [ ] All existing regression tests still pass
- [ ] Performance regression test (should be < 5% slower)

## Technical Requirements

### Integration Tests

**File:** `tests/test_continuous_physics_integration.py` (new)

```python
def test_full_match_with_continuous_physics():
    """Run complete match with continuous physics."""
    # Run 10-turn match
    # Verify:
    # - Match completes without errors
    # - AE values stay in valid range [0, 100]
    # - Phaser cooldowns work
    # - Ships move correctly
    # - Replay saves correctly
    pass

def test_determinism_continuous_physics():
    """Verify continuous physics is deterministic."""
    # Run same match 10 times
    # Compare replay JSONs byte-for-byte
    # Must be identical
    pass

def test_energy_economy_accuracy():
    """Verify continuous energy economy is accurate."""
    # Test scenarios:
    # 1. FORWARD + NONE = 0 net AE (energy neutral)
    # 2. PERPENDICULAR + HARD = -0.67 AE/s net (drains)
    # 3. STOP + NONE = +0.33 AE/s net (recharges)
    pass

def test_phaser_cooldown_full_match():
    """Verify phaser cooldown works in full match."""
    # Track phaser firings over multiple turns
    # Verify cooldown prevents spam
    # Verify ~4 shots per 15s turn possible
    pass
```

### Performance Regression Test

```python
def test_continuous_physics_performance():
    """Verify continuous physics doesn't degrade performance significantly."""
    import time

    # Run 100-turn match
    start = time.time()
    run_match(turns=100)
    duration = time.time() - start

    # Should complete in reasonable time
    # (Baseline: ~X seconds, continuous: < 1.05X seconds)
    assert duration < BASELINE_DURATION * 1.05
```

## Definition of Done

- [ ] All integration tests passing
- [ ] Determinism validated
- [ ] Performance acceptable
- [ ] No regressions in existing tests

## Files Changed

- Create: `tests/test_continuous_physics_integration.py`

## Dependencies

- Stories 020-024: All continuous physics implementation

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
