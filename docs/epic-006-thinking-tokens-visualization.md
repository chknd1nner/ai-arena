# Epic 006: Thinking Tokens Visualization & Frontend Polish

**Status:** In Progress
**Priority:** P0 (Core Entertainment Value)
**Estimated Size:** Medium (4 stories, 8-10 hours)
**Target for:** Claude Code Web

---

## Overview

Implement polished thinking token visualization in the replay viewer, fulfilling the game spec's core promise: "Spectators watch... both models' thinking tokens displayed side-by-side, exposing different prediction strategies and moments of miscalculation." This epic transforms AI Arena from a functional tactical simulator into compelling AI theater by making AI reasoning transparent and entertaining.

## Problem Statement

The backend captures thinking tokens for both AIs on every turn, but the frontend ignores them completely:
- ✅ Backend captures `thinking_a` and `thinking_b` in replays (verified in replay JSON)
- ✅ Replay system includes thinking tokens in turn data
- ❌ Frontend has ZERO components for displaying thinking tokens
- ❌ Users cannot see AI reasoning or decision-making process
- ❌ Missing the #1 entertainment value proposition from game spec

**Current state:**
```javascript
// ReplayViewer.jsx shows canvas + controls + stats
// Thinking tokens are in the data but never displayed:
const currentTurn = replay.turns[currentTurnIndex];
// currentTurn.thinking_a exists but is unused
// currentTurn.thinking_b exists but is unused
```

**Desired state:**
```
┌─────────────────────────────────────────────────────────┐
│  Ship A Thinking          |  Ship B Thinking            │
│  ──────────────────────   |  ──────────────────────    │
│  "Distance 250 units,     |  "Opponent moving forward, │
│   too far for phasers.    |   I'll rotate to track     │
│   Will launch torpedo     |   with FOCUSED phasers...  │
│   and close distance..."  |   Detonating torpedo at    │
│                           |   8s to deny approach..."   │
└─────────────────────────────────────────────────────────┘
```

## Goals

1. **Transparent Reasoning**: Display both AIs' thinking tokens side-by-side every turn
2. **Maximum Polish**: Production-ready UI with excellent readability and visual hierarchy
3. **Tactical Insight**: Make AI decision-making clear and entertaining to watch
4. **Toggle-able**: Allow users to focus on action or reasoning as desired
5. **Responsive Layout**: Work well on different screen sizes
6. **Match Summary**: Create compelling end-of-match summary with key moments

## Success Criteria

- [ ] Thinking tokens visible for both ships on every turn
- [ ] Side-by-side layout clearly shows competing strategies
- [ ] Syntax highlighting or formatting for structured reasoning
- [ ] Toggle to show/hide thinking panel
- [ ] Turn-by-turn thinking token history accessible
- [ ] Responsive layout (thinking panel + canvas + controls)
- [ ] Visual polish: colors, spacing, typography all production-ready
- [ ] Match summary screen showing winner + key tactical moments
- [ ] Works seamlessly with existing replay viewer
- [ ] No performance degradation from rendering thinking tokens
- [ ] Thinking tokens are the visual centerpiece of the viewer

## User Stories

1. [Story 037: Thinking Panel Component](stories/story-037-thinking-panel-component.md)
2. [Story 038: Thinking Token Display Integration](stories/story-038-thinking-token-integration.md)
3. [Story 039: UI/UX Polish & Layout](stories/story-039-ui-polish-layout.md)
4. [Story 040: Testing & Documentation](stories/story-040-testing-documentation.md)

## Technical Approach

### Game Specification Reference

From `docs/game_spec_revised.md` (lines 5, 15, 641-642, 1059, 1136, 1275):

**Vision Statement (line 5):**
> "Spectators watch the full battlefield, both models' thinking tokens, and the consequences of tactical predictions that succeed or fail."

**Compelling Feature #1 (line 15):**
> "**Transparent Reasoning** — Spectators see both models' thinking tokens displayed side-by-side, exposing different prediction strategies and moments of miscalculation"

