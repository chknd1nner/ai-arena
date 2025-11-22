# Story 042: Externalize LLM System Prompts

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

1. **Create `ai_arena/prompts/` directory structure**
2. **Extract system prompt** from `adapter.py` (lines 114-323) to Markdown file
3. **Implement prompt loading** with caching in `adapter.py`
4. **Test prompt rendering** with config value substitution
5. **Verify LLM behavior unchanged** (same prompt text, just external)

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of work completed
- Prompt file structure created
- File paths for all created/modified files
- Any issues encountered and resolutions
- Code references (file:line format)

---

## QA Agent Record

**Validation Date:** _Pending_
**Validator:** _TBD_
**Verdict:** ⏸️ Awaiting Implementation

### QA Checklist

- [ ] `ai_arena/prompts/system_prompt.md` exists with full prompt text
- [ ] `ai_arena/prompts/README.md` documents prompt structure
- [ ] `adapter.py` loads prompt from file (not embedded string)
- [ ] Config values (`{wide_arc}`, `{cooldown}`, etc.) correctly substituted
- [ ] Prompt caching works (file read once per adapter initialization)
- [ ] Changing prompt file affects next match (no code restart needed)
- [ ] All LLM tests pass
- [ ] Full match runs successfully with externalized prompts

**After validation, update this section with:**
- QA date and validator name
- Test results for each criterion
- Prompt rendering verification
- Any bugs found and their resolution
- Final verdict (Pass/Fail with justification)

---

## User Story

**As a** prompt engineer working on AI-Arena
**I want** the LLM system prompts externalized to Markdown files
**So that** I can iterate on prompts without touching Python code, enabling faster experimentation and version control

### Context

Currently, the system prompt is a **200+ line string** embedded in `ai_arena/llm_adapter/adapter.py` (lines 114-323).

**Problems:**
- Cannot edit prompts without modifying Python code
- Hard to review prompt changes in PRs (mixed with code)
- Impossible to A/B test prompts without code branches
- No syntax highlighting for prompt content
- Difficult to collaborate on prompt engineering
- Can't version prompts independently

**Example Current Code:**
```python
system_prompt = """You are an AI pilot controlling a starship...
## MOVEMENT & ROTATION SYSTEM
[200 more lines of embedded text]
"""
```

### Goal

Move all LLM prompts to external Markdown files in `ai_arena/prompts/` directory, enabling:
- Prompt editing without code changes
- Markdown syntax highlighting
- Easy A/B testing
- Independent prompt versioning
- Better collaboration

---

## Acceptance Criteria

### Must Have:

- [ ] `ai_arena/prompts/system_prompt.md` contains full system prompt
- [ ] `ai_arena/prompts/README.md` documents prompt structure and placeholder syntax
- [ ] `adapter.py` loads prompts from files (not embedded strings)
- [ ] Config value substitution works (e.g., `{wide_arc}` → `90`)
- [ ] Prompt caching implemented (file read once per adapter init)
- [ ] All existing LLM tests pass
- [ ] Full match runs successfully

### Should Have:

- [ ] Tactical examples extracted to separate `tactical_examples.md`
- [ ] Prompt composition supported (include sections modularly)
- [ ] Clear error message if prompt file missing

### Nice to Have:

- [ ] Prompt versioning system (e.g., `system_prompt_v2.md`)
- [ ] Template validation (check all placeholders provided)
- [ ] Prompt unit tests (verify rendering)

---

## Technical Specification

### Current State

**`ai_arena/llm_adapter/adapter.py` (lines 114-323):**
```python
def _build_prompt(self, state: GameState, ship_id: str) -> list:
    system_prompt = """You are an AI pilot controlling a starship in a tactical 1v1 space duel.

    ## MOVEMENT & ROTATION SYSTEM
    [200+ lines of embedded text with game rules, examples, formatting]
    """

    # Later, config values are substituted
    system_prompt = system_prompt.format(
        wide_arc=self.config.phaser.wide.arc_degrees,
        # ... 10 more config values
    )
```

