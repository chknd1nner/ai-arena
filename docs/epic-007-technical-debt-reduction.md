# Epic 007: Technical Debt Reduction & Code Quality

**Status:** Not Started
**Priority:** P1 (Technical Foundation)
**Estimated Size:** Large (7 stories, ~9 days)
**Target for:** Claude Code Web

---

## Overview

Systematic elimination of accumulated technical debt across the AI-Arena codebase. This epic consolidates inconsistent patterns, removes legacy code, externalizes embedded configuration, and improves code organization without adding new features. The refactoring establishes a cleaner foundation for future development (tournaments, analytics, live streaming).

## Problem Statement

After completing 6 feature epics (Configuration, Movement, Replay, Physics, Blast Zones, Thinking Tokens), the codebase has accumulated **moderate technical debt**:

### Current Issues:

1. **Legacy Code Pollution** (Physics Engine)
   - Old `MovementType` enum still present alongside new `MovementDirection` system
   - Two movement paradigms coexist (ships vs torpedoes)
   - `movement_costs` dict marked "for backward compatibility" but never removed
   - Confusion: which system should new code use?

2. **Embedded Configuration** (LLM Adapter)
   - 200+ line system prompt hardcoded in `adapter.py`
   - Impossible to A/B test prompts without code changes
   - No version control for prompt iterations
   - Hard to read, maintain, or collaborate on prompt engineering

3. **Code Duplication** (Multiple Components)
   - `_parse_torpedo_action()` exists in both `physics.py` AND `adapter.py`
   - State copying logic inconsistent
   - Blast zone formatting repeated

4. **Inline Styling Bloat** (Frontend)
   - 130+ lines of inline `style={{}}` objects in `ReplayViewer.jsx`
   - No CSS modules or styled-components
   - Hard to maintain consistent theming
   - Performance overhead from repeated object creation

5. **Test Coverage Gaps**
   - No unit tests for parsing logic
   - No integration tests for refactored components
   - Refactoring without tests is high-risk

### Impact:

- **Developer Velocity**: Slower feature development due to confusion
- **Maintainability**: Hard to onboard new contributors
- **Prompt Iteration**: Can't experiment with LLM prompts without code changes
- **Styling Changes**: UI updates require touching JSX instead of CSS

### Why Now?

- All core features complete (Epics 001-006)
- Before adding tournaments/analytics (future epics)
- Clean foundation prevents compounding debt
- Current debt is **manageable** (~9 days), but will grow if ignored

---

## Goals

1. **Eliminate Legacy Code**: Remove deprecated `MovementType` enum and old movement system
2. **Externalize Configuration**: Move prompts, constants to external files
3. **Consolidate Duplication**: Single source of truth for shared logic
4. **Organize Frontend Styles**: CSS modules for all components
5. **Improve Testability**: Clean separation enables better unit tests
6. **Maintain Stability**: Zero breaking changes to public APIs or game mechanics

---

## Success Criteria

- [ ] No legacy `MovementType` references in codebase
- [ ] System prompts externalized to `ai_arena/prompts/` directory
- [ ] Zero duplicate function implementations
- [ ] All inline styles moved to CSS modules
- [ ] All refactored code has unit tests
- [ ] All existing tests still pass
- [ ] No changes to replay format or game behavior
- [ ] Documentation updated to reflect new structure

---

## User Stories

1. [Story 041: Remove Legacy Movement Code](stories/story-041-remove-legacy-movement-code.md)
2. [Story 042: Externalize LLM System Prompts](stories/story-042-externalize-llm-prompts.md)
3. [Story 043: Consolidate Duplicate Code](stories/story-043-consolidate-duplicate-code.md)
4. [Story 044: Match Orchestrator & Replay Cleanup](stories/story-044-orchestrator-replay-cleanup.md)
5. [Story 045: Extract Frontend CSS to Modules](stories/story-045-extract-css-modules.md)
6. [Story 046: Refactor Canvas Rendering Effects](stories/story-046-refactor-canvas-effects.md)
7. [Story 047: Add Unit Tests for Refactored Code](stories/story-047-add-unit-tests.md)

---

## Technical Approach

### Architecture Changes

**Before Epic 007:**

```
ai_arena/
├── game_engine/
│   ├── physics.py           # 707 lines, legacy code mixed in
│   ├── data_models.py       # MovementType + MovementDirection enums
├── llm_adapter/
│   ├── adapter.py           # 493 lines, 200-line prompt embedded
├── orchestrator/
│   ├── match_orchestrator.py # Accesses private physics methods
├── replay/
│   ├── recorder.py          # Manual serialization boilerplate

frontend/
├── src/components/
│   ├── ReplayViewer.jsx     # 130 lines of inline styles
│   ├── CanvasRenderer.jsx   # Complex useEffect chains, mock data
```

