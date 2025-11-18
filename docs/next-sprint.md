# Next Sprint: Epic 006 - Thinking Tokens Visualization & Frontend Polish

**Sprint ID:** epic-006-complete
**Date Planned:** 2025-11-18
**Planned By:** Scrum Master Agent
**Target Branch:** `claude/plan-sprint-epic-006-01MrUNNZisVjKCJCEau1DART`

---

## Sprint Goal

Complete Epic 006 by implementing a production-ready thinking tokens visualization system that makes AI reasoning transparent and entertaining - the core entertainment value proposition of AI Arena.

---

## Sprint Scope

This sprint includes **all 4 stories** from Epic 006:

1. ✅ **Story 037: Thinking Panel Component** (~2-3 hours)
   - Create standalone ThinkingPanel.jsx component
   - Implement split-screen layout with color theming
   - Ensure maximum readability with polished typography
   - Handle edge cases (empty, long, null thinking tokens)

2. ✅ **Story 038: Thinking Token Display Integration** (~2-3 hours)
   - Integrate ThinkingPanel into ReplayViewer
   - Wire up thinking token data from replay JSON
   - Add toggle button and keyboard shortcut (T key)
   - Update layout to accommodate thinking panel

3. ✅ **Story 039: UI/UX Polish & Layout** (~3-4 hours)
   - Apply visual polish to all thinking token elements
   - Create MatchSummary component for end-of-match display
   - Add smooth transitions and animations
   - Optimize responsive layout for different screen sizes
   - Create utility functions for thinking token formatting

4. ✅ **Story 040: Testing & Documentation** (~2-3 hours)
   - Run comprehensive E2E tests with real replay data
   - Take screenshots for evidence (multiple screen sizes)
   - Update README.md with thinking token feature
   - Update CLAUDE.md with implementation documentation
   - Performance validation and accessibility check

**Total Estimated Time:** 9-13 hours (medium epic scope)

---

## Why These Stories Together?

These 4 stories form a **natural development pipeline** that should be completed together:

1. **Story 037** builds the component foundation
2. **Story 038** integrates it into the app
3. **Story 039** polishes it to production quality
4. **Story 040** validates and documents it

**Dependencies:** Sequential but within same epic - designed to flow naturally in one development session.

**Deliverable:** Complete, polished, tested, and documented thinking token visualization system.

---

## Dev Agent Instructions

You are implementing **Epic 006: Thinking Tokens Visualization & Frontend Polish**.

### Context

From the game specification:
> "**Transparent Reasoning** — Spectators see both models' thinking tokens displayed side-by-side, exposing different prediction strategies and moments of miscalculation"

This is the **#1 entertainment value proposition** of AI Arena. The backend already captures thinking tokens in replay JSON - your job is to make them visible with maximum polish.

### Implementation Order

Complete the stories in this exact order:

#### 1. Story 037: Thinking Panel Component
**File:** `/home/user/ai-arena/docs/stories/story-037-thinking-panel-component.md`

