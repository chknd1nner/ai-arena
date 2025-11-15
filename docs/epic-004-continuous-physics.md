# Epic 004: Continuous Physics System

**Status:** In Progress
**Priority:** P0 (Foundational)
**Estimated Size:** Medium (7 stories, 8-10 hours)
**Target for:** Claude Code Web

---

## Overview

Transform the discrete turn-based physics simulation into a continuous real-time system with per-substep AE tracking and phaser cooldown mechanics. This makes combat feel more dynamic and realistic, enabling better tactical depth through energy management and weapon rate limiting.

## Problem Statement

Currently, physics operates in discrete turn chunks:
- AE costs are deducted once per 15-second decision interval
- AE regeneration happens once per turn
- Phasers can fire every turn with no cooldown (if in arc and have target)
- Everything feels "turn-based" rather than "real-time simulation"
- Net AE drain/gain calculations are coarse (per-turn granularity)
- LLMs can spam phasers every decision interval

**Example of current discrete behavior:**
```
Turn 1 (15s):
  - Deduct 10 AE for movement (full turn cost upfront)
  - Deduct 5 AE for rotation (full turn cost upfront)
  - Fire phaser (instant, no cooldown tracking)
  - Regenerate 5 AE (15s × 0.33 AE/s)
  - Net: -10 AE this turn
```

**Desired continuous behavior:**
```
Each 0.1s substep within 15s turn:
  - Deduct 0.0667 AE for movement (10 AE ÷ 150 substeps)
  - Deduct 0.0333 AE for rotation (5 AE ÷ 150 substeps)
  - Regenerate 0.033 AE (0.33 AE/s × 0.1s)
  - Track phaser cooldown (3.5s remaining → 3.4s → ...)
  - Only allow phaser fire when cooldown = 0.0s
  - Net: More granular, continuous energy economy
```

## Goals

1. **Continuous AE Tracking**: Apply AE costs and regeneration per substep (0.1s), not per turn (15s)
2. **Phaser Cooldown System**: Prevent phaser spam with 3.5s cooldown between shots
3. **Realistic Energy Economy**: Net AE drain/gain feels continuous and realistic
4. **Maintain Determinism**: Same inputs must produce identical outputs (critical for replays)
5. **Backward Compatible**: Old replays should still work or gracefully degrade

## Success Criteria

- [ ] AE tracking operates per substep (0.1s granularity)
- [ ] Movement AE cost applied continuously during action phase
- [ ] Rotation AE cost applied continuously during action phase
- [ ] Phaser cooldown prevents firing more than once per 3.5 seconds
- [ ] ShipState tracks cooldown timer accurately
- [ ] Physics remains 100% deterministic (regression tests pass)
- [ ] At least one match demonstrates phaser cooldown working
- [ ] Energy economy feels realistic (continuous drain/regen)
- [ ] All existing tests still pass (or updated appropriately)

## User Stories

1. [Story 020: Phaser Cooldown State & Config](stories/story-020-phaser-cooldown-state-config.md)
2. [Story 021: Substep AE Tracking System](stories/story-021-substep-ae-tracking.md)
3. [Story 022: Continuous Movement AE Application](stories/story-022-continuous-movement-ae.md)
4. [Story 023: Continuous Rotation AE Application](stories/story-023-continuous-rotation-ae.md)
5. [Story 024: Phaser Cooldown Enforcement](stories/story-024-phaser-cooldown-enforcement.md)
6. [Story 025: Continuous Physics Testing & Validation](stories/story-025-continuous-physics-testing.md)
7. [Story 026: Balance Tuning & Integration Testing](stories/story-026-balance-tuning-integration.md)

## Technical Approach

### Current Implementation (Epic 003 State)

**Discrete Per-Turn Physics:**
```python
def _update_ship_physics(ship: ShipState, orders: Orders, config: GameConfig) -> None:
    """Apply physics for entire 15s decision interval."""

    # Deduct AE costs (once per turn)
    movement_ae_cost = calculate_movement_cost(orders.movement, config)
    rotation_ae_cost = calculate_rotation_cost(orders.rotation, config)
    ship.available_energy -= (movement_ae_cost + rotation_ae_cost)

    # Apply movement/rotation over substeps
    for substep in range(num_substeps):
        # ... position/heading updates ...

    # Regenerate AE (once per turn, at end)
    ship.available_energy += config.ship.ae_regeneration_rate * decision_interval
```

**Problems:**
- AE deducted upfront (entire 15s worth)
- Regeneration happens at end
- No phaser cooldown tracking
- Can't model continuous energy drain

### Target Implementation (Epic 004 Goal)

