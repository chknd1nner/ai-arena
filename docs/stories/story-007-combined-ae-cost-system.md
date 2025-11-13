# Story 007: Combined AE Cost System

**Epic:** [Epic 002: Independent Movement & Rotation System](../epic-002-independent-movement-rotation.md)
**Status:** Ready for Development
**Size:** Small
**Priority:** P1

---

## User Story

**As a** game physics engine
**I want** to calculate combined AE costs for movement + rotation
**So that** ships consume AE based on both their movement and rotation choices

## Context

After Stories 005-006, movement and rotation work independently. However, AE costs are currently only calculated for movement. Ships should consume AE for BOTH movement AND rotation, as specified in the game spec.

**Example from game spec:**
- Forward movement: 0.33 AE/s
- Hard left rotation: 0.33 AE/s
- Combined cost: 0.66 AE/s
- Net burn (after 0.33 AE/s regen): 0.33 AE/s net drain

## Acceptance Criteria

- [ ] Movement AE cost calculated per second from config
- [ ] Rotation AE cost calculated per second from config
- [ ] Combined cost = movement cost + rotation cost
- [ ] AE deducted once per turn (movement + rotation combined)
- [ ] Insufficient AE handled gracefully (orders validated/downgraded)
- [ ] Tests verify combined costs for various movement + rotation combinations

## Technical Details

### Files to Modify

- `ai_arena/game_engine/physics.py` - Update AE cost calculation
- `tests/test_physics.py` - Add combined cost tests

### Implementation Approach

**1. Add Rotation AE Cost Method:**

```python
def _get_rotation_ae_cost(self, rotation: RotationCommand) -> float:
    """Get AE cost per second for rotation command."""
    cost_map = {
        RotationCommand.NONE: self.config.rotation.none_ae_per_second,
        RotationCommand.SOFT_LEFT: self.config.rotation.soft_turn_ae_per_second,
        RotationCommand.SOFT_RIGHT: self.config.rotation.soft_turn_ae_per_second,
        RotationCommand.HARD_LEFT: self.config.rotation.hard_turn_ae_per_second,
        RotationCommand.HARD_RIGHT: self.config.rotation.hard_turn_ae_per_second,
    }
    return cost_map[rotation]
```

**2. Update AE Deduction in `resolve_turn()`:**

```python
def resolve_turn(self, state: GameState, orders_a: Orders, orders_b: Orders) -> Tuple[GameState, List[Event]]:
    # ... existing code ...

    # Calculate combined AE costs
    movement_cost_a = self._get_movement_ae_cost(orders_a.movement) * self.action_phase_duration
    rotation_cost_a = self._get_rotation_ae_cost(orders_a.rotation) * self.action_phase_duration
    total_cost_a = movement_cost_a + rotation_cost_a

    movement_cost_b = self._get_movement_ae_cost(orders_b.movement) * self.action_phase_duration
    rotation_cost_b = self._get_rotation_ae_cost(orders_b.rotation) * self.action_phase_duration
    total_cost_b = movement_cost_b + rotation_cost_b

    # Deduct combined costs
    state.ship_a.ae = max(0, state.ship_a.ae - total_cost_a)
    state.ship_b.ae = max(0, state.ship_b.ae - total_cost_b)

    # ... continue with substeps ...
```

**3. Order Validation (Optional Enhancement):**

If ship doesn't have enough AE for the requested movement + rotation, consider downgrading orders:

```python
def _validate_and_adjust_orders(self, ship: ShipState, orders: Orders) -> Orders:
    """Validate orders and adjust if insufficient AE."""
    movement_cost = self._get_movement_ae_cost(orders.movement) * self.action_phase_duration
    rotation_cost = self._get_rotation_ae_cost(orders.rotation) * self.action_phase_duration
    total_cost = movement_cost + rotation_cost

    if ship.ae < total_cost:
        # Option 1: Reduce to STOP + NONE
        return Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action=orders.weapon_action,
            torpedo_orders=orders.torpedo_orders
        )
        # Option 2: Keep movement, drop rotation
        # Option 3: Keep rotation, drop movement
        # Decision depends on game design

    return orders
```

## Test Requirements

**`tests/test_physics.py`**

