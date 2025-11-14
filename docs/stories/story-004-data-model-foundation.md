# Story 004: Data Model Foundation

**Epic:** [Epic 002: Independent Movement & Rotation System](../epic-002-independent-movement-rotation.md)
**Status:** ✅ COMPLETED - All Tests Passing
**Size:** Small
**Priority:** P0

---

## QA Agent Review

**Reviewed By:** task-completion-validator
**Date:** 2025-11-14
**Verdict:** ✅ APPROVED - Fully Implemented

**Implementation Verified:**
- ✅ `MovementDirection` enum created with 9 directions (data_models.py:50-64)
- ✅ `RotationCommand` enum created with 5 commands (data_models.py:66-76)
- ✅ `Orders.rotation` field added (data_models.py:121)
- ✅ `Orders.movement` type changed to `MovementDirection` (data_models.py:120)
- ✅ `MovementType` kept for backward compatibility with torpedoes (data_models.py:38-48)
- ✅ Comprehensive test file created: tests/test_data_models.py (159 lines, 14 tests)

**Test Results:** 14/14 tests passing
- 3 MovementDirection enum tests ✓
- 3 RotationCommand enum tests ✓
- 6 Orders dataclass tests ✓
- 2 backward compatibility tests ✓

**Quality Assessment:**
- Excellent docstrings explaining independence of movement and rotation
- Clean enum definitions matching specification exactly
- Proper serialization support for replay system

**Code References:**
- ai_arena/game_engine/data_models.py:50-76 - New enums
- ai_arena/game_engine/data_models.py:113-123 - Updated Orders dataclass
- tests/test_data_models.py:1-159 - Comprehensive test coverage

---

## User Story

**As a** game engine developer
**I want** data models that support independent movement and rotation commands
**So that** the physics engine can process decoupled movement/rotation orders

## Context

Currently, the `Orders` dataclass only has a `movement` field that controls both velocity direction and ship rotation. The `MovementType` enum conflates these two concepts (e.g., `HARD_LEFT` means both "move in a leftward arc" and "rotate left 45°").

To implement independent movement and rotation:
1. Movement should control velocity direction relative to current heading
2. Rotation should control heading change independent of velocity
3. Orders must have separate fields for movement and rotation
4. New enums needed: `MovementDirection` and `RotationCommand`

## Acceptance Criteria

- [ ] `MovementDirection` enum created with 9 directions (FORWARD, LEFT, RIGHT, BACKWARD, diagonals, STOP)
- [ ] `RotationCommand` enum created with 5 commands (NONE, SOFT_LEFT, SOFT_RIGHT, HARD_LEFT, HARD_RIGHT)
- [ ] `Orders` dataclass updated with `rotation` field
- [ ] `Orders.movement` field type changed from `MovementType` to `MovementDirection`
- [ ] Old `MovementType` enum deprecated or removed
- [ ] All data model changes are backward compatible with serialization
- [ ] Type hints and docstrings updated

## Technical Details

### Files to Modify

- `ai_arena/game_engine/data_models.py` - Add new enums, update Orders

### Implementation Notes

**1. Create MovementDirection Enum:**

```python
class MovementDirection(Enum):
    """Movement direction relative to current heading.

    Movement sets the velocity direction but does NOT change heading.
    Combine with RotationCommand for independent facing control.
    """
    FORWARD = "FORWARD"               # 0° - Continue straight ahead
    FORWARD_LEFT = "FORWARD_LEFT"     # -45° - Diagonal left-forward
    FORWARD_RIGHT = "FORWARD_RIGHT"   # +45° - Diagonal right-forward
    LEFT = "LEFT"                     # -90° - Perpendicular left
    RIGHT = "RIGHT"                   # +90° - Perpendicular right
    BACKWARD = "BACKWARD"             # 180° - Reverse direction
    BACKWARD_LEFT = "BACKWARD_LEFT"   # -135° - Diagonal left-backward
    BACKWARD_RIGHT = "BACKWARD_RIGHT" # +135° - Diagonal right-backward
    STOP = "STOP"                     # 0 velocity - Coast to halt
```

**2. Create RotationCommand Enum:**

```python
class RotationCommand(Enum):
    """Ship rotation command independent of movement.

    Rotation changes heading but does NOT change velocity direction.
    Phasers always point in heading direction.
    """
    NONE = "NONE"               # 0.0°/s - Maintain current heading
    SOFT_LEFT = "SOFT_LEFT"     # +1.0°/s - Gentle left rotation
    SOFT_RIGHT = "SOFT_RIGHT"   # -1.0°/s - Gentle right rotation
    HARD_LEFT = "HARD_LEFT"     # +3.0°/s - Aggressive left rotation
    HARD_RIGHT = "HARD_RIGHT"   # -3.0°/s - Aggressive right rotation
```

**3. Update Orders Dataclass:**

```python
@dataclass
class Orders:
    """Commands from LLM for one ship.

    Movement and rotation are independent:
    - movement: Sets velocity direction relative to heading
    - rotation: Changes heading independent of velocity
    """
    movement: MovementDirection      # Changed from MovementType
    rotation: RotationCommand        # NEW: Independent rotation
    weapon_action: str
    torpedo_orders: Dict[str, MovementType] = field(default_factory=dict)
```

**4. Deprecate MovementType:**