**UI Specification (lines 641-642):**
> **Thinking Tokens Panel:**
> Split-screen showing each model's reasoning in real-time during decision phase

**Key Value (line 1059):**
> "Thinking tokens reveal model reasoning, enhancing drama"

### Current Data Structure

Thinking tokens are already captured in replay JSON:

```json
{
  "turn": 5,
  "state": { /* game state */ },
  "orders_a": { /* orders */ },
  "orders_b": { /* orders */ },
  "thinking_a": "Distance is 250 units, far too long for phasers. I'll launch torpedo #1 forward and close distance with FORWARD movement...",
  "thinking_b": "[BALANCED] Turn 5: Adaptive tactical decision. Opponent approaching, I'll rotate HARD_LEFT to track while moving RIGHT to maintain distance...",
  "events": [ /* events */ ]
}
```

### Architecture Changes

#### New Component: ThinkingPanel.jsx

**Purpose:** Display thinking tokens for both ships with maximum polish

**Features:**
- Split-screen layout (Ship A | Ship B)
- Color-coded by ship (blue for A, red for B)
- Auto-expanding text areas with scroll
- Syntax highlighting for structured text
- Turn number indicator
- Visual separators and excellent typography
- Diff highlighting (show what changed from previous turn)
- Collapsible sections for long reasoning

**Props:**
```javascript
<ThinkingPanel
  thinkingA={string}           // Ship A's thinking tokens
  thinkingB={string}           // Ship B's thinking tokens
  turnNumber={number}          // Current turn
  modelA={string}              // Model name for Ship A
  modelB={string}              // Model name for Ship B
  isVisible={boolean}          // Toggle visibility
  previousThinkingA={string}   // Previous turn (for diff highlighting)
  previousThinkingB={string}   // Previous turn (for diff highlighting)
/>
```

#### Updated Component: ReplayViewer.jsx

**Changes:**
- Add `ThinkingPanel` import and usage
- Create state for thinking panel visibility toggle
- Pass thinking tokens from current turn
- Add keyboard shortcut (T key) to toggle thinking panel
- Reorganize layout to accommodate thinking panel

**New Layout:**
```
┌─────────────────────────────────────────────────────┐
│  Match Info (Ship A vs Ship B)                      │
├─────────────────────────────────────────────────────┤
│  Thinking Tokens Panel (split-screen)               │
│  ┌────────────────────┬────────────────────┐        │
│  │ Ship A Thinking    │ Ship B Thinking    │        │
│  │ (Blue theme)       │ (Red theme)        │        │
│  └────────────────────┴────────────────────┘        │
├─────────────────────────────────────────────────────┤
│  Canvas Renderer (tactical view)                    │
├─────────────────────────────────────────────────────┤
│  Playback Controls                                  │
├─────────────────────────────────────────────────────┤
│  State Overlay (shields, AE, events)                │
└─────────────────────────────────────────────────────┘
```

#### New Component: MatchSummary.jsx

**Purpose:** Show compelling end-of-match summary

**Features:**
- Winner announcement with dramatic styling
- Match statistics (total turns, damage dealt, torpedoes launched)
- Key moments timeline (first blood, big damage events, critical decisions)
- Thinking tokens from decisive turns
- Replay button to watch again

### Visual Design Principles

1. **Thinking Tokens are the Star:**
   - Largest section of screen real estate
   - Excellent readability: good font, line height, contrast
   - Visual hierarchy: important info stands out

