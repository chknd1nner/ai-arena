# Story 044: Match Orchestrator & Replay Cleanup

**Epic:** [Epic 007: Technical Debt Reduction & Code Quality](../epic-007-technical-debt-reduction.md)
**Status:** ⏸️ Not Started
**Size:** Small (~0.5 days)
**Priority:** P1

---

## Dev Agent Record

**Implementation Date:** _Pending_
**Agent:** _TBD_
**Status:** ⏸️ Not Started

### Instructions for Dev Agent

When implementing this story:

1. **Update Match Orchestrator** to use public `copy_state()` from Story 043
2. **Replace hardcoded constants** (`3.14159` → `np.pi`)
3. **Add match timeout** mechanism to prevent hanging
4. **(Optional) Evaluate replay auto-serialization** using `dataclasses.asdict()`

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of work completed
- Timeout mechanism implemented
- File paths for modified files
- Any issues encountered and resolutions

---

## QA Agent Record

**Validation Date:** _Pending_
**Validator:** _TBD_
**Verdict:** ⏸️ Awaiting Implementation

### QA Checklist

- [ ] Match orchestrator uses public `copy_state()` method
- [ ] `np.pi` used instead of `3.14159`
- [ ] Match timeout implemented and working
- [ ] Timeout test verified (mock timeout scenario)
- [ ] All orchestrator tests pass
- [ ] Full match runs successfully

**After validation, update this section with:**
- QA date and validator name
- Test results for each criterion
- Timeout verification results
- Final verdict

---

## User Story

**As a** developer running AI-Arena matches
**I want** the Match Orchestrator to use proper APIs and have timeout protection
**So that** the system is more robust and matches can't hang indefinitely

### Context

The Match Orchestrator has minor issues:

1. **Encapsulation Violation**: Calls private `_copy_state()` method
2. **Hardcoded Constants**: Uses `3.14159` instead of `np.pi`
3. **No Timeout Protection**: Match could hang if LLM stalls repeatedly

These are small issues but should be fixed for code quality.

---

## Acceptance Criteria

### Must Have:

- [ ] Match orchestrator uses public `PhysicsEngine.copy_state()` method
- [ ] All hardcoded constants replaced with proper values
- [ ] Match timeout implemented (default: 30 minutes)
- [ ] All orchestrator tests pass
- [ ] Full match runs successfully

### Should Have:

- [ ] Timeout configurable via environment variable or config
- [ ] Clear timeout error message
- [ ] Timeout logged with match statistics

### Nice to Have:

- [ ] Replay auto-serialization evaluated (use `dataclasses.asdict()` if beneficial)

---

## Technical Specification

### Current Issues

**Issue 1: Private Method Access** (`match_orchestrator.py:33`)
```python
# Bad - accessing private method
state_for_replay = self.physics_engine._copy_state(state)
```

**Fix:**
```python
# Good - using public API (from Story 043)
state_for_replay = self.physics_engine.copy_state(state)
```

**Issue 2: Hardcoded Pi** (`match_orchestrator.py:74`)
```python
heading=3.14159,  # pi, facing left
```

**Fix:**
```python
import numpy as np
heading=np.pi,  # Pi radians, facing left (180 degrees)
```

**Issue 3: No Match Timeout**

Current code has no maximum time limit for entire match. LLM calls have 30s timeout, but match could still hang if:
- Many turns with slow LLMs
- Network issues causing repeated retries
- Infinite loop (unlikely but possible)

### Proposed Solution: Match Timeout

```python
import time

class MatchOrchestrator:
    def __init__(self, model_a: str, model_b: str, max_match_time_seconds: int = 1800):
        """
        Args:
            model_a: Model identifier for ship A
            model_b: Model identifier for ship B
            max_match_time_seconds: Maximum time for entire match (default: 30 minutes)
        """
        self.model_a = model_a
        self.model_b = model_b
        self.max_match_time_seconds = max_match_time_seconds
        # ... rest of initialization ...

    async def run_match(self, max_turns: int) -> dict:
        """Run a complete match and return results."""
        start_time = time.time()

        print(f"Starting match between {self.model_a} and {self.model_b}")
        print(f"Match timeout: {self.max_match_time_seconds}s ({self.max_match_time_seconds / 60:.1f} minutes)")

        state = self._initialize_match()

        for turn in range(1, max_turns + 1):
            # Check timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > self.max_match_time_seconds:
                logger.warning(f"Match timeout after {elapsed_time:.1f}s (limit: {self.max_match_time_seconds}s)")
                final_data = self.replay_recorder.finalize("timeout", turn - 1)
                final_data['status'] = 'timeout'
                final_data['elapsed_time_seconds'] = elapsed_time
                return final_data

            print(f"Turn {turn} (elapsed: {elapsed_time:.1f}s)")

            # ... rest of turn logic ...

        # Match completed normally
        final_data = self.replay_recorder.finalize("tie", max_turns)
        final_data['status'] = 'completed'
        final_data['elapsed_time_seconds'] = time.time() - start_time
        return final_data
```

