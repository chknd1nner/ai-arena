# Claude Code Web Implementation Prompt: Epic 002 Phase 1

## Overview

Implement the **physics foundation** for independent movement and rotation in AI Arena. This phase (Stories 004-007) creates the core mechanics WITHOUT requiring LLM integration, making it independently testable and verifiable.

---

## What You'll Implement

### Phase 1 Scope: Stories 004-007 (Physics Layer Only)

1. **Story 004:** Data Model Foundation - New enums and Orders structure
2. **Story 005:** Movement Direction System - Decouple velocity from heading
3. **Story 006:** Independent Rotation System - Separate heading control
4. **Story 007:** Combined AE Cost System - Both movement + rotation costs

**Total Estimated Effort:** 4-6 hours

---

## Why This Phase is Self-Contained

- ✅ **No LLM changes required** - Keep existing adapter as-is
- ✅ **Independently testable** - Physics tests validate everything
- ✅ **Clear success criteria** - Ships move + rotate independently
- ✅ **Backward compatible** - Can run with mock orders for testing
- ✅ **Deterministic** - Same inputs = same outputs (replay validation)

---

## Epic Context

**Read these files for context:**
- `docs/epic-002-independent-movement-rotation.md` - Full epic overview
- `docs/stories/story-004-data-model-foundation.md` - Data models
- `docs/stories/story-005-movement-direction-system.md` - Movement physics
- `docs/stories/story-006-independent-rotation-system.md` - Rotation physics
- `docs/stories/story-007-combined-ae-cost-system.md` - AE costs
- `docs/game_spec_revised.md` (lines 96-197) - Game specification

**Current system:** Movement commands control BOTH velocity and rotation (coupled).

**Target system:** Movement sets velocity direction, rotation sets heading (independent).

---

## Implementation Steps

### Step 1: Data Models (Story 004)

**File:** `ai_arena/game_engine/data_models.py`

**Add two new enums:**

```python
class MovementDirection(Enum):
    """Movement direction relative to current heading."""
    FORWARD = "FORWARD"
    FORWARD_LEFT = "FORWARD_LEFT"
    FORWARD_RIGHT = "FORWARD_RIGHT"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BACKWARD = "BACKWARD"
    BACKWARD_LEFT = "BACKWARD_LEFT"
    BACKWARD_RIGHT = "BACKWARD_RIGHT"
    STOP = "STOP"

class RotationCommand(Enum):
    """Ship rotation command independent of movement."""
    NONE = "NONE"
    SOFT_LEFT = "SOFT_LEFT"
    SOFT_RIGHT = "SOFT_RIGHT"
    HARD_LEFT = "HARD_LEFT"
    HARD_RIGHT = "HARD_RIGHT"
```

**Update Orders dataclass:**

```python
@dataclass
class Orders:
    """Commands from LLM for one ship."""
    movement: MovementDirection      # Changed from MovementType
    rotation: RotationCommand        # NEW: Independent rotation
    weapon_action: str
    torpedo_orders: Dict[str, MovementType] = field(default_factory=dict)
```

**Note:** Keep `MovementType` enum for torpedo orders (they still use old system).

**Tests:** Create `tests/test_data_models.py` with enum value tests and Orders serialization tests.

---

### Step 2: Movement Direction System (Story 005)

**File:** `ai_arena/game_engine/physics.py`

**Add movement direction offsets to PhysicsEngine:**

```python
# Movement direction offsets (relative to current heading)
MOVEMENT_DIRECTION_OFFSETS = {
    MovementDirection.FORWARD: 0.0,              # 0° - Straight ahead
    MovementDirection.FORWARD_LEFT: -np.pi/4,    # -45°
    MovementDirection.FORWARD_RIGHT: np.pi/4,    # +45°
    MovementDirection.LEFT: -np.pi/2,            # -90°
    MovementDirection.RIGHT: np.pi/2,            # +90°
    MovementDirection.BACKWARD: np.pi,           # 180°
    MovementDirection.BACKWARD_LEFT: -3*np.pi/4, # -135°
    MovementDirection.BACKWARD_RIGHT: 3*np.pi/4, # +135°
    MovementDirection.STOP: 0.0,                 # Special case
}
```

