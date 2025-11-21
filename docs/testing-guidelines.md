# Testing Guidelines

This document provides comprehensive guidance on testing practices for the AI Arena project, including test file organization, validation strategies, and visual gameplay testing.

---

## Test File Organization

**CRITICAL RULES FOR TEST FILES:**

### 1. ALL test files MUST go in the `/tests` directory

- Unit tests: `/tests/test_*.py`
- Integration tests: `/tests/test_*_integration.py`
- Test fixtures: `/tests/fixtures/`
- Test mocks: `/tests/mocks/`
- Test helpers: `/tests/helpers.py`, `/tests/conftest.py`

### 2. NEVER create test files in the project root

- No `test_*.py` files in root directory
- No `qa_*.py` files in root directory
- No `validate_*.py` files in root directory
- All tests belong in `/tests` regardless of type

### 3. For temporary visual/E2E tests

If you need to run Playwright or visual validation tests temporarily:
- Create the script
- Run it immediately
- Delete it after validation is complete
- **DO NOT commit temporary test scripts**
- If the test needs to be permanent, add it to `/tests`

### 4. Why this matters

- Keeps the repository clean and organized
- Makes it clear where all tests live
- Prevents accumulation of redundant QA validation scripts
- Maintains a single source of truth for testing

### Example: Correct test structure

```
/tests
  ├── test_physics.py              # Unit test for physics
  ├── test_llm_adapter.py          # Unit test for LLM adapter
  ├── test_continuous_physics.py   # Integration test
  ├── conftest.py                  # Pytest configuration
  ├── helpers.py                   # Test helper functions
  ├── mocks/                       # Mock implementations
  │   └── mock_llm.py
  └── fixtures/                    # Test fixtures
      └── sample_replay.json
```

---

## Running Tests

### All tests
```bash
pytest
```

### Specific test file
```bash
pytest tests/test_physics.py
```

### Specific test with verbose output
```bash
pytest tests/test_physics.py -v
```

### With coverage report
```bash
pytest --cov=ai_arena tests/
```

---

## Unit Testing Strategy

**For each feature branch before creating a PR:**

```bash
pytest                           # All tests pass
pytest tests/test_physics.py -v # Verify physics tests
pytest tests/test_config.py -v  # Verify related tests
```

**Test naming convention:**
- Test files: `test_*.py`
- Test functions: `test_<what_is_being_tested>()`
- Test classes: `Test<ComponentName>`

**What to test:**
- Physics calculations (determinism is critical)
- Order parsing and validation
- LLM adapter error handling
- Data model conversions
- Game state transitions

---

## Visual/Gameplay Testing

### Manual Gameplay Testing

Use this process to validate that actual game mechanics work correctly in the frontend:

1. **Start both servers:**
   ```bash
   python3 main.py                    # Backend
   cd frontend && npm start           # Frontend (in another terminal)
   ```

2. **Open the application:**
   - Navigate to http://localhost:3000
   - Select a replay or click "Start New Match"

3. **Visual validation checklist:**
   - [ ] Ships render at correct positions (not NaN, not clustered in corner)
   - [ ] Torpedoes move smoothly across the arena
   - [ ] Blast zones appear when explosions occur
   - [ ] Ships animate their rotations correctly
   - [ ] Turn counter updates as playback progresses
   - [ ] Speed controls work (slow, normal, fast)
   - [ ] Seeking to specific turns works correctly

4. **Thinking tokens validation:**
   - [ ] Thinking panel toggles with T key
   - [ ] Thinking text displays clearly for both ships
   - [ ] Split-screen layout shows Ship A (blue) on left, Ship B (red) on right
   - [ ] Thinking text updates when changing turns

5. **Screenshot validation:**
   - Take a screenshot of the final rendered state
   - Verify ships are at expected positions based on replay data
   - Compare with manual calculations from replay JSON

### Automated Visual Testing (Playwright)

For temporary automated visual tests:

```javascript
// test_gameplay.js - temporary test file
import { test, expect } from '@playwright/test';

test('ships render at correct positions', async ({ page }) => {
  await page.goto('http://localhost:3000');

  // Wait for canvas to render
  const canvas = page.locator('canvas');
  await canvas.waitFor();

  // Take screenshot for comparison
  await page.screenshot({ path: '/tmp/gameplay.png' });

  // Verify no errors in console
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  expect(errors).toHaveLength(0);
});
```

