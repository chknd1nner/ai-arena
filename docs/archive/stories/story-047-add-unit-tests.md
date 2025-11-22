# Story 047: Add Unit Tests for Refactored Code

**Epic:** [Epic 007: Technical Debt Reduction & Code Quality](../epic-007-technical-debt-reduction.md)
**Status:** ⏸️ Not Started
**Size:** Small (~0.5 days)
**Priority:** P0 (Quality Gate)

---

## Dev Agent Record

**Implementation Date:** _Pending_
**Agent:** _TBD_
**Status:** ⏸️ Not Started

### Instructions for Dev Agent

When implementing this story:

1. **Create unit tests** for all shared utilities from Story 043
2. **Create tests** for prompt formatters
3. **Create tests** for frontend hooks (useAnimationLoop)
4. **Run coverage report** to verify 90%+ coverage for refactored code
5. **Ensure all tests pass** in CI/CD

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of tests written
- Coverage report results
- File paths for all test files created
- Any issues encountered and resolutions

---

## QA Agent Record

**Validation Date:** _Pending_
**Validator:** _TBD_
**Verdict:** ⏸️ Awaiting Implementation

### QA Checklist

- [ ] `tests/test_utils.py` exists with 90%+ coverage
- [ ] `tests/test_prompt_formatter.py` exists with 90%+ coverage
- [ ] Frontend hook tests exist and pass
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Coverage report generated
- [ ] No regressions in existing tests
- [ ] CI/CD pipeline passes

**After validation, update this section with:**
- QA date and validator name
- Test coverage results
- Test execution results
- Any failing tests and their resolution
- Final verdict

---

## User Story

**As a** developer maintaining AI-Arena
**I want** comprehensive unit tests for all refactored code
**So that** I have confidence that refactoring didn't break functionality and future changes won't introduce regressions

### Context

Stories 041-046 refactored significant portions of the codebase:
- Shared utilities (`game_engine/utils.py`, `llm_adapter/prompt_formatter.py`)
- Frontend hooks (`useAnimationLoop`)
- Physics engine changes
- LLM adapter changes

**Without tests:**
- No confidence refactoring didn't break things
- Future changes risk regressions
- Hard to verify edge cases handled correctly

### Goal

Write comprehensive unit tests for all refactored code with 90%+ coverage.

---

## Acceptance Criteria

### Must Have:

- [ ] `tests/test_utils.py` with 90%+ coverage of `game_engine/utils.py`
- [ ] `tests/test_prompt_formatter.py` with 90%+ coverage of `llm_adapter/prompt_formatter.py`
- [ ] Frontend hook tests (`useAnimationLoop.test.js`)
- [ ] All tests pass (`pytest tests/ -v` and `npm test`)
- [ ] Coverage report shows no regressions
- [ ] CI/CD pipeline passes

### Should Have:

- [ ] Edge case tests (null inputs, boundary values, error conditions)
- [ ] Integration tests for refactored components
- [ ] Performance tests (where applicable)

### Nice to Have:

- [ ] Mutation testing to verify test quality
- [ ] Test documentation/comments

---

## Technical Specification

### Test Coverage Requirements

| Module | Coverage Target | Priority |
|--------|----------------|----------|
| `game_engine/utils.py` | 90%+ | P0 |
| `llm_adapter/prompt_formatter.py` | 90%+ | P0 |
| `hooks/useAnimationLoop.js` | 80%+ | P1 |

### Testing Framework

**Backend (Python):**
- `pytest` for test execution
- `pytest-cov` for coverage reporting
- `pytest-asyncio` for async tests (if needed)

**Frontend (JavaScript):**
- `Jest` for unit tests
- `@testing-library/react-hooks` for hook testing

---

## Implementation Guidance

### Backend Tests

#### Test 1: `tests/test_utils.py`

