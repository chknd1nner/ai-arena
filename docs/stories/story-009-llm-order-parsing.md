# Story 009: LLM Order Parsing

**Epic:** [Epic 002: Independent Movement & Rotation System](../epic-002-independent-movement-rotation.md)
**Status:** Ready for Development
**Size:** Medium
**Priority:** P0

---

## User Story

**As an** LLM adapter
**I want** to parse LLM JSON responses with separate movement and rotation fields
**So that** orders can be passed to the physics engine with both commands

## Context

After Story 008 updates the system prompt, LLMs will return JSON with `ship_movement` and `ship_rotation` fields. The adapter must parse these new fields and create `Orders` objects with `MovementDirection` and `RotationCommand` enums.

## Acceptance Criteria

- [ ] Parse `ship_movement` field from LLM JSON response
- [ ] Parse `ship_rotation` field from LLM JSON response
- [ ] Convert movement strings to `MovementDirection` enum
- [ ] Convert rotation strings to `RotationCommand` enum
- [ ] Handle invalid movement values (default to STOP)
- [ ] Handle invalid rotation values (default to NONE)
- [ ] Handle missing fields gracefully (use safe defaults)
- [ ] Log parsing errors for debugging
- [ ] Update default orders to include rotation field
- [ ] Tests verify parsing for all valid combinations

## Technical Details

### Files to Modify

- `ai_arena/llm_adapter/adapter.py` - Update `_parse_orders()` method

### Implementation Approach

**1. Update `_parse_orders()` Method:**

```python
def _parse_orders(self, response_json: dict, ship_id: str) -> Orders:
    """Parse LLM JSON response into Orders object.

    Args:
        response_json: Raw JSON from LLM
        ship_id: "ship_a" or "ship_b" for error logging

    Returns:
        Orders object with movement, rotation, and weapon commands
    """
    try:
        # Parse movement direction
        movement_str = response_json.get("ship_movement", "STOP").upper()
        try:
            movement = MovementDirection[movement_str]
        except KeyError:
            logger.warning(f"{ship_id} invalid movement '{movement_str}', defaulting to STOP")
            movement = MovementDirection.STOP

        # Parse rotation command (NEW)
        rotation_str = response_json.get("ship_rotation", "NONE").upper()
        try:
            rotation = RotationCommand[rotation_str]
        except KeyError:
            logger.warning(f"{ship_id} invalid rotation '{rotation_str}', defaulting to NONE")
            rotation = RotationCommand.NONE

        # Parse weapon action (existing logic)
        weapon_action = response_json.get("weapon_action", "MAINTAIN_CONFIG")

        # Parse torpedo orders (existing logic)
        torpedo_orders = self._parse_torpedo_orders(response_json.get("torpedo_orders", {}))

        return Orders(
            movement=movement,
            rotation=rotation,  # NEW field
            weapon_action=weapon_action,
            torpedo_orders=torpedo_orders
        )

    except Exception as e:
        logger.error(f"{ship_id} failed to parse orders: {e}")
        return self._default_orders()

def _default_orders(self) -> Orders:
    """Return safe default orders if parsing fails."""
    return Orders(
        movement=MovementDirection.STOP,
        rotation=RotationCommand.NONE,  # NEW
        weapon_action="MAINTAIN_CONFIG",
        torpedo_orders={}
    )
```

**2. Handle Backward Compatibility (Optional):**

If LLM returns old-style MovementType instead of separate movement/rotation:

```python
def _parse_orders_with_fallback(self, response_json: dict, ship_id: str) -> Orders:
    """Parse orders with fallback to old MovementType format."""
    # Try new format first
    if "ship_movement" in response_json and "ship_rotation" in response_json:
        return self._parse_orders_new_format(response_json, ship_id)

    # Fall back to old format
    if "movement" in response_json:
        return self._parse_orders_old_format(response_json, ship_id)

    # No valid format found
    logger.warning(f"{ship_id} no valid movement format, using defaults")
    return self._default_orders()
```

**3. Add Validation:**

```python
def _validate_orders(self, orders: Orders, ship: ShipState) -> Orders:
    """Validate orders against ship state (AE, etc).

    Args:
        orders: Parsed orders from LLM
        ship: Current ship state

    Returns:
        Validated orders (possibly downgraded if insufficient AE)
    """
    # Calculate total AE cost
    movement_cost = self._get_movement_ae_cost(orders.movement)
    rotation_cost = self._get_rotation_ae_cost(orders.rotation)
    total_cost = (movement_cost + rotation_cost) * ACTION_PHASE_DURATION

    # If insufficient AE, downgrade to STOP + NONE
    if ship.ae < total_cost:
        logger.warning(f"Insufficient AE ({ship.ae}) for orders (cost: {total_cost}), downgrading to STOP+NONE")
        return Orders(
            movement=MovementDirection.STOP,
            rotation=RotationCommand.NONE,
            weapon_action=orders.weapon_action,
            torpedo_orders={}
        )

    return orders
```

## Test Requirements

**`tests/test_llm_adapter.py`**

