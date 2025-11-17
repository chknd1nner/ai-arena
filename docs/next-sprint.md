# Next Sprint: Epic 005 - Story 028

**Sprint Goal:** Implement blast zone data models foundation for advanced torpedo system

**Story:** [Story 028: Blast Zone Data Models](stories/story-028-blast-zone-data-models.md)

**Estimated Duration:** 1-2 hours

**Branch:** `claude/epic-005-story-028-blast-zone-models-[session-id]`

---

## Sprint Overview

This sprint kicks off **Epic 005: Advanced Torpedo & Blast Zone System**, implementing the foundational data models needed for persistent blast zones with timed detonation. This is P0 work that completes the core weapon system from the game specification.

### Why This Story First?

Story 028 is the foundation for all Epic 005 work:
- Creates the `BlastZone` and `BlastZonePhase` data structures
- Updates `GameState` to track blast zones
- Adds `detonation_timer` to torpedoes
- Establishes configuration parameters
- **No dependencies** on other Epic 005 stories
- **Independently testable** via data model tests
- **Blocks no other work** while in progress

### Epic 005 Context

From the game specification (docs/game_spec_revised.md lines 351-387):
- Torpedoes create **persistent blast zones** on detonation
- Blast zones have 70-second lifecycle: Expansion (5s) → Persistence (60s) → Dissipation (5s)
- Continuous damage while ships inside blast radius
- Self-damage enabled (tactical risk/reward)
- LLM-controlled timed detonation

**Current state:**
- ✅ Torpedoes launch, fly, and collide (Epic 002-004)
- ❌ No timed detonation (instant collision only)
- ❌ No persistent blast zones (damage is instant, not area-based)
- ❌ No lifecycle phases (expansion/persistence/dissipation)

**After Story 028:**
- ✅ Data structures exist for blast zones
- ✅ Configuration supports blast zone parameters
- ⏳ Ready for Story 029 (timed detonation implementation)

---

## Your Task: Implement Story 028

### Step 1: Read the Story

**Start by reading:**
- [`docs/stories/story-028-blast-zone-data-models.md`](stories/story-028-blast-zone-data-models.md) - Complete story specification
- [`docs/epic-005-torpedo-blast-zones.md`](epic-005-torpedo-blast-zones.md) - Epic context and technical approach
- [`docs/game_spec_revised.md`](game_spec_revised.md) lines 351-387 - Blast zone specification

### Step 2: Understand Current Code

**Read these files to understand the existing architecture:**
- `ai_arena/game_engine/data_models.py` - Current data model patterns (see `ShipState`, `TorpedoState`, `PhaserConfig` enum)
- `config.json` - Configuration structure (see `torpedo` section)
- `ai_arena/config/loader.py` - Config validation patterns (see `TorpedoConfig` class)

**Key patterns to follow:**
- Enums use `Enum` class with string values (see `PhaserConfig`, `MovementDirection`)
- Dataclasses use `@dataclass` decorator with type hints
- Lists use `field(default_factory=list)` pattern
- Config classes mirror JSON structure with validation

### Step 3: Implementation Checklist

Follow the story's **Technical Requirements** section exactly. Here's the implementation order:

#### 3.1: Data Models (`ai_arena/game_engine/data_models.py`)

**Add BlastZonePhase enum:**
```python
class BlastZonePhase(Enum):
    """Lifecycle phase for blast zones."""
    EXPANSION = "expansion"       # Growing from 0→15 units
    PERSISTENCE = "persistence"   # Holding at 15 units
    DISSIPATION = "dissipation"   # Shrinking from 15→0 units
```

**Add BlastZone dataclass:**
```python
@dataclass
class BlastZone:
    """Persistent area of damage from torpedo detonation.

    Lifecycle: Expansion (5s) → Persistence (60s) → Dissipation (5s) = 70s total

    Attributes:
        id: Unique identifier (e.g., "ship_a_torp_5_blast")
        position: Center point of blast zone (fixed for lifetime)
        base_damage: Total damage potential ((AE at detonation) × 1.5)
        phase: Current lifecycle phase (EXPANSION/PERSISTENCE/DISSIPATION)
        age: Time since creation in seconds (0.0 → 70.0)
        current_radius: Current blast radius in units (0.0 → 15.0 → 15.0 → 0.0)
        owner: Ship that launched torpedo ("ship_a" or "ship_b")
    """
    id: str
    position: Vec2D
    base_damage: float
    phase: BlastZonePhase
    age: float
    current_radius: float
    owner: str
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
    detonation_timer: Optional[float] = None  # NEW: Seconds until timed detonation
```