```python
"""
Unit tests for game_engine/utils.py

Tests for shared utility functions used across the game engine.
"""
import pytest
import copy
from ai_arena.game_engine.utils import parse_torpedo_action, deep_copy_game_state
from ai_arena.game_engine.data_models import (
    GameState, ShipState, TorpedoState, BlastZone, Vec2D, PhaserConfig, BlastZonePhase
)


class TestParseTorpedoAction:
    """Tests for parse_torpedo_action() function."""

    def test_movement_command_straight(self):
        """Test parsing simple movement command."""
        action_type, delay = parse_torpedo_action("STRAIGHT")
        assert action_type == "STRAIGHT"
        assert delay is None

    def test_movement_command_hard_left(self):
        """Test parsing HARD_LEFT command."""
        action_type, delay = parse_torpedo_action("HARD_LEFT")
        assert action_type == "HARD_LEFT"
        assert delay is None

    def test_movement_command_hard_right(self):
        """Test parsing HARD_RIGHT command."""
        action_type, delay = parse_torpedo_action("HARD_RIGHT")
        assert action_type == "HARD_RIGHT"
        assert delay is None

    def test_detonate_after_valid_middle(self):
        """Test parsing valid detonate_after command."""
        action_type, delay = parse_torpedo_action("detonate_after:8.5")
        assert action_type == "detonate_after"
        assert delay == 8.5

    def test_detonate_after_min_boundary(self):
        """Test detonate_after at minimum boundary (0.0)."""
        action_type, delay = parse_torpedo_action("detonate_after:0.0")
        assert action_type == "detonate_after"
        assert delay == 0.0

    def test_detonate_after_max_boundary(self):
        """Test detonate_after at maximum boundary (15.0)."""
        action_type, delay = parse_torpedo_action("detonate_after:15.0")
        assert action_type == "detonate_after"
        assert delay == 15.0

    def test_detonate_after_out_of_range_negative(self):
        """Test detonate_after with negative delay (should raise ValueError)."""
        with pytest.raises(ValueError, match="outside valid range"):
            parse_torpedo_action("detonate_after:-0.1")

    def test_detonate_after_out_of_range_too_high(self):
        """Test detonate_after with delay > 15.0 (should raise ValueError)."""
        with pytest.raises(ValueError, match="outside valid range"):
            parse_torpedo_action("detonate_after:15.1")

    def test_invalid_delay_format_non_numeric(self):
        """Test invalid delay format (non-numeric)."""
        with pytest.raises(ValueError, match="Invalid detonation delay format"):
            parse_torpedo_action("detonate_after:abc")

    def test_invalid_delay_format_empty(self):
        """Test invalid delay format (empty string after colon)."""
        with pytest.raises(ValueError, match="Invalid detonation delay format"):
            parse_torpedo_action("detonate_after:")

    def test_case_insensitive_detonate_after(self):
        """Test that detonate_after is case-insensitive."""
        action_type1, delay1 = parse_torpedo_action("detonate_after:5.0")
        action_type2, delay2 = parse_torpedo_action("DETONATE_AFTER:5.0")
        action_type3, delay3 = parse_torpedo_action("Detonate_After:5.0")

        assert action_type1 == action_type2 == action_type3 == "detonate_after"
        assert delay1 == delay2 == delay3 == 5.0


class TestDeepCopyGameState:
    """Tests for deep_copy_game_state() function."""

    def create_test_state(self):
        """Helper to create a test GameState."""
        ship_a = ShipState(
            position=Vec2D(100, 200),
            velocity=Vec2D(10, 5),
            heading=1.57,
            shields=85,
            ae=67,
            phaser_config=PhaserConfig.WIDE,
            reconfiguring_phaser=False,
            phaser_cooldown_remaining=0.0
        )
        ship_b = ShipState(
            position=Vec2D(500, 300),
            velocity=Vec2D(-10, -5),
            heading=3.14,
            shields=92,
            ae=54,
            phaser_config=PhaserConfig.FOCUSED,
            reconfiguring_phaser=False,
            phaser_cooldown_remaining=2.5
        )
        torpedo = TorpedoState(
            id="torpedo_1",
            position=Vec2D(250, 250),
            velocity=Vec2D(15, 0),
            heading=0.0,
            ae_remaining=30,
            owner="ship_a",
            just_launched=False
        )
        blast_zone = BlastZone(
            id="blast_1",
            position=Vec2D(200, 200),
            base_damage=45.0,
            phase=BlastZonePhase.EXPANSION,
            age=2.5,
            current_radius=7.5,
            owner="ship_a"
        )

        return GameState(
            turn=5,
            ship_a=ship_a,
            ship_b=ship_b,
            torpedoes=[torpedo],
            blast_zones=[blast_zone]
        )

    def test_creates_new_object(self):
        """Test that deep copy creates a new object."""
        state = self.create_test_state()
        state_copy = deep_copy_game_state(state)

        assert state is not state_copy
        assert id(state) != id(state_copy)

    def test_creates_new_nested_objects(self):
        """Test that nested objects are also copied."""
        state = self.create_test_state()
        state_copy = deep_copy_game_state(state)

        assert state.ship_a is not state_copy.ship_a
        assert state.ship_b is not state_copy.ship_b
        assert state.torpedoes[0] is not state_copy.torpedoes[0]
        assert state.blast_zones[0] is not state_copy.blast_zones[0]

    def test_preserves_values(self):
        """Test that all values are preserved in the copy."""
        state = self.create_test_state()
        state_copy = deep_copy_game_state(state)

        assert state.turn == state_copy.turn
        assert state.ship_a.shields == state_copy.ship_a.shields
        assert state.ship_a.position.x == state_copy.ship_a.position.x
        assert state.ship_b.ae == state_copy.ship_b.ae
        assert state.torpedoes[0].id == state_copy.torpedoes[0].id
        assert state.blast_zones[0].age == state_copy.blast_zones[0].age

    def test_modifications_are_independent(self):
        """Test that modifying copy doesn't affect original."""
        state = self.create_test_state()
        state_copy = deep_copy_game_state(state)

        # Modify copy
        state_copy.turn = 999
        state_copy.ship_a.shields = 0
        state_copy.ship_a.position.x = -999
        state_copy.torpedoes[0].ae_remaining = 0
        state_copy.blast_zones[0].age = 100.0

        # Original unchanged
        assert state.turn == 5
        assert state.ship_a.shields == 85
        assert state.ship_a.position.x == 100
        assert state.torpedoes[0].ae_remaining == 30
        assert state.blast_zones[0].age == 2.5

    def test_nested_vec2d_independence(self):
        """Test that Vec2D objects are deep copied."""
        state = self.create_test_state()
        state_copy = deep_copy_game_state(state)

        # Modify copy's Vec2D
        state_copy.ship_a.position.x = 9999
        state_copy.ship_a.position.y = 9999

        # Original Vec2D unchanged
        assert state.ship_a.position.x == 100
        assert state.ship_a.position.y == 200
```

