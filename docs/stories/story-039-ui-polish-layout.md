# Story 039: UI/UX Polish & Layout

**Epic:** [Epic 006: Thinking Tokens Visualization & Frontend Polish](../epic-006-thinking-tokens-visualization.md)
**Status:** Not Started
**Size:** Medium-Large (~3-4 hours)
**Priority:** P0

---

## Dev Agent Record

**Implementation Date:** [To be filled by Dev Agent]
**Agent:** [To be filled by Dev Agent]
**Status:** [To be filled by Dev Agent]

### Instructions for Dev Agent

When implementing this story:

1. **Apply visual polish** to all thinking token UI elements
2. **Create MatchSummary component** for end-of-match display
3. **Add syntax highlighting** for structured thinking tokens (if applicable)
4. **Implement diff highlighting** (changes from previous turn - optional enhancement)
5. **Optimize responsive layout** for different screen sizes
6. **Add smooth transitions** and animations
7. **Create utility functions** for thinking token formatting
8. **Polish overall app layout** to make thinking tokens the centerpiece
9. **Test on multiple screen sizes** (1366x768, 1920x1080, 2560x1440)

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of polish work completed
- Design decisions and rationale
- File paths for all created/modified files
- Before/after screenshots showing polish improvements
- Any UX considerations or tradeoffs made
- Code references (file:line format)

---

## QA Agent Record

**Validation Date:** [To be filled by QA Agent]
**Validator:** [To be filled by QA Agent]
**Verdict:** [To be filled by QA Agent]

### Instructions for QA Agent

When validating this story:

1. **Visual polish validation:**
   - Check overall aesthetic quality (does it look professional?)
   - Verify color consistency across all elements
   - Check spacing is uniform (8px grid)
   - Verify shadows and borders are subtle and tasteful
   - Check typography hierarchy is clear

2. **Thinking token formatting:**
   - Verify long thinking tokens are readable
   - Check line wrapping works correctly
   - Verify special characters display properly
   - Check syntax highlighting (if implemented)
   - Verify diff highlighting works (if implemented)

3. **Match summary validation:**
   - Load a completed replay and navigate to end
   - Verify MatchSummary component displays
   - Check winner announcement is clear
   - Verify match statistics are accurate
   - Check "Watch Again" button works

4. **Responsive design validation:**
   - Test on 1366x768 screen - verify usable
   - Test on 1920x1080 screen - verify optimal layout
   - Test on 2560x1440 screen - verify doesn't waste space
   - Test at narrow widths (1024px) - verify stacking works

5. **Animation and transitions:**
   - Verify smooth fade in/out when toggling thinking panel
   - Check that transitions don't feel sluggish
   - Verify no janky animations or layout shifts

6. **Overall UX assessment:**
   - Does the UI feel polished and production-ready?
   - Is the thinking panel the clear visual centerpiece?
   - Are there any UX rough edges that need smoothing?
   - Would this be compelling for content creators/streamers?

**After validation, update this section with:**
- Validation date and your name
- Detailed UX assessment
- Screenshots from multiple screen sizes
- Any visual issues found
- Polish suggestions (if any)
- Overall verdict (PASSED/FAILED)

---

## User Story

**As a** spectator
**I want** a polished, professional UI that makes thinking tokens the centerpiece
**So that** I can enjoy watching AI matches and understanding AI reasoning

## Context

Stories 037-038 made thinking tokens visible. This story makes them *beautiful*.

From the Epic 006 design philosophy:
> "Thinking tokens are not a side feature — they ARE the feature. The tactical simulation is just the stage. The AI reasoning is the show."

This story applies maximum polish to create a production-ready experience worthy of content creation and streaming.

## Acceptance Criteria

- [ ] Visual polish applied to all thinking token elements
- [ ] MatchSummary component created for end-of-match display
- [ ] Thinking token formatting utility functions created
- [ ] Syntax highlighting implemented (if thinking tokens are structured)
- [ ] Diff highlighting shows changes from previous turn (optional)
- [ ] Smooth transitions when toggling thinking panel (300ms fade)
- [ ] Responsive layout tested on 1366x768, 1920x1080, 2560x1440
- [ ] Typography hierarchy clear (thinking tokens > canvas > stats)
- [ ] Color consistency across all UI elements
- [ ] Spacing follows 8px grid system
- [ ] Loading states polished (no flashing/jumping)
- [ ] Overall aesthetic is professional and production-ready
- [ ] Before/after screenshots demonstrate improvement

