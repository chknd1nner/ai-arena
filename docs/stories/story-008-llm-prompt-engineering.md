# Story 008: LLM Prompt Engineering

**Epic:** [Epic 002: Independent Movement & Rotation System](../epic-002-independent-movement-rotation.md)
**Status:** Ready for Development
**Size:** Medium
**Priority:** P0

---

## User Story

**As an** LLM adapter
**I want** to teach models the independent movement and rotation system through clear prompts
**So that** LLMs can effectively use both commands to execute tactical maneuvers

## Context

After Stories 004-007, the physics engine supports independent movement and rotation. Now we need to update the LLM system prompt to:
1. Explain the two-command system (movement + rotation)
2. Provide clear examples of tactical maneuvers
3. Document the new JSON response format
4. Help LLMs understand when to use each combination

## Acceptance Criteria

- [ ] System prompt documents all 9 movement directions with descriptions
- [ ] System prompt documents all 5 rotation commands with descriptions
- [ ] AE costs listed for each movement and rotation option
- [ ] Tactical maneuver examples provided (strafing, retreat, reposition, drift)
- [ ] JSON response format clearly specified with both fields
- [ ] Examples show combined movement + rotation scenarios
- [ ] Prompt explains independence of movement (velocity) vs rotation (heading)
- [ ] Prompt explains phasers point at heading, not movement direction

## Technical Details

### Files to Modify

- `ai_arena/llm_adapter/adapter.py` - Update `_build_system_prompt()`

### Implementation Approach

**Update System Prompt:**

```python
def _build_system_prompt(self) -> str:
    return """You are an AI pilot controlling a starship in a tactical 1v1 space duel.

## MOVEMENT & ROTATION SYSTEM

Your ship has TWO independent control systems:

1. **MOVEMENT DIRECTION** - Controls velocity (where you move)
2. **ROTATION COMMAND** - Controls heading (where you face)

These are INDEPENDENT. You can move in one direction while facing another direction.

### MOVEMENT DIRECTIONS (Velocity Control)

Movement sets your velocity direction relative to your current heading:

| Direction | Description | Angle | AE/Second | Total (15s) |
|-----------|-------------|-------|-----------|-------------|
| FORWARD | Continue straight ahead | 0° | 0.33 | 5.0 |
| FORWARD_LEFT | Diagonal left-forward | -45° | 0.53 | 8.0 |
| FORWARD_RIGHT | Diagonal right-forward | +45° | 0.53 | 8.0 |
| LEFT | Perpendicular left | -90° | 0.67 | 10.0 |
| RIGHT | Perpendicular right | +90° | 0.67 | 10.0 |
| BACKWARD | Reverse direction | 180° | 0.67 | 10.0 |
| BACKWARD_LEFT | Diagonal left-backward | -135° | 0.80 | 12.0 |
| BACKWARD_RIGHT | Diagonal right-backward | +135° | 0.80 | 12.0 |
| STOP | Coast to halt | N/A | 0.0 | 0.0 |

**Movement sets velocity direction but does NOT change heading.**

### ROTATION COMMANDS (Heading Control)

Rotation changes where your ship faces (and where phasers point):

| Rotation | Description | Rate | Total (15s) | AE/Second | Total (15s) |
|----------|-------------|------|-------------|-----------|-------------|
| NONE | Maintain current heading | 0°/s | 0° | 0.0 | 0.0 |
| SOFT_LEFT | Gentle left rotation | 1°/s | 15° | 0.13 | 2.0 |
| SOFT_RIGHT | Gentle right rotation | 1°/s | 15° | 0.13 | 2.0 |
| HARD_LEFT | Aggressive left rotation | 3°/s | 45° | 0.33 | 5.0 |
| HARD_RIGHT | Aggressive right rotation | 3°/s | 45° | 0.33 | 5.0 |

**Rotation changes heading but does NOT change velocity direction.**

### COMBINED AE COST

Total AE cost = Movement cost + Rotation cost

Examples:
- FORWARD + NONE = 0.33 + 0.0 = 0.33 AE/s
- FORWARD + HARD_LEFT = 0.33 + 0.33 = 0.66 AE/s
- LEFT + HARD_RIGHT = 0.67 + 0.33 = 1.0 AE/s

Your ship regenerates 0.33 AE/s, so net burn = total cost - 0.33 AE/s.

### TACTICAL MANEUVERS

**1. Strafing Run (Evasive Fire)**
```
Movement: RIGHT (move perpendicular right)
Rotation: HARD_LEFT (rotate to face left)
Result: Circle right around enemy while keeping phasers pointed at them
Cost: 0.67 + 0.33 = 1.0 AE/s (net drain: 0.67 AE/s)
Use when: Evading while maintaining firing solution
```

**2. Retreat with Coverage (Defensive Withdrawal)**
```
Movement: BACKWARD (reverse away)
Rotation: NONE (keep facing forward)
Result: Back away while phasers still point at enemy
Cost: 0.67 + 0.0 = 0.67 AE/s (net drain: 0.34 AE/s)
Use when: Low shields, need to create distance while covering
```

**3. Aggressive Reposition (Flanking)**
```
Movement: FORWARD (advance straight)
Rotation: HARD_RIGHT (rotate 45° right)
Result: Close distance while angling for better firing arc
Cost: 0.33 + 0.33 = 0.66 AE/s (net drain: 0.33 AE/s)
Use when: Maneuvering for tactical advantage
```

**4. The Drift (Tracking Evasion)**
```
Movement: LEFT (slide left)
Rotation: SOFT_LEFT (slowly rotate left)
Result: Slide laterally while gradually tracking enemy movement
Cost: 0.67 + 0.13 = 0.80 AE/s (net drain: 0.47 AE/s)
Use when: Evading while maintaining partial firing solution
```

### PHASERS & HEADING

**CRITICAL:** Phasers always point in your HEADING direction, not your movement direction.

Example:
- You're facing East (heading = 0°)
- You move LEFT (velocity = North)
- Your phasers fire EAST (heading direction)
- You're moving north but shooting east

This is why rotation matters - it controls where you shoot!

## WEAPONS

(... existing weapon documentation ...)

## JSON RESPONSE FORMAT

You must respond with valid JSON in this exact format:

```json
{
  "thinking": "Describe your tactical reasoning here",
  "ship_movement": "FORWARD|LEFT|RIGHT|BACKWARD|FORWARD_LEFT|FORWARD_RIGHT|BACKWARD_LEFT|BACKWARD_RIGHT|STOP",
  "ship_rotation": "NONE|SOFT_LEFT|SOFT_RIGHT|HARD_LEFT|HARD_RIGHT",
  "weapon_action": "MAINTAIN_CONFIG|RECONFIGURE_WIDE|RECONFIGURE_FOCUSED|LAUNCH_TORPEDO",
  "torpedo_orders": {}
}
```

**Required fields:**
- `ship_movement`: One of the 9 movement directions
- `ship_rotation`: One of the 5 rotation commands
- `weapon_action`: Weapon command
- `thinking`: Your tactical reasoning

## GAME STATE

(... existing game state documentation ...)
"""
```

