# Story 043: Consolidate Duplicate Code

**Epic:** [Epic 007: Technical Debt Reduction & Code Quality](../epic-007-technical-debt-reduction.md)
**Status:** ⏸️ Not Started
**Size:** Medium (~1.5 days)
**Priority:** P0

---

## Dev Agent Record

**Implementation Date:** _Pending_
**Agent:** _TBD_
**Status:** ⏸️ Not Started

### Instructions for Dev Agent

When implementing this story:

1. **Create shared utility modules** (`game_engine/utils.py`, `llm_adapter/prompt_formatter.py`)
2. **Consolidate duplicate implementations** (torpedo parsing, state copying, formatting)
3. **Update all import statements** to use shared utilities
4. **Run comprehensive tests** to ensure no regressions
5. **Verify Match Orchestrator uses public APIs** (not private methods)

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of work completed
- Design decisions for shared utilities
- File paths for all created/modified files
- Any issues encountered and resolutions
- Code references (file:line format)

---

## QA Agent Record

**Validation Date:** _Pending_
**Validator:** _TBD_
**Verdict:** ⏸️ Awaiting Implementation

### QA Checklist

- [ ] `ai_arena/game_engine/utils.py` created with shared functions
- [ ] `ai_arena/llm_adapter/prompt_formatter.py` created
- [ ] `parse_torpedo_action()` only exists once (in utils.py)
- [ ] State copying uses `copy.deepcopy()` with proper handling
- [ ] `PhysicsEngine.copy_state()` is public method
- [ ] Match Orchestrator uses public API only
- [ ] Prompt formatting functions are reusable
- [ ] All tests pass (physics, LLM adapter, orchestrator)
- [ ] No duplicate code found in grep audit

**After validation, update this section with:**
- QA date and validator name
- Test results for each criterion
- Code duplication audit results
- Any bugs found and their resolution
- Final verdict (Pass/Fail with justification)

---

## User Story

**As a** developer maintaining AI-Arena
**I want** duplicate code consolidated into shared utility modules
**So that** there's a single source of truth for shared logic, reducing bugs and maintenance burden

### Context

Currently, several pieces of logic are duplicated across the codebase:

1. **Torpedo Action Parsing** - Exists in both:
   - `ai_arena/game_engine/physics.py:413-442`
   - `ai_arena/llm_adapter/adapter.py:392-421`

2. **State Copying** - Inconsistent implementations:
   - `physics.py`: Manual `_copy_state()` with comment "A proper deepcopy would be better"
   - Orchestrator accesses private method: `state_for_replay = self.physics_engine._copy_state(state)`

3. **Prompt Formatting** - Repeated code in `adapter.py`:
   - Ship status formatting
   - Torpedo list formatting
   - Blast zone formatting

**Problems:**
- Changes must be synchronized across duplicate implementations
- Bug fixes might miss one location
- No clear "source of truth"
- Hard to test duplicate logic separately

### Goal

Create shared utility modules and consolidate all duplicate code into single, well-tested implementations.

---

## Acceptance Criteria

### Must Have:

- [ ] `ai_arena/game_engine/utils.py` created with shared game utilities
- [ ] `ai_arena/llm_adapter/prompt_formatter.py` created with formatting functions
- [ ] `parse_torpedo_action()` only exists once (in `utils.py`)
- [ ] `PhysicsEngine.copy_state()` is public method (not private `_copy_state()`)
- [ ] Match Orchestrator uses public `copy_state()` method
- [ ] State copying uses `copy.deepcopy()` with proper memo handling
- [ ] All tests pass (no regressions)

### Should Have:

- [ ] Prompt formatting functions are pure functions (no side effects)
- [ ] Comprehensive unit tests for shared utilities
- [ ] Documentation for shared modules

### Nice to Have:

- [ ] Type hints for all shared functions
- [ ] Docstrings following NumPy/Google style

---

## Technical Specification

### Current Duplication Analysis

#### 1. Torpedo Action Parsing (Duplicated)

**Location 1: `physics.py:413-442`**
```python
def _parse_torpedo_action(self, action_str: str) -> Tuple[str, Optional[float]]:
    if ":" in action_str:
        parts = action_str.split(":", 1)
        if parts[0].lower() == "detonate_after":
            delay = float(parts[1])
            if delay < 0.0 or delay > 15.0:
                raise ValueError(f"Detonation delay {delay} outside valid range")
            return ("detonate_after", delay)
    return (action_str, None)
```