Option A: Remove entirely (breaking change)
Option B: Keep for torpedo orders, rename to `TorpedoMovement`
Option C: Add deprecation warning

**Recommendation:** Keep `MovementType` for torpedo orders (they use different movement mechanics). Torpedoes still use the old system where movement=rotation.

### Design Decisions

**Why 9 movement directions?**
- Matches game spec (8 cardinals + stop)
- Provides full 360° coverage with 45° increments
- Simple for LLMs to understand and use

**Why 5 rotation commands?**
- Matches game spec exactly
- NONE is critical for independent movement (e.g., strafe without rotating)
- Soft vs Hard provides tactical choice (15° vs 45° per decision interval)

**Why angles are relative to heading, not absolute?**
- More intuitive: "LEFT" means "move perpendicular to where I'm facing"
- Simplifies LLM reasoning: Don't need to calculate absolute bearings
- Matches naval/aviation conventions

**Why keep positive = counterclockwise?**
- Consistent with existing coordinate system (0° = East, +θ = counterclockwise)
- LEFT rotation means +θ (counterclockwise)
- RIGHT rotation means -θ (clockwise)

## Test Requirements

**`tests/test_data_models.py` (new file)**

```python
def test_movement_direction_enum_values():
    """Verify all 9 movement directions exist."""
    assert MovementDirection.FORWARD
    assert MovementDirection.LEFT
    assert MovementDirection.RIGHT
    assert MovementDirection.BACKWARD
    assert MovementDirection.FORWARD_LEFT
    assert MovementDirection.FORWARD_RIGHT
    assert MovementDirection.BACKWARD_LEFT
    assert MovementDirection.BACKWARD_RIGHT
    assert MovementDirection.STOP

def test_rotation_command_enum_values():
    """Verify all 5 rotation commands exist."""
    assert RotationCommand.NONE
    assert RotationCommand.SOFT_LEFT
    assert RotationCommand.SOFT_RIGHT
    assert RotationCommand.HARD_LEFT
    assert RotationCommand.HARD_RIGHT

def test_orders_has_rotation_field():
    """Verify Orders dataclass has rotation field."""
    orders = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )
    assert orders.movement == MovementDirection.FORWARD
    assert orders.rotation == RotationCommand.NONE

def test_orders_serialization():
    """Verify Orders can be serialized to dict."""
    orders = Orders(
        movement=MovementDirection.LEFT,
        rotation=RotationCommand.HARD_RIGHT,
        weapon_action="MAINTAIN_CONFIG"
    )
    # Should be able to convert to dict for replay system
    assert orders.movement.value == "LEFT"
    assert orders.rotation.value == "HARD_RIGHT"
```

## Implementation Checklist

- [ ] Add `MovementDirection` enum with 9 directions
- [ ] Add `RotationCommand` enum with 5 commands
- [ ] Update `Orders` dataclass with `rotation: RotationCommand` field
- [ ] Change `Orders.movement` from `MovementType` to `MovementDirection`
- [ ] Add docstrings explaining independence of movement and rotation
- [ ] Keep `MovementType` enum for torpedo orders (if needed)
- [ ] Write unit tests for new enums
- [ ] Write unit tests for updated Orders
- [ ] Verify serialization works (for replay system)

## Edge Cases to Handle

1. **Default rotation value:** If rotation not specified, default to `RotationCommand.NONE`
2. **Type validation:** Ensure movement is MovementDirection, rotation is RotationCommand
3. **Serialization:** Enum values must serialize to strings for JSON replay
4. **Backward compatibility:** Old replays may use MovementType - handle gracefully

## Performance Considerations

None - this is a pure data model change with no performance impact.

## Definition of Done

- [ ] All acceptance criteria met
- [ ] New enums created with correct values
- [ ] Orders dataclass updated
- [ ] Unit tests written and passing
- [ ] Docstrings explain independent movement/rotation
- [ ] No breaking changes to existing code (yet - physics will change in Story 005)

## Files Changed

- Create: `tests/test_data_models.py`
- Modify: `ai_arena/game_engine/data_models.py`

## Dependencies

- None - This is the foundation story for Epic 002

## Blocks

- Story 005: Movement Direction System (needs MovementDirection enum)
- Story 006: Independent Rotation System (needs RotationCommand enum)

## Notes

**Important:** This story only changes data models. The physics engine will still use the old movement system until Story 005-006. This means:
- New enums exist but aren't used yet
- Tests will fail if they try to create Orders with new types
- This is expected - Stories 005-006 will connect everything

**Testing Strategy:** Write tests for the data models only. Don't test physics integration yet.

**Migration Path:** Consider writing a replay migration script if old replays need to be compatible with new order format.

## Developer Notes

**Why separate movement direction from rotation angle?**

Old system:
```python
HARD_LEFT = 45° rotation AND leftward arc movement
```

New system:
```python
movement=LEFT (perpendicular velocity)
rotation=HARD_LEFT (45° heading change)
```

This separation enables:
- Strafing: `movement=LEFT, rotation=NONE` (move left, face forward)
- Retreat: `movement=BACKWARD, rotation=NONE` (move back, face forward)
- Drift: `movement=LEFT, rotation=SOFT_LEFT` (move left, slowly rotate)

Without this separation, these maneuvers are impossible!