**After Epic 007:**

```
ai_arena/
├── game_engine/
│   ├── physics.py           # ~650 lines, no legacy code
│   ├── data_models.py       # Only MovementDirection + RotationCommand
│   ├── utils.py             # Shared utilities (NEW)
├── llm_adapter/
│   ├── adapter.py           # ~250 lines, loads external prompts
│   ├── prompt_formatter.py  # Formatting utilities (NEW)
├── prompts/                  # (NEW)
│   ├── system_prompt.md     # Externalized prompt
│   ├── tactical_examples.md # Examples library
├── orchestrator/
│   ├── match_orchestrator.py # Uses public APIs
├── replay/
│   ├── recorder.py          # Auto-serialization with dataclasses

frontend/
├── src/
│   ├── components/
│   │   ├── ReplayViewer.jsx     # ~150 lines, no inline styles
│   │   ├── ReplayViewer.module.css # (NEW)
│   │   ├── CanvasRenderer.jsx   # Simplified effects
│   ├── constants/
│   │   ├── rendering.js         # Extracted constants (NEW)
│   ├── hooks/
│   │   ├── useAnimationLoop.js  # Custom hook (NEW)
```

---

## Implementation Phases

### **Phase 1: Backend Cleanup** (Stories 041-043, ~5 days)

**Goal:** Clean up Python backend code without touching frontend

**Stories:**
- Story 041: Remove legacy movement code
- Story 042: Externalize LLM prompts
- Story 043: Consolidate duplicate code

**Testing Strategy:**
- All existing backend tests must pass
- Run full match with new code
- Compare replay output to baseline

**Risk:** Low (backend changes, well-tested)

---

### **Phase 2: Component Polish** (Story 044, ~0.5 days)

**Goal:** Minor fixes to Match Orchestrator and Replay system

**Stories:**
- Story 044: Match Orchestrator & Replay cleanup

**Testing Strategy:**
- Match orchestration tests
- Replay serialization tests

**Risk:** Very Low (isolated changes)

---

### **Phase 3: Frontend Refactor** (Stories 045-046, ~4 days)

**Goal:** Extract inline styles, simplify rendering logic

**Stories:**
- Story 045: Extract CSS to modules
- Story 046: Refactor canvas effects

**Testing Strategy:**
- Visual regression tests (screenshots)
- Playback functionality tests
- Responsive layout tests

**Risk:** Medium (CSS changes can break layouts)

---

### **Phase 4: Testing & Documentation** (Story 047, ~0.5 days)

**Goal:** Add unit tests for refactored code, update docs

**Stories:**
- Story 047: Add unit tests

**Testing Strategy:**
- 80%+ code coverage for refactored modules
- Integration tests pass

**Risk:** Low

---

## Testing Strategy

### Per-Story Testing

Each story has inline testing requirements. General approach:

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test component interactions
3. **Visual Tests**: Screenshots for frontend changes
4. **Regression Tests**: Ensure no existing functionality breaks

### Overall Epic Testing

After all stories complete:

```bash
# Backend tests
pytest tests/ -v --cov=ai_arena

# Full match integration test
python3 main.py  # Run complete match, verify it works

# Frontend tests
cd frontend
npm test
npm start  # Manual visual verification

# Replay compatibility test
python3 -c "from ai_arena.replay.recorder import ReplayLoader; \
            replays = ReplayLoader.list_matches(); \
            print(f'Found {len(replays)} replays, all loadable')"
```

### Visual Regression Testing

**Baseline Creation:**
```bash
# Before starting Epic 007
cd frontend
npm start
# Take screenshots of:
# - Match selector
# - Replay viewer (turn 1, 5, 10)
# - Thinking panel
# - Match summary
# Save to docs/screenshots/baseline/
```

**Comparison:**
```bash
# After Epic 007 complete
# Take same screenshots
# Save to docs/screenshots/epic-007/
# Manual comparison (or use visual diff tool)
```

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Breaking Changes** | Medium | High | Extensive testing between stories, feature flags for risky changes |
| **CSS Bugs** | Medium | Medium | Visual regression screenshots, responsive layout tests |
| **Performance Regression** | Low | Medium | Profile before/after, check animation frame rate |
| **Prompt Changes Behavior** | Low | Low | Use exact same prompt text initially, only externalize location |
| **Incomplete Migration** | Low | High | Thorough grep audits, deprecation warnings before deletion |

---

## Dependencies

### Required (Blocking):

- All stories in Epic 006 complete ✅

### Enables (Future):

