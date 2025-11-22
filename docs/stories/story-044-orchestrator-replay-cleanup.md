# Story 044: Match Orchestrator & Replay Cleanup

**Epic:** 007 - Technical Debt Reduction & Code Quality
**Phase:** 2 - Component Polish
**Priority:** P1
**Estimated Effort:** 0.5 days
**Status:** QA Passed

---

## User Story

As a developer, I want the replay system to correctly serialize all torpedo state fields, so that replays accurately preserve timed detonation data and can be reliably reconstructed.

---

## Problem Statement

During Epic 007 Phase 1, we consolidated duplicate code and externalized prompts. However, the replay serialization in `recorder.py` is missing the `detonation_timer` field when serializing `TorpedoState` objects. This means:

1. Replays don't preserve timed detonation information
2. Replays can't accurately reconstruct torpedo behavior involving timed detonations
3. The serialization is incomplete and doesn't match the full `TorpedoState` dataclass

### Current Issue

**`TorpedoState` dataclass** (in `data_models.py`):
```python
@dataclass
class TorpedoState:
    id: str
    position: Vec2D
    velocity: Vec2D
    heading: float
    ae_remaining: int
    owner: str
    just_launched: bool = False
    detonation_timer: Optional[float] = None  # ← Missing in serialization
```

**Current serialization** (in `recorder.py`):
```python
def _serialize_torpedo(self, torpedo: TorpedoState) -> dict:
    return {
        "id": torpedo.id,
        "position": [torpedo.position.x, torpedo.position.y],
        "velocity": [torpedo.velocity.x, torpedo.velocity.y],
        "heading": torpedo.heading,
        "ae_remaining": torpedo.ae_remaining,
        "owner": torpedo.owner,
        "just_launched": torpedo.just_launched
        # ← detonation_timer is MISSING
    }
```

---

## Acceptance Criteria

- [x] `_serialize_torpedo()` includes `detonation_timer` field
- [x] Test added for torpedo serialization with detonation timer
- [x] All existing tests continue to pass
- [x] Replays with timed detonations serialize correctly
- [x] Documentation updated

---

## Implementation Details

### Changes Required

#### 1. Fix Torpedo Serialization

**File:** `ai_arena/replay/recorder.py`

Update `_serialize_torpedo()` method to include `detonation_timer`:

```python
def _serialize_torpedo(self, torpedo: TorpedoState) -> dict:
    return {
        "id": torpedo.id,
        "position": [torpedo.position.x, torpedo.position.y],
        "velocity": [torpedo.velocity.x, torpedo.velocity.y],
        "heading": torpedo.heading,
        "ae_remaining": torpedo.ae_remaining,
        "owner": torpedo.owner,
        "just_launched": torpedo.just_launched,
        "detonation_timer": torpedo.detonation_timer  # ← Add this field
    }
```

#### 2. Add Test Coverage

**File:** `tests/test_replay_serialization.py` (new file)

Add tests to verify:
- Torpedo without detonation timer serializes correctly (None)
- Torpedo with detonation timer serializes the timer value
- Full replay serialization includes torpedo detonation timers
- Deserialization handles both presence and absence of timer field

---

## Testing Strategy

### Unit Tests

```bash
# Run new replay serialization tests
python3 -m pytest tests/test_replay_serialization.py -v

# Run all replay-related tests
python3 -m pytest tests/ -k "replay or recorder" -v
```

### Integration Test

```bash
# Run a full match with timed detonations
python3 main.py
# Verify the replay file includes detonation_timer fields
```

### Verification Steps

1. Create a match with torpedo timed detonations
2. Check the generated replay JSON file
3. Verify `detonation_timer` field is present in torpedo objects
4. Confirm replay loads and plays back correctly

---

## Files Modified

### Backend
- `ai_arena/replay/recorder.py` - Add `detonation_timer` to `_serialize_torpedo()`
- `tests/test_replay_serialization.py` - New test file for replay serialization

### Documentation
- `docs/stories/story-044-orchestrator-replay-cleanup.md` - This file
- `docs/epic-007-technical-debt-reduction.md` - Update status

---

## Dependencies

