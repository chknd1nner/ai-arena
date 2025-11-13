# Epic 002: Independent Movement & Rotation System

**Status:** Ready for Development
**Priority:** P0 (Foundational)
**Estimated Size:** Medium-Large (8 stories, 2-3 weeks)
**Target for:** Claude Code Web testing

---

## Overview

Implement the "face move" system where ships can move in one direction while facing another, enabling advanced tactical maneuvers like strafing runs, retreat with coverage, and drift attacks. This is a fundamental enhancement to tactical gameplay depth described in the game specification.

## Problem Statement

Currently, movement and ship facing are conflated:
- Movement commands directly control rotation (e.g., HARD_LEFT rotates ship 45°)
- Ships always face the direction they're moving
- Cannot perform tactical maneuvers like "circle right while guns point backward"
- Rotation config exists in config.json but is completely unused
- Game spec describes independent movement and rotation, but it's not implemented

**Example of missing capability:**
- **Strafing Run:** Ship should be able to move right (90° arc) while rotating hard left (45°) to keep phasers pointed at enemy
- **Current behavior:** Ship moves right and faces right (phasers point away from enemy)
- **Desired behavior:** Ship moves right but faces backward (phasers maintain lock)

## Goals

1. **Decouple Movement from Rotation**: Movement sets velocity direction, rotation sets heading
2. **Two-Command System**: LLMs issue separate movement and rotation commands each turn
3. **Tactical Maneuvers**: Enable all 4 advanced maneuvers from game spec
4. **Combined AE Economy**: Both movement and rotation cost AE, calculated continuously
5. **Config Integration**: Use existing rotation config values

## Success Criteria

- [ ] Ships can move in one direction while facing another
- [ ] All movement directions work independently of rotation
- [ ] All rotation commands work independently of movement
- [ ] Combined AE costs calculated correctly (movement + rotation)
- [ ] LLMs can successfully issue both movement and rotation commands
- [ ] Physics remains deterministic (same inputs = same outputs)
- [ ] All 4 tactical maneuvers validated (strafing, retreat, reposition, drift)
- [ ] Tests cover all movement/rotation combinations
- [ ] At least one match shows LLM using advanced tactics

## User Stories

1. [Story 004: Data Model Foundation](stories/story-004-data-model-foundation.md)
2. [Story 005: Movement Direction System](stories/story-005-movement-direction-system.md)
3. [Story 006: Independent Rotation System](stories/story-006-independent-rotation-system.md)
4. [Story 007: Combined AE Cost System](stories/story-007-combined-ae-cost-system.md)
5. [Story 008: LLM Prompt Engineering](stories/story-008-llm-prompt-engineering.md)
6. [Story 009: LLM Order Parsing](stories/story-009-llm-order-parsing.md)
7. [Story 010: Physics Testing Suite](stories/story-010-physics-testing-suite.md)
8. [Story 011: Tactical Validation](stories/story-011-tactical-validation.md)

## Technical Approach

### Current Implementation (Epic 001 State)

**Movement System:**
```python
# Movement directly controls rotation
movement_params = {
    MovementType.STRAIGHT: {"rotation": 0.0},
    MovementType.HARD_LEFT: {"rotation": 0.785},  # 45° in radians
    # ...
}

def _update_ship_physics(ship, orders, dt):
    # Rotation happens based on MOVEMENT choice
    rotation_per_dt = movement_params[orders.movement]["rotation"] * dt / action_phase_duration
    ship.heading += rotation_per_dt
```

**Problem:** Movement and rotation are coupled.

### Target Implementation (Epic 002 Goal)

**Decoupled System:**
```python
# Movement controls velocity direction only
movement_directions = {
    MovementDirection.FORWARD: 0.0,      # Continue current heading
    MovementDirection.LEFT: -np.pi/2,    # 90° left of current heading
    MovementDirection.RIGHT: np.pi/2,    # 90° right of current heading
    # ...
}

# Rotation controls heading change only
rotation_rates = {
    RotationCommand.NONE: 0.0,
    RotationCommand.HARD_LEFT: -3.0,  # degrees per second
    RotationCommand.HARD_RIGHT: 3.0,
    # ...
}

def _update_ship_physics(ship, orders, dt):
    # 1. Apply rotation (independent)
    rotation_rate = rotation_rates[orders.rotation]
    ship.heading += np.radians(rotation_rate * dt)

    # 2. Apply movement (independent)
    movement_angle = ship.heading + movement_directions[orders.movement]
    ship.velocity = Vec2D(
        np.cos(movement_angle) * ship_speed,
        np.sin(movement_angle) * ship_speed
    )
    ship.position = ship.position + (ship.velocity * dt)
```

**Result:** Movement and rotation are independent.

## Architecture Changes

### Data Models (data_models.py)

**New Enums:**
```python
class MovementDirection(Enum):
    FORWARD = "FORWARD"         # Continue current heading
    FORWARD_LEFT = "FORWARD_LEFT"   # 45° left
    FORWARD_RIGHT = "FORWARD_RIGHT" # 45° right
    LEFT = "LEFT"               # 90° left
    RIGHT = "RIGHT"             # 90° right
    BACKWARD = "BACKWARD"       # 180° reverse
    BACKWARD_LEFT = "BACKWARD_LEFT"   # 135° left
    BACKWARD_RIGHT = "BACKWARD_RIGHT" # 135° right
    STOP = "STOP"               # Coast to halt

class RotationCommand(Enum):
    NONE = "NONE"               # No rotation
    SOFT_LEFT = "SOFT_LEFT"     # 1.0°/s
    SOFT_RIGHT = "SOFT_RIGHT"   # 1.0°/s
    HARD_LEFT = "HARD_LEFT"     # 3.0°/s
    HARD_RIGHT = "HARD_RIGHT"   # 3.0°/s
```

