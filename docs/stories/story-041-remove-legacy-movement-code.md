# Story 041: Remove Legacy Movement Code

**Epic:** [Epic 007: Technical Debt Reduction & Code Quality](../epic-007-technical-debt-reduction.md)
**Status:** ⏸️ Not Started
**Size:** Medium (~1.5 days)
**Priority:** P0

---

## Dev Agent Record

**Implementation Date:** _Pending_
**Agent:** _TBD_
**Status:** ⏸️ Not Started

### Instructions for Dev Agent

When implementing this story:

1. **Audit all legacy references** to `MovementType` enum across the codebase
2. **Migrate torpedo movement system** to use simple string commands
3. **Delete legacy code** (`MovementType` enum, `movement_costs` dict, `movement_params` dict)
4. **Run all tests** to ensure no regressions
5. **Verify replay compatibility** - old replays should still load correctly

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of work completed
- Any design decisions made
- File paths for all created/modified files
- Any issues encountered and resolutions
- Code references (file:line format)

---

## QA Agent Record

**Validation Date:** _Pending_
**Validator:** _TBD_
**Verdict:** ⏸️ Awaiting Implementation

### QA Checklist

- [ ] `MovementType` enum deleted from `data_models.py`
- [ ] `movement_costs` dict removed from `physics.py`
- [ ] `movement_params` dict removed or simplified
- [ ] Torpedoes use simple string commands (`"STRAIGHT"`, `"HARD_LEFT"`, etc.)
- [ ] All physics tests pass (`pytest tests/test_physics.py -v`)
- [ ] Full match runs successfully (`python3 main.py`)
- [ ] No grep results for `MovementType` (except git history)
- [ ] Replay compatibility verified (old replays still load)

**After validation, update this section with:**
- QA date and validator name
- Test results for each criterion
- Any bugs found and their resolution
- Final verdict (Pass/Fail with justification)

---

## User Story

**As a** developer working on AI-Arena
**I want** to remove the deprecated `MovementType` enum and legacy movement system
**So that** the codebase has a single, clear movement paradigm without confusion

### Context

Currently, two movement systems coexist in the codebase:

1. **New System** (Epic 002): `MovementDirection` + `RotationCommand` (independent movement/rotation)
2. **Old System** (Legacy): `MovementType` enum with coupled movement (e.g., `SOFT_LEFT`)

This creates confusion:
- Ships use the new system
- Torpedoes still reference the old system
- Legacy dicts (`movement_costs`, `movement_params`) still exist "for backward compatibility"
- Developers don't know which system to use

### Goal

Eliminate all references to `MovementType` and consolidate on a single movement paradigm.

---

## Acceptance Criteria

### Must Have:

- [ ] `MovementType` enum deleted from `ai_arena/game_engine/data_models.py`
- [ ] `movement_costs` dict removed from `ai_arena/game_engine/physics.py`
- [ ] Torpedoes use simple string commands instead of `MovementType` enum
- [ ] All existing tests pass (no regressions)
- [ ] Full match runs successfully from start to finish
- [ ] Old replays still load and play correctly

### Should Have:

- [ ] Comprehensive grep audit shows no `MovementType` references
- [ ] Code comments updated to remove references to old system
- [ ] Torpedo movement simplified and well-documented

### Nice to Have:

- [ ] Unit tests added for torpedo command parsing
- [ ] Documentation updated to reflect single movement system

---

## Technical Specification

### Current State Analysis

**Legacy Code Locations:**

1. **`ai_arena/game_engine/data_models.py`:**
   - `MovementType` enum definition (deprecated)
   - `MovementDirection` enum definition (current)
   - `RotationCommand` enum definition (current)

2. **`ai_arena/game_engine/physics.py`:**
   - Lines 73-83: `movement_costs` dict (legacy, marked "for backward compatibility")
   - Lines 86-97: `movement_params` dict (used by torpedoes)
   - Torpedo physics methods reference old movement system

3. **`ai_arena/llm_adapter/adapter.py`:**
   - May have references to old movement types

4. **`ai_arena/replay/recorder.py`:**
   - Serialization may reference `MovementType`

### Proposed Solution

**Option A: Convert Torpedoes to New System** (Complex)
- Torpedoes get `MovementDirection` + `RotationCommand`
- Full parity with ship movement system
- More complex prompt engineering for LLMs

**Option B: Simplify Torpedo Commands** (Recommended)
- Torpedoes use simple string commands: `"STRAIGHT"`, `"HARD_LEFT"`, `"HARD_RIGHT"`, `"SOFT_LEFT"`, `"SOFT_RIGHT"`
- No enum needed - just parse strings directly
- Simpler for LLMs to understand
- Torpedoes don't need full movement independence

**Recommendation:** Option B - Keep torpedo movement simple with string commands.

### Implementation Steps

1. **Audit Legacy References** (0.5 days)
   ```bash
   # Find all MovementType references
   grep -r "MovementType" ai_arena/
   grep -r "movement_costs" ai_arena/
   grep -r "movement_params" ai_arena/
   ```

2. **Migrate Torpedo Movement** (0.5 days)
   - Update `_update_torpedo_physics()` in `physics.py`
   - Parse torpedo commands as strings: `"STRAIGHT"`, `"HARD_LEFT"`, etc.
   - Remove `MovementType` enum parsing
   - Keep rotation logic simple (fixed angles)