**Issues:**
- Embedded in Python code (hard to edit)
- No syntax highlighting (treated as string)
- Mixed content (rules, examples, formatting instructions)

### Proposed Solution

**New Directory Structure:**
```
ai_arena/
├── prompts/
│   ├── README.md              # Prompt documentation
│   ├── system_prompt.md       # Main system prompt (200+ lines)
│   ├── tactical_examples.md   # Tactical maneuver examples
│   └── movement_reference.md  # Movement/rotation reference table
```

**Prompt Loading:**
```python
class LLMAdapter:
    def __init__(self, model_a: str, model_b: str, config: GameConfig):
        self.model_a = model_a
        self.model_b = model_b
        self.config = config

        # Load and cache system prompt
        self.system_prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load system prompt from file with caching."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompt.md"

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"System prompt not found: {prompt_path}\n"
                "Please ensure ai_arena/prompts/system_prompt.md exists."
            )

        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _build_prompt(self, state: GameState, ship_id: str) -> list:
        # Render template with config values
        system_prompt = self.system_prompt_template.format(
            wide_arc=self.config.phaser.wide.arc_degrees,
            wide_range=self.config.phaser.wide.range_units,
            # ... all config values
        )

        # Rest of prompt building logic...
```

### Placeholder Syntax

**In `system_prompt.md`:**
```markdown
## PHASERS

Phasers fire automatically if enemy is in arc AND cooldown = 0:
- **WIDE**: {wide_arc}° arc, {wide_range} range, {wide_damage} damage
- **FOCUSED**: {focused_arc}° arc, {focused_range} range, {focused_damage} damage
- **Switching config**: Takes {reconfig_time}s (can't fire during reconfiguration)
```

**Rendered output:**
```
## PHASERS

Phasers fire automatically if enemy is in arc AND cooldown = 0:
- **WIDE**: 90° arc, 250 range, 10 damage
- **FOCUSED**: 30° arc, 400 range, 15 damage
- **Switching config**: 15s (can't fire during reconfiguration)
```

---

## Implementation Guidance

### Step 1: Create Prompt Directory (0.2 days)

```bash
mkdir -p ai_arena/prompts
```

Create `ai_arena/prompts/README.md`:
```markdown
# AI-Arena LLM Prompts

This directory contains externalized LLM prompts for AI-Arena.

## Files

- **system_prompt.md**: Main system prompt with game rules and instructions
- **tactical_examples.md**: Tactical maneuver examples and strategies

## Placeholder Syntax

Prompts use Python `.format()` placeholders for config values:

- `{wide_arc}` → `self.config.phaser.wide.arc_degrees`
- `{cooldown}` → `self.config.phaser.wide.cooldown_seconds`
- etc.

## Editing Prompts

1. Edit Markdown files directly (no code changes needed)
2. Test changes by running a match: `python3 main.py`
3. Changes take effect immediately (no restart needed)

## Version Control

Prompts are version controlled in git. To A/B test:
1. Create feature branch: `git checkout -b prompt-experiment`
2. Edit prompts
3. Run matches and compare results
4. Merge if improved
```

### Step 2: Extract System Prompt (0.5 days)

Copy `adapter.py` lines 114-323 to `ai_arena/prompts/system_prompt.md`:

```markdown
# AI-Arena System Prompt

You are an AI pilot controlling a starship in a tactical 1v1 space duel.

## MOVEMENT & ROTATION SYSTEM

Your ship has TWO independent control systems:

1. **MOVEMENT DIRECTION** - Controls velocity (where you move)
2. **ROTATION COMMAND** - Controls heading (where you face)

[... rest of prompt content ...]

## JSON RESPONSE FORMAT

You must respond with valid JSON in this exact format:

```json
{
  "thinking": "Describe your tactical reasoning here",
  "ship_movement": "FORWARD|LEFT|RIGHT|...",
  "ship_rotation": "NONE|SOFT_LEFT|...",
  "weapon_action": "MAINTAIN_CONFIG|...",
  "torpedo_orders": {}
}
```
```

