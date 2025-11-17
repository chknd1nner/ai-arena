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

**Implementation Date:** [Fill in date when implementing]
**Agent:** [Fill in agent name]
**Status:** [Fill in status: Ready for QA / Blocked / In Progress]

### Instructions for Dev Agent

[When implementing this story:

1. **Start by reading** the following files to understand current structure:
   - `ai_arena/game_engine/data_models.py` (existing data models)
   - `config.json` (current config structure)
   - `ai_arena/config/loader.py` (config validation patterns)

2. **Add the BlastZonePhase enum** to data_models.py following the pattern of existing enums like `PhaserConfig`

3. **Add the BlastZone dataclass** to data_models.py with proper type hints and docstrings

4. **Update GameState** to include `blast_zones: List[BlastZone] = field(default_factory=list)`

5. **Update TorpedoState** to include `detonation_timer: Optional[float] = None`

6. **Update config.json** with the blast zone parameters under the torpedo section

7. **Update config/loader.py** TorpedoConfig class to include blast zone fields with validation

8. **Create comprehensive tests** in `tests/test_blast_zone_models.py` covering:
   - BlastZone creation and field validation
   - BlastZonePhase enum usage
   - GameState serialization with blast zones
   - Config loading and validation

9. **Run all existing tests** to ensure no breaking changes

10. **Update this Dev Agent Record** with:
    - Summary of changes made
    - Any issues encountered
    - Test results
    - Files created/modified]

### Summary

[Fill in summary of implementation work]

### Work Completed

- [ ] [List completed tasks]

### Test Results

[Fill in test results - all passing, any failures, coverage]

### Issues Encountered

[Fill in any issues, blockers, or decisions made]

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
