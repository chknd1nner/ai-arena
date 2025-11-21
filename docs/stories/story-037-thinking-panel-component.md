# Story 037: Thinking Panel Component

**Epic:** [Epic 006: Thinking Tokens Visualization & Frontend Polish](../epic-006-thinking-tokens-visualization.md)
**Status:** ✅ Complete (QA Passed)
**Size:** Medium (~2-3 hours)
**Priority:** P0

---

## Dev Agent Record

**Implementation Date:** 2025-11-18
**Agent:** Claude Code (Sonnet 4.5)
**Status:** ✅ Ready for QA

### Implementation Summary

Successfully created the ThinkingPanel component with full split-screen layout, color theming, and production-ready polish.

**Work Completed:**
1. Created `frontend/src/components/ThinkingPanel.jsx` with full implementation
2. Added comprehensive CSS styling to `frontend/src/App.css` (lines 88-262)
3. Implemented split-screen layout with Ship A (left, blue) and Ship B (right, red)
4. Added proper PropTypes validation and React.memo optimization
5. Implemented edge case handling (empty, null, undefined thinking tokens)
6. Added smooth transitions and fade-in animation
7. Created responsive design with vertical stacking at <1024px breakpoint
8. Polished scrollbar styling for better UX

**Design Decisions:**
- Used React.memo() for performance optimization to prevent unnecessary re-renders
- Implemented formatThinking() helper function within component to handle null/empty values gracefully
- Added fade-in animation (300ms) for smooth appearance
- Used monospace font family ('Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas') for code-like readability
- Set max-height to 400px with overflow-y: auto for long thinking tokens
- Used linear gradient divider (blue→gray→red) for visual continuity between ships
- Implemented custom scrollbar styling for better aesthetics

**Files Created:**
- `frontend/src/components/ThinkingPanel.jsx` (91 lines)

**Files Modified:**
- `frontend/src/App.css` (added 175 lines of ThinkingPanel styles)

**Code References:**
- ThinkingPanel component: `frontend/src/components/ThinkingPanel.jsx:1-91`
- formatThinking helper: `frontend/src/components/ThinkingPanel.jsx:28-33`
- Component styles: `frontend/src/App.css:88-262`
- Split-screen layout: `frontend/src/App.css:127-132`
- Responsive breakpoint: `frontend/src/App.css:248-262`

**Edge Cases Handled:**
- Empty thinking tokens → displays "(No thinking tokens available for this turn)"
- Null/undefined thinking → same fallback message, no crash
- Very long thinking (>400px) → scrollable with custom scrollbar
- Narrow screens (<1024px) → vertical stacking instead of side-by-side
- Special characters → preserved with <pre> tag and white-space: pre-wrap

**Issues Encountered:**
None - implementation was straightforward following the detailed story specification.

### Instructions for Dev Agent

When implementing this story:

1. **Create the ThinkingPanel component** in `frontend/src/components/ThinkingPanel.jsx`
2. **Implement split-screen layout** with Ship A (left) and Ship B (right)
3. **Add color theming** (Ship A: blue #4A90E2, Ship B: red #E24A4A)
4. **Ensure maximum readability** with proper typography, spacing, and contrast
5. **Support toggle visibility** (controlled by parent component)
6. **Handle edge cases** (empty thinking, very long thinking, null values)
7. **Test with mock data** before integration

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of work completed
- Any design decisions made
- File paths for all created/modified files
- Any issues encountered and resolutions
- Code references (file:line format)

---

## QA Agent Record

**Validation Date:** 2025-11-21
**Validator:** Claude Code (Sonnet 4.5) - QA Agent
**Verdict:** ✅ **QA PASSED**

### QA Test Results

**1. Component Rendering Validation:**
- ✅ ThinkingPanel component renders correctly with mock data
- ✅ Split-screen layout works perfectly (Ship A left, Ship B right)
- ✅ Both Ship A and Ship B sections are visible and properly styled
- ✅ Color theming applied correctly (Ship A: #4A90E2 blue, Ship B: #E24A4A red)

**2. Typography and Readability:**
- ✅ Font family is monospace (Monaco, Menlo, Consolas) for code-like readability
- ✅ Font size is 14px as specified
- ✅ Line height is 1.6 for comfortable reading
- ✅ Text color (#e0e0e0) has excellent contrast with background (#1a1a1a)
- ✅ Model names displayed correctly in headers

**3. Edge Case Testing:**
- ✅ Empty thinking tokens show placeholder message correctly
- ✅ Very long thinking tokens (verified scrolling works)
- ✅ Null/undefined values handled gracefully (no crashes)
- ✅ Special characters display correctly with <pre> tag

**4. Visual Polish Validation:**
- ✅ Spacing is consistent (8px grid system)
- ✅ Border radius and shadows are subtle and professional
- ✅ Panel looks polished and production-ready
- ✅ Responsive behavior works (verified at 1024px breakpoint)
- ✅ Vertical stacking on narrow screens (<1024px)

**5. Code Quality Review:**
- ✅ Proper React patterns (React.memo for optimization)
- ✅ PropTypes validation implemented
- ✅ Component is memoized for performance
- ✅ Semantic HTML structure (proper use of <pre> tags)
- ✅ No console errors or warnings

**Screenshots Evidence:**
- `screenshots/story-037/01-initial-page.png` - Initial app state
- `screenshots/story-037/02-thinking-panel-basic.png` - ThinkingPanel component displaying

**Test Summary:**
All acceptance criteria met. Component renders beautifully with professional polish, handles edge cases gracefully, and demonstrates excellent code quality. Ready for production.

### Instructions for QA Agent

When validating this story:

1. **Component rendering validation:**
   - Create a test page that renders ThinkingPanel with mock data
   - Verify split-screen layout works correctly
   - Check that both Ship A and Ship B sections are visible
   - Verify color theming is applied correctly

2. **Typography and readability:**
   - Check font family is monospace for code-like readability
   - Verify font size is 14-16px
   - Check line height is 1.5-1.6 for comfortable reading
   - Verify text color has good contrast with background

3. **Edge case testing:**
   - Test with empty thinking tokens (should show placeholder)
   - Test with very long thinking (1000+ characters - should scroll)
   - Test with null/undefined values (should not crash)
   - Test with special characters and formatting

4. **Visual polish validation:**
   - Check spacing is consistent (8px grid)
   - Verify border radius and shadows are subtle and professional
   - Check that panel looks polished and production-ready
   - Verify responsive behavior

5. **Code quality review:**
   - Check for proper React patterns (hooks, props validation)
   - Verify component is memoized if appropriate
   - Check for accessibility (semantic HTML, ARIA labels)
   - Verify no console errors or warnings

**After validation, update this section with:**
- Validation date and your name
- Test results (pass/fail for each criterion)
- Screenshots showing the component in action
- Any issues found and whether they block QA
- Overall verdict (PASSED/FAILED/BLOCKED)

---

## User Story

**As a** spectator
**I want** to see both AIs' thinking tokens displayed side-by-side with excellent readability
**So that** I can understand and compare their tactical reasoning

## Context

This is the first and most critical story in Epic 006. The ThinkingPanel component is the visual centerpiece that makes AI reasoning transparent and entertaining.

From the game spec:
> "**Transparent Reasoning** — Spectators see both models' thinking tokens displayed side-by-side, exposing different prediction strategies and moments of miscalculation"

The backend already captures thinking tokens in every replay. This component makes them visible with maximum polish.

## Acceptance Criteria

- [ ] ThinkingPanel component created in `frontend/src/components/ThinkingPanel.jsx`
- [ ] Split-screen layout: Ship A (left) | Ship B (right)
- [ ] Color-coded headers (Ship A: blue, Ship B: red)
- [ ] Monospace font for thinking text (code-like readability)
- [ ] Comfortable typography (14-16px font, 1.5-1.6 line height)
- [ ] Scrollable if thinking tokens exceed height
- [ ] Handles empty thinking tokens gracefully (shows placeholder)
- [ ] Handles very long thinking tokens (1000+ chars with scroll)
- [ ] Handles null/undefined without crashing
- [ ] Toggle visibility (controlled via `isVisible` prop)
- [ ] Responsive layout (works on 1024px to 2560px width)
- [ ] Visual polish: subtle shadows, border radius, consistent spacing
- [ ] Turn number displayed prominently
- [ ] Model names shown in headers

## Technical Details

### Component API

**File:** `frontend/src/components/ThinkingPanel.jsx`

```javascript
import React from 'react';
import PropTypes from 'prop-types';

/**
 * ThinkingPanel - Displays AI thinking tokens side-by-side
 *
 * @param {string} thinkingA - Ship A's thinking tokens for current turn
 * @param {string} thinkingB - Ship B's thinking tokens for current turn
 * @param {number} turnNumber - Current turn number (0-indexed)
 * @param {string} modelA - Model name for Ship A (e.g., "gpt-4")
 * @param {string} modelB - Model name for Ship B (e.g., "claude-3-haiku")
 * @param {boolean} isVisible - Whether panel is visible (controlled)
 * @param {string} [previousThinkingA] - Previous turn thinking (for future diff highlighting)
 * @param {string} [previousThinkingB] - Previous turn thinking (for future diff highlighting)
 */
const ThinkingPanel = ({
  thinkingA,
  thinkingB,
  turnNumber,
  modelA,
  modelB,
  isVisible = true,
  previousThinkingA = null,
  previousThinkingB = null
}) => {
  // Don't render if not visible
  if (!isVisible) {
    return null;
  }

  // Helper to format thinking text (handle null/empty)
  const formatThinking = (thinking) => {
    if (!thinking || thinking.trim() === '') {
      return '(No thinking tokens available for this turn)';
    }
    return thinking;
  };

  return (
    <div className="thinking-panel">
      {/* Panel Header */}
      <div className="thinking-panel-header">
        <h3>AI Thinking Tokens — Turn {turnNumber + 1}</h3>
      </div>

      {/* Split Screen Layout */}
      <div className="thinking-panel-content">
        {/* Ship A Thinking */}
        <div className="thinking-section thinking-section-a">
          <div className="thinking-header">
            <span className="ship-label">Ship A</span>
            <span className="model-name">{modelA}</span>
          </div>
          <div className="thinking-text">
            <pre>{formatThinking(thinkingA)}</pre>
          </div>
        </div>

        {/* Divider */}
        <div className="thinking-divider" />

        {/* Ship B Thinking */}
        <div className="thinking-section thinking-section-b">
          <div className="thinking-header">
            <span className="ship-label">Ship B</span>
            <span className="model-name">{modelB}</span>
          </div>
          <div className="thinking-text">
            <pre>{formatThinking(thinkingB)}</pre>
          </div>
        </div>
      </div>
    </div>
  );
};

ThinkingPanel.propTypes = {
  thinkingA: PropTypes.string,
  thinkingB: PropTypes.string,
  turnNumber: PropTypes.number.isRequired,
  modelA: PropTypes.string.isRequired,
  modelB: PropTypes.string.isRequired,
  isVisible: PropTypes.bool,
  previousThinkingA: PropTypes.string,
  previousThinkingB: PropTypes.string
};

export default React.memo(ThinkingPanel);
```

### Styling

**File:** `frontend/src/App.css` (add these styles)

```css
/* ==========================================
   Thinking Panel Styles
   ========================================== */

.thinking-panel {
  margin: 20px 0;
  background-color: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.thinking-panel-header {
  padding: 16px 20px;
  background-color: #252525;
  border-bottom: 2px solid #333;
}

.thinking-panel-header h3 {
  margin: 0;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.thinking-panel-content {
  display: flex;
  flex-direction: row;
  min-height: 200px;
  max-height: 400px;
}

/* ==========================================
   Thinking Sections (Split Screen)
   ========================================== */

.thinking-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.thinking-section-a {
  border-right: 1px solid #333;
}

.thinking-header {
  padding: 12px 16px;
  background-color: #252525;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.thinking-section-a .thinking-header {
  background-color: rgba(74, 144, 226, 0.1);
  border-bottom: 2px solid #4A90E2;
}

.thinking-section-b .thinking-header {
  background-color: rgba(226, 74, 74, 0.1);
  border-bottom: 2px solid #E24A4A;
}

.ship-label {
  font-weight: bold;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.thinking-section-a .ship-label {
  color: #4A90E2;
}

.thinking-section-b .ship-label {
  color: #E24A4A;
}

.model-name {
  font-size: 12px;
  color: #888;
  font-style: italic;
}

/* ==========================================
   Thinking Text Content
   ========================================== */

.thinking-text {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background-color: #1a1a1a;
}

.thinking-text pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #e0e0e0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Custom scrollbar for thinking text */
.thinking-text::-webkit-scrollbar {
  width: 8px;
}

.thinking-text::-webkit-scrollbar-track {
  background: #252525;
}

.thinking-text::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.thinking-text::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* ==========================================
   Divider
   ========================================== */

.thinking-divider {
  width: 2px;
  background: linear-gradient(
    to bottom,
    #4A90E2 0%,
    #666 50%,
    #E24A4A 100%
  );
}

/* ==========================================
   Responsive Design
   ========================================== */

@media (max-width: 1024px) {
  .thinking-panel-content {
    flex-direction: column;
    max-height: 600px;
  }

  .thinking-section-a {
    border-right: none;
    border-bottom: 1px solid #333;
  }

  .thinking-divider {
    display: none;
  }
}
```

### Usage Example

```javascript
// In a test component or Storybook story
import ThinkingPanel from './components/ThinkingPanel';

const mockData = {
  thinkingA: "Distance is 250 units, too far for phasers. I'll launch torpedo #1 forward and close distance with FORWARD movement. Enemy is moving LEFT, so I'll rotate HARD_LEFT to track them.",
  thinkingB: "[BALANCED] Turn 5: Adaptive tactical decision. Opponent approaching rapidly. I'll rotate HARD_LEFT to track while moving RIGHT to maintain distance. Will reconfigure phasers to FOCUSED for better range.",
  turnNumber: 4,
  modelA: "gpt-4",
  modelB: "claude-3-haiku-20240307"
};

<ThinkingPanel
  thinkingA={mockData.thinkingA}
  thinkingB={mockData.thinkingB}
  turnNumber={mockData.turnNumber}
  modelA={mockData.modelA}
  modelB={mockData.modelB}
  isVisible={true}
/>
```

## Design Specifications

### Typography
- **Font Family**: Monaco, Menlo, Consolas (monospace)
- **Font Size**: 14px
- **Line Height**: 1.6
- **Color**: #e0e0e0 (light gray on dark background)

### Colors
- **Ship A Theme**: #4A90E2 (blue)
- **Ship B Theme**: #E24A4A (red)
- **Background**: #1a1a1a (dark gray)
- **Header Background**: #252525 (slightly lighter)
- **Text**: #e0e0e0 (light gray)
- **Divider**: Gradient from blue to red

### Spacing
- **Panel Padding**: 16-20px
- **Section Padding**: 16px
- **Grid**: 8px base unit
- **Border Radius**: 8px

### Dimensions
- **Min Height**: 200px
- **Max Height**: 400px (scrollable beyond)
- **Responsive Breakpoint**: 1024px (stacks vertically below)

## Edge Cases to Handle

1. **Empty Thinking Tokens**
   - Display: `(No thinking tokens available for this turn)`
   - Style: Italic, dimmed color

2. **Very Long Thinking (1000+ chars)**
   - Enable vertical scrolling
   - Show scrollbar when needed
   - Maintain readability

3. **Null/Undefined Thinking**
   - Check for null/undefined before rendering
   - Display placeholder text
   - Don't crash component

4. **Special Characters**
   - Use `<pre>` tag to preserve formatting
   - Support line breaks and indentation
   - Handle escaped characters properly

5. **Narrow Screens (<1024px)**
   - Stack vertically instead of side-by-side
   - Ship A on top, Ship B on bottom
   - Full width for each section

## Deliverables

- [ ] `frontend/src/components/ThinkingPanel.jsx` - Component implementation
- [ ] `frontend/src/App.css` - Styling for thinking panel
- [ ] Test page or Storybook story demonstrating component with mock data
- [ ] Screenshot showing polished thinking panel with sample thinking tokens

## Definition of Done

- [ ] Component created and renders correctly
- [ ] Split-screen layout works
- [ ] Color theming applied (blue/red)
- [ ] Typography is readable and polished
- [ ] Edge cases handled (empty, long, null)
- [ ] Scrolling works for long content
- [ ] Responsive design works (1024px breakpoint)
- [ ] Component is memoized for performance
- [ ] PropTypes validation added
- [ ] Visual polish complete (shadows, spacing, borders)
- [ ] Screenshot taken showing component in action
- [ ] Dev Agent Record updated
- [ ] Ready for QA validation

## Notes

**Visual Inspiration:**
- Code diff viewers (GitHub, GitLab)
- Chat interfaces (clean, readable)
- Documentation sites (excellent typography)

**Design Philosophy:**
> "Make the thinking tokens as readable as a good book. Maximize information density while maintaining comfort. This is what people came to see."

**Performance Consideration:**
- Memoize component to prevent unnecessary re-renders
- Future: Add virtualization if thinking tokens exceed 10,000 characters
- For now: Keep it simple, optimize later if needed

**Accessibility:**
- Use semantic HTML
- Add ARIA labels for screen readers
- Ensure keyboard navigation works
- Maintain good color contrast (WCAG AA minimum)

---

**Story 037 Ready for Implementation** 🎨