- Epic 008: Tournament Mode (clean foundation)
- Epic 009: Advanced Analytics (easier to extend)
- Epic 010: Live Streaming (modular components)

---

## Definition of Done

- [ ] All 7 stories completed
- [ ] No `MovementType` references in codebase
- [ ] System prompts in `ai_arena/prompts/` directory
- [ ] No duplicate code implementations
- [ ] All inline styles replaced with CSS modules
- [ ] All refactored code has unit tests (90%+ coverage)
- [ ] All existing tests pass
- [ ] Visual regression tests pass
- [ ] Full match runs successfully (integration test)
- [ ] Documentation updated (`CLAUDE.md`, `README.md`, architecture docs)
- [ ] No regressions in game behavior or replay format

---

## Files Summary

### Files to Create (12+ new files):

**Backend:**
- `ai_arena/prompts/README.md`
- `ai_arena/prompts/system_prompt.md`
- `ai_arena/prompts/tactical_examples.md`
- `ai_arena/game_engine/utils.py`
- `ai_arena/llm_adapter/prompt_formatter.py`
- `tests/test_utils.py`
- `tests/test_prompt_formatter.py`

**Frontend:**
- `frontend/src/components/*.module.css` (5 files)
- `frontend/src/styles/colors.css`
- `frontend/src/styles/animations.css`
- `frontend/src/constants/rendering.js`
- `frontend/src/hooks/useAnimationLoop.js`
- `frontend/src/hooks/__tests__/useAnimationLoop.test.js`

### Files to Modify (12 files):

**Backend:**
- `ai_arena/game_engine/data_models.py`
- `ai_arena/game_engine/physics.py`
- `ai_arena/llm_adapter/adapter.py`
- `ai_arena/orchestrator/match_orchestrator.py`
- `ai_arena/replay/recorder.py`
- `CLAUDE.md`
- `docs/architecture.md`

**Frontend:**
- `frontend/src/components/ReplayViewer.jsx`
- `frontend/src/components/ThinkingPanel.jsx`
- `frontend/src/components/PlaybackControls.jsx`
- `frontend/src/components/StateOverlay.jsx`
- `frontend/src/components/CanvasRenderer.jsx`

### Files to Delete:

No files deleted - only code sections removed within existing files.

---

## Story Execution Order

**Critical Path:**

```
Story 041 (Legacy Code)
    ↓
Story 043 (Consolidation) ← depends on 041 cleanup
    ↓
Story 042 (Prompts) ← can run parallel with 043
    ↓
Story 044 (Orchestrator) ← depends on 043 (copy_state)
    ↓
Story 045 (Frontend CSS) ← independent, can start anytime
    ↓
Story 046 (Canvas) ← depends on 045 (constants)
    ↓
Story 047 (Tests) ← runs last, validates everything
```

**Recommended Execution:**

1. **Session 1**: Story 041 (Remove legacy code) - 1.5 days
2. **Session 2**: Story 043 (Consolidate duplication) - 1.5 days
3. **Session 3**: Story 042 (Externalize prompts) - 1.5 days
4. **Session 4**: Story 044 (Orchestrator cleanup) - 0.5 days
5. **Session 5**: Story 045 (CSS modules) - 2 days
6. **Session 6**: Story 046 (Canvas refactor) - 1.5 days
7. **Session 7**: Story 047 (Unit tests) - 0.5 days

**Total:** 7 sessions, ~9 days

---

## Post-Epic 007 Benefits

### Developer Experience:

- ✅ Prompt iteration without code changes (markdown editing)
- ✅ Consistent styling system (CSS modules)
- ✅ No legacy code confusion
- ✅ Better unit test coverage
- ✅ Faster onboarding for new contributors

### Maintainability:

- ✅ Single source of truth for shared logic
- ✅ Clear separation of concerns
- ✅ Easier to extend for future features
- ✅ Reduced cognitive load when reading code

### Performance:

- ✅ Fewer inline style object recreations
- ✅ Simpler React re-render logic
- ✅ Cleaner useEffect dependencies

---

## Notes

**Why This Epic Matters:**

- Sets foundation for scalability (tournaments, analytics)
- Prevents debt from compounding
- Improves developer velocity
- Makes codebase more accessible to collaborators

**Post-Epic Roadmap:**

- Epic 008: Tournament & Match Infrastructure
- Epic 009: Advanced Analytics & Statistics
- Epic 010: Live Match Streaming (WebSocket)

**Design Philosophy:**

> "Refactoring is not rewriting. We're polishing the gem, not starting over. Every change must be independently verifiable and maintain backward compatibility."

---

**Epic 007 Ready for Implementation** 🧹✨
