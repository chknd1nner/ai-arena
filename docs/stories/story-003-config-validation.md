# Story 003: Configuration Validation

**Epic:** [Epic 001: Configuration Loading System](../epic-001-configuration-system.md)
**Status:** Ready for Development
**Size:** Small
**Priority:** P1

---

## User Story

**As a** developer or system administrator
**I want** configuration errors to be caught immediately on startup
**So that** I get clear error messages instead of mysterious runtime failures

## Context

Without validation:
- Missing config values cause AttributeError at runtime
- Invalid values (negative speeds, zero damage) cause weird game behavior
- Typos in config.json are not caught until something breaks
- Debugging configuration issues is time-consuming

## Acceptance Criteria

- [ ] Config is validated immediately after loading
- [ ] All required fields are checked for presence
- [ ] Value ranges are validated (speeds > 0, percentages 0-100, etc.)
- [ ] Clear error messages identify the problem field
- [ ] Application fails fast with helpful message if config is invalid
- [ ] Tests verify validation catches common errors

## Validation Rules

### Required Fields
All fields in `config.json` must be present (no optional fields for MVP).

### Value Constraints

**Simulation:**
- `decision_interval_seconds` > 0
- `physics_tick_rate_seconds` > 0
- `physics_tick_rate_seconds` ≤ `decision_interval_seconds`

**Ship:**
- `starting_shields` > 0
- `starting_ae` > 0
- `max_ae` ≥ `starting_ae`
- `ae_regen_per_second` ≥ 0
- `base_speed_units_per_second` > 0
- `collision_damage` ≥ 0

**Movement & Rotation:**
- All `ae_per_second` values ≥ 0
- All `degrees_per_second` values ≥ 0

**Phaser:**
- `arc_degrees` > 0 and ≤ 360
- `range_units` > 0
- `damage` > 0
- `cooldown_seconds` ≥ 0

**Torpedo:**
- `launch_cost_ae` > 0
- `max_ae_capacity` > 0
- `speed_units_per_second` > 0
- `max_active_per_ship` > 0
- `blast_radius_units` > 0
- `blast_damage_multiplier` > 0

**Arena:**
- `width_units` > 0
- `height_units` > 0
- `spawn_distance_units` > 0

### Logical Consistency

- Spawn distance should fit within arena dimensions
- Phaser ranges should be reasonable (< arena size)
- Ship speed should be < torpedo speed (currently violated!)

## Technical Details

### Implementation Approach

**Add validation to ConfigLoader:**

```python
class ConfigLoader:
    def load(self, filepath: str) -> GameConfig:
        config = self._parse_json(filepath)
        self._validate(config)  # ← New
        return config

    def _validate(self, config: GameConfig):
        """Validate configuration values"""
        errors = []

        # Check simulation values
        if config.simulation.decision_interval_seconds <= 0:
            errors.append("simulation.decision_interval_seconds must be > 0")

        # ... more checks ...

        if errors:
            raise ConfigError(
                f"Invalid configuration:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )
```

### Error Message Format

**Good error message example:**
```
Invalid configuration:
  - ship.starting_shields must be > 0 (got: -10)
  - phaser.wide.arc_degrees must be > 0 and <= 360 (got: 450)
  - torpedo.speed_units_per_second must be > 0 (got: 0)
```

**Bad error message example:**
```
ValueError: invalid literal for int() with base 10: 'abc'
```

## Test Requirements

**`tests/test_config.py` (add to existing file)**

New test cases:
1. `test_validate_negative_values()` - Rejects negative speeds, damage
2. `test_validate_zero_values()` - Rejects zero for required positive values
3. `test_validate_range_violations()` - Phaser arc > 360, etc.
4. `test_validate_missing_sections()` - Missing entire config sections
5. `test_validate_missing_fields()` - Missing individual fields
6. `test_validate_type_errors()` - String where number expected
7. `test_validate_multiple_errors()` - Reports all errors at once
8. `test_validate_logical_consistency()` - Spawn distance vs arena size