2. **Color Coding:**
   - Ship A: Blue theme (#4A90E2)
   - Ship B: Red theme (#E24A4A)
   - Consistent throughout UI

3. **Typography:**
   - Monospace font for thinking tokens (code-like readability)
   - Comfortable font size (14-16px)
   - Line height 1.5-1.6 for readability
   - White text on dark background (low eye strain)

4. **Visual Polish:**
   - Smooth transitions (fade in/out)
   - Subtle shadows for depth
   - Border radius for modern feel
   - Consistent spacing (8px grid system)
   - Loading states and skeleton screens

5. **Information Density:**
   - Balance between information and whitespace
   - Collapsible sections for long text
   - Progressive disclosure (show summary, expand for details)

### Interaction Design

**Keyboard Shortcuts:**
- `T` - Toggle thinking panel visibility
- `Space` - Play/Pause (existing)
- `← →` - Previous/Next turn (existing)
- `Home/End` - First/Last turn (existing)

**Mouse Interactions:**
- Click ship in canvas → highlight that ship's thinking
- Click thinking panel → expand to full screen view
- Scroll within thinking panel (independent scrolling)

**Toggle Button:**
- Prominent "Show/Hide Thinking" button
- Keyboard hint displayed (press T)
- Remembers user preference (localStorage)

### Performance Considerations

**Potential Issues:**
- Long thinking tokens (1000+ characters) could slow rendering
- Re-rendering thinking panel on every frame

**Optimizations:**
- Memoize ThinkingPanel component (React.memo)
- Virtualize long text if needed (react-window)
- Only update thinking panel when turn changes
- Lazy load match history (don't render all turns at once)

## Implementation Phases

### Phase 1: Core Component (Story 037)
- Create `ThinkingPanel.jsx` component
- Implement split-screen layout
- Add basic styling and typography
- Support toggle visibility
- **Deliverable:** Standalone thinking panel component

### Phase 2: Integration (Story 038)
- Integrate ThinkingPanel into ReplayViewer
- Wire up thinking token data from replay
- Add toggle button and keyboard shortcut
- Update layout to accommodate panel
- **Deliverable:** Thinking tokens visible in replay viewer

### Phase 3: Polish (Story 039)
- Visual polish (colors, spacing, shadows)
- Responsive layout for different screen sizes
- Syntax highlighting for structured text
- Diff highlighting (changes from previous turn)
- Match summary component
- **Deliverable:** Production-ready polished UI

### Phase 4: Testing & Docs (Story 040)
- E2E testing with real replays
- Documentation updates
- Screenshots for evidence
- Performance validation
- **Deliverable:** Epic 006 complete and production-ready

## Testing Strategy

### Component Testing
- ThinkingPanel renders correctly with mock data
- Toggle visibility works
- Handles empty thinking tokens gracefully
- Handles very long thinking tokens (1000+ chars)
- Responsive layout works on different screen sizes

### Integration Testing
- Thinking tokens display for all turns in replay
- Turn navigation updates thinking tokens correctly
- Keyboard shortcuts work
- Layout doesn't break with thinking panel visible
- Performance acceptable (no lag when rendering)

### E2E Testing
1. Load a real replay with LLM thinking tokens
2. Verify both ships' thinking visible
3. Navigate through turns, verify thinking updates
4. Toggle thinking panel on/off
5. Take screenshots showing polished UI
6. Verify match summary displays at end

### Visual Regression Testing
- Screenshot key screens (thinking panel visible/hidden)
- Verify layout consistency
- Check color theming
- Validate typography and spacing

## Impact on User Experience

### Before Epic 006:
```
User watches replay:
- Sees ships moving and shooting
- Reads events log ("Ship A fired phaser")
- Guesses at AI strategy from actions
- Entertainment: Moderate (tactical simulation)
```

### After Epic 006:
```
User watches replay:
- Sees ships moving and shooting
- READS AI REASONING side-by-side
- Understands why AI made each decision
- Sees competing strategies clash
- Notices AI mistakes or brilliant predictions
- Entertainment: HIGH (AI theater + tactical simulation)
```

### Key Improvements:
1. **Transparency**: Users see AI thought process, not just actions
2. **Drama**: Moments of AI miscalculation become visible and entertaining
3. **Education**: Users learn tactical thinking by reading AI reasoning
4. **Comparison**: Side-by-side view highlights different AI personalities/strategies
5. **Engagement**: Reading thinking tokens adds new layer of interest

## Risks & Mitigations

### Risk 1: Thinking Tokens Too Long
**Impact:** UI becomes cluttered, hard to read
**Mitigation:**
- Collapsible sections for long text
- "Show more" button for truncated text
- Scrollable containers with max height

### Risk 2: Thinking Tokens Unreadable
**Impact:** Generic text like "[BALANCED] Turn 5: Decision" lacks interest
**Mitigation:**
- Document in Epic what good thinking tokens look like
- Future: Improve LLM prompts to encourage detailed reasoning
- For now: Display whatever we have, polish the presentation

### Risk 3: Layout Complexity
**Impact:** Adding thinking panel breaks existing layout
**Mitigation:**
- Careful CSS layout (flexbox/grid)
- Responsive design testing
- Progressive enhancement (works with/without thinking panel)

### Risk 4: Performance Degradation
**Impact:** Large thinking tokens slow down rendering
**Mitigation:**
- React.memo for memoization
- Virtualization if needed
- Profile before/after to measure impact

## Dependencies

### Required
- Epic 003: Canvas Replay Viewer (completed)
- Replay system captures thinking tokens (completed)
- React frontend infrastructure (exists)

### Enables
- Enhanced spectator experience (primary goal)
- Content creation (streamers can showcase AI reasoning)
- Debugging AI behavior (developers can see AI thought process)
- Future: Live match streaming with real-time thinking tokens

## Definition of Done

- [ ] All 4 stories completed (037-040)
- [ ] ThinkingPanel component created and tested
- [ ] Thinking tokens visible in replay viewer
- [ ] Side-by-side layout works perfectly
- [ ] Toggle visibility working (button + keyboard shortcut)
- [ ] Visual polish complete (colors, spacing, typography)
- [ ] Responsive layout tested on multiple screen sizes
- [ ] Match summary component created
- [ ] E2E testing passed with real replays
- [ ] Screenshots showing polished UI
- [ ] Documentation updated (README, CLAUDE.md)
- [ ] No performance regressions
- [ ] Epic 006 ready for production

## Files to Create/Modify

### Create
- `frontend/src/components/ThinkingPanel.jsx` - Core thinking display component
- `frontend/src/components/MatchSummary.jsx` - End-of-match summary
- `frontend/src/utils/thinkingFormatter.js` - Utility for formatting/highlighting thinking tokens
- `screenshots/epic-006-thinking-tokens-*.png` - Screenshots for documentation

### Modify
- `frontend/src/components/ReplayViewer.jsx` - Integrate thinking panel
- `frontend/src/App.css` - Add styling for thinking panel
- `frontend/src/components/StateOverlay.jsx` - Update layout if needed
- `README.md` - Update with thinking token screenshots
- `CLAUDE.md` - Document thinking token display

## Success Metrics

**Technical:**
- Component renders in <50ms
- No layout shifts when toggling thinking panel
- Works on screen widths 1024px to 2560px
- All React tests passing

**User Experience:**
- Thinking tokens are readable and well-formatted
- Side-by-side comparison is intuitive
- Visual hierarchy is clear (important info stands out)
- Toggle interaction is smooth and responsive

**Entertainment Value:**
- Thinking tokens add clear value to spectating
- AI reasoning is transparent and interesting
- Differences in AI strategies are visible
- Matches become more engaging with thinking visible

## Notes

**Why This Epic Matters:**
- Fulfills the core vision statement from game spec
- Unlocks the primary entertainment value proposition
- Transforms AI Arena from "functional" to "compelling"
- Enables content creation and streaming
- Quick win (backend already done, just frontend work)

**Post-Epic 006 Roadmap:**
- Epic 007: Tournament & Match Infrastructure (scaling)
- Epic 008: Live Match Streaming (WebSocket, real-time)
- Epic 009: Advanced Analytics (damage charts, tactical heatmaps)

**Design Philosophy:**
> "Thinking tokens are not a side feature — they ARE the feature. The tactical simulation is just the stage. The AI reasoning is the show."

---

**Epic 006 Ready for Implementation** 🚀
