# Story 020: Phaser Cooldown State & Config

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Ready for dev
**Size:** Small (~1-1.5 hours)
**Priority:** P0

---

## User Story

**As a** game engine developer
**I want** cooldown tracking added to ship state and configuration
**So that** the physics engine can enforce phaser rate limiting

## Context

This is the foundation story for Epic 004. Currently, phasers can fire every decision interval (15s) with no cooldown tracking. The game spec specifies a 3.5-second cooldown between phaser shots, but this is not implemented.

To enable continuous physics with phaser cooldown:
1. ShipState must track cooldown time remaining
2. Configuration must define cooldown duration
3. Cooldown value must persist across substeps
4. Cooldown must serialize correctly for replays

This story adds the data structures only - no logic changes yet.

## Acceptance Criteria

- [ ] `ShipState` dataclass has `phaser_cooldown_remaining: float` field
- [ ] Default cooldown value is `0.0` (can fire immediately at match start)
- [ ] `config.json` has new `weapons.phaser.cooldown_seconds` field
- [ ] ConfigLoader validates cooldown value (>= 0.0)
- [ ] Cooldown value loads correctly from config
- [ ] ShipState serialization includes cooldown (for replays)
- [ ] Existing tests still pass with new field
- [ ] Type hints and docstrings updated

## Technical Requirements

### 1. Update ShipState Data Model

**File:** `ai_arena/game_engine/data_models.py`

**Add cooldown field:**
```python
@dataclass
class ShipState:
    """State of one ship during match.

    Tracks position, velocity, heading, shields, energy, and weapon cooldowns.
    """
    id: str
    position: Vec2D
    velocity: Vec2D
    heading: float  # radians, 0 = east, positive = counterclockwise
    shields: float
    available_energy: float
    phaser_cooldown_remaining: float = 0.0  # NEW: Seconds until can fire again

    def __post_init__(self):
        """Validate ship state values."""
        assert self.shields >= 0.0, "Shields cannot be negative"
        assert self.available_energy >= 0.0, "Available energy cannot be negative"
        assert self.phaser_cooldown_remaining >= 0.0, "Cooldown cannot be negative"
```

**Example usage:**
```python
# Match start (cooldown = 0.0, can fire immediately)
ship = ShipState(
    id="ship1",
    position=Vec2D(0.0, 0.0),
    velocity=Vec2D(0.0, 0.0),
    heading=0.0,
    shields=100.0,
    available_energy=100.0,
    phaser_cooldown_remaining=0.0  # Ready to fire
)

# After firing phaser (cooldown = 3.5s)
ship.phaser_cooldown_remaining = 3.5

# After 1 substep of 0.1s
ship.phaser_cooldown_remaining -= 0.1  # Now 3.4s
```

### 2. Add Cooldown to Configuration

**File:** `config.json`

**Add cooldown config:**
```json
{
  "weapons": {
    "phaser": {
      "cooldown_seconds": 3.5,
      "wide": {
        "damage": 15,
        "range": 30,
        "arc_degrees": 90
      },
      "focused": {
        "damage": 35,
        "range": 50,
        "arc_degrees": 10
      }
    },
    "torpedo": {
      "launch_cost": 20,
      "max_capacity": 40,
      "speed": 4.0,
      "blast_radius": 15,
      "max_blast_damage": 80
    }
  }
}
```

**Configuration structure:**
```python
# Nested config access
config.weapons.phaser.cooldown_seconds  # 3.5
```

### 3. Update Configuration Loader

**File:** `ai_arena/config/loader.py`

**Add weapons config class:**
```python
@dataclass
class PhaserConfig:
    """Phaser weapon configuration."""
    cooldown_seconds: float
    wide: Dict[str, Any]
    focused: Dict[str, Any]

@dataclass
class WeaponsConfig:
    """All weapons configuration."""
    phaser: PhaserConfig
    torpedo: Dict[str, Any]

@dataclass
class GameConfig:
    """Complete game configuration."""
    simulation: SimulationConfig
    arena: ArenaConfig
    ship: ShipConfig
    movement: MovementConfig
    rotation: RotationConfig
    weapons: WeaponsConfig  # NEW

    # ... existing methods ...
```