**Location 2: `adapter.py:392-421`**
```python
def _parse_torpedo_action(self, action_str: str) -> Tuple[str, Optional[float]]:
    # IDENTICAL implementation (30 lines)
```

**Solution:** Move to `ai_arena/game_engine/utils.py` as standalone function.

#### 2. State Copying (Inconsistent)

**Current: `physics.py:172-180`**
```python
def _copy_state(self, state: GameState) -> GameState:
    # A proper deepcopy would be better, but this is fine for now
    return GameState(
        turn=state.turn,
        ship_a=ShipState(**state.ship_a.__dict__),
        ship_b=ShipState(**state.ship_b.__dict__),
        torpedoes=[TorpedoState(**t.__dict__) for t in state.torpedoes],
        blast_zones=[BlastZone(**bz.__dict__) for bz in state.blast_zones]
    )
```

**Problem:** Manual copying is fragile (breaks if dataclass structure changes).

**Solution:** Use `copy.deepcopy()` with proper handling.

#### 3. Prompt Formatting (Repeated)

**Current: `adapter.py:343-384`**
```python
# Ship status formatting (inline)
user_prompt = f"""YOUR STATUS ({ship_id}):
- Position: ({us.position.x:.1f}, {us.position.y:.1f})
- Heading: {np.degrees(us.heading):.1f}°
[...]
"""

# Torpedo formatting (inline)
for t in our_torpedoes:
    user_prompt += f"\n- {t.id}: pos ({t.position.x:.1f}, {t.position.y:.1f}), AE {t.ae_remaining}"

# Blast zone formatting (inline)
for zone in state.blast_zones:
    user_prompt += f"\n- {zone.id} ({owner_marker}):"
    user_prompt += f"\n  Position: ({zone.position.x:.1f}, {zone.position.y:.1f})"
    [...]
```

**Solution:** Extract to reusable formatting functions.

---

## Implementation Guidance

### Step 1: Create `ai_arena/game_engine/utils.py` (0.3 days)

```python
"""
Shared game engine utilities.

This module contains shared functions used across the game engine.
"""
from typing import Tuple, Optional
import copy
import logging

logger = logging.getLogger(__name__)

def parse_torpedo_action(action_str: str) -> Tuple[str, Optional[float]]:
    """Parse torpedo action string.

    Args:
        action_str: Action string, e.g., "HARD_LEFT" or "detonate_after:8.5"

    Returns:
        Tuple of (action_type, delay) where delay is None for movement commands

    Raises:
        ValueError: If delay is outside valid range [0.0, 15.0] or format is invalid

    Examples:
        >>> parse_torpedo_action("HARD_LEFT")
        ("HARD_LEFT", None)

        >>> parse_torpedo_action("detonate_after:8.5")
        ("detonate_after", 8.5)
    """
    if ":" in action_str:
        # Handle "detonate_after:X" commands
        parts = action_str.split(":", 1)
        if parts[0].lower() == "detonate_after":
            try:
                delay = float(parts[1])
            except (ValueError, IndexError) as e:
                logger.error(f"Invalid detonation delay format: {action_str}")
                raise ValueError(f"Invalid detonation delay format: {action_str}") from e

            # Validate delay range
            if delay < 0.0 or delay > 15.0:
                raise ValueError(f"Detonation delay {delay} outside valid range [0.0, 15.0]")

            return ("detonate_after", delay)

    # Regular movement command
    return (action_str, None)


def deep_copy_game_state(state):
    """Deep copy a GameState object.

    Uses copy.deepcopy() with proper handling for nested objects.

    Args:
        state: GameState object to copy

    Returns:
        Deep copy of the GameState

    Note:
        This is safer than manual copying as it handles nested structures
        and will continue to work if dataclass structure changes.
    """
    return copy.deepcopy(state)
```

### Step 2: Create `ai_arena/llm_adapter/prompt_formatter.py` (0.4 days)