### Step 3: Update Adapter to Load Prompts (0.5 days)

**Modify `ai_arena/llm_adapter/adapter.py`:**

```python
from pathlib import Path

class LLMAdapter:
    def __init__(self, model_a: str, model_b: str, config: GameConfig):
        self.model_a = model_a
        self.model_b = model_b
        self.config = config

        # Load and cache system prompt template
        self._system_prompt_template = None

    @property
    def system_prompt_template(self) -> str:
        """Lazy-load system prompt template with caching."""
        if self._system_prompt_template is None:
            self._system_prompt_template = self._load_prompt_template()
        return self._system_prompt_template

    def _load_prompt_template(self) -> str:
        """Load system prompt from external Markdown file."""
        # Get path to prompts directory
        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompt_path = prompts_dir / "system_prompt.md"

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"System prompt file not found: {prompt_path}\n"
                f"Expected location: ai_arena/prompts/system_prompt.md"
            )

        logger.info(f"Loading system prompt from {prompt_path}")

        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()

        return template

    def _build_prompt(self, state: GameState, ship_id: str) -> list:
        """Build prompt with game state and rules."""
        us = state.ship_a if ship_id == "ship_a" else state.ship_b
        enemy = state.ship_b if ship_id == "ship_a" else state.ship_a
        our_torpedoes = [t for t in state.torpedoes if t.owner == ship_id]
        enemy_torpedoes = [t for t in state.torpedoes if t.owner != ship_id]

        # Render system prompt template with config values
        turn_duration = self.config.simulation.decision_interval_seconds
        cooldown = self.config.phaser.wide.cooldown_seconds
        max_shots = int(turn_duration / cooldown) if cooldown > 0 else 99

        system_prompt = self.system_prompt_template.format(
            wide_arc=self.config.phaser.wide.arc_degrees,
            wide_range=self.config.phaser.wide.range_units,
            wide_damage=self.config.phaser.wide.damage,
            focused_arc=self.config.phaser.focused.arc_degrees,
            focused_range=self.config.phaser.focused.range_units,
            focused_damage=self.config.phaser.focused.damage,
            reconfig_time=self.config.phaser.reconfiguration_time_seconds,
            cooldown=cooldown,
            turn_duration=turn_duration,
            max_shots=max_shots
        )

        # Build user prompt (state information)
        user_prompt = f"""TURN {state.turn}

YOUR STATUS ({ship_id}):
[... rest of user prompt ...]
"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
```

### Step 4: Test Prompt Loading (0.3 days)

```python
# Test script: test_prompt_loading.py
from ai_arena.llm_adapter.adapter import LLMAdapter
from ai_arena.config import ConfigLoader

def test_prompt_loading():
    """Test that prompts load correctly from files."""
    config = ConfigLoader().load("config.json")
    adapter = LLMAdapter("gpt-4", "gpt-4", config)

    # Verify prompt loaded
    assert adapter.system_prompt_template is not None
    assert len(adapter.system_prompt_template) > 1000  # Should be long

    # Verify caching works
    template1 = adapter.system_prompt_template
    template2 = adapter.system_prompt_template
    assert template1 is template2  # Same object (cached)

    print("✅ Prompt loading works correctly")

if __name__ == "__main__":
    test_prompt_loading()
```

---

## Testing Requirements

### Unit Tests

