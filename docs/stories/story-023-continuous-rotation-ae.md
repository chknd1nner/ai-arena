# Story 023: Continuous Rotation AE Application

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Not Started
**Size:** Small (~1 hour)
**Priority:** P0

---

## User Story

**As a** game engine developer
**I want** rotation AE costs applied per substep instead of per turn
**So that** energy drain from rotation feels continuous

## Context

Similar to Story 022, but for rotation. This completes the transition to fully continuous AE economy.

**Target behavior:**
```python
# Each 0.1s substep
rotation_rate = _get_rotation_ae_rate(orders.rotation, config)  # e.g., 0.33 AE/s for HARD
ae_cost_this_substep = rotation_rate * dt  # 0.33 * 0.1 = 0.033 AE
ship.available_energy -= ae_cost_this_substep
```

## Acceptance Criteria

- [ ] Rotation AE cost applied per substep
- [ ] All 5 rotation commands have correct rates
- [ ] Total cost over full turn matches previous per-turn cost
- [ ] Tests verify continuous rotation costs
- [ ] Combined movement + rotation costs work correctly

## Technical Requirements

```python
def _get_rotation_ae_rate(rotation: RotationCommand, config: GameConfig) -> float:
    """Get AE cost rate for rotation command."""
    rates = {
        RotationCommand.NONE: config.rotation.none_ae_per_second,
        RotationCommand.SOFT_LEFT: config.rotation.soft_turn_ae_per_second,
        RotationCommand.SOFT_RIGHT: config.rotation.soft_turn_ae_per_second,
        RotationCommand.HARD_LEFT: config.rotation.hard_turn_ae_per_second,
        RotationCommand.HARD_RIGHT: config.rotation.hard_turn_ae_per_second
    }
    return rates[rotation]
```

## Testing & Validation

```python
def test_rotation_ae_cost_per_substep():
    """Verify rotation AE cost applied per substep."""
    # Similar to test_movement_ae_cost_per_substep but for rotation
    pass

def test_combined_movement_and_rotation_costs():
    """Verify movement + rotation costs combine correctly."""
    # Test aggressive maneuver: PERPENDICULAR + HARD_LEFT
    # Should cost 0.67 + 0.33 = 1.0 AE/s
    # Regen: 0.33 AE/s
    # Net: -0.67 AE/s
    pass
```

## Definition of Done

- [ ] Rotation AE applied continuously
- [ ] All tests passing
- [ ] Combined costs work correctly

## Files Changed

- Modify: `ai_arena/game_engine/physics.py`
- Modify: `tests/test_continuous_physics.py`

## Dependencies

- Story 022: Continuous Movement AE

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