**Add validation:**
```python
def _validate_weapons_config(config: Dict[str, Any]) -> None:
    """Validate weapons configuration section."""
    weapons = config.get("weapons", {})

    # Validate phaser config
    phaser = weapons.get("phaser", {})
    cooldown = phaser.get("cooldown_seconds")

    if cooldown is None:
        raise ConfigError("Missing weapons.phaser.cooldown_seconds")

    if not isinstance(cooldown, (int, float)):
        raise ConfigError(f"Cooldown must be numeric, got {type(cooldown)}")

    if cooldown < 0.0:
        raise ConfigError(f"Cooldown cannot be negative: {cooldown}")

    # Validate phaser wide config exists
    if "wide" not in phaser:
        raise ConfigError("Missing weapons.phaser.wide configuration")

    # Validate phaser focused config exists
    if "focused" not in phaser:
        raise ConfigError("Missing weapons.phaser.focused configuration")
```

### 4. Update Serialization

**File:** `ai_arena/game_engine/data_models.py`

Ensure ShipState serialization includes cooldown:
```python
# ShipState should use @dataclass with default serialization
# Cooldown field will automatically serialize via dataclasses.asdict()

# In replay recorder:
ship_state_dict = {
    "id": ship.id,
    "position": {"x": ship.position.x, "y": ship.position.y},
    "velocity": {"x": ship.velocity.x, "y": ship.velocity.y},
    "heading": ship.heading,
    "shields": ship.shields,
    "available_energy": ship.available_energy,
    "phaser_cooldown_remaining": ship.phaser_cooldown_remaining  # NEW
}
```

## Testing & Validation

### Unit Tests

**File:** `tests/test_config.py` (add to existing)

```python
def test_weapons_config_loaded():
    """Verify weapons config loads from config.json."""
    config = load_config()
    assert hasattr(config, 'weapons')
    assert hasattr(config.weapons, 'phaser')
    assert hasattr(config.weapons.phaser, 'cooldown_seconds')

def test_phaser_cooldown_value():
    """Verify phaser cooldown has expected value."""
    config = load_config()
    assert config.weapons.phaser.cooldown_seconds == 3.5

def test_phaser_cooldown_validation_negative():
    """Reject negative cooldown values."""
    bad_config = {
        "weapons": {
            "phaser": {
                "cooldown_seconds": -1.0,
                "wide": {},
                "focused": {}
            }
        }
    }
    with pytest.raises(ConfigError, match="Cooldown cannot be negative"):
        validate_config(bad_config)

def test_phaser_cooldown_validation_missing():
    """Reject missing cooldown configuration."""
    bad_config = {
        "weapons": {
            "phaser": {
                "wide": {},
                "focused": {}
            }
        }
    }
    with pytest.raises(ConfigError, match="Missing.*cooldown"):
        validate_config(bad_config)
```

**File:** `tests/test_data_models.py` (add to existing)

```python
def test_ship_state_has_cooldown_field():
    """Verify ShipState includes phaser_cooldown_remaining."""
    ship = ShipState(
        id="test_ship",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=100.0,
        phaser_cooldown_remaining=2.5
    )
    assert ship.phaser_cooldown_remaining == 2.5

def test_ship_state_cooldown_defaults_to_zero():
    """Verify cooldown defaults to 0.0 if not specified."""
    ship = ShipState(
        id="test_ship",
        position=Vec2D(0.0, 0.0),
        velocity=Vec2D(0.0, 0.0),
        heading=0.0,
        shields=100.0,
        available_energy=100.0
        # phaser_cooldown_remaining not specified
    )
    assert ship.phaser_cooldown_remaining == 0.0

def test_ship_state_cooldown_validation_negative():
    """Reject negative cooldown values."""
    with pytest.raises(AssertionError, match="Cooldown cannot be negative"):
        ship = ShipState(
            id="test_ship",
            position=Vec2D(0.0, 0.0),
            velocity=Vec2D(0.0, 0.0),
            heading=0.0,
            shields=100.0,
            available_energy=100.0,
            phaser_cooldown_remaining=-1.0  # Invalid
        )

def test_ship_state_serialization_includes_cooldown():
    """Verify cooldown appears in serialized state."""
    ship = ShipState(
        id="test_ship",
        position=Vec2D(10.0, 20.0),
        velocity=Vec2D(3.0, 0.0),
        heading=1.57,
        shields=85.0,
        available_energy=72.0,
        phaser_cooldown_remaining=1.2
    )

    # Serialize (implementation may vary, adjust as needed)
    state_dict = {
        "id": ship.id,
        "position": {"x": ship.position.x, "y": ship.position.y},
        "velocity": {"x": ship.velocity.x, "y": ship.velocity.y},
        "heading": ship.heading,
        "shields": ship.shields,
        "available_energy": ship.available_energy,
        "phaser_cooldown_remaining": ship.phaser_cooldown_remaining
    }

    assert state_dict["phaser_cooldown_remaining"] == 1.2
```