```python
def test_combined_ae_cost_forward_none():
    """FORWARD + NONE should cost only movement."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_ae=100)
    orders_a = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # Only movement cost: 0.33 AE/s × 15s = 4.95 AE
    # But also regen: +0.33 AE/s × 15s = +4.95 AE
    # Net change depends on when regen happens
    # For simplicity, just verify AE decreased
    assert new_state.ship_a.ae < 100

def test_combined_ae_cost_forward_hard_left():
    """FORWARD + HARD_LEFT should cost movement + rotation."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_ae=100)
    orders_a = Orders(
        movement=MovementDirection.FORWARD,
        rotation=RotationCommand.HARD_LEFT,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # Combined cost: (0.33 + 0.33) AE/s × 15s = 9.9 AE
    # Minus regen: 0.33 AE/s × 15s = 4.95 AE
    # Net cost: ~5 AE
    ae_cost = 100 - new_state.ship_a.ae
    assert 3 < ae_cost < 7  # Rough check (accounts for regen)

def test_combined_ae_cost_left_hard_right():
    """LEFT + HARD_RIGHT should cost perpendicular movement + rotation."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_ae=100)
    orders_a = Orders(
        movement=MovementDirection.LEFT,
        rotation=RotationCommand.HARD_RIGHT,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # Combined cost: (0.67 + 0.33) AE/s × 15s = 15 AE
    # Minus regen: 4.95 AE
    # Net cost: ~10 AE
    ae_cost = 100 - new_state.ship_a.ae
    assert 8 < ae_cost < 12

def test_combined_ae_cost_stop_none():
    """STOP + NONE should cost nothing (only regen)."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_ae=50)
    orders_a = Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # No cost, only regen: +4.95 AE
    assert new_state.ship_a.ae > 50

def test_insufficient_ae_for_orders():
    """Ship with insufficient AE should have orders adjusted."""
    engine = PhysicsEngine(config)
    state = create_test_state(ship_a_ae=3)  # Very low AE
    orders_a = Orders(
        movement=MovementDirection.BACKWARD_LEFT,  # Expensive
        rotation=RotationCommand.HARD_LEFT,         # Expensive
        weapon_action="MAINTAIN_CONFIG"
    )

    new_state, _ = engine.resolve_turn(state, orders_a, orders_b)

    # Ship should still move (or be stopped if validation kicks in)
    # Verify no negative AE
    assert new_state.ship_a.ae >= 0
```

## Implementation Checklist

- [ ] Implement `_get_rotation_ae_cost()` method
- [ ] Update `resolve_turn()` to calculate combined costs
- [ ] Deduct combined movement + rotation cost per turn
- [ ] Handle insufficient AE gracefully (don't go negative)
- [ ] Write tests for various movement + rotation combinations
- [ ] Optional: Implement order validation/downgrading

## Edge Cases

1. **Insufficient AE:** Ship has 5 AE but orders cost 15 AE
2. **Zero cost:** STOP + NONE should cost exactly 0 AE
3. **Regen vs cost:** Net AE change depends on regen timing
4. **Negative AE:** Never allow AE to go below 0

## Definition of Done

- [ ] Combined AE costs calculated correctly
- [ ] Movement and rotation costs both applied
- [ ] Tests verify various cost combinations
- [ ] No negative AE values
- [ ] Insufficient AE handled gracefully

## Files Changed

- Modify: `ai_arena/game_engine/physics.py`
- Modify: `tests/test_physics.py`

## Dependencies

- **Requires:** Story 005 (Movement costs) and Story 006 (Rotation costs)

## Blocks

- None - This completes the physics changes

## Notes

**Design Decision:** Should AE regen happen before or after deducting costs?

**Option A:** Deduct first, then regen
- Simpler logic
- Ship can go to 0 AE, then regen brings it back

**Option B:** Regen first, then deduct
- More forgiving (ship gets energy before spending it)
- May prevent hitting 0 AE as often

**Recommendation:** Deduct first (matches current implementation).

**AE Economy Math:**

Scenario: Ship with 50 AE uses FORWARD + HARD_LEFT for one turn:
- Starting AE: 50
- Movement cost: 0.33 × 15 = 4.95 AE
- Rotation cost: 0.33 × 15 = 4.95 AE
- Total cost: 9.9 AE
- Regen: 0.33 × 15 = 4.95 AE (happens at end of turn)
- Final AE: 50 - 9.9 + 4.95 = 45.05 AE

Net drain: 4.95 AE per turn (the combined cost minus regen).