**Refactor `_update_ship_physics()` to decouple movement:**

```python
def _update_ship_physics(self, ship: ShipState, orders: Orders, dt: float):
    # Handle STOP as special case
    if orders.movement == MovementDirection.STOP:
        ship.velocity = Vec2D(0, 0)
        return

    # Calculate velocity direction (independent of rotation)
    movement_offset = self.MOVEMENT_DIRECTION_OFFSETS[orders.movement]
    velocity_angle = ship.heading + movement_offset

    # Set velocity based on movement direction
    ship.velocity = Vec2D(
        np.cos(velocity_angle) * self.ship_speed,
        np.sin(velocity_angle) * self.ship_speed
    )

    # Update position
    ship.position = ship.position + (ship.velocity * dt)

    # NOTE: Heading is NOT modified here
    # (Rotation will be added in Story 006)
```

**Update `config.json` movement section:**

```json
"movement": {
  "forward_ae_per_second": 0.33,
  "diagonal_ae_per_second": 0.53,
  "perpendicular_ae_per_second": 0.67,
  "backward_ae_per_second": 0.67,
  "backward_diagonal_ae_per_second": 0.80,
  "stop_ae_per_second": 0.0
}
```

**Add movement AE cost method:**

```python
def _get_movement_ae_cost(self, movement: MovementDirection) -> float:
    """Get AE cost per second for movement direction."""
    cost_map = {
        MovementDirection.FORWARD: self.config.movement.forward_ae_per_second,
        MovementDirection.FORWARD_LEFT: self.config.movement.diagonal_ae_per_second,
        MovementDirection.FORWARD_RIGHT: self.config.movement.diagonal_ae_per_second,
        MovementDirection.LEFT: self.config.movement.perpendicular_ae_per_second,
        MovementDirection.RIGHT: self.config.movement.perpendicular_ae_per_second,
        MovementDirection.BACKWARD: self.config.movement.backward_ae_per_second,
        MovementDirection.BACKWARD_LEFT: self.config.movement.backward_diagonal_ae_per_second,
        MovementDirection.BACKWARD_RIGHT: self.config.movement.backward_diagonal_ae_per_second,
        MovementDirection.STOP: self.config.movement.stop_ae_per_second,
    }
    return cost_map[movement]
```

**Tests:** Update `tests/test_physics.py` with tests for all 9 movement directions verifying heading never changes.

---

### Step 3: Independent Rotation System (Story 006)

**File:** `ai_arena/game_engine/physics.py`

**Add rotation rates to PhysicsEngine:**

```python
def __init__(self, config: GameConfig):
    # ... existing init ...

    # Load rotation rates from config
    self.ROTATION_RATES = {
        RotationCommand.NONE: 0.0,
        RotationCommand.SOFT_LEFT: config.rotation.soft_turn_degrees_per_second,
        RotationCommand.SOFT_RIGHT: -config.rotation.soft_turn_degrees_per_second,
        RotationCommand.HARD_LEFT: config.rotation.hard_turn_degrees_per_second,
        RotationCommand.HARD_RIGHT: -config.rotation.hard_turn_degrees_per_second,
    }
```

**Update `_update_ship_physics()` to add rotation BEFORE movement:**

