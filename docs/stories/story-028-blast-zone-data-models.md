# Story 028: Blast Zone Data Models

**Epic:** [Epic 005: Advanced Torpedo & Blast Zone System](../epic-005-torpedo-blast-zones.md)
**Status:** Ready for development
**Size:** Small (~1-2 hours)
**Priority:** P0

---

## User Story

**As a** physics engine developer
**I want** data models for blast zones with lifecycle phases
**So that** I can track blast zone state throughout expansion, persistence, and dissipation

## Context

Blast zones are persistent areas of damage created when torpedoes detonate. They have a 70-second lifecycle with three distinct phases:
- **Expansion** (5s): Radius grows from 0 to 15 units
- **Persistence** (60s): Radius remains at 15 units
- **Dissipation** (5s): Radius shrinks from 15 to 0 units

This story creates the data structures needed to represent blast zones in the physics simulation.

## Acceptance Criteria

- [ ] `BlastZonePhase` enum created with EXPANSION, PERSISTENCE, DISSIPATION values
- [ ] `BlastZone` dataclass created with all required fields
- [ ] `GameState.blast_zones` field added (List[BlastZone])
- [ ] `TorpedoState.detonation_timer` field added (Optional[float])
- [ ] Blast zone configuration added to config.json
- [ ] Config loader validates blast zone parameters
- [ ] All existing tests still pass
- [ ] New tests validate data model serialization

## Technical Requirements

### Data Models (data_models.py)

**Create BlastZonePhase enum:**
```python
class BlastZonePhase(Enum):
    """Lifecycle phase for blast zones."""
    EXPANSION = "expansion"       # Growing from 0→15 units
    PERSISTENCE = "persistence"   # Holding at 15 units
    DISSIPATION = "dissipation"   # Shrinking from 15→0 units
```

**Create BlastZone dataclass:**
```python
@dataclass
class BlastZone:
    """Persistent area of damage from torpedo detonation.

    Lifecycle: Expansion (5s) → Persistence (60s) → Dissipation (5s) = 70s total
    """
    id: str                      # "ship_a_torp_5_blast"
    position: Vec2D              # Center point (fixed for lifetime)
    base_damage: float           # (Torpedo AE at detonation) × 1.5
    phase: BlastZonePhase       # Current lifecycle phase
    age: float                   # Seconds since creation (0.0 → 70.0)
    current_radius: float        # 0.0 → 15.0 → 15.0 → 0.0
    owner: str                   # "ship_a" or "ship_b"
```

**Update GameState:**
```python
@dataclass
class GameState:
    turn: int
    ship_a: ShipState
    ship_b: ShipState
    torpedoes: List[TorpedoState]
    blast_zones: List[BlastZone] = field(default_factory=list)  # NEW
```

**Update TorpedoState:**
```python
@dataclass
class TorpedoState:
    # ... existing fields ...
    detonation_timer: Optional[float] = None  # NEW: Seconds until detonation
```

### Configuration (config.json)

**Add blast zone section:**
```json
{
  "torpedo": {
    "launch_cost_ae": 20,
    "max_ae_capacity": 40,
    "speed_units_per_second": 4.0,
    "max_active_per_ship": 4,
    "blast_expansion_seconds": 5.0,
    "blast_persistence_seconds": 60.0,
    "blast_dissipation_seconds": 5.0,
    "blast_radius_units": 15.0,
    "blast_damage_multiplier": 1.5
  }
}
```

### Config Loader (loader.py)

**Add validation for blast zone config:**
```python
class TorpedoConfig:
    # ... existing fields ...
    blast_expansion_seconds: float
    blast_persistence_seconds: float
    blast_dissipation_seconds: float
    blast_radius_units: float
    blast_damage_multiplier: float
```

### Tests

**Create tests/test_blast_zone_models.py:**
- Test BlastZone creation with valid data
- Test BlastZonePhase enum values
- Test GameState with blast_zones list
- Test TorpedoState with detonation_timer
- Test JSON serialization/deserialization
- Test config loading with blast zone parameters

## Deliverables

- [ ] `ai_arena/game_engine/data_models.py` - BlastZone, BlastZonePhase added
- [ ] `config.json` - Blast zone parameters added
- [ ] `ai_arena/config/loader.py` - Blast zone config validation
- [ ] `tests/test_blast_zone_models.py` - Data model tests (~6-8 tests)

## Definition of Done

- [ ] BlastZone and BlastZonePhase classes created
- [ ] GameState.blast_zones field exists
- [ ] TorpedoState.detonation_timer field exists
- [ ] Config.json updated with blast zone parameters
- [ ] Config loader validates blast zone config
- [ ] All tests pass (existing + new)
- [ ] Code follows project conventions
- [ ] No breaking changes to existing functionality

## Files to Create/Modify

**Create:**
- `tests/test_blast_zone_models.py`

**Modify:**
- `ai_arena/game_engine/data_models.py`
- `config.json`
- `ai_arena/config/loader.py`

## Dependencies

- Epic 004: Continuous physics system (completed)
- Epic 001: Configuration system (completed)

---

## Dev Agent Record

**Implementation Date:** 2025-11-17
**Agent:** Claude (Sonnet 4.5)
**Status:** Ready for QA

### Summary