## Implementation Checklist

- [ ] Add `phaser_cooldown_remaining: float = 0.0` to ShipState
- [ ] Add cooldown validation to `ShipState.__post_init__()`
- [ ] Add `cooldown_seconds: 3.5` to config.json
- [ ] Create PhaserConfig and WeaponsConfig dataclasses
- [ ] Update GameConfig to include WeaponsConfig
- [ ] Add weapons config validation to ConfigLoader
- [ ] Write unit tests for cooldown field
- [ ] Write config validation tests
- [ ] Verify existing tests still pass
- [ ] Verify serialization includes cooldown

## Edge Cases to Handle

1. **Missing cooldown in config:** Should fail validation with clear error
2. **Negative cooldown:** Should fail validation (cooldown can't be negative)
3. **Zero cooldown:** Valid (means no cooldown, can spam phasers)
4. **Cooldown > decision interval:** Valid (means can fire at most once per turn)
5. **Cooldown serialization:** Must serialize to replay JSON correctly

## Performance Considerations

None - this is a pure data structure change with no performance impact.

## Definition of Done

- [ ] All acceptance criteria met
- [ ] ShipState has cooldown field with default value 0.0
- [ ] config.json has cooldown configuration
- [ ] ConfigLoader validates cooldown value
- [ ] Unit tests written and passing
- [ ] Existing tests still pass
- [ ] Cooldown serializes correctly
- [ ] Docstrings explain cooldown purpose

## Files Changed

- Modify: `ai_arena/game_engine/data_models.py`
- Modify: `config.json`
- Modify: `ai_arena/config/loader.py`
- Modify: `tests/test_config.py` (add tests)
- Modify: `tests/test_data_models.py` (add tests)

## Dependencies

- None - This is the foundation story for Epic 004

## Blocks

- Story 021: Substep AE Tracking (needs cooldown field to exist)
- Story 024: Phaser Cooldown Enforcement (needs cooldown field to exist)

## Notes

**Important:** This story only adds the data structures. No behavior changes yet. Cooldown will not actually count down or prevent firing until Story 024.

**Testing Strategy:** Unit tests only. No integration testing needed since cooldown isn't used yet.

**Design Decision:** Cooldown defaults to 0.0 (ready to fire) at match start. This means both ships can fire immediately on turn 1, which seems fair.

**Future Consideration:** Could add separate cooldowns for wide vs focused phasers. For now, both modes share the same cooldown.

---

## Dev Agent Record

**Implementation Date:** [To be filled in by Dev Agent]
**Agent:** [To be filled in by Dev Agent]
**Status:** [To be filled in by Dev Agent]

### Implementation Summary

[Dev Agent: Summarize what was implemented, any challenges encountered, and decisions made]

### Files Created

[Dev Agent: List any new files created]

### Files Modified

[Dev Agent: List files modified with brief description of changes]

### Testing Notes

[Dev Agent: Describe testing performed, test results, any edge cases discovered]

### Technical Notes

[Dev Agent: Any important implementation details, gotchas, or notes for future developers]

### Known Issues / Future Work

[Dev Agent: Any issues discovered, limitations, or follow-up work needed]

---

## QA Agent Record

**Validation Date:** [To be filled in by QA Agent]
**Validator:** [To be filled in by QA Agent]
**Verdict:** [To be filled in by QA Agent]

### Acceptance Criteria Validation

[QA Agent: Go through each acceptance criterion and verify it was met. Provide evidence (file paths, line numbers, test output)]

### Test Results

[QA Agent: Report test execution results. All tests should pass.]

### Code Quality Assessment

[QA Agent: Evaluate code quality, adherence to patterns, documentation quality]

### Issues Found

[QA Agent: Document any bugs, regressions, or quality issues discovered]

### Final Verdict

[QA Agent: PASS/FAIL with justification]

---

**Story Status:** Ready for Development