```python
"""
Prompt formatting utilities for LLM adapter.

This module contains functions for formatting game state into prompt strings.
"""
import numpy as np
from typing import List

def format_ship_status(ship, ship_id: str) -> str:
    """Format ship status for prompt.

    Args:
        ship: ShipState object
        ship_id: Ship identifier ("ship_a" or "ship_b")

    Returns:
        Formatted ship status string
    """
    return f"""YOUR STATUS ({ship_id}):
- Position: ({ship.position.x:.1f}, {ship.position.y:.1f})
- Heading: {np.degrees(ship.heading):.1f}°
- Shields: {ship.shields}/100
- AE: {ship.ae}/100
- Phaser: {ship.phaser_config.value}
- Phaser Cooldown: {ship.phaser_cooldown_remaining:.1f}s (0 = ready to fire)"""


def format_enemy_status(enemy, our_position) -> str:
    """Format enemy ship status for prompt.

    Args:
        enemy: Enemy ShipState object
        our_position: Our ship's position (for distance calculation)

    Returns:
        Formatted enemy status string
    """
    distance = our_position.distance_to(enemy.position)
    return f"""ENEMY:
- Position: ({enemy.position.x:.1f}, {enemy.position.y:.1f})
- Shields: {enemy.shields}/100
- Distance: {distance:.1f} units"""


def format_torpedo_list(torpedoes: List, owner: str) -> str:
    """Format list of torpedoes for prompt.

    Args:
        torpedoes: List of TorpedoState objects
        owner: Owner ship ID ("ship_a" or "ship_b")

    Returns:
        Formatted torpedo list string
    """
    count = len(torpedoes)
    result = f"\n\nTORPEDOES ({count}/4):"

    if count == 0:
        result += " None active"
    else:
        for t in torpedoes:
            result += f"\n- {t.id}: pos ({t.position.x:.1f}, {t.position.y:.1f}), AE {t.ae_remaining:.0f}"

    return result


def format_blast_zones(blast_zones: List, our_position, our_ship_id: str) -> str:
    """Format blast zones for prompt.

    Args:
        blast_zones: List of BlastZone objects
        our_position: Our ship's position (for distance calculation)
        our_ship_id: Our ship ID (to mark zones as "YOUR" or "ENEMY")

    Returns:
        Formatted blast zone list string
    """
    if not blast_zones:
        return "\n\nBLAST ZONES: None active"

    result = f"\n\nBLAST ZONES ({len(blast_zones)} active):"

    for zone in blast_zones:
        owner_marker = "YOUR" if zone.owner == our_ship_id else "ENEMY"
        result += f"\n- {zone.id} ({owner_marker}):"
        result += f"\n  Position: ({zone.position.x:.1f}, {zone.position.y:.1f})"
        result += f"\n  Phase: {zone.phase.value}, Age: {zone.age:.1f}s"
        result += f"\n  Radius: {zone.current_radius:.1f} units"

        damage_rate = zone.base_damage / 15.0
        result += f"\n  Damage rate: {damage_rate:.2f}/second"

        distance = our_position.distance_to(zone.position)
        result += f"\n  Distance from you: {distance:.1f} units"

        if distance < zone.current_radius:
            result += f"\n  ⚠️  YOU ARE INSIDE THIS BLAST ZONE! Taking {damage_rate:.2f} damage/second!"

    return result
```

### Step 3: Update Physics Engine (0.5 days)

**Modify `ai_arena/game_engine/physics.py`:**

```python
from ai_arena.game_engine.utils import parse_torpedo_action, deep_copy_game_state

class PhysicsEngine:
    # ... existing code ...

    def copy_state(self, state: GameState) -> GameState:
        """Create a deep copy of game state.

        Public method for external use (e.g., Match Orchestrator).

        Args:
            state: GameState to copy

        Returns:
            Deep copy of the state
        """
        return deep_copy_game_state(state)

    def resolve_turn(self, state: GameState, orders_a: Orders, orders_b: Orders):
        """Resolve one complete turn."""
        events = []
        new_state = self.copy_state(state)  # Use public method
        # ... rest of implementation ...

    # DELETE _copy_state() private method

    def _apply_torpedo_orders(self, state: GameState, orders_a: Orders, orders_b: Orders):
        """Apply torpedo orders at start of turn."""
        for torpedo in state.torpedoes:
            orders = orders_a if torpedo.owner == "ship_a" else orders_b
            action_str = orders.torpedo_orders.get(torpedo.id)

            if action_str:
                try:
                    # Use shared utility function
                    action_type, delay = parse_torpedo_action(action_str)
                    if action_type == "detonate_after":
                        torpedo.detonation_timer = delay
                except ValueError as e:
                    logger.warning(f"Invalid torpedo action '{action_str}' for {torpedo.id}: {e}")

    # DELETE _parse_torpedo_action() method
```

