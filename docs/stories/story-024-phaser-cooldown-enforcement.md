# Story 024: Phaser Cooldown Enforcement

**Epic:** [Epic 004: Continuous Physics System](../epic-004-continuous-physics.md)
**Status:** Not Started
**Size:** Medium (~2 hours)
**Priority:** P0

---

## User Story

**As a** game engine developer
**I want** phaser firing prevented when cooldown > 0
**So that** phasers respect the 3.5-second rate limit

## Context

With cooldown tracking in place (Story 020-021), we now need to enforce it during weapon firing. Currently, phasers can fire every turn. After this story, they can only fire when cooldown reaches 0.0 seconds.

## Acceptance Criteria

- [ ] Phaser fire only allowed when `ship.phaser_cooldown_remaining == 0.0`
- [ ] After successful phaser fire, cooldown set to `config.weapons.phaser.cooldown_seconds`
- [ ] Weapon action still processed, just firing prevented during cooldown
- [ ] LLM observations updated to show cooldown status
- [ ] Tests verify cooldown prevents rapid firing
- [ ] At least one full match demonstrates cooldown working

## Technical Requirements

### Update Weapon Firing Logic

**File:** `ai_arena/game_engine/physics.py`

Current weapon firing (approximate):
```python
def _process_weapon_action(ship: ShipState, target: ShipState, weapon_action: str, config: GameConfig):
    """Process weapon firing."""
    if weapon_action.startswith("FIRE_PHASER_"):
        # Fire phaser (no cooldown check currently)
        damage = calculate_phaser_damage(weapon_action, config)
        target.shields -= damage
```

Target implementation:
```python
def _process_weapon_action(ship: ShipState, target: ShipState, weapon_action: str, config: GameConfig) -> bool:
    """Process weapon firing.

    Returns:
        True if weapon fired successfully, False if on cooldown or other reason
    """
    if weapon_action.startswith("FIRE_PHASER_"):
        # Check cooldown (NEW)
        if ship.phaser_cooldown_remaining > 0.0:
            # Cannot fire - still on cooldown
            return False

        # Fire phaser
        damage = calculate_phaser_damage(weapon_action, config)
        target.shields -= damage

        # Set cooldown (NEW)
        ship.phaser_cooldown_remaining = config.weapons.phaser.cooldown_seconds

        return True

    return False
```

### Update LLM Observations

**File:** `ai_arena/llm_adapter/adapter.py`

Add cooldown to observation:
```python
observation = {
    "turn": turn_number,
    "my_ship": {
        "shields": my_ship.shields,
        "available_energy": my_ship.available_energy,
        "phaser_cooldown_remaining": my_ship.phaser_cooldown_remaining,  # NEW
        # ...
    }
}
```

Update system prompt:
```
PHASER COOLDOWN:
- After firing, phasers need 3.5 seconds to recharge
- Check `my_ship.phaser_cooldown_remaining` in observations
- If cooldown > 0, you cannot fire phasers this turn
- Plan your shots carefully - can't spam every turn!
```

## Testing & Validation

```python
def test_phaser_respects_cooldown():
    """Verify phaser won't fire during cooldown."""
    ship = ShipState(..., phaser_cooldown_remaining=2.0)
    target = ShipState(..., shields=100.0)

    fired = _process_weapon_action(ship, target, "FIRE_PHASER_WIDE", config)

    assert fired is False  # Should not fire
    assert target.shields == 100.0  # No damage dealt
    assert ship.phaser_cooldown_remaining == 2.0  # Cooldown unchanged

def test_phaser_fires_when_ready():
    """Verify phaser fires when cooldown = 0."""
    ship = ShipState(..., phaser_cooldown_remaining=0.0)
    target = ShipState(..., shields=100.0)

    fired = _process_weapon_action(ship, target, "FIRE_PHASER_WIDE", config)

    assert fired is True
    assert target.shields < 100.0  # Damage dealt
    assert ship.phaser_cooldown_remaining == 3.5  # Cooldown set

def test_phaser_can_fire_multiple_times_per_turn():
    """Verify phasers can fire ~4 times in 15s turn."""
    # Simulate 15s turn with 0.1s substeps
    # With 3.5s cooldown, should be able to fire at:
    # t=0.0s, t=3.5s, t=7.0s, t=10.5s, t=14.0s = 5 shots per turn
    pass
```

## Definition of Done

- [ ] Phaser cooldown enforced
- [ ] Cooldown visible in LLM observations
- [ ] All tests passing
- [ ] Full match runs successfully with cooldown

## Files Changed

- Modify: `ai_arena/game_engine/physics.py`
- Modify: `ai_arena/llm_adapter/adapter.py`
- Modify: `tests/test_continuous_physics.py`

## Dependencies

- Story 020, 021: Cooldown tracking

---

## Dev Agent Record

**Implementation Date:** [To be filled in by Dev Agent]
**Agent:** [To be filled in by Dev Agent]
**Status:** [To be filled in by Dev Agent]

---

## QA Agent Record

**Validation Date:** [To be filled in by QA Agent]
**Validator:** [To be filled in by QA Agent]
**Verdict:** [To be filled in by QA Agent]

---

**Story Status:** Ready for Development