```python
def test_parse_orders_with_movement_and_rotation():
    """Parse valid movement and rotation commands."""
    adapter = LLMAdapter(model="gpt-4")
    response_json = {
        "ship_movement": "FORWARD",
        "ship_rotation": "HARD_LEFT",
        "weapon_action": "MAINTAIN_CONFIG"
    }

    orders = adapter._parse_orders(response_json, "ship_a")

    assert orders.movement == MovementDirection.FORWARD
    assert orders.rotation == RotationCommand.HARD_LEFT
    assert orders.weapon_action == "MAINTAIN_CONFIG"

def test_parse_orders_with_invalid_movement():
    """Invalid movement should default to STOP."""
    adapter = LLMAdapter(model="gpt-4")
    response_json = {
        "ship_movement": "INVALID_MOVEMENT",
        "ship_rotation": "NONE",
        "weapon_action": "MAINTAIN_CONFIG"
    }

    orders = adapter._parse_orders(response_json, "ship_a")

    assert orders.movement == MovementDirection.STOP
    assert orders.rotation == RotationCommand.NONE

def test_parse_orders_with_invalid_rotation():
    """Invalid rotation should default to NONE."""
    adapter = LLMAdapter(model="gpt-4")
    response_json = {
        "ship_movement": "LEFT",
        "ship_rotation": "SPIN_WILDLY",
        "weapon_action": "MAINTAIN_CONFIG"
    }

    orders = adapter._parse_orders(response_json, "ship_a")

    assert orders.movement == MovementDirection.LEFT
    assert orders.rotation == RotationCommand.NONE

def test_parse_orders_missing_rotation_field():
    """Missing rotation field should default to NONE."""
    adapter = LLMAdapter(model="gpt-4")
    response_json = {
        "ship_movement": "RIGHT",
        "weapon_action": "MAINTAIN_CONFIG"
        # No ship_rotation field
    }

    orders = adapter._parse_orders(response_json, "ship_a")

    assert orders.movement == MovementDirection.RIGHT
    assert orders.rotation == RotationCommand.NONE

def test_parse_orders_case_insensitive():
    """Parsing should be case-insensitive."""
    adapter = LLMAdapter(model="gpt-4")
    response_json = {
        "ship_movement": "forward",  # Lowercase
        "ship_rotation": "Hard_Left",  # Mixed case
        "weapon_action": "MAINTAIN_CONFIG"
    }

    orders = adapter._parse_orders(response_json, "ship_a")

    assert orders.movement == MovementDirection.FORWARD
    assert orders.rotation == RotationCommand.HARD_LEFT

def test_parse_all_movement_directions():
    """Test parsing all 9 movement directions."""
    adapter = LLMAdapter(model="gpt-4")
    directions = [
        "FORWARD", "FORWARD_LEFT", "FORWARD_RIGHT",
        "LEFT", "RIGHT",
        "BACKWARD", "BACKWARD_LEFT", "BACKWARD_RIGHT",
        "STOP"
    ]

    for direction_str in directions:
        response_json = {
            "ship_movement": direction_str,
            "ship_rotation": "NONE",
            "weapon_action": "MAINTAIN_CONFIG"
        }
        orders = adapter._parse_orders(response_json, "ship_a")
        assert orders.movement == MovementDirection[direction_str]

def test_parse_all_rotation_commands():
    """Test parsing all 5 rotation commands."""
    adapter = LLMAdapter(model="gpt-4")
    rotations = ["NONE", "SOFT_LEFT", "SOFT_RIGHT", "HARD_LEFT", "HARD_RIGHT"]

    for rotation_str in rotations:
        response_json = {
            "ship_movement": "FORWARD",
            "ship_rotation": rotation_str,
            "weapon_action": "MAINTAIN_CONFIG"
        }
        orders = adapter._parse_orders(response_json, "ship_a")
        assert orders.rotation == RotationCommand[rotation_str]

def test_default_orders_on_parse_failure():
    """Completely malformed JSON should return default orders."""
    adapter = LLMAdapter(model="gpt-4")
    response_json = {"invalid": "response"}

    orders = adapter._parse_orders(response_json, "ship_a")

    # Should return safe defaults
    assert orders.movement == MovementDirection.STOP
    assert orders.rotation == RotationCommand.NONE
```

## Implementation Checklist

- [ ] Update `_parse_orders()` to parse `ship_rotation` field
- [ ] Convert rotation string to `RotationCommand` enum
- [ ] Handle invalid rotation values (default to NONE)
- [ ] Handle missing rotation field (default to NONE)
- [ ] Make parsing case-insensitive
- [ ] Update `_default_orders()` to include rotation
- [ ] Add validation for combined AE costs (optional)
- [ ] Write tests for all movement directions
- [ ] Write tests for all rotation commands
- [ ] Write tests for error cases

## Edge Cases

1. **Missing rotation field:** Default to NONE
2. **Invalid enum value:** Log warning, use NONE
3. **Typos:** "HARD_LETF" → NONE (with warning)
4. **Case variations:** "hard_left", "Hard_Left", "HARD_LEFT" all valid
5. **Empty string:** "" → NONE
6. **Null value:** null → NONE

## Definition of Done

- [ ] LLM responses parsed correctly for both movement and rotation
- [ ] All valid movement/rotation combinations parse successfully
- [ ] Invalid values default safely
- [ ] Tests cover all enum values
- [ ] Tests cover error cases
- [ ] Logging added for debugging

## Files Changed

- Modify: `ai_arena/llm_adapter/adapter.py`
- Modify: `tests/test_llm_adapter.py`

## Dependencies

- **Requires:** Story 004 (Data models) and Story 008 (Prompt updates)

## Blocks

- Story 010-011: Testing stories (need parsing to work first)

## Notes

**Error Handling Philosophy:**

- **Never crash:** Bad LLM output should never crash the game
- **Safe defaults:** STOP + NONE is always safe
- **Log everything:** Parsing errors help debug prompts
- **Fail gracefully:** Game continues even if one ship's orders fail

**Testing Strategy:**

1. Unit tests for parsing logic
2. Integration tests with mock LLM responses
3. Real LLM tests to verify prompts work
4. Monitor logs during matches for parsing errors

**Common LLM Mistakes:**

- Forgetting `ship_rotation` field → defaults to NONE
- Typos in enum values → defaults to STOP/NONE
- Using old MovementType values → invalid, defaults to STOP
- Creative movements like "DIAGONAL" → invalid, defaults to STOP