---

## Implementation Guidance

### Step 1: Fix Encapsulation (0.1 days)

**Modify `ai_arena/orchestrator/match_orchestrator.py`:**

```python
async def run_match(self, max_turns: int) -> dict:
    """Run a complete match and return results."""
    # ... existing code ...

    for turn in range(1, max_turns + 1):
        orders_a, thinking_a, orders_b, thinking_b = await self.llm_adapter.get_orders_for_both_ships(state)

        # Use public copy_state() method (Story 043)
        state_for_replay = self.physics_engine.copy_state(state)

        new_state, events = self.physics_engine.resolve_turn(state, orders_a, orders_b)
        # ... rest of implementation ...
```

### Step 2: Replace Hardcoded Constants (0.1 days)

```python
import numpy as np

class MatchOrchestrator:
    def _initialize_match(self) -> GameState:
        """Initializes the game state using config values."""
        # ... existing code ...

        ship_b = ShipState(
            position=Vec2D((arena_width + spawn_distance) / 2, center_y),
            velocity=Vec2D(0.0, 0.0),
            heading=np.pi,  # Pi radians (180 degrees), facing left
            shields=self.config.ship.starting_shields,
            ae=self.config.ship.starting_ae,
            phaser_config=PhaserConfig.WIDE,
            reconfiguring_phaser=False,
        )
```

### Step 3: Add Match Timeout (0.2 days)

```python
import time
import os

class MatchOrchestrator:
    def __init__(self, model_a: str, model_b: str):
        self.model_a = model_a
        self.model_b = model_b

        # Load game configuration
        self.config = ConfigLoader().load("config.json")

        # Match timeout (default 30 minutes, configurable via env var)
        self.max_match_time_seconds = int(
            os.getenv("AI_ARENA_MATCH_TIMEOUT_SECONDS", "1800")
        )

        # Initialize components with config
        self.llm_adapter = LLMAdapter(model_a, model_b, self.config)
        self.physics_engine = PhysicsEngine(self.config)
        self.replay_recorder = ReplayRecorder(model_a, model_b)

    async def run_match(self, max_turns: int) -> dict:
        """Run a complete match and return results."""
        start_time = time.time()

        print(f"Starting match between {self.model_a} and {self.model_b}")
        print(f"Match timeout: {self.max_match_time_seconds}s ({self.max_match_time_seconds / 60:.1f} min)")

        state = self._initialize_match()

        for turn in range(1, max_turns + 1):
            # Check timeout before each turn
            elapsed_time = time.time() - start_time
            if elapsed_time > self.max_match_time_seconds:
                print(f"⏱️  Match timeout after {elapsed_time:.1f}s")
                logger.warning(
                    f"Match {self.replay_recorder.match_id} timed out "
                    f"after {elapsed_time:.1f}s (limit: {self.max_match_time_seconds}s)"
                )

                # Finalize as timeout
                final_data = self.replay_recorder.finalize("timeout", turn - 1)
                final_data['status'] = 'timeout'
                final_data['elapsed_time_seconds'] = elapsed_time
                return final_data

            print(f"Turn {turn} (elapsed: {elapsed_time:.1f}s)")

            # ... rest of turn logic ...

        # Match completed normally
        print("Match ended due to max turns reached.")
        final_data = self.replay_recorder.finalize("tie", max_turns)
        final_data['status'] = 'completed'
        final_data['elapsed_time_seconds'] = time.time() - start_time
        return final_data
```

### Step 4: Optional - Evaluate Replay Auto-Serialization (0.1 days)