**Requires:**
- Story 041 ✅ (Remove legacy movement code)
- Story 042 ✅ (Externalize LLM prompts)
- Story 043 ✅ (Consolidate duplicate code)

**Blocks:**
- Story 045 (Frontend CSS modules) - Independent, can proceed in parallel
- Story 046 (Canvas refactor) - Independent, can proceed in parallel

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing replays | Low | Field is optional, old replays without it still work |
| Deserialization issues | Low | Use `.get("detonation_timer")` when loading replays |
| Test coverage gaps | Medium | Add comprehensive serialization tests |

---

## Verification Checklist

Before marking complete:

- [x] `detonation_timer` added to `_serialize_torpedo()`
- [x] New test file created with serialization tests
- [x] All 278 tests pass (270 existing + 8 new)
- [x] Manual replay verification with timed detonations
- [x] Documentation updated

---

## Notes

**Why This Matters:**

This is a **bug fix** rather than a feature. The timed detonation feature (Epic 005) was implemented, but the replay serialization wasn't updated to include the new field. This story ensures data integrity and replay accuracy.

**Post-Story State:**

After this story, all `TorpedoState` fields will be properly serialized in replays, ensuring complete and accurate replay data for all match scenarios.

---

## QA Agent Record

**QA Date:** 2025-11-22
**QA Agent:** Senior QA Developer
**Branch:** claude/epic-007-phase-2-0151aVQ9Ns3GpnQrMXpmmaTp
**Status:** ✅ QA PASSED

### Test Results

#### Unit Tests
- **Test File:** `tests/test_replay_serialization.py`
- **Tests Added:** 8 new tests
- **Total Tests:** 278 (all passing)
- **Coverage:**
  - Torpedo serialization with/without timer ✅
  - Game state serialization with torpedo timers ✅
  - Full replay serialization ✅
  - Backward compatibility ✅

#### Code Review
- **File Modified:** `ai_arena/replay/recorder.py:104`
- **Change:** Added `"detonation_timer": torpedo.detonation_timer` to `_serialize_torpedo()` method
- **Implementation:** ✅ Correct - field properly added to serialization
- **Code Quality:** ✅ Clean, follows existing patterns

#### Replay Data Verification
- **Replays Checked:** 100 replay files
- **Replays with Torpedoes:** 1 (gpt-4_vs_claude-3-h_20251122_051142.json)
- **Detonation Timer Field Present:** ✅ Verified
- **Sample Value:** `detonation_timer: 4.2`
- **JSON Serialization:** ✅ Valid

#### Visual Testing (webapp-testing skill)
- **Frontend:** http://localhost:3000 ✅ Operational
- **Backend:** http://localhost:8000 ✅ Operational
- **Canvas Rendering:** ✅ Ships, positions, labels displayed correctly
- **Turn Navigation:** ✅ Slider functional, states update correctly
- **Match Summary:** ✅ Winner, turns, models displayed
- **Thinking Panels:** ✅ Split-screen display operational
- **Ship Stats:** ✅ Shields, AE, phaser config visible

### Verification Artifacts

**Screenshots:** `screenshots/story-044/`
- `story-044-match-list.png` - Match selection interface
- `story-044-replay-initial.png` - Initial game state with canvas
- `story-044-replay-midgame.png` - Mid-game visualization
- `story-044-replay-endgame.png` - End-game state with match summary
- `story-044-replay-final.png` - Final state verification

**Test Script:** `test_story_044_visual.py`
- Automated Playwright test
- Replay data verification
- Visual regression testing

### Issues Found

**None** - All acceptance criteria met.

### QA Summary

Story 044 successfully implements the missing `detonation_timer` field in torpedo serialization. The implementation:

1. ✅ Adds the field to `_serialize_torpedo()` method
2. ✅ Includes comprehensive test coverage (8 new tests)
3. ✅ Maintains backward compatibility (None values handled)
4. ✅ Preserves replay accuracy for timed detonations
5. ✅ Does not break any existing functionality (278/278 tests passing)
6. ✅ Frontend visualization unaffected (as expected for backend-only change)

This bug fix ensures complete data integrity in replay files and enables accurate reconstruction of torpedo behavior involving timed detonations.

**Recommendation:** ✅ Approve for merge to main

---

**Story 044 Implementation Ready** ✨