**Continuous Per-Substep Physics:**
```python
def _update_ship_physics(ship: ShipState, orders: Orders, config: GameConfig) -> None:
    """Apply physics per 0.1s substep."""

    dt = config.simulation.physics_tick  # 0.1s

    # Apply continuous AE costs per substep
    movement_ae_rate = get_movement_ae_rate(orders.movement, config)  # AE/s
    rotation_ae_rate = get_rotation_ae_rate(orders.rotation, config)  # AE/s

    ae_cost_this_substep = (movement_ae_rate + rotation_ae_rate) * dt
    ship.available_energy -= ae_cost_this_substep

    # Regenerate AE per substep
    ship.available_energy += config.ship.ae_regeneration_rate * dt

    # Update phaser cooldown
    if ship.phaser_cooldown_remaining > 0.0:
        ship.phaser_cooldown_remaining -= dt
        ship.phaser_cooldown_remaining = max(0.0, ship.phaser_cooldown_remaining)

    # ... position/heading updates ...
```

**Benefits:**
- Continuous energy drain/regen
- Phaser cooldown prevents spam
- More realistic simulation
- Better tactical depth

## Architecture Changes

### Data Models (data_models.py)

**Add Cooldown to ShipState:**
```python
@dataclass
class ShipState:
    # ... existing fields ...
    phaser_cooldown_remaining: float = 0.0  # NEW: Seconds until can fire again
```

**Example state during match:**
```python
# Turn 3, substep 50 (5.0s into turn)
ship = ShipState(
    shields=85.0,
    available_energy=72.5,
    phaser_cooldown_remaining=1.2,  # Fired 2.3s ago, need 1.2s more
    # ...
)
```

### Configuration (config.json)

**Add Phaser Cooldown Config:**
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
    }
  }
}
```

### Physics Engine (physics.py)

**Key Changes:**

1. **AE Tracking per Substep** (Story 021)
   - Movement AE: `movement_ae_rate * dt` per substep
   - Rotation AE: `rotation_ae_rate * dt` per substep
   - Regeneration: `regen_rate * dt` per substep

2. **Cooldown Tracking** (Story 020, 024)
   - Decrement `ship.phaser_cooldown_remaining` each substep
   - Only allow phaser fire when cooldown = 0.0
   - Set cooldown = 3.5s after successful phaser fire

3. **Determinism Preservation** (Story 025)
   - All floating-point operations must be identical across runs
   - No platform-specific math
   - Regression tests validate byte-identical replays

## Impact on Gameplay

### Before (Discrete Physics):
```
Turn 1: Fire phaser, deal 35 damage
Turn 2: Fire phaser, deal 35 damage  ← Can spam every 15s
Turn 3: Fire phaser, deal 35 damage
Total: 105 damage in 45s
```

### After (Continuous Physics):
```
Turn 1 @ 0.0s: Fire phaser, deal 35 damage (cooldown = 3.5s)
Turn 1 @ 3.5s: Can't fire (only 3.5s elapsed, need cooldown reset)
Turn 1 @ 7.0s: Fire phaser, deal 35 damage (cooldown = 3.5s)
Turn 1 @ 10.5s: Fire phaser, deal 35 damage (cooldown = 3.5s)
Turn 1 @ 14.0s: Fire phaser, deal 35 damage (cooldown = 3.5s)
Turn 2 @ 15.0s: Can't fire (only 1.0s since last shot)
Turn 2 @ 17.5s: Fire phaser, deal 35 damage (cooldown = 3.5s)