**Important:**
- Always run Playwright tests headless first: `HEADLESS=true npm test`
- If tests fail, run with visible window to debug: `HEADLESS=false npm test`
- Delete test file after validation completes (unless making it permanent in `/tests`)
- Screenshots are saved to `/tmp/` directory

### Replay Data Validation

When testing data transformations (like coordinate format changes):

1. **Check replay JSON structure:**
   ```bash
   # Inspect a replay file
   cat replays/*.json | jq '.turns[0].state.ship_a.position'
   # Should show either [x, y] (array) or {x: x, y: y} (object)
   ```

2. **Verify transformation is applied:**
   - Frontend should convert arrays to objects
   - Both ships should be visible and correctly positioned
   - No (NaN, NaN) positions in the viewport

3. **Test with multiple replays:**
   - Old replays (arrays format)
   - New replays (object format)
   - Both should work without errors

---

## Backend Testing

### Physics Testing

Physics tests are critical because the simulation must be deterministic:

```bash
pytest tests/test_physics.py -v
```

**What physics tests verify:**
- Same inputs always produce same outputs
- Movement calculations are correct
- Phaser/torpedo mechanics work as expected
- Collisions are detected accurately
- Energy accounting is correct

### LLM Adapter Testing

```bash
pytest tests/test_llm_adapter.py -v
```

**What adapter tests verify:**
- Order parsing from LLM responses
- Error handling for malformed responses
- Thinking token extraction
- Model string format handling

### Integration Testing

```bash
pytest tests/test_*_integration.py -v
```

**What integration tests verify:**
- Match orchestration (turn loop works)
- Physics + LLM integration (orders execute correctly)
- Replay generation (data is correctly captured)
- State transitions are valid

---

## Debugging Failed Tests

### Common Issues

**❌ Test fails: "replay not reproducible"**
- Physics is non-deterministic
- Check for randomness in `physics.py`
- Verify floating-point operations are consistent
- Run the same inputs multiple times, expect identical output

**❌ Test fails: "coordinate transformation missing"**
- Frontend receiving array positions: `[100, 200]`
- Expected object format: `{x: 100, y: 200}`
- Check `useReplayData.js` transformation function
- Verify all position/velocity fields are transformed

**❌ Test fails: "LLM returns invalid JSON"**
- Ensure `response_format={"type": "json_object"}` is set
- Check that system prompt is clear about expected format
- Test with smaller models first (Haiku, GPT-3.5-turbo)
- Inspect `thinking_a` / `thinking_b` in replay for error messages

**❌ Test fails: "order validation error"**
- Check `_validate_orders()` in `physics.py`
- Insufficient action energy → STOP order issued
- Invalid movement type → STOP order issued
- Torpedo command references non-existent torpedo → STOP order issued

### Debugging Steps

1. **Run test in verbose mode:**
   ```bash
   pytest tests/test_name.py -v -s
   ```

2. **Inspect replay JSON:**
   ```bash
   cat replays/last_replay.json | jq . | less
   ```

3. **Check console output for specific errors:**
   - Backend: look for "LLM error", "JSON parse error"
   - Frontend: open browser console for JavaScript errors

4. **Reduce scope:**
   - Test a single turn instead of full match
   - Test with simpler models (Haiku)
   - Test with hardcoded orders instead of LLM

---

## Test Coverage Goals

**Minimum coverage targets:**

| Component | Target | Why |
|-----------|--------|-----|
| `physics.py` | 90%+ | Determinism is non-negotiable |
| `data_models.py` | 85%+ | Data integrity critical |
| `adapter.py` | 80%+ | LLM integration error-prone |
| `match_orchestrator.py` | 75%+ | Complex orchestration logic |
| Frontend components | 60%+ | Visual testing catches most issues |

**Run coverage report:**
```bash
pytest --cov=ai_arena --cov-report=html tests/
open htmlcov/index.html
```

---

## Before Creating a PR

**Verification checklist:**

- [ ] All tests pass: `pytest`
- [ ] No console errors (backend or frontend)
- [ ] Manual gameplay test completed (if UI changes)
- [ ] Replay reproduction verified (if physics changes)
- [ ] Test file organization follows `/tests` structure
- [ ] No temporary test scripts committed
- [ ] Documentation updated if needed

---

## References

- **CLAUDE.md** → Quick testing commands
- **development-workflow.md** → Integration with Claude Code Web workflow
- **architecture.md** → Component testing boundaries