#### 3.2: Configuration (`config.json`)

**Add blast zone parameters to torpedo section:**
```json
{
  "torpedo": {
    "launch_cost_ae": 20,
    "max_ae_capacity": 40,
    "speed_units_per_second": 4.0,
    "max_active_per_ship": 4,
    "blast_radius_units": 15.0,
    "blast_damage_multiplier": 1.5,
    "blast_expansion_seconds": 5.0,
    "blast_persistence_seconds": 60.0,
    "blast_dissipation_seconds": 5.0
  }
}
```

**Parameters explained:**
- `blast_expansion_seconds`: Time for radius to grow from 0→15 units (5.0s)
- `blast_persistence_seconds`: Time at full radius (60.0s)
- `blast_dissipation_seconds`: Time for radius to shrink from 15→0 units (5.0s)
- `blast_radius_units`: Maximum blast zone radius (15.0 units)
- `blast_damage_multiplier`: Converts AE to damage (1.5×)

#### 3.3: Config Loader (`ai_arena/config/loader.py`)

**Update TorpedoConfig class:**
```python
@dataclass
class TorpedoConfig:
    launch_cost_ae: int
    max_ae_capacity: int
    speed_units_per_second: float
    max_active_per_ship: int
    blast_radius_units: float
    blast_damage_multiplier: float
    blast_expansion_seconds: float      # NEW
    blast_persistence_seconds: float    # NEW
    blast_dissipation_seconds: float    # NEW
```

**Add validation (if not auto-validated):**
- Ensure all blast zone parameters are positive numbers
- Consider adding min/max ranges if ConfigLoader does validation

#### 3.4: Tests (`tests/test_blast_zone_models.py`)

**Create comprehensive test file with ~6-8 tests:**

```python
import pytest
from ai_arena.game_engine.data_models import (
    BlastZone, BlastZonePhase, GameState, TorpedoState, Vec2D, ShipState
)
from ai_arena.config import ConfigLoader

def test_blast_zone_phase_enum():
    """Test BlastZonePhase enum has all required values."""
    assert BlastZonePhase.EXPANSION.value == "expansion"
    assert BlastZonePhase.PERSISTENCE.value == "persistence"
    assert BlastZonePhase.DISSIPATION.value == "dissipation"

def test_blast_zone_creation():
    """Test BlastZone can be created with all required fields."""
    zone = BlastZone(
        id="ship_a_torp_1_blast",
        position=Vec2D(100.0, 150.0),
        base_damage=45.0,
        phase=BlastZonePhase.EXPANSION,
        age=0.0,
        current_radius=0.0,
        owner="ship_a"
    )
    assert zone.id == "ship_a_torp_1_blast"
    assert zone.position.x == 100.0
    assert zone.position.y == 150.0
    assert zone.base_damage == 45.0
    assert zone.phase == BlastZonePhase.EXPANSION
    assert zone.age == 0.0
    assert zone.current_radius == 0.0
    assert zone.owner == "ship_a"

def test_game_state_with_blast_zones():
    """Test GameState can hold blast zones."""
    # Create game state with empty blast zones
    state = GameState(
        turn=1,
        ship_a=ShipState(...),  # Use appropriate constructor
        ship_b=ShipState(...),
        torpedoes=[],
        blast_zones=[]
    )
    assert state.blast_zones == []

    # Add blast zone
    zone = BlastZone(...)
    state.blast_zones.append(zone)
    assert len(state.blast_zones) == 1

def test_torpedo_state_with_detonation_timer():
    """Test TorpedoState has optional detonation_timer field."""
    # Torpedo without timer (auto-detonate)
    torp1 = TorpedoState(
        id="ship_a_torp_1",
        # ... other fields ...
        detonation_timer=None
    )
    assert torp1.detonation_timer is None

    # Torpedo with timer (timed detonation)
    torp2 = TorpedoState(
        id="ship_a_torp_2",
        # ... other fields ...
        detonation_timer=8.5
    )
    assert torp2.detonation_timer == 8.5

def test_config_loading_blast_zone_params():
    """Test config.json loads with blast zone parameters."""
    config = ConfigLoader().load("config.json")
    assert config.torpedo.blast_expansion_seconds == 5.0
    assert config.torpedo.blast_persistence_seconds == 60.0
    assert config.torpedo.blast_dissipation_seconds == 5.0
    assert config.torpedo.blast_radius_units == 15.0
    assert config.torpedo.blast_damage_multiplier == 1.5

def test_blast_zone_serialization():
    """Test BlastZone can be serialized to dict/JSON."""
    zone = BlastZone(...)
    # Test serialization logic (if implemented)
    # This may be handled by dataclasses automatically

# Add more tests as needed:
# - Test GameState serialization with blast_zones
# - Test invalid blast zone parameters
# - Test edge cases (negative age, negative radius, etc.)
```