```python
def _update_ship_physics(self, ship: ShipState, orders: Orders, dt: float):
    # 1. Apply rotation (independent)
    rotation_rate_deg_per_sec = self.ROTATION_RATES[orders.rotation]
    rotation_per_dt_rad = np.radians(rotation_rate_deg_per_sec * dt)
    ship.heading += rotation_per_dt_rad
    ship.heading = ship.heading % (2 * np.pi)  # Wrap to [0, 2π)

    # 2. Apply movement (independent)
    if orders.movement == MovementDirection.STOP:
        ship.velocity = Vec2D(0, 0)
        return

    movement_offset = self.MOVEMENT_DIRECTION_OFFSETS[orders.movement]
    velocity_angle = ship.heading + movement_offset

    ship.velocity = Vec2D(
        np.cos(velocity_angle) * self.ship_speed,
        np.sin(velocity_angle) * self.ship_speed
    )

    # 3. Update position
    ship.position = ship.position + (ship.velocity * dt)
```

**Tests:** Add rotation tests verifying all 5 rotation commands work correctly and heading changes independently of movement.

---

### Step 4: Combined AE Cost System (Story 007)

**File:** `ai_arena/game_engine/physics.py`

**Add rotation AE cost method:**

```python
def _get_rotation_ae_cost(self, rotation: RotationCommand) -> float:
    """Get AE cost per second for rotation command."""
    cost_map = {
        RotationCommand.NONE: self.config.rotation.none_ae_per_second,
        RotationCommand.SOFT_LEFT: self.config.rotation.soft_turn_ae_per_second,
        RotationCommand.SOFT_RIGHT: self.config.rotation.soft_turn_ae_per_second,
        RotationCommand.HARD_LEFT: self.config.rotation.hard_turn_ae_per_second,
        RotationCommand.HARD_RIGHT: self.config.rotation.hard_turn_ae_per_second,
    }
    return cost_map[rotation]
```

**Update `resolve_turn()` to calculate combined costs:**

```python
def resolve_turn(self, state: GameState, orders_a: Orders, orders_b: Orders) -> Tuple[GameState, List[Event]]:
    # ... existing validation ...

    # Calculate combined AE costs
    movement_cost_a = self._get_movement_ae_cost(orders_a.movement) * self.action_phase_duration
    rotation_cost_a = self._get_rotation_ae_cost(orders_a.rotation) * self.action_phase_duration
    total_cost_a = movement_cost_a + rotation_cost_a

    movement_cost_b = self._get_movement_ae_cost(orders_b.movement) * self.action_phase_duration
    rotation_cost_b = self._get_rotation_ae_cost(orders_b.rotation) * self.action_phase_duration
    total_cost_b = movement_cost_b + rotation_cost_b

    # Deduct combined costs
    state.ship_a.ae = max(0, state.ship_a.ae - total_cost_a)
    state.ship_b.ae = max(0, state.ship_b.ae - total_cost_b)

    # ... continue with substeps ...
```

**Tests:** Add combined cost tests verifying movement + rotation AE costs are both applied.

---

## Testing Strategy

### Unit Tests (Required)

**`tests/test_data_models.py` (new file):**
- Test all enum values exist
- Test Orders with new fields
- Test serialization

**`tests/test_physics.py` (update existing):**
- Test all 9 movement directions
- Test all 5 rotation commands
- Test movement doesn't affect rotation
- Test rotation doesn't affect movement
- Test combined AE costs
- Test determinism

### Integration Tests (Optional but Recommended)

Create simple test fixtures in `tests/fixtures/` with mock orders:

```python
# tests/test_epic_002_phase_1_integration.py
def test_strafing_run_physics():
    """Test ship can move RIGHT while rotating HARD_LEFT."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_heading=0.0)  # Facing east
    orders_a = Orders(
        movement=MovementDirection.RIGHT,     # Move south
        rotation=RotationCommand.HARD_LEFT,   # Rotate toward north
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, default_orders_b)

    # Verify moved south
    assert new_state.ship_a.position.y < state.ship_a.position.y
    # Verify rotated north
    assert new_state.ship_a.heading > 0.0
```

---

## Success Criteria

Phase 1 is complete when:

1. ✅ All new enums created (`MovementDirection`, `RotationCommand`)
2. ✅ `Orders` dataclass updated with `rotation` field
3. ✅ Movement sets velocity independent of heading
4. ✅ Rotation sets heading independent of velocity
5. ✅ Combined AE costs calculated (movement + rotation)
6. ✅ All unit tests pass
7. ✅ Physics remains deterministic
8. ✅ Can create Orders with new types and simulate turns

---

## Important Notes

### Temporary State

**After Phase 1:**
- ✅ Physics engine works with new system
- ⚠️ LLM adapter still uses old system (will be updated in Phase 2)
- ⚠️ Existing tests that create Orders need updating
- ⚠️ Can't run full matches yet (LLM adapter incompatible)

**Workaround for testing:**
Create mock orders directly:
```python
orders_a = Orders(
    movement=MovementDirection.FORWARD,
    rotation=RotationCommand.HARD_LEFT,
    weapon_action="MAINTAIN_CONFIG"
)
```

### Do NOT Modify (Yet)

**Leave these unchanged in Phase 1:**
- `ai_arena/llm_adapter/adapter.py` - LLM integration (Phase 2)
- `ai_arena/orchestrator/match_orchestrator.py` - Only update if needed for tests
- `main.py` - Don't try to run full matches yet

### Config Changes

**Update these config sections:**
- `movement` - Add per-second costs for all directions
- `rotation` - Already exists, verify values match game spec

**File:** `ai_arena/config/loader.py`

May need to update `MovementConfig` dataclass:

```python
@dataclass
class MovementConfig:
    forward_ae_per_second: float
    diagonal_ae_per_second: float
    perpendicular_ae_per_second: float
    backward_ae_per_second: float
    backward_diagonal_ae_per_second: float
    stop_ae_per_second: float
```

---

## Verification Checklist

Before marking Phase 1 complete:

- [ ] `MovementDirection` enum with 9 values created
- [ ] `RotationCommand` enum with 5 values created
- [ ] `Orders.rotation` field added
- [ ] `Orders.movement` type changed to `MovementDirection`
- [ ] Movement offsets dictionary created
- [ ] Rotation rates dictionary created
- [ ] `_update_ship_physics()` refactored (rotation first, then movement)
- [ ] `_get_movement_ae_cost()` method created
- [ ] `_get_rotation_ae_cost()` method created
- [ ] Combined AE cost calculation in `resolve_turn()`
- [ ] All unit tests written and passing
- [ ] Physics determinism verified
- [ ] Config updated with movement costs
- [ ] ConfigLoader updated if needed

---

## Next Steps (Phase 2 - Out of Scope)

Phase 2 will handle LLM integration (Stories 008-009):
- Update system prompt to teach new system
- Update order parsing for new JSON format
- Enable full matches with LLMs

Phase 3 will validate tactical maneuvers (Stories 010-011):
- Comprehensive physics testing
- Tactical validation (strafing, retreat, etc.)

---

## Questions? Check These Files

- **Epic overview:** `docs/epic-002-independent-movement-rotation.md`
- **Story details:** `docs/stories/story-004-*.md` through `story-007-*.md`
- **Game spec:** `docs/game_spec_revised.md` (lines 96-197)
- **Architecture:** `docs/architecture.md` (physics engine section)
- **Project guidance:** `CLAUDE.md`

---

## Git Workflow

**Branch name:** `feature/epic-002-phase-1-physics-foundation`

**Commit message template:**
```
Implement independent movement & rotation physics (Epic 002 Phase 1)

- Add MovementDirection and RotationCommand enums
- Decouple velocity (movement) from heading (rotation)
- Implement combined AE cost system
- Update physics engine with independent controls

Stories completed:
- Story 004: Data Model Foundation
- Story 005: Movement Direction System
- Story 006: Independent Rotation System
- Story 007: Combined AE Cost System

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

Good luck! This is a significant refactor but the stories provide clear guidance. Focus on getting the physics right - the LLM integration in Phase 2 will be much easier once the foundation is solid.