## Technical Details

### Thinking Token Formatting Utility

**File:** `frontend/src/utils/thinkingFormatter.js`

```javascript
/**
 * Thinking token formatting and highlighting utilities
 */

/**
 * Format thinking tokens for display
 * - Trim excess whitespace
 * - Preserve line breaks
 * - Handle empty/null gracefully
 */
export function formatThinking(thinking) {
  if (!thinking || thinking.trim() === '') {
    return '(No thinking tokens available for this turn)';
  }

  // Trim leading/trailing whitespace but preserve internal line breaks
  return thinking.trim();
}

/**
 * Detect if thinking token has structured format (e.g., JSON-like)
 */
export function hasStructuredFormat(thinking) {
  if (!thinking) return false;

  // Check for common structured patterns
  const jsonPattern = /^\s*\{.*\}\s*$/s;
  const listPattern = /^(\s*[-*•]\s+.+\n?)+$/m;
  const sectionPattern = /^.+:\n(\s+.+\n?)+$/m;

  return jsonPattern.test(thinking) ||
         listPattern.test(thinking) ||
         sectionPattern.test(thinking);
}

/**
 * Simple syntax highlighting for structured thinking
 * Returns array of {text, className} objects
 */
export function highlightSyntax(thinking) {
  if (!thinking) return [{ text: '', className: '' }];

  // For now, just highlight key phrases
  // Future: Full markdown/JSON syntax highlighting
  const keyPhrases = [
    { pattern: /\b(Distance|Range|Position|Heading|Velocity)\b/g, className: 'syntax-metric' },
    { pattern: /\b(FORWARD|BACKWARD|LEFT|RIGHT|STOP|HARD_LEFT|HARD_RIGHT|SOFT_LEFT|SOFT_RIGHT)\b/g, className: 'syntax-movement' },
    { pattern: /\b(WIDE|FOCUSED)\b/g, className: 'syntax-weapon' },
    { pattern: /\b(torpedo|phaser|blast zone)\b/gi, className: 'syntax-weapon-type' },
    { pattern: /\b(\d+\.?\d*)\s*(units?|seconds?|AE|damage)\b/g, className: 'syntax-number' }
  ];

  // Simple implementation: return original text
  // Future: Implement proper syntax highlighting
  return [{ text: thinking, className: 'thinking-text-content' }];
}

/**
 * Calculate diff between current and previous thinking
 * Returns array of {text, type: 'added'|'removed'|'unchanged'}
 */
export function calculateDiff(currentThinking, previousThinking) {
  if (!currentThinking && !previousThinking) {
    return [];
  }

  if (!previousThinking) {
    return [{ text: currentThinking, type: 'added' }];
  }

  if (!currentThinking) {
    return [{ text: previousThinking, type: 'removed' }];
  }

  // Simple implementation: check if identical
  if (currentThinking === previousThinking) {
    return [{ text: currentThinking, type: 'unchanged' }];
  }

  // For now, just show as changed
  // Future: Use proper diff algorithm (e.g., Myers diff)
  return [
    { text: previousThinking, type: 'removed' },
    { text: currentThinking, type: 'added' }
  ];
}

/**
 * Truncate thinking for preview (e.g., in match summary)
 */
export function truncateThinking(thinking, maxLength = 200) {
  if (!thinking || thinking.length <= maxLength) {
    return thinking;
  }

  return thinking.substring(0, maxLength) + '...';
}
```

### MatchSummary Component

**File:** `frontend/src/components/MatchSummary.jsx`