#### Test 2: `tests/test_prompt_formatter.py`

```python
"""
Unit tests for llm_adapter/prompt_formatter.py

Tests for prompt formatting utility functions.
"""
import pytest
import numpy as np
from ai_arena.llm_adapter.prompt_formatter import (
    format_ship_status,
    format_enemy_status,
    format_torpedo_list,
    format_blast_zones
)
from ai_arena.game_engine.data_models import (
    ShipState, TorpedoState, BlastZone, Vec2D, PhaserConfig, BlastZonePhase
)


class MockTorpedo:
    """Mock torpedo for testing."""
    def __init__(self, id, position, ae_remaining):
        self.id = id
        self.position = position
        self.ae_remaining = ae_remaining


class MockBlastZone:
    """Mock blast zone for testing."""
    def __init__(self, id, position, phase, age, current_radius, base_damage, owner):
        self.id = id
        self.position = position
        self.phase = phase
        self.age = age
        self.current_radius = current_radius
        self.base_damage = base_damage
        self.owner = owner


class TestFormatShipStatus:
    """Tests for format_ship_status()."""

    def test_basic_ship_status(self):
        """Test basic ship status formatting."""
        ship = ShipState(
            position=Vec2D(100, 200),
            velocity=Vec2D(0, 0),
            heading=1.5708,  # ~90 degrees
            shields=85,
            ae=67,
            phaser_config=PhaserConfig.WIDE,
            reconfiguring_phaser=False,
            phaser_cooldown_remaining=0.0
        )

        result = format_ship_status(ship, "ship_a")

        assert "ship_a" in result
        assert "100.0" in result  # Position X
        assert "200.0" in result  # Position Y
        assert "85" in result  # Shields
        assert "67" in result  # AE
        assert "WIDE" in result  # Phaser config

    def test_heading_in_degrees(self):
        """Test that heading is converted to degrees."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=np.pi,  # 180 degrees
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.FOCUSED,
            reconfiguring_phaser=False,
            phaser_cooldown_remaining=0.0
        )

        result = format_ship_status(ship, "ship_b")

        # Should contain degrees (180 or close to it)
        assert "180" in result or "179.9" in result

    def test_phaser_cooldown_displayed(self):
        """Test that phaser cooldown is displayed."""
        ship = ShipState(
            position=Vec2D(0, 0),
            velocity=Vec2D(0, 0),
            heading=0.0,
            shields=100,
            ae=100,
            phaser_config=PhaserConfig.WIDE,
            reconfiguring_phaser=False,
            phaser_cooldown_remaining=2.5
        )

        result = format_ship_status(ship, "ship_a")

        assert "2.5" in result  # Cooldown value


class TestFormatTorpedoList:
    """Tests for format_torpedo_list()."""

    def test_empty_torpedo_list(self):
        """Test formatting empty torpedo list."""
        result = format_torpedo_list([], "ship_a")

        assert "0/4" in result
        assert "None active" in result

    def test_single_torpedo(self):
        """Test formatting single torpedo."""
        torpedoes = [
            MockTorpedo("torpedo_1", Vec2D(50, 50), 30)
        ]

        result = format_torpedo_list(torpedoes, "ship_a")

        assert "1/4" in result
        assert "torpedo_1" in result
        assert "50.0" in result
        assert "30" in result

    def test_multiple_torpedoes(self):
        """Test formatting multiple torpedoes."""
        torpedoes = [
            MockTorpedo("torpedo_1", Vec2D(50, 50), 30),
            MockTorpedo("torpedo_2", Vec2D(100, 100), 25),
            MockTorpedo("torpedo_3", Vec2D(150, 150), 20),
        ]

        result = format_torpedo_list(torpedoes, "ship_a")

        assert "3/4" in result
        assert "torpedo_1" in result
        assert "torpedo_2" in result
        assert "torpedo_3" in result


class TestFormatBlastZones:
    """Tests for format_blast_zones()."""

    def test_empty_blast_zones(self):
        """Test formatting empty blast zone list."""
        our_position = Vec2D(0, 0)
        result = format_blast_zones([], our_position, "ship_a")

        assert "None active" in result

    def test_single_blast_zone_enemy(self):
        """Test formatting enemy blast zone."""
        zones = [
            MockBlastZone(
                id="blast_1",
                position=Vec2D(100, 100),
                phase=BlastZonePhase.EXPANSION,
                age=2.5,
                current_radius=7.5,
                base_damage=45.0,
                owner="ship_b"
            )
        ]

        our_position = Vec2D(0, 0)
        result = format_blast_zones(zones, our_position, "ship_a")

        assert "1 active" in result
        assert "blast_1" in result
        assert "ENEMY" in result  # Enemy's blast zone
        assert "EXPANSION" in result

    def test_blast_zone_our_own(self):
        """Test formatting our own blast zone."""
        zones = [
            MockBlastZone(
                id="blast_1",
                position=Vec2D(100, 100),
                phase=BlastZonePhase.PERSISTENCE,
                age=10.0,
                current_radius=15.0,
                base_damage=45.0,
                owner="ship_a"
            )
        ]

        our_position = Vec2D(0, 0)
        result = format_blast_zones(zones, our_position, "ship_a")

        assert "YOUR" in result  # Our own blast zone

    def test_blast_zone_warning_when_inside(self):
        """Test warning when ship is inside blast zone."""
        zones = [
            MockBlastZone(
                id="blast_danger",
                position=Vec2D(10, 10),  # Very close
                phase=BlastZonePhase.PERSISTENCE,
                age=10.0,
                current_radius=20.0,  # Large radius
                base_damage=45.0,
                owner="ship_b"
            )
        ]

        our_position = Vec2D(15, 15)  # Inside the blast radius
        result = format_blast_zones(zones, our_position, "ship_a")

        assert "⚠️" in result or "WARNING" in result.upper()
        assert "INSIDE" in result.upper()
```