### Step 4: Validation

**Before marking story complete, verify:**

1. **All tests pass:**
   ```bash
   pytest tests/test_blast_zone_models.py -v
   pytest tests/ -v  # Full suite to check for regressions
   ```

2. **Code quality:**
   - [ ] Type hints on all new fields
   - [ ] Docstrings on `BlastZone` and `BlastZonePhase`
   - [ ] Follows existing code style (see other data models)
   - [ ] No breaking changes to existing code

3. **Configuration:**
   - [ ] `config.json` parses without errors
   - [ ] Config loader validates new fields
   - [ ] Sensible default values (match game spec)

4. **Acceptance criteria met:**
   - [ ] All 8 criteria from story checked off
   - [ ] See "Acceptance Criteria" section in story

### Step 5: Documentation

**Update the Dev Agent Record in story-028:**
- Fill in implementation date, agent name, status
- Write summary of changes made
- List files created/modified
- Document test results (e.g., "8 tests, all passing")
- Note any issues encountered or decisions made

### Step 6: Commit and Push

**Create clear commit message:**
```bash
git add ai_arena/game_engine/data_models.py \
        ai_arena/config/loader.py \
        config.json \
        tests/test_blast_zone_models.py \
        docs/stories/story-028-blast-zone-data-models.md

git commit -m "$(cat <<'EOF'
Story 028: Blast Zone Data Models

Implemented foundational data structures for Epic 005 blast zone system:
- Created BlastZonePhase enum (EXPANSION/PERSISTENCE/DISSIPATION)
- Created BlastZone dataclass with lifecycle tracking
- Updated GameState to include blast_zones list
- Updated TorpedoState with detonation_timer field
- Added blast zone config parameters to config.json
- Updated TorpedoConfig in config loader with validation

Tests: 8 new tests in test_blast_zone_models.py, all passing
Coverage: BlastZone creation, serialization, config loading
Regressions: None - all 149 existing tests still pass

Ready for Story 029 (Timed Torpedo Detonation)
EOF
)"

git push -u origin claude/epic-005-story-028-blast-zone-models-[session-id]
```

---

## Success Criteria

**Story 028 is complete when:**
- [ ] BlastZonePhase enum exists with 3 values
- [ ] BlastZone dataclass exists with 7 fields
- [ ] GameState.blast_zones field exists
- [ ] TorpedoState.detonation_timer field exists
- [ ] config.json has 5 new blast zone parameters
- [ ] Config loader validates blast zone parameters
- [ ] 6-8 new tests in test_blast_zone_models.py pass
- [ ] All 149 existing tests still pass (no regressions)
- [ ] Dev Agent Record filled out completely
- [ ] Code committed and pushed

---

## Next Steps After Story 028

Once this story is complete and QA-approved:
- **Story 029:** Timed Torpedo Detonation (implement command parsing, timer mechanics, blast zone creation)
- **Story 030:** Blast Zone Expansion Phase (implement radius growth at 3 units/second)
- **Stories 031-035:** Persistence, dissipation, damage, self-damage, and integration

---

## Key References

- **Game Spec:** `docs/game_spec_revised.md` (lines 351-387 for blast zones)
- **Epic 005:** `docs/epic-005-torpedo-blast-zones.md` (full epic plan)
- **Story 028:** `docs/stories/story-028-blast-zone-data-models.md` (this story's details)
- **CLAUDE.md:** Project development guide
- **Architecture:** `docs/architecture.md` (system design context)

---

## Questions or Issues?

If you encounter blockers:
1. Review the "Instructions for Dev Agent" in the story file
2. Check Epic 005 for technical approach details
3. Look at existing data models for patterns
4. Document issues in Dev Agent Record
5. Mark story as "Blocked" if unable to complete

---

**Good luck! This is the foundation of a major feature. Take your time and follow the patterns established in Epic 004.**

🚀 **Ready to begin Story 028!**