**Current Serialization** (manual, in `recorder.py`):
```python
def _serialize_ship(self, ship: ShipState) -> dict:
    return {
        "position": [ship.position.x, ship.position.y],
        "velocity": [ship.velocity.x, ship.velocity.y],
        "heading": ship.heading,
        # ... manual field mapping
    }
```

**Potential Auto-Serialization:**
```python
from dataclasses import asdict

def _serialize_ship(self, ship: ShipState) -> dict:
    return asdict(ship, dict_factory=custom_dict_factory)

def custom_dict_factory(items):
    """Custom serialization for special types."""
    result = {}
    for key, value in items:
        if isinstance(value, Vec2D):
            result[key] = [value.x, value.y]
        elif isinstance(value, Enum):
            result[key] = value.value
        else:
            result[key] = value
    return result
```

**Recommendation:** Only implement if it significantly reduces boilerplate. Current manual serialization is clear and works well.

---

## Testing Requirements

### Unit Tests

```python
# tests/test_match_orchestrator.py

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_match_timeout():
    """Test that match times out after max_match_time_seconds."""
    orchestrator = MatchOrchestrator("gpt-4", "gpt-4")
    orchestrator.max_match_time_seconds = 2  # 2 second timeout for test

    # Mock LLM adapter to be slow
    async def slow_get_orders(*args, **kwargs):
        await asyncio.sleep(1.5)  # Each turn takes 1.5 seconds
        return (default_orders, "thinking", default_orders, "thinking")

    orchestrator.llm_adapter.get_orders_for_both_ships = slow_get_orders

    # Run match (should timeout after 2 turns)
    result = await orchestrator.run_match(max_turns=10)

    assert result['status'] == 'timeout'
    assert result['winner'] == 'timeout'
    assert result['elapsed_time_seconds'] > 2.0
    assert result['total_turns'] < 10  # Didn't complete all turns

def test_copy_state_uses_public_api():
    """Test that orchestrator uses public copy_state() method."""
    from ai_arena.orchestrator.match_orchestrator import MatchOrchestrator
    import inspect

    # Get source code of run_match method
    source = inspect.getsource(MatchOrchestrator.run_match)

    # Should use public copy_state(), not private _copy_state()
    assert "copy_state(" in source
    assert "_copy_state(" not in source

def test_no_hardcoded_pi():
    """Test that no hardcoded pi values exist."""
    from ai_arena.orchestrator.match_orchestrator import MatchOrchestrator
    import inspect

    source = inspect.getsource(MatchOrchestrator._initialize_match)

    # Should not have hardcoded 3.14159
    assert "3.14159" not in source
    assert "np.pi" in source or "math.pi" in source
```

### Integration Tests

```bash
# Test full match with timeout
AI_ARENA_MATCH_TIMEOUT_SECONDS=60 python3 main.py

# Test normal match (no timeout)
python3 main.py
```

---

## Files to Modify

1. **`ai_arena/orchestrator/match_orchestrator.py`**
   - Use public `copy_state()` method
   - Replace `3.14159` with `np.pi`
   - Add match timeout mechanism
   - Track and log elapsed time

2. **`ai_arena/replay/recorder.py`** (optional)
   - Evaluate auto-serialization with `dataclasses.asdict()`
   - Only if it simplifies code significantly

3. **`.env.example`** (if not exists, create)
   - Document `AI_ARENA_MATCH_TIMEOUT_SECONDS` variable

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Match orchestrator uses public API only
- [ ] No hardcoded constants
- [ ] Match timeout implemented and tested
- [ ] All orchestrator tests pass
- [ ] Full match runs successfully
- [ ] Timeout mechanism verified (mock test)
- [ ] Documentation updated

---

## Dependencies

**Blocks:**
- None

**Blocked By:**
- Story 043 (Consolidate Duplicate Code) - provides public `copy_state()` method

---

## Notes

### Design Decisions

- **30-minute default timeout**: Generous for most matches, prevents infinite hangs
- **Configurable via env var**: Easy to adjust for different environments
- **Timeout status**: Distinct from "tie" - makes clear what happened
- **Elapsed time tracking**: Useful for performance analysis

### Benefits

After this story:
- ✅ Proper API encapsulation
- ✅ No magic numbers
- ✅ Protection against hanging matches
- ✅ Better debugging (elapsed time logged)