### Frontend Tests

#### Test 3: `frontend/src/hooks/__tests__/useAnimationLoop.test.js`

**(Already provided in Story 046)**

---

## Testing Requirements

### Running Tests

**Backend:**
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_utils.py -v

# Run with coverage
pytest tests/ -v --cov=ai_arena --cov-report=html

# Open coverage report
open htmlcov/index.html
```

**Frontend:**
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test useAnimationLoop.test.js
```

### Coverage Targets

| Module | Current | Target | Status |
|--------|---------|--------|--------|
| `game_engine/utils.py` | 0% | 90%+ | ⏸️ Not Started |
| `llm_adapter/prompt_formatter.py` | 0% | 90%+ | ⏸️ Not Started |
| `hooks/useAnimationLoop.js` | 0% | 80%+ | ⏸️ Not Started |

---

## Files to Create

### Backend Tests (2 files):
1. **`tests/test_utils.py`** - Tests for `game_engine/utils.py`
2. **`tests/test_prompt_formatter.py`** - Tests for `llm_adapter/prompt_formatter.py`

### Frontend Tests (1 file):
3. **`frontend/src/hooks/__tests__/useAnimationLoop.test.js`** - Tests for animation hook (from Story 046)

---

## Files to Modify

None - only creating new test files.

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] `tests/test_utils.py` created with 90%+ coverage
- [ ] `tests/test_prompt_formatter.py` created with 90%+ coverage
- [ ] Frontend hook tests created
- [ ] All tests pass (`pytest` and `npm test`)
- [ ] Coverage report generated
- [ ] No regressions in existing tests
- [ ] CI/CD pipeline passes
- [ ] Code reviewed

---

## Dependencies

**Blocks:**
- Epic 007 completion (this is the final quality gate)

**Blocked By:**
- All previous stories (041-046) must be complete

---

## Notes

### Design Decisions

- **90% coverage target**: High confidence without excessive test burden
- **Edge case focus**: Boundary values, error conditions, null inputs
- **Fast tests**: Unit tests should run quickly (<1s per test)
- **Clear test names**: Descriptive names explain what's being tested

### Benefits

After this story:
- ✅ Confidence that refactoring didn't break functionality
- ✅ Protection against future regressions
- ✅ Documentation via tests (show how code should be used)
- ✅ Easier debugging (failing tests pinpoint issues)

### Test Quality Checklist

Good unit tests should be:
- **Fast**: Run in milliseconds
- **Independent**: No dependencies on other tests
- **Repeatable**: Same result every time
- **Self-validating**: Pass or fail (no manual checking)
- **Timely**: Written alongside code

### CI/CD Integration

Ensure tests run in CI/CD pipeline:

```yaml
# .github/workflows/test.yml (example)
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v --cov=ai_arena --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: 16
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Run tests
        run: cd frontend && npm test -- --coverage
```