### Step 4: Update LLM Adapter (0.5 days)

**Modify `ai_arena/llm_adapter/adapter.py`:**

```python
from ai_arena.game_engine.utils import parse_torpedo_action
from ai_arena.llm_adapter.prompt_formatter import (
    format_ship_status,
    format_enemy_status,
    format_torpedo_list,
    format_blast_zones
)

class LLMAdapter:
    # ... existing code ...

    def _build_prompt(self, state: GameState, ship_id: str) -> list:
        """Build prompt with game state and rules."""
        us = state.ship_a if ship_id == "ship_a" else state.ship_b
        enemy = state.ship_b if ship_id == "ship_a" else state.ship_a
        our_torpedoes = [t for t in state.torpedoes if t.owner == ship_id]
        enemy_torpedoes = [t for t in state.torpedoes if t.owner != ship_id]

        # Load system prompt (from Story 042)
        system_prompt = self.system_prompt_template.format(...)

        # Build user prompt using formatting utilities
        user_prompt = f"TURN {state.turn}\n\n"
        user_prompt += format_ship_status(us, ship_id)
        user_prompt += "\n\n"
        user_prompt += format_enemy_status(enemy, us.position)
        user_prompt += format_torpedo_list(our_torpedoes, ship_id)
        user_prompt += f"\n\nENEMY TORPEDOES ({len(enemy_torpedoes)}):"
        for t in enemy_torpedoes:
            user_prompt += f"\n- {t.id}: pos ({t.position.x:.1f}, {t.position.y:.1f}), AE {t.ae_remaining:.0f}"
        user_prompt += format_blast_zones(state.blast_zones, us.position, ship_id)
        user_prompt += "\n\nYour orders (JSON only):"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    # DELETE _parse_torpedo_action() method (use shared one)
```

### Step 5: Update Match Orchestrator (0.3 days)

**Modify `ai_arena/orchestrator/match_orchestrator.py`:**

```python
import numpy as np

class MatchOrchestrator:
    async def run_match(self, max_turns: int) -> dict:
        """Run a complete match and return results."""
        # ... existing code ...

        for turn in range(1, max_turns + 1):
            orders_a, thinking_a, orders_b, thinking_b = await self.llm_adapter.get_orders_for_both_ships(state)

            # Use public API (not private _copy_state)
            state_for_replay = self.physics_engine.copy_state(state)

            new_state, events = self.physics_engine.resolve_turn(state, orders_a, orders_b)
            # ... rest of implementation ...

    def _initialize_match(self) -> GameState:
        """Initializes the game state using config values."""
        # ... existing code ...

        ship_b = ShipState(
            position=Vec2D((arena_width + spawn_distance) / 2, center_y),
            velocity=Vec2D(0.0, 0.0),
            heading=np.pi,  # Use np.pi instead of 3.14159
            # ... rest of initialization ...
        )
```

---

## Testing Requirements

### Unit Tests for Shared Utilities

Create `tests/test_utils.py`:

```python
import pytest
from ai_arena.game_engine.utils import parse_torpedo_action, deep_copy_game_state
from ai_arena.game_engine.data_models import GameState, ShipState, Vec2D, PhaserConfig

class TestParseTorpedoAction:
    def test_movement_command(self):
        action_type, delay = parse_torpedo_action("HARD_LEFT")
        assert action_type == "HARD_LEFT"
        assert delay is None

    def test_detonate_after_valid(self):
        action_type, delay = parse_torpedo_action("detonate_after:8.5")
        assert action_type == "detonate_after"
        assert delay == 8.5

    def test_detonate_after_min_range(self):
        action_type, delay = parse_torpedo_action("detonate_after:0.0")
        assert delay == 0.0

    def test_detonate_after_max_range(self):
        action_type, delay = parse_torpedo_action("detonate_after:15.0")
        assert delay == 15.0

    def test_detonate_after_out_of_range_low(self):
        with pytest.raises(ValueError, match="outside valid range"):
            parse_torpedo_action("detonate_after:-1.0")

    def test_detonate_after_out_of_range_high(self):
        with pytest.raises(ValueError, match="outside valid range"):
            parse_torpedo_action("detonate_after:16.0")

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid detonation delay format"):
            parse_torpedo_action("detonate_after:invalid")


class TestDeepCopyGameState:
    def test_deep_copy_creates_new_object(self):
        state = create_test_game_state()
        state_copy = deep_copy_game_state(state)

        assert state is not state_copy
        assert state.ship_a is not state_copy.ship_a
        assert state.ship_b is not state_copy.ship_b

    def test_deep_copy_preserves_values(self):
        state = create_test_game_state()
        state_copy = deep_copy_game_state(state)

        assert state.turn == state_copy.turn
        assert state.ship_a.shields == state_copy.ship_a.shields
        assert state.ship_a.position.x == state_copy.ship_a.position.x

    def test_deep_copy_independence(self):
        state = create_test_game_state()
        state_copy = deep_copy_game_state(state)

        # Modify copy
        state_copy.ship_a.shields = 50
        state_copy.ship_a.position.x = 999

        # Original unchanged
        assert state.ship_a.shields != 50
        assert state.ship_a.position.x != 999
```