**Tasks:**
- Create `frontend/src/components/ThinkingPanel.jsx`
- Implement split-screen layout (Ship A left, Ship B right)
- Add color theming (Ship A: #4A90E2 blue, Ship B: #E24A4A red)
- Use monospace font, 14px size, 1.6 line height for readability
- Handle edge cases: empty thinking, very long thinking (scrollable), null values
- Add PropTypes validation and memoization (React.memo)
- Add styles to `frontend/src/App.css`

**Acceptance:**
- Component renders correctly with mock data
- Split-screen layout works
- Edge cases handled gracefully
- Visual polish complete (shadows, spacing, typography)

**Dev Agent Record:**
After completing, update the "Dev Agent Record" section in story-037 with:
- Implementation date and your agent name
- Summary of work completed
- Design decisions made
- File paths created/modified
- Code references (file:line format)
- Any issues encountered
- Update YAML status to "Ready for QA"

---

#### 2. Story 038: Thinking Token Display Integration
**File:** `/home/user/ai-arena/docs/stories/story-038-thinking-token-integration.md`

**Tasks:**
- Import ThinkingPanel into `frontend/src/components/ReplayViewer.jsx`
- Extract thinking tokens from replay data: `currentTurn.thinking_a`, `currentTurn.thinking_b`
- Extract model names: `replay.model_a || replay.models?.ship_a` (handle both old/new format)
- Add state for visibility toggle: `const [showThinking, setShowThinking] = useState(true)`
- Add toggle button to UI with clear styling
- Add keyboard shortcut: T key toggles visibility
- Update keyboard shortcuts help text
- Wire up ThinkingPanel with correct props

**Acceptance:**
- Thinking tokens visible when loading replay
- Turn navigation updates thinking tokens correctly
- Toggle button and T key both work
- Layout accommodates panel without breaking existing UI
- Model names displayed correctly

**Dev Agent Record:**
After completing, update the "Dev Agent Record" section in story-038 with:
- Implementation summary
- Layout decisions
- File paths modified
- Integration challenges (if any)
- Screenshot showing integrated panel
- Update YAML status to "Ready for QA"

---

#### 3. Story 039: UI/UX Polish & Layout
**File:** `/home/user/ai-arena/docs/stories/story-039-ui-polish-layout.md`

**Tasks:**
- Create `frontend/src/utils/thinkingFormatter.js` with formatting utilities
- Create `frontend/src/components/MatchSummary.jsx` for end-of-match display
- Add smooth transitions to thinking panel (300ms fade animation)
- Add MatchSummary integration to ReplayViewer (show after final turn)
- Polish scrollbars with custom styling
- Add @keyframes fadeIn animation
- Implement responsive design (vertical stacking below 1024px)
- Add match summary styles with victory animation
- Test on multiple screen sizes

**Acceptance:**
- Visual polish applied to all elements
- MatchSummary displays at end of match with winner announcement
- Smooth transitions when toggling panel
- Responsive layout works on 1366x768, 1920x1080, 2560x1440
- Typography hierarchy clear (thinking tokens are centerpiece)
- Overall aesthetic is production-ready

**Dev Agent Record:**
After completing, update the "Dev Agent Record" section in story-039 with:
- Polish work completed
- Design decisions and rationale
- Before/after comparison notes
- File paths created/modified
- UX considerations
- Update YAML status to "Ready for QA"

---

#### 4. Story 040: Testing & Documentation
**File:** `/home/user/ai-arena/docs/stories/story-040-testing-documentation.md`

**Tasks:**
- Run all E2E test scenarios (7 scenarios defined in story)
- Take screenshots (14+ required - see checklist in story)
- Test responsive design on multiple screen sizes
- Verify performance (turn navigation <100ms)
- Check accessibility (keyboard navigation, color contrast)
- Test browser compatibility (Chrome, Firefox minimum)
- Update README.md with thinking token showcase section
- Update CLAUDE.md with implementation documentation
- Create `docs/epic-006-summary.md` (use template in story)

**Acceptance:**
- All E2E tests pass
- All required screenshots collected
- README.md and CLAUDE.md updated
- Performance validated (no lag)
- Epic 006 completion verified

**Dev Agent Record:**
After completing, update the "Dev Agent Record" section in story-040 with:
- Test results summary
- Screenshots collected (list file paths)
- Documentation updates made
- Performance metrics
- Epic 006 completion summary
- Update YAML status to "Completed"

---

## Key Implementation Guidelines

### Data Structure (From Replay JSON)

```json
{
  "turn": 5,
  "thinking_a": "Distance is 250 units, too far for phasers...",
  "thinking_b": "[BALANCED] Turn 5: Adaptive decision...",
  "state": { /* game state */ }
}
```

### Component Props Flow

```
Replay JSON → ReplayViewer → ThinkingPanel
  ├─ thinking_a
  ├─ thinking_b
  ├─ turnNumber
  ├─ modelA (from replay.model_a || replay.models.ship_a)
  ├─ modelB (from replay.model_b || replay.models.ship_b)
  └─ isVisible (from state)
```

### Color Scheme (Consistent Throughout)

- **Ship A**: #4A90E2 (blue)
- **Ship B**: #E24A4A (red)
- **Background**: #1a1a1a (dark gray)
- **Text**: #e0e0e0 (light gray)
- **Spacing**: 8px grid system

### Critical Design Principles

1. **Thinking tokens are the centerpiece** - largest screen real estate
2. **Maximum readability** - monospace font, good line height, high contrast
3. **Smooth interactions** - 300ms transitions, no jank
4. **Handle all edge cases** - empty, long, null thinking tokens
5. **Production-ready polish** - this is the flagship feature

---

## Definition of Done

Epic 006 is **COMPLETE** when:

- [ ] All 4 stories (037-040) completed
- [ ] ThinkingPanel component created and integrated
- [ ] Thinking tokens visible in replay viewer
- [ ] Toggle visibility working (button + T key)
- [ ] MatchSummary component displays at match end
- [ ] Visual polish production-ready
- [ ] Responsive layout tested (3+ screen sizes)
- [ ] All E2E tests passing
- [ ] Performance validated (<100ms turn updates)
- [ ] Screenshots collected (14+ screenshots)
- [ ] README.md updated with thinking token showcase
- [ ] CLAUDE.md updated with implementation docs
- [ ] Epic 006 summary document created
- [ ] All Dev Agent Records completed
- [ ] All stories marked "Ready for QA" or "Completed"
- [ ] No console errors or warnings
- [ ] No known bugs

---

## Testing Requirements

### Must Test With Real Replays

Use the test replay buttons in `App.js`:
- "Watch Tactical Showcase"
- "Watch Strafing Maneuver"
- "Watch Retreat Coverage"

### Screenshot Checklist (Minimum Required)

1. `epic-006-basic-display.png` - Basic thinking panel
2. `epic-006-turn-navigation.png` - Turn navigation working
3. `epic-006-panel-hidden.png` - Toggle hidden state
4. `epic-006-panel-visible.png` - Toggle visible state
5. `epic-006-match-summary.png` - End-of-match summary
6. `epic-006-responsive-1920.png` - 1920x1080 layout
7. `epic-006-responsive-narrow.png` - Narrow window stacking

Additional screenshots recommended - see Story 040 for full list.

---

## File Checklist

### Files to Create:
- [ ] `frontend/src/components/ThinkingPanel.jsx`
- [ ] `frontend/src/components/MatchSummary.jsx`
- [ ] `frontend/src/utils/thinkingFormatter.js`
- [ ] `docs/epic-006-summary.md`
- [ ] `screenshots/epic-006-*.png` (14+ screenshots)

### Files to Modify:
- [ ] `frontend/src/components/ReplayViewer.jsx`
- [ ] `frontend/src/App.css`
- [ ] `README.md`
- [ ] `CLAUDE.md`

### Files to Update (Dev Agent Records):
- [ ] `docs/stories/story-037-thinking-panel-component.md`
- [ ] `docs/stories/story-038-thinking-token-integration.md`
- [ ] `docs/stories/story-039-ui-polish-layout.md`
- [ ] `docs/stories/story-040-testing-documentation.md`

---

## Success Criteria

This sprint is successful when:

1. **Functional**: Thinking tokens visible and working perfectly
2. **Polished**: Production-ready visual quality
3. **Tested**: All scenarios pass, screenshots collected
4. **Documented**: README and CLAUDE.md updated
5. **Complete**: All 4 stories done, Epic 006 closed

---

## Final Checklist Before Completion

Before marking sprint complete:

- [ ] Start both servers (backend + frontend) and verify everything works
- [ ] Load at least 2 different replays and verify thinking tokens display correctly
- [ ] Test toggle button and T key
- [ ] Navigate through multiple turns and verify updates
- [ ] Check match summary appears at end
- [ ] Take all required screenshots
- [ ] Update all 4 Dev Agent Records with detailed notes
- [ ] Update README.md and CLAUDE.md
- [ ] Create epic-006-summary.md
- [ ] Review all acceptance criteria met
- [ ] Commit all changes with clear commit messages
- [ ] Push to branch `claude/plan-sprint-epic-006-01MrUNNZisVjKCJCEau1DART`

---

## Notes

**Why This Matters:**
This epic delivers the core entertainment value of AI Arena. Thinking tokens transform the experience from "watching ships fight" to "understanding how AIs think." This is what makes AI Arena compelling for spectators and content creators.

**Design Philosophy:**
> "Thinking tokens are not a side feature — they ARE the feature. The tactical simulation is just the stage. The AI reasoning is the show."

**Quality Bar:**
This is the flagship feature - it must be perfect. No rough edges, no "good enough for now." Production-ready means stream-worthy.

---

## Get Started

1. Read this entire document carefully
2. Read the 4 story files in order (037 → 038 → 039 → 040)
3. Start with Story 037 and work sequentially
4. Update Dev Agent Records as you complete each story
5. Test frequently with real replays
6. Take screenshots as you go
7. When all done, create the epic summary

**Good luck! This is the most important feature in AI Arena.** 🚀

---

**Sprint Planned:** 2025-11-18
**Ready for Dev Agent Implementation**