3. **Delete Legacy Code** (0.5 days)
   - Delete `MovementType` enum from `data_models.py`
   - Delete `movement_costs` dict from `physics.py` (lines 73-83)
   - Simplify `movement_params` to use string keys instead of enum
   - Update any references in `adapter.py` or `recorder.py`

4. **Test & Validate** (included in above)
   - Run `pytest tests/test_physics.py -v`
   - Run full match: `python3 main.py`
   - Load old replay: verify it still works
   - Grep audit: `grep -r "MovementType" ai_arena/` should return nothing

---

## Implementation Guidance

### Torpedo Command Parsing

**Before:**
```python
# Old system - uses MovementType enum
movement = MovementType[action_type.upper()]
rotation_per_dt = self.movement_params.get(movement, {"rotation": 0})["rotation"]
```

**After:**
```python
# New system - simple string parsing
TORPEDO_ROTATION_ANGLES = {
    "STRAIGHT": 0,
    "SOFT_LEFT": np.radians(15),
    "SOFT_RIGHT": -np.radians(15),
    "HARD_LEFT": np.radians(45),
    "HARD_RIGHT": -np.radians(45),
}

rotation_angle = TORPEDO_ROTATION_ANGLES.get(action_str.upper(), 0)
rotation_per_dt = rotation_angle * dt / self.action_phase_duration
```

### State Copying

No changes needed - `_copy_state()` already handles current data models correctly.

### Replay Compatibility

Old replays may have `MovementType` values serialized. Ensure backward compatibility:

```python
# In recorder.py - handle both old and new formats
def _serialize_orders(self, orders: Orders) -> dict:
    # New format - movement is MovementDirection enum
    return {
        "movement": orders.movement.value,
        "rotation": orders.rotation.value,
        # ...
    }
```

---

## Testing Requirements

### Unit Tests

```python
# tests/test_physics.py

def test_torpedo_string_commands():
    """Test torpedo movement with string commands."""
    engine = PhysicsEngine(config)
    state = create_test_state_with_torpedo()

    # Test STRAIGHT command
    orders_a = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={"ship_a_torpedo_1": "STRAIGHT"}
    )

    new_state, events = engine.resolve_turn(state, orders_a, default_orders_b)

    # Torpedo should maintain heading
    assert new_state.torpedoes[0].heading == state.torpedoes[0].heading

def test_no_movement_type_references():
    """Ensure MovementType enum is deleted."""
    with pytest.raises(ImportError):
        from ai_arena.game_engine.data_models import MovementType
```

### Integration Tests

```bash
# Full match test
python3 main.py
# Should complete successfully

# Replay compatibility test
python3 -c "
from ai_arena.replay.recorder import ReplayLoader
replays = ReplayLoader.list_matches()
for replay in replays[:3]:
    data = ReplayLoader.load(replay['match_id'])
    print(f'✅ {replay[\"match_id\"]} loads successfully')
"
```

### Manual Testing

1. Start a new match with torpedo usage
2. Verify torpedoes respond to commands (`HARD_LEFT`, `STRAIGHT`, etc.)
3. Check no errors in console
4. Load an old replay - verify it plays correctly

---

## Files to Modify

### Delete Code From:

1. **`ai_arena/game_engine/data_models.py`**
   - Delete `MovementType` enum entirely
   - Keep `MovementDirection` and `RotationCommand`

2. **`ai_arena/game_engine/physics.py`**
   - Delete `movement_costs` dict (lines ~73-83)
   - Replace `movement_params` dict with simple `TORPEDO_ROTATION_ANGLES` dict
   - Update `_update_torpedo_physics()` to parse string commands

3. **`ai_arena/llm_adapter/adapter.py`** (if needed)
   - Remove any `MovementType` references
   - Ensure torpedo commands are sent as strings

4. **`ai_arena/replay/recorder.py`** (if needed)
   - Ensure serialization uses `MovementDirection` values

### No New Files:

This story only removes code, no new files created.

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] `MovementType` enum deleted from codebase
- [ ] `grep -r "MovementType" ai_arena/` returns no results (except git history)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Full match runs successfully
- [ ] Old replays still load and play correctly
- [ ] Code reviewed (self-review or peer review)
- [ ] No console errors or warnings during match
- [ ] Documentation updated (if needed)

---

## Dependencies

**Blocks:**
- Story 043: Consolidate Duplicate Code (depends on clean movement system)

**Blocked By:**
- None (can start immediately)

---

## Notes

### Design Decisions

- **Torpedo commands as strings**: Simpler than full enum system, easier for LLMs
- **Keep rotation angles**: Torpedoes still need turning mechanics, just simplified
- **Backward compatibility**: Old replays must still work (don't break replay format)

### Risk Assessment

**Risk:** Medium
**Reason:** Touching core physics code
**Mitigation:** Comprehensive testing, replay compatibility checks

### Future Considerations

After this story, the codebase will have:
- Ships: `MovementDirection` + `RotationCommand` (independent)
- Torpedoes: Simple string commands (coupled, but simple)

This is acceptable - torpedoes don't need the full complexity of independent movement/rotation.