**Updated Orders:**
```python
@dataclass
class Orders:
    movement: MovementDirection  # Changed from MovementType
    rotation: RotationCommand    # NEW: Independent rotation
    weapon_action: str
    torpedo_orders: Dict[str, MovementType] = field(default_factory=dict)
```

### Configuration (config.json)

**Movement Config (Updated):**
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

**Rotation Config (Already Exists, Will Use):**
```json
"rotation": {
  "none_ae_per_second": 0.0,
  "soft_turn_ae_per_second": 0.13,
  "soft_turn_degrees_per_second": 1.0,
  "hard_turn_ae_per_second": 0.33,
  "hard_turn_degrees_per_second": 3.0
}
```

### LLM Adapter (adapter.py)

**Updated JSON Response Format:**
```json
{
  "thinking": "Enemy is at my 3 o'clock. I'll strafe right to evade while rotating left to maintain phaser lock.",
  "ship_movement": "RIGHT",
  "ship_rotation": "HARD_LEFT",
  "weapon_action": "MAINTAIN_CONFIG",
  "torpedo_orders": {}
}
```

**System Prompt Addition:**
```
MOVEMENT DIRECTIONS (velocity):
- FORWARD: Continue straight ahead (0.33 AE/s)
- LEFT: Move 90° left while maintaining facing (0.67 AE/s)
- RIGHT: Move 90° right while maintaining facing (0.67 AE/s)
- BACKWARD: Reverse direction (0.67 AE/s)
- Diagonals: FORWARD_LEFT, FORWARD_RIGHT, BACKWARD_LEFT, BACKWARD_RIGHT
- STOP: Coast to halt (0.0 AE/s)

ROTATION COMMANDS (facing):
- NONE: Don't change facing (0.0 AE/s)
- SOFT_LEFT: Rotate 1.0°/s left (0.13 AE/s)
- SOFT_RIGHT: Rotate 1.0°/s right (0.13 AE/s)
- HARD_LEFT: Rotate 3.0°/s left (0.33 AE/s)
- HARD_RIGHT: Rotate 3.0°/s right (0.33 AE/s)

TACTICAL EXAMPLES:
1. Strafing Run: movement=RIGHT, rotation=HARD_LEFT (circle right, guns face left)
2. Retreat with Coverage: movement=BACKWARD, rotation=NONE (back away, guns face forward)
3. Aggressive Reposition: movement=FORWARD, rotation=HARD_RIGHT (advance while angling guns)
```

## Dependencies

- **Requires:** Epic 001 (Configuration System) - ✅ Complete
- **Blocks:** Epic 003+ (Advanced torpedo tactics depend on movement system)

## Risk Assessment

**Medium-High Risk**

**Technical Risks:**
- Physics refactor may introduce bugs in determinism
- Edge cases (e.g., backward movement while rotating) need careful testing
- Continuous AE burn calculation adds complexity

**Gameplay Risks:**
- New system may make certain tactics overpowered
- LLMs may not understand two-command system initially
- Balance tuning may require multiple iterations

**Mitigation Strategies:**
1. **Incremental Development:** Stories 1-4 build foundation before LLM integration
2. **Comprehensive Testing:** Stories 7-8 dedicated to validation
3. **Config-Based Tuning:** All values in config.json for easy adjustment
4. **Determinism Validation:** Every physics change verified with replay tests

## Testing Strategy

1. **Unit Tests**: Each movement direction × rotation command combination
2. **Integration Tests**: Full turn resolution with combined AE costs
3. **Tactical Tests**: Verify all 4 advanced maneuvers work correctly
4. **LLM Tests**: Real matches with both models using new system
5. **Replay Tests**: Verify determinism (same inputs = same outputs)
6. **Balance Tests**: Playtest and tune AE costs if needed

## Definition of Done

- All acceptance criteria met for all user stories
- Tests pass (existing + new)
- Physics remains deterministic (replay validation)
- LLMs successfully use both movement and rotation commands
- At least one recorded match shows advanced tactical maneuver
- Documentation updated (CLAUDE.md, game_spec notes)
- Code reviewed and merged to main

## Notes for Claude Code Web

This epic is designed for **one feature branch** with all stories completed together:
- Clear scope: Movement/rotation decoupling only
- Natural progression: Data models → Physics → LLM → Testing
- Stories are sequential and build on each other
- Creates foundation for all future tactical enhancements
- Estimated: 8-12 hours of Claude Code Web development time

**Alternative Approach (Lower Risk):**
Split into two smaller epics:
- **Epic 002A:** Stories 1-4 (Physics changes only, keep old LLM interface)
- **Epic 002B:** Stories 5-6 (LLM integration)
- **Pros:** Smaller PRs, easier to review, can validate physics first
- **Cons:** Epic 002A doesn't provide user value until 002B complete

**Recommendation:** Complete all together for coherent change.

## Future Enhancements (Out of Scope)

- Continuous AE burn tracking at substep level (currently per-turn)
- Variable movement speeds (currently fixed at base_speed)
- Momentum and inertia (currently instant velocity changes)
- Advanced rotation (spin, drift effects)

## Next Steps After Epic 002

Once independent movement/rotation is complete, consider:

1. **Epic 003: Continuous AE Economy** - Per-substep AE burn/regen
2. **Epic 004: Phaser Cooldown System** - Add continuous cooldown tracking
3. **Epic 005: Torpedo Timed Detonation** - Add `detonate_after:X` command
4. **Epic 006: Frontend Replay Viewer** - Canvas-based visualization