Successfully implemented all foundational data structures for Epic 005 blast zone system. Added BlastZonePhase enum with 3 lifecycle phases (EXPANSION, PERSISTENCE, DISSIPATION), created BlastZone dataclass with 7 fields tracking position, damage, phase, age, radius, and owner. Updated GameState to track blast zones and TorpedoState to support timed detonation. Renamed config parameter from `blast_duration_seconds` to `blast_persistence_seconds` for semantic clarity. All 17 new tests pass with no regressions in 149 existing tests.

### Work Completed

- [x] Added BlastZonePhase enum to data_models.py with EXPANSION, PERSISTENCE, DISSIPATION values
- [x] Added BlastZone dataclass to data_models.py with comprehensive docstring
- [x] Updated GameState to include `blast_zones: List[BlastZone] = field(default_factory=list)`
- [x] Updated TorpedoState to include `detonation_timer: Optional[float] = None`
- [x] Renamed `blast_duration_seconds` to `blast_persistence_seconds` in config.json (semantic improvement)
- [x] Updated TorpedoConfig in loader.py with `blast_persistence_seconds` field
- [x] Added validation for blast_expansion_seconds, blast_persistence_seconds, and blast_dissipation_seconds
- [x] Created comprehensive test suite in tests/test_blast_zone_models.py with 17 tests
- [x] Fixed test fixture files to use new `blast_persistence_seconds` field name
- [x] Verified all 166 tests pass (17 new + 149 existing)

### Test Results

**New Tests:** 17/17 passing in `tests/test_blast_zone_models.py`
- 3 tests for BlastZonePhase enum
- 3 tests for BlastZone dataclass creation and serialization
- 4 tests for GameState with blast_zones field
- 4 tests for TorpedoState with detonation_timer field
- 3 tests for config loading and validation

**Regression Tests:** 149/149 passing (no regressions)

**Total:** 166/166 tests passing

**Coverage:**
- BlastZone creation and lifecycle phases
- GameState serialization with blast zones
- TorpedoState with optional detonation timer
- Config loading with all 5 blast zone parameters
- Validation of blast zone timing parameters

### Issues Encountered

**Issue 1: Config Field Naming**
- Initial implementation found existing config had `blast_duration_seconds` but story spec required `blast_persistence_seconds`
- **Resolution:** Renamed field throughout codebase for semantic clarity (persistence phase is conceptually different from total duration)
- **Impact:** Required updating test fixture files in `tests/fixtures/` directory

**Issue 2: Test Fixture Compatibility**
- Test fixtures `invalid_range_violations.json` and `invalid_negative_values.json` still used old field name
- **Resolution:** Updated both fixtures to use `blast_persistence_seconds`
- **Impact:** All validation tests now pass

**Design Decisions:**
1. Used `Optional[float]` for `detonation_timer` to clearly distinguish between timed detonation (value present) and collision-only detonation (None)
2. Followed existing dataclass patterns with `field(default_factory=list)` for `blast_zones`
3. Added comprehensive docstring to BlastZone explaining lifecycle and field meanings
4. Validation enforces all timing parameters > 0 (consistent with other config validations)

### Files Created/Modified

**Created:**
- `tests/test_blast_zone_models.py` (17 new tests)

**Modified:**
- `ai_arena/game_engine/data_models.py` (added BlastZonePhase, BlastZone, updated GameState and TorpedoState)
- `config.json` (renamed `blast_duration_seconds` → `blast_persistence_seconds`)
- `ai_arena/config/loader.py` (updated TorpedoConfig, added validation)
- `tests/fixtures/invalid_range_violations.json` (updated field name)
- `tests/fixtures/invalid_negative_values.json` (updated field name)

---

## QA Agent Record

**Validation Date:** [Fill in date when validating]
**Validator:** [Fill in validator name]
**Verdict:** [Fill in: PASSED / FAILED / NEEDS REVISION]

### Instructions for QA Agent

[When validating this story:

1. **Run the full test suite** (`pytest tests/ -v`) and verify:
   - All existing tests still pass (no regressions)
   - New tests in test_blast_zone_models.py pass
   - Test coverage is adequate (at least 6-8 tests for data models)

2. **Code review checklist:**
   - [ ] BlastZonePhase enum has all three phases (EXPANSION, PERSISTENCE, DISSIPATION)
   - [ ] BlastZone dataclass has all required fields with correct types
   - [ ] GameState.blast_zones uses field(default_factory=list) pattern
   - [ ] TorpedoState.detonation_timer is Optional[float]
   - [ ] Config.json has all blast zone parameters with sensible defaults
   - [ ] Config loader validates blast zone parameters
   - [ ] Type hints are correct throughout
   - [ ] Docstrings explain purpose of new classes

3. **Functional validation:**
   - [ ] Create a BlastZone instance and verify all fields accessible
   - [ ] Verify GameState can be serialized to JSON with blast_zones
   - [ ] Verify config loads successfully with new parameters
   - [ ] Check that existing replays can still be loaded

4. **Documentation:**
   - [ ] Dev Agent Record is filled out completely
   - [ ] Any deviations from spec are documented
   - [ ] Code comments explain non-obvious design decisions

5. **Update this QA Agent Record** with findings and verdict]

### Test Summary

[Fill in test results]

### Issues Found

[Fill in any issues discovered during QA]

### Recommendations

[Fill in recommendations for improvement or next steps]

---

**Story Status:** [Update when complete]
