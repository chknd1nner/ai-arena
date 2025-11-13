# Story 001: Load and Parse Configuration

**Epic:** [Epic 001: Configuration Loading System](../epic-001-configuration-system.md)
**Status:** Ready for Development
**Size:** Small
**Priority:** P0

---

## User Story

**As a** developer
**I want** a configuration loader module
**So that** game parameters can be loaded from `config.json` instead of being hardcoded

## Acceptance Criteria

- [ ] New module `ai_arena/config/loader.py` exists
- [ ] `ConfigLoader` class can load and parse `config.json`
- [ ] All config sections are accessible as typed objects
- [ ] File not found errors are handled gracefully
- [ ] Invalid JSON errors are handled gracefully
- [ ] Unit tests verify correct loading

## Technical Details

### Files to Create

**`ai_arena/config/__init__.py`**
```python
from .loader import ConfigLoader, GameConfig

__all__ = ['ConfigLoader', 'GameConfig']
```

**`ai_arena/config/loader.py`**
- Create `GameConfig` dataclass with nested structures matching `config.json`
- Create `ConfigLoader` class with `load(filepath)` method
- Return typed `GameConfig` object

### Data Structures

```python
@dataclass
class SimulationConfig:
    decision_interval_seconds: float
    physics_tick_rate_seconds: float

@dataclass
class ShipConfig:
    starting_shields: float
    starting_ae: float
    max_ae: float
    ae_regen_per_second: float
    base_speed_units_per_second: float
    collision_damage: float

# ... similar for MovementConfig, RotationConfig, PhaserConfig, TorpedoConfig, ArenaConfig

@dataclass
class GameConfig:
    simulation: SimulationConfig
    ship: ShipConfig
    movement: MovementConfig
    rotation: RotationConfig
    phaser: PhaserConfig
    torpedo: TorpedoConfig
    arena: ArenaConfig
```

### Implementation Notes

1. Use Python's built-in `json` module
2. Use `dataclasses` for type safety
3. Config path should be relative to project root
4. Default to `config.json` but allow override

### Error Handling

```python
class ConfigError(Exception):
    """Raised when config cannot be loaded or is invalid"""
    pass
```

Handle:
- File not found
- Invalid JSON syntax
- Missing required fields

## Test Requirements

**`tests/test_config.py`**

Test cases:
1. `test_load_valid_config()` - Loads config.json successfully
2. `test_config_structure()` - All sections present and typed correctly
3. `test_file_not_found()` - Raises ConfigError with helpful message
4. `test_invalid_json()` - Raises ConfigError for malformed JSON
5. `test_missing_sections()` - Raises ConfigError for incomplete config

## Example Usage

```python
from ai_arena.config import ConfigLoader

loader = ConfigLoader()
config = loader.load("config.json")

print(config.ship.starting_shields)  # 100.0
print(config.phaser.wide.damage)     # 15.0
```

## Definition of Done

- [ ] Code written and follows existing style
- [ ] All acceptance criteria met
- [ ] Unit tests written and passing
- [ ] No breaking changes to existing code
- [ ] Documented in code with docstrings

## Files Changed

- ✅ Create: `ai_arena/config/__init__.py`
- ✅ Create: `ai_arena/config/loader.py`
- ✅ Create: `tests/test_config.py`

## Dependencies

None - standalone module

## Developer Agent Report

**🤖 To be completed by Claude Code Web when implementation is done:**

### Implementation Summary
<!-- Brief description of what was implemented -->

### Files Changed
<!-- List all files created/modified with brief description of changes -->
- [ ] Created: `ai_arena/config/__init__.py`
- [ ] Created: `ai_arena/config/loader.py`
- [ ] Created: `tests/test_config.py`

### Test Results
<!-- Paste test output showing all tests passing -->
```
# Example:
# pytest tests/test_config.py -v
# ====== X passed in Y.YYs ======
```

### Acceptance Criteria Status
- [ ] New module `ai_arena/config/loader.py` exists
- [ ] `ConfigLoader` class can load and parse `config.json`
- [ ] All config sections are accessible as typed objects
- [ ] File not found errors are handled gracefully
- [ ] Invalid JSON errors are handled gracefully
- [ ] Unit tests verify correct loading

### Known Issues / Limitations
<!-- Any issues encountered or compromises made -->

### Code Review Notes
<!-- Specific areas that need careful review -->

### Next Steps
<!-- What should be done next or dependencies for other work -->

---

## Next Steps

After completion, proceed to [Story 002: Use Configuration in Physics Engine](story-002-physics-constants.md)