```javascript
import React from 'react';
import PropTypes from 'prop-types';
import { truncateThinking } from '../utils/thinkingFormatter';

/**
 * MatchSummary - Displays compelling end-of-match summary
 */
const MatchSummary = ({
  matchInfo,
  totalTurns,
  finalTurn,
  onWatchAgain
}) => {
  if (!matchInfo || !finalTurn) return null;

  const winner = matchInfo.winner;
  const winnerShip = winner === 'ship_a' ? 'Ship A' : 'Ship B';
  const winnerModel = winner === 'ship_a' ? matchInfo.model_a : matchInfo.model_b;
  const winnerColor = winner === 'ship_a' ? '#4A90E2' : '#E24A4A';

  // Extract final thinking tokens
  const finalThinkingA = truncateThinking(finalTurn.thinking_a, 300);
  const finalThinkingB = truncateThinking(finalTurn.thinking_b, 300);

  return (
    <div className="match-summary">
      {/* Winner Announcement */}
      <div className="match-summary-header">
        <div className="victory-icon">🏆</div>
        <h1 style={{ color: winnerColor }}>
          {winnerShip} Wins!
        </h1>
        <div className="winner-model">{winnerModel}</div>
      </div>

      {/* Match Statistics */}
      <div className="match-stats">
        <div className="stat">
          <span className="stat-label">Total Turns</span>
          <span className="stat-value">{totalTurns}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Match ID</span>
          <span className="stat-value">{matchInfo.match_id}</span>
        </div>
      </div>

      {/* Final Thinking Tokens */}
      <div className="final-thinking">
        <h3>Final Thoughts</h3>
        <div className="final-thinking-content">
          <div className="final-thinking-ship">
            <div className="final-thinking-header" style={{ borderColor: '#4A90E2' }}>
              Ship A's Final Turn
            </div>
            <div className="final-thinking-text">
              {finalThinkingA || '(No thinking available)'}
            </div>
          </div>
          <div className="final-thinking-ship">
            <div className="final-thinking-header" style={{ borderColor: '#E24A4A' }}>
              Ship B's Final Turn
            </div>
            <div className="final-thinking-text">
              {finalThinkingB || '(No thinking available)'}
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="match-summary-actions">
        <button onClick={onWatchAgain} className="btn-primary">
          ▶️ Watch Again
        </button>
        <button onClick={() => window.location.reload()} className="btn-secondary">
          🏠 Back to Matches
        </button>
      </div>
    </div>
  );
};

MatchSummary.propTypes = {
  matchInfo: PropTypes.shape({
    match_id: PropTypes.string.isRequired,
    model_a: PropTypes.string.isRequired,
    model_b: PropTypes.string.isRequired,
    winner: PropTypes.string.isRequired
  }).isRequired,
  totalTurns: PropTypes.number.isRequired,
  finalTurn: PropTypes.object,
  onWatchAgain: PropTypes.func.isRequired
};

export default MatchSummary;
```

### MatchSummary Styling

**File:** `frontend/src/App.css` (add these styles)

```css
/* ==========================================
   Match Summary Styles
   ========================================== */

.match-summary {
  margin: 40px auto;
  max-width: 900px;
  padding: 40px;
  background: linear-gradient(135deg, #1a1a1a 0%, #252525 100%);
  border-radius: 12px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
  text-align: center;
}

.match-summary-header {
  margin-bottom: 32px;
}

.victory-icon {
  font-size: 64px;
  margin-bottom: 16px;
  animation: bounce 1s ease-in-out;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.match-summary-header h1 {
  margin: 0;
  font-size: 48px;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.winner-model {
  margin-top: 8px;
  font-size: 18px;
  color: #aaa;
  font-style: italic;
}

.match-stats {
  display: flex;
  justify-content: center;
  gap: 48px;
  margin: 32px 0;
  padding: 24px;
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 12px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #fff;
}

.final-thinking {
  margin: 32px 0;
  text-align: left;
}

.final-thinking h3 {
  margin: 0 0 16px 0;
  color: #fff;
  font-size: 20px;
  text-align: center;
}

.final-thinking-content {
  display: flex;
  gap: 16px;
}

.final-thinking-ship {
  flex: 1;
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.final-thinking-header {
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.05);
  border-bottom: 2px solid;
  font-weight: bold;
  font-size: 14px;
  color: #fff;
}

.final-thinking-text {
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #e0e0e0;
  max-height: 200px;
  overflow-y: auto;
}

.match-summary-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.btn-primary,
.btn-secondary {
  padding: 14px 32px;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: #4A90E2;
  color: #fff;
}

.btn-primary:hover {
  background-color: #357ABD;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(74, 144, 226, 0.3);
}

.btn-secondary {
  background-color: #555;
  color: #fff;
}

.btn-secondary:hover {
  background-color: #666;
  transform: translateY(-2px);
}
```

### Enhanced ThinkingPanel Transitions

Update `frontend/src/App.css`:

```css
/* Add smooth transitions to thinking panel */
.thinking-panel {
  margin: 20px 0;
  background-color: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease; /* NEW: Smooth transitions */
  animation: fadeIn 0.3s ease; /* NEW: Fade in on mount */
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Improve scrollbar aesthetics */
.thinking-text::-webkit-scrollbar {
  width: 10px; /* Slightly wider for easier grabbing */
}

.thinking-text::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 4px;
}

.thinking-text::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #555 0%, #444 100%);
  border-radius: 4px;
  border: 2px solid #1a1a1a;
}

.thinking-text::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #666 0%, #555 100%);
}
```

### Syntax Highlighting Styles

**File:** `frontend/src/App.css` (add these styles)

```css
/* ==========================================
   Syntax Highlighting for Thinking Tokens
   ========================================== */

.syntax-metric {
  color: #4EC9B0; /* Teal for metrics */
  font-weight: 500;
}

.syntax-movement {
  color: #C586C0; /* Purple for movement commands */
  font-weight: 600;
}

.syntax-weapon {
  color: #DCDCAA; /* Yellow for weapon configs */
  font-weight: 600;
}

.syntax-weapon-type {
  color: #4FC1FF; /* Light blue for weapon types */
}

.syntax-number {
  color: #B5CEA8; /* Light green for numbers */
}

/* Diff highlighting */
.thinking-diff-added {
  background-color: rgba(76, 175, 80, 0.2);
  border-left: 3px solid #4CAF50;
}

.thinking-diff-removed {
  background-color: rgba(244, 67, 54, 0.2);
  border-left: 3px solid #F44336;
  text-decoration: line-through;
  opacity: 0.7;
}

.thinking-diff-unchanged {
  opacity: 0.6;
}
```

## Integration with ReplayViewer

Update `ReplayViewer.jsx` to show MatchSummary at end:

```javascript
import MatchSummary from './MatchSummary';

// In component body
const isMatchComplete = currentTurnIndex === totalTurns - 1;
const [showSummary, setShowSummary] = useState(false);

// Show summary when reaching final turn
useEffect(() => {
  if (isMatchComplete && !playing) {
    const timer = setTimeout(() => setShowSummary(true), 1000);
    return () => clearTimeout(timer);
  } else {
    setShowSummary(false);
  }
}, [isMatchComplete, playing]);

// In render, before main replay content
{showSummary && (
  <MatchSummary
    matchInfo={{
      match_id: replay.match_id,
      model_a: modelA,
      model_b: modelB,
      winner: replay.winner
    }}
    totalTurns={totalTurns}
    finalTurn={currentTurn}
    onWatchAgain={() => {
      setShowSummary(false);
      jumpToTurn(0);
    }}
  />
)}
```

## Deliverables

- [ ] `frontend/src/utils/thinkingFormatter.js` - Formatting utilities
- [ ] `frontend/src/components/MatchSummary.jsx` - End-of-match component
- [ ] `frontend/src/App.css` - Enhanced styling with polish
- [ ] Updated `ThinkingPanel.jsx` with smooth transitions
- [ ] Updated `ReplayViewer.jsx` with MatchSummary integration
- [ ] Before/after screenshots demonstrating polish
- [ ] Responsive design tested on 3+ screen sizes

## Definition of Done

- [ ] Visual polish applied to all thinking token elements
- [ ] MatchSummary component created and working
- [ ] Thinking token formatting utilities implemented
- [ ] Smooth transitions added (300ms fade)
- [ ] Syntax highlighting implemented (at least key phrases)
- [ ] Responsive layout validated on 1366x768, 1920x1080, 2560x1440
- [ ] Typography hierarchy clear
- [ ] Color consistency verified
- [ ] Spacing follows 8px grid
- [ ] Loading states polished
- [ ] Before/after screenshots taken
- [ ] Overall aesthetic is production-ready
- [ ] Dev Agent Record completed
- [ ] Ready for QA validation

## Notes

**Design Philosophy:**
- Maximize readability above all else
- Thinking tokens should be the visual centerpiece
- Polish should feel subtle, not flashy
- Every pixel counts - sweat the details

**Polish Priorities:**
1. Typography (most important for readability)
2. Color consistency (visual coherence)
3. Spacing (visual breathing room)
4. Transitions (smooth interactions)
5. Shadows and depth (subtle 3D feel)

**Optional Enhancements:**
- Diff highlighting (nice to have, not required)
- Full syntax highlighting (nice to have)
- Collapsible sections (future)
- Copy to clipboard button (future)

---

**Story 039 Ready for Implementation** ✨