**Test data:**
Create `tests/fixtures/` directory with invalid config samples:
- `invalid_negative_values.json`
- `invalid_missing_fields.json`
- `invalid_types.json`

## Implementation Checklist

- [ ] Add `_validate()` method to ConfigLoader
- [ ] Implement validation rules for all sections
- [ ] Collect all errors before raising (don't fail on first error)
- [ ] Write clear error messages with field names and values
- [ ] Add validation tests
- [ ] Test with intentionally broken configs
- [ ] Document validation rules in docstring

## Edge Cases to Handle

1. **Type mismatches**: Config has string where float expected
2. **Extra fields**: Config has fields not in dataclass (ignore or warn?)
3. **Case sensitivity**: "WIDE" vs "wide" in config
4. **Infinity/NaN**: Config has `Infinity` or `NaN` values
5. **Scientific notation**: Config uses `1e-3` notation

## Performance Considerations

Validation is O(1) - just checking values, not processing large data structures. Run on startup only, not per-match.

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Validation catches all specified error conditions
- [ ] Error messages are clear and actionable
- [ ] Tests cover all validation rules
- [ ] Application fails fast on invalid config
- [ ] No breaking changes to valid configs

## Files Changed

- ✅ Modify: `ai_arena/config/loader.py` (add validation)
- ✅ Modify: `tests/test_config.py` (add validation tests)
- ✅ Create: `tests/fixtures/invalid_negative_values.json`
- ✅ Create: `tests/fixtures/invalid_missing_fields.json`

## Dependencies

- Requires Story 001 (config loader) to be completed first
- Can be done in parallel with or after Story 002

## Developer Agent Report

**🤖 To be completed by Claude Code Web when implementation is done:**

### Implementation Summary
<!-- Brief description of validation system implemented -->

### Files Changed
<!-- List all files modified/created -->
- [ ] Modified: `ai_arena/config/loader.py` (added validation)
- [ ] Modified: `tests/test_config.py` (added validation tests)
- [ ] Created: `tests/fixtures/invalid_negative_values.json`
- [ ] Created: `tests/fixtures/invalid_missing_fields.json`

### Test Results
<!-- Full validation test output -->
```
# pytest tests/test_config.py -v
# Should show all validation tests passing
```

### Validation Rules Implemented
<!-- Checklist of validation rules added -->
- [ ] Required fields presence check
- [ ] Positive value constraints (speeds, damage, etc.)
- [ ] Range constraints (arc degrees, percentages)
- [ ] Logical consistency checks
- [ ] Type validation

### Example Error Messages
<!-- Paste examples of error messages from tests -->
```
# Example validation error output
```

### Edge Cases Handled
<!-- List edge cases tested and handled -->

### Acceptance Criteria Status
- [ ] Config is validated immediately after loading
- [ ] All required fields are checked for presence
- [ ] Value ranges are validated
- [ ] Clear error messages identify the problem field
- [ ] Application fails fast with helpful message if config is invalid
- [ ] Tests verify validation catches common errors

### Known Issues / Limitations
<!-- Any validation rules not yet implemented or edge cases not covered -->

### Code Review Focus Areas
<!-- Areas needing careful review -->
- Error message clarity and helpfulness
- Completeness of validation rules
- Test coverage of edge cases

### Epic Completion Notes
<!-- Since this completes Epic 001 -->
- [ ] All three stories complete
- [ ] Full test suite passes
- [ ] Ready for CLAUDE.md update

---

## Optional Enhancements (Future)

- Schema validation with JSON Schema or Pydantic
- Config hot-reload during development
- Config diff tool to compare changes
- Warning for unusual but valid values (e.g., ship faster than torpedo)

## Next Steps

After completion:
- Epic 001 is complete!
- Update CLAUDE.md to mention config system
- Consider Epic 002: Independent Movement & Rotation System