## Test Requirements

**Manual Testing:**

Since this is prompt engineering, testing involves:
1. Running matches with updated prompts
2. Checking LLM responses parse correctly
3. Verifying LLMs actually use rotation commands
4. Inspecting `thinking` tokens for understanding

**Automated Tests:**

```python
def test_system_prompt_includes_movement_directions():
    """Verify system prompt documents all movement directions."""
    adapter = LLMAdapter()
    prompt = adapter._build_system_prompt()

    assert "FORWARD" in prompt
    assert "LEFT" in prompt
    assert "RIGHT" in prompt
    assert "BACKWARD" in prompt
    assert "STOP" in prompt

def test_system_prompt_includes_rotation_commands():
    """Verify system prompt documents all rotation commands."""
    adapter = LLMAdapter()
    prompt = adapter._build_system_prompt()

    assert "NONE" in prompt
    assert "SOFT_LEFT" in prompt
    assert "HARD_LEFT" in prompt

def test_system_prompt_includes_tactical_examples():
    """Verify system prompt includes tactical maneuver examples."""
    adapter = LLMAdapter()
    prompt = adapter._build_system_prompt()

    assert "Strafing" in prompt or "strafing" in prompt
    assert "Retreat" in prompt or "retreat" in prompt
```

## Implementation Checklist

- [ ] Document all 9 movement directions in system prompt
- [ ] Document all 5 rotation commands in system prompt
- [ ] List AE costs for each option
- [ ] Provide 4 tactical maneuver examples
- [ ] Explain independence of movement vs rotation
- [ ] Explain phasers point at heading
- [ ] Update JSON response format documentation
- [ ] Add examples with combined movement + rotation
- [ ] Test prompt with actual LLM calls
- [ ] Verify LLMs understand and use the system

## Definition of Done

- [ ] System prompt updated with complete documentation
- [ ] All movement directions and rotation commands listed
- [ ] Tactical examples provided
- [ ] JSON format clearly specified
- [ ] LLMs successfully parse and use new format

## Files Changed

- Modify: `ai_arena/llm_adapter/adapter.py`

## Dependencies

- **Requires:** Stories 004-007 (physics system complete)

## Blocks

- Story 009: LLM Order Parsing (parsing must match prompt format)

## Notes

**Prompt Engineering Tips:**

1. **Be explicit:** LLMs may not understand "independent" without examples
2. **Show, don't tell:** Tactical examples are more effective than abstract explanations
3. **Repeat key concepts:** "Phasers point at heading" said multiple ways
4. **Use tables:** Structured format helps LLMs parse options
5. **Provide reasoning:** Explain WHY each maneuver is useful

**Testing Strategy:**

Run initial matches and check LLM thinking tokens:
- Do they understand the two-command system?
- Do they use rotation commands (not just NONE)?
- Do they attempt tactical maneuvers?
- Are their explanations coherent?

If LLMs struggle:
- Add more examples
- Simplify language
- Make format more rigid
- Provide anti-patterns ("DON'T do this")
