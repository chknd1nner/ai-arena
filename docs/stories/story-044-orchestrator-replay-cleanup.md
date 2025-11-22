# Story 044: Match Orchestrator & Replay Cleanup

**Epic:** 007 - Technical Debt Reduction & Code Quality
**Phase:** 2 - Component Polish
**Priority:** P1
**Estimated Effort:** 0.5 days
**Status:** Complete

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

**Story 044 Implementation Ready** ✨