Create `tests/test_prompt_formatter.py`:

```python
from ai_arena.llm_adapter.prompt_formatter import (
    format_ship_status,
    format_torpedo_list,
    format_blast_zones
)
from ai_arena.game_engine.data_models import ShipState, Vec2D, PhaserConfig

def test_format_ship_status():
    ship = ShipState(
        position=Vec2D(100, 200),
        velocity=Vec2D(0, 0),
        heading=1.57,  # ~90 degrees
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
    assert "85/100" in result  # Shields
    assert "67/100" in result  # AE
    assert "90" in result or "89.9" in result  # Heading in degrees

def test_format_torpedo_list_empty():
    result = format_torpedo_list([], "ship_a")
    assert "0/4" in result
    assert "None active" in result

def test_format_torpedo_list_multiple():
    torpedoes = [
        MockTorpedo(id="torpedo_1", position=Vec2D(50, 50), ae_remaining=30),
        MockTorpedo(id="torpedo_2", position=Vec2D(100, 100), ae_remaining=25),
    ]

    result = format_torpedo_list(torpedoes, "ship_a")

    assert "2/4" in result
    assert "torpedo_1" in result
    assert "torpedo_2" in result
    assert "30" in result
    assert "25" in result
```

---

## Files to Create

1. **`ai_arena/game_engine/utils.py`** - Shared game utilities
2. **`ai_arena/llm_adapter/prompt_formatter.py`** - Prompt formatting functions
3. **`tests/test_utils.py`** - Unit tests for game utilities
4. **`tests/test_prompt_formatter.py`** - Unit tests for prompt formatters

---

## Files to Modify

1. **`ai_arena/game_engine/physics.py`**
   - Import `parse_torpedo_action` and `deep_copy_game_state` from utils
   - Rename `_copy_state()` to public `copy_state()`
   - Delete `_parse_torpedo_action()` method
   - Use shared utilities

2. **`ai_arena/llm_adapter/adapter.py`**
   - Import formatting functions from `prompt_formatter`
   - Update `_build_prompt()` to use formatters
   - Delete `_parse_torpedo_action()` method

3. **`ai_arena/orchestrator/match_orchestrator.py`**
   - Use `self.physics_engine.copy_state()` (public method)
   - Replace `3.14159` with `np.pi`

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Shared utility modules created and tested
- [ ] No duplicate `parse_torpedo_action()` implementations
- [ ] State copying uses `copy.deepcopy()`
- [ ] Physics engine exposes public `copy_state()` method
- [ ] Match orchestrator uses public APIs only
- [ ] All tests pass (90%+ coverage for new modules)
- [ ] Code reviewed
- [ ] Documentation updated

---

## Dependencies

**Blocks:**
- Story 044 (Orchestrator Cleanup) - depends on public `copy_state()` method

**Blocked By:**
- Story 041 (Remove Legacy Movement Code) - recommended to complete first for cleaner utils

**Can Run Parallel With:**
- Story 042 (Externalize Prompts) - independent work

---

## Notes

### Design Decisions

- **Shared utilities in separate modules**: Better organization, easier to test
- **Pure formatting functions**: No side effects, easier to test and reuse
- **Public `copy_state()` method**: Proper encapsulation, better API design
- **`copy.deepcopy()` for state**: Safer than manual copying, handles nested structures

### Benefits

After this story:
- ✅ Single source of truth for shared logic
- ✅ Better testability (isolated functions)
- ✅ Cleaner code organization
- ✅ Proper encapsulation (public vs private methods)
- ✅ Reduced maintenance burden