Can fire ~4 times per 15s turn (vs 1 time in old system)
Total damage per turn: ~140 damage (vs 35 damage)
```

**Wait, this is a BUFF to phasers!**

**Design decision needed:** Should phaser cooldown be:
- Option A: 3.5s (can fire ~4 times per turn) ← Current game spec
- Option B: 15s+ (can fire once per turn max) ← Preserve current balance
- Option C: 7.5s (can fire ~2 times per turn) ← Middle ground

**Recommendation:** Start with 3.5s per spec, then tune in Story 026 based on playtesting.

## Energy Economy Changes

### Movement Costs (Per Second)

| Movement Direction | AE/s | Cost per Turn (15s) | Cost per Substep (0.1s) |
|--------------------|------|---------------------|-------------------------|
| FORWARD | 0.33 | 4.95 | 0.033 |
| DIAGONAL | 0.53 | 7.95 | 0.053 |
| PERPENDICULAR | 0.67 | 10.05 | 0.067 |
| BACKWARD | 0.67 | 10.05 | 0.067 |
| STOP | 0.0 | 0.0 | 0.0 |

### Rotation Costs (Per Second)

| Rotation Command | AE/s | Cost per Turn (15s) | Cost per Substep (0.1s) |
|------------------|------|---------------------|-------------------------|
| NONE | 0.0 | 0.0 | 0.0 |
| SOFT | 0.13 | 1.95 | 0.013 |
| HARD | 0.33 | 4.95 | 0.033 |

### Regeneration

- **Rate:** 0.33 AE/s
- **Per Turn (15s):** 4.95 AE
- **Per Substep (0.1s):** 0.033 AE

### Net AE Examples

**Scenario 1: Aggressive Maneuver**
- Movement: PERPENDICULAR (0.67 AE/s)
- Rotation: HARD_LEFT (0.33 AE/s)
- Regeneration: +0.33 AE/s
- **Net: -0.67 AE/s** (depletes energy over time)

**Scenario 2: Efficient Advance**
- Movement: FORWARD (0.33 AE/s)
- Rotation: NONE (0.0 AE/s)
- Regeneration: +0.33 AE/s
- **Net: 0.0 AE/s** (energy neutral!)

**Scenario 3: Recharge Mode**
- Movement: STOP (0.0 AE/s)
- Rotation: NONE (0.0 AE/s)
- Regeneration: +0.33 AE/s
- **Net: +0.33 AE/s** (recharges energy)

## Testing Strategy

### Unit Tests (Story 025)

1. **Substep AE Tracking**
   - Test AE deduction per substep
   - Test AE regeneration per substep
   - Test net AE change over multiple substeps

2. **Phaser Cooldown**
   - Test cooldown decrements per substep
   - Test cooldown prevents firing when > 0
   - Test cooldown resets after firing

3. **Determinism**
   - Run same match 10 times
   - Compare replay JSONs byte-for-byte
   - Must be identical

### Integration Tests (Story 026)

1. **Full Match with Continuous Physics**
   - Run complete LLM vs LLM match
   - Verify phaser fires multiple times per turn
   - Verify AE economy behaves continuously
   - Check for any NaN or infinity values

2. **Balance Validation**
   - Compare match outcomes with old discrete physics
   - Measure phaser DPS change
   - Adjust cooldown if needed

## Risks & Mitigations

### Risk 1: Breaking Determinism
**Impact:** High - Replays won't work, matches not reproducible
**Mitigation:**
- Comprehensive regression tests
- Use same floating-point operations as before
- Test on multiple platforms

### Risk 2: Performance Degradation
**Impact:** Low - Per-substep calculations could slow simulation
**Mitigation:**
- Profile before/after
- Optimize hot paths if needed
- Substep loop already exists, just adding AE tracking

### Risk 3: Balance Changes
**Impact:** Medium - Phaser cooldown could break game balance
**Mitigation:**
- Make cooldown configurable
- Test with different values
- Story 026 dedicated to tuning

### Risk 4: LLM Confusion
**Impact:** Low - LLMs might not understand cooldown
**Mitigation:**
- Update system prompts to explain cooldown
- Show cooldown status in observations
- Test with both Claude and GPT-4

## Dependencies

### Required
- Epic 001: Configuration system (for cooldown config)
- Epic 002: Movement/rotation system (for AE rate calculations)

### Blocks
- Future weapon enhancements (will use same cooldown pattern)
- Future torpedo improvements (may add cooldown)
- Tournament system (needs stable physics first)

## Implementation Phases

### Phase 1: Foundation (Stories 020-021)
- Add cooldown state to ShipState
- Add cooldown config
- Implement substep AE tracking
- **Deliverable:** AE tracking works per substep

### Phase 2: Application (Stories 022-023)
- Apply movement AE per substep
- Apply rotation AE per substep
- **Deliverable:** Continuous energy economy

### Phase 3: Cooldown (Story 024)
- Implement phaser cooldown enforcement
- Update weapon firing logic
- **Deliverable:** Phasers respect cooldown

### Phase 4: Validation (Stories 025-026)
- Comprehensive physics testing
- Determinism validation
- Balance tuning
- **Deliverable:** Production-ready continuous physics

## Rollout Strategy

1. **Feature Branch:** `feature/continuous-physics-system`
2. **Incremental PRs:** One PR per phase (or per story if preferred)
3. **Testing:** Run full test suite after each story
4. **Validation:** Compare old vs new physics with sample matches
5. **Merge:** Only merge when all tests pass and determinism verified

## Definition of Done

- [ ] All 7 stories completed
- [ ] AE tracking operates per substep
- [ ] Phaser cooldown system working
- [ ] All tests passing (unit + integration)
- [ ] Determinism validated (byte-identical replays)
- [ ] At least 3 full matches run successfully
- [ ] Balance tuning complete
- [ ] Documentation updated
- [ ] Merged to main

## Files to Create/Modify

### Create
- `tests/test_continuous_physics.py` - Continuous physics tests
- `tests/test_phaser_cooldown.py` - Cooldown-specific tests

### Modify
- `ai_arena/game_engine/data_models.py` - Add `phaser_cooldown_remaining`
- `ai_arena/game_engine/physics.py` - Substep AE tracking, cooldown logic
- `config.json` - Add phaser cooldown config
- `ai_arena/config/loader.py` - Validate new config fields
- Existing physics tests - Update for new behavior

## Notes

**Why This Epic Matters:**
- Completes the physics foundation started in Epic 002
- Makes combat feel more realistic and dynamic
- Enables better energy management tactics
- Prevents phaser spam abuse
- Aligns with game spec's "continuous real-time" vision

**Alternative Considered:**
- Could have done Tournament System first
- Decision: Finish core gameplay before building testing infrastructure
- Rationale: Want stable, balanced physics before systematic testing

**Post-Epic 004 Roadmap:**
- Epic 005: Tournament & Match Infrastructure (systematic testing)
- Epic 006: Enhanced Torpedo Tactics (timed detonation, etc.)
- Epic 007: Advanced Analytics (damage charts, timeline visualization)

---

**Epic 004 Ready for Implementation** 🚀