```python
# tests/test_llm_adapter.py

def test_load_prompt_template():
    """Test that system prompt loads from file."""
    from ai_arena.llm_adapter.adapter import LLMAdapter
    from ai_arena.config import ConfigLoader

    config = ConfigLoader().load("config.json")
    adapter = LLMAdapter("gpt-4", "gpt-4", config)

    template = adapter.system_prompt_template

    # Verify template loaded
    assert template is not None
    assert isinstance(template, str)
    assert len(template) > 1000

    # Verify placeholders exist
    assert "{wide_arc}" in template
    assert "{cooldown}" in template

def test_prompt_rendering():
    """Test that prompt renders with config values."""
    from ai_arena.llm_adapter.adapter import LLMAdapter
    from ai_arena.config import ConfigLoader
    from ai_arena.game_engine.data_models import GameState, ShipState, Vec2D, PhaserConfig

    config = ConfigLoader().load("config.json")
    adapter = LLMAdapter("gpt-4", "gpt-4", config)

    # Create minimal state
    state = GameState(
        turn=1,
        ship_a=ShipState(...),
        ship_b=ShipState(...),
        torpedoes=[]
    )

    # Build prompt
    prompt = adapter._build_prompt(state, "ship_a")

    # Verify rendering
    system_prompt = prompt[0]["content"]
    assert "{wide_arc}" not in system_prompt  # Placeholder substituted
    assert "90" in system_prompt or "30" in system_prompt  # Config value present

def test_missing_prompt_file():
    """Test error handling when prompt file missing."""
    from ai_arena.llm_adapter.adapter import LLMAdapter
    from ai_arena.config import ConfigLoader
    import shutil
    from pathlib import Path

    # Temporarily rename prompt file
    prompt_path = Path("ai_arena/prompts/system_prompt.md")
    backup_path = prompt_path.with_suffix(".md.bak")

    try:
        shutil.move(prompt_path, backup_path)

        config = ConfigLoader().load("config.json")

        with pytest.raises(FileNotFoundError):
            adapter = LLMAdapter("gpt-4", "gpt-4", config)
            _ = adapter.system_prompt_template

    finally:
        # Restore prompt file
        if backup_path.exists():
            shutil.move(backup_path, prompt_path)
```

### Integration Tests

```bash
# Test full match with externalized prompts
python3 main.py

# Should complete successfully with no errors

# Test prompt editing workflow
echo "# Modified prompt" >> ai_arena/prompts/system_prompt.md
python3 main.py  # Should use modified prompt immediately
git checkout ai_arena/prompts/system_prompt.md  # Restore
```

---

## Files to Create

1. **`ai_arena/prompts/README.md`** - Prompt documentation
2. **`ai_arena/prompts/system_prompt.md`** - Main system prompt (200+ lines)
3. **`ai_arena/prompts/tactical_examples.md`** - Tactical examples (optional)

---

## Files to Modify

1. **`ai_arena/llm_adapter/adapter.py`**
   - Add `_load_prompt_template()` method
   - Add `system_prompt_template` property
   - Modify `_build_prompt()` to use external template
   - Remove embedded prompt string (lines 114-323)

2. **`CLAUDE.md`** - Document new prompt structure
3. **`docs/architecture.md`** - Update LLM Adapter section

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] `ai_arena/prompts/system_prompt.md` contains full prompt
- [ ] `adapter.py` loads prompt from file
- [ ] Config substitution works correctly
- [ ] All LLM tests pass
- [ ] Full match runs successfully
- [ ] Prompt caching verified (file read only once)
- [ ] Error handling for missing prompt file
- [ ] Documentation updated
- [ ] Code reviewed

---

## Dependencies

**Blocks:**
- None (independent story)

**Blocked By:**
- None (can start immediately)

**Can Run Parallel With:**
- Story 041 (Remove Legacy Movement Code)
- Story 043 (Consolidate Duplicate Code)

---

## Notes

### Design Decisions

- **Markdown format**: Better syntax highlighting than plain text
- **Single template file**: Start simple, can split later if needed
- **Python `.format()`**: Simple, no dependencies, works well for config values
- **Lazy loading with caching**: Read file once per adapter instance

### Benefits

After this story:
- ✅ Edit prompts without touching code
- ✅ Faster prompt iteration cycle
- ✅ Better collaboration (Markdown PRs)
- ✅ Independent prompt versioning
- ✅ A/B testing via git branches

### Future Enhancements

- Prompt versioning system (e.g., `v1/system_prompt.md`, `v2/system_prompt.md`)
- Template composition (include tactical examples conditionally)
- Prompt validation (ensure all placeholders provided)
- Multi-language prompts (for i18n)
