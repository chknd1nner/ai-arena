# Story 045: Extract Frontend CSS to Modules

**Epic:** [Epic 007: Technical Debt Reduction & Code Quality](../epic-007-technical-debt-reduction.md)
**Status:** ⏸️ Not Started
**Size:** Medium (~2 days)
**Priority:** P1

---

## Dev Agent Record

**Implementation Date:** _Pending_
**Agent:** _TBD_
**Status:** ⏸️ Not Started

### Instructions for Dev Agent

When implementing this story:

1. **Take baseline screenshots** of all components (before changes)
2. **Create CSS module files** for each component
3. **Extract all inline styles** to CSS classes
4. **Create shared styles** (colors, animations) in separate CSS files
5. **Test responsive layout** at different screen sizes
6. **Compare screenshots** to ensure visual appearance unchanged

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of work completed
- CSS module structure created
- Visual regression test results
- File paths for all created/modified files
- Any layout issues encountered and resolutions

---

## QA Agent Record

**Validation Date:** _Pending_
**Validator:** _TBD_
**Verdict:** ⏸️ Awaiting Implementation

### QA Checklist

- [ ] No inline `style={{}}` objects in any component
- [ ] All components use CSS modules (`.module.css` files)
- [ ] Shared colors defined in CSS variables
- [ ] Animations in separate CSS file
- [ ] Visual appearance unchanged (pixel-perfect comparison)
- [ ] Responsive layout still works (1024px, 1440px, 1920px, 2560px)
- [ ] Hot reload works with CSS changes
- [ ] No console warnings or errors

**After validation, update this section with:**
- QA date and validator name
- Visual regression test results
- Screenshot comparisons
- Responsive layout verification
- Final verdict

---

## User Story

**As a** frontend developer working on AI-Arena
**I want** all component styles extracted to CSS modules
**So that** styling is maintainable, performant, and follows React best practices

### Context

Currently, AI-Arena frontend has **heavy inline styling**:

**Example: `ReplayViewer.jsx` (lines 176-309)**
```jsx
<div style={{ width: '100%', padding: '20px' }}>
  <div style={{
    marginBottom: '20px',
    padding: '15px',
    backgroundColor: '#1a1a1a',
    borderRadius: '8px',
    color: '#fff',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  }}>
    {/* 130+ more lines of inline styles */}
  </div>
</div>
```

**Problems:**
- 130+ lines of inline `style={{}}` objects
- Object creation on every render (performance overhead)
- Hard to maintain consistent styling
- Can't use CSS features (pseudo-classes, media queries, animations)
- Difficult to theme or style globally
- Hard to find and change styles (scattered across JSX)

### Goal

Move all inline styles to CSS modules, enabling:
- Better performance (no object recreation)
- Maintainable styling system
- Full CSS feature support
- Easy theming and global style changes

---

## Acceptance Criteria

### Must Have:

- [ ] No inline `style={{}}` in any component
- [ ] All components have corresponding `.module.css` files
- [ ] Shared colors in `styles/colors.css` as CSS custom properties
- [ ] Animations in `styles/animations.css` with keyframes
- [ ] Visual appearance unchanged (pixel-perfect)
- [ ] Responsive layout works at all breakpoints
- [ ] Hot reload works with CSS changes

### Should Have:

- [ ] Consistent naming convention (BEM or similar)
- [ ] CSS organized by component responsibility
- [ ] Shared utility classes for common patterns

### Nice to Have:

- [ ] Dark/light theme support (CSS variables)
- [ ] CSS documentation/comments

---

## Technical Specification

### Current State

**Inline Styles Problem:**
```jsx
// ReplayViewer.jsx - inline styles
<div style={{
  marginBottom: '20px',
  padding: '15px',
  backgroundColor: '#1a1a1a',
  borderRadius: '8px',
  color: '#fff',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center'
}}>
```

**After CSS Modules:**
```jsx
// ReplayViewer.jsx - CSS modules
import styles from './ReplayViewer.module.css';

<div className={styles.matchInfoHeader}>
```

```css
/* ReplayViewer.module.css */
.matchInfoHeader {
  margin-bottom: 20px;
  padding: 15px;
  background-color: var(--bg-dark);
  border-radius: 8px;
  color: var(--text-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

### Proposed Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ReplayViewer.jsx
│   │   ├── ReplayViewer.module.css       # NEW
│   │   ├── ThinkingPanel.jsx
│   │   ├── ThinkingPanel.module.css      # NEW (some styles exist in App.css)
│   │   ├── PlaybackControls.jsx
│   │   ├── PlaybackControls.module.css   # NEW
│   │   ├── StateOverlay.jsx
│   │   ├── StateOverlay.module.css       # NEW
│   │   ├── MatchSummary.jsx
│   │   ├── MatchSummary.module.css       # NEW
│   │   ├── MatchSelector.jsx
│   │   ├── MatchSelector.module.css      # NEW
│   │   └── CanvasRenderer.jsx            # No inline styles, leave as-is
│   ├── styles/
│   │   ├── colors.css                    # NEW - Color variables
│   │   └── animations.css                # NEW - Keyframe animations
│   └── App.css                            # Keep for global styles
```

### CSS Module Naming Convention

Use **BEM-like naming** for clarity:

```css
/* Component name as prefix */
.replayViewer { }

/* Element within component */
.replayViewer__header { }
.replayViewer__controls { }

/* Modifier */
.replayViewer__button--active { }
.replayViewer__button--disabled { }
```

Or simpler approach (nested selectors):

```css
.container { }
.header { }
.controls { }
.button { }
.buttonActive { }
```

**Recommendation:** Use simple camelCase names (CSS modules provide scoping automatically).

---

## Implementation Guidance

### Step 1: Create Baseline Screenshots (0.2 days)

```bash
cd frontend
npm start

# Take screenshots of:
# 1. Match selector page
# 2. Replay viewer - turn 1
# 3. Replay viewer - turn 10
# 4. Thinking panel visible
# 5. Thinking panel hidden
# 6. Match summary
# 7. Different screen sizes: 1024px, 1920px, 2560px

# Save to: docs/screenshots/baseline-epic-007/
```

### Step 2: Create Shared Styles (0.3 days)

**Create `frontend/src/styles/colors.css`:**
```css
:root {
  /* Primary colors */
  --ship-a-color: #4A90E2;    /* Blue */
  --ship-b-color: #E24A4A;    /* Red */

  /* Background colors */
  --bg-primary: #0a0a0a;
  --bg-secondary: #1a1a1a;
  --bg-tertiary: #2a2a2a;

  /* Text colors */
  --text-primary: #ffffff;
  --text-secondary: #aaaaaa;
  --text-tertiary: #888888;
  --text-disabled: #666666;

  /* Border colors */
  --border-primary: #333333;
  --border-secondary: #444444;

  /* Status colors */
  --color-success: #4CAF50;
  --color-warning: #FFA726;
  --color-error: #ff4444;
  --color-info: #29B6F6;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 20px;
  --spacing-xl: 30px;

  /* Border radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
}
```

**Create `frontend/src/styles/animations.css`:**
```css
/* Fade in animation */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Spin animation (for loading spinners) */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Slide in from top */
@keyframes slideInFromTop {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Pulse animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

Import shared styles in `App.css`:
```css
@import './styles/colors.css';
@import './styles/animations.css';
```

### Step 3: Extract ReplayViewer Styles (0.5 days)

**Create `frontend/src/components/ReplayViewer.module.css`:**
```css
.container {
  width: 100%;
  padding: var(--spacing-lg);
}

.matchInfoHeader {
  margin-bottom: var(--spacing-lg);
  padding: 15px;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-lg);
  color: var(--text-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.matchInfoHeader h3 {
  margin: 0 0 10px 0;
}

.matchInfoDetails {
  display: flex;
  gap: 30px;
  font-size: 14px;
  color: var(--text-secondary);
}

.shipLabel {
  font-weight: bold;
}

.shipLabelA {
  color: var(--ship-a-color);
}

.shipLabelB {
  color: var(--ship-b-color);
}

.toggleButton {
  background-color: var(--ship-a-color);
  color: var(--text-primary);
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.toggleButton:hover {
  background-color: #5FA0F2;
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.5);
}

.toggleButtonInactive {
  background-color: #555;
  box-shadow: none;
}

.toggleButtonInactive:hover {
  background-color: #666;
}

.keyboardShortcuts {
  margin-bottom: var(--spacing-lg);
  padding: 12px 15px;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-lg);
  font-size: 12px;
  color: var(--text-tertiary);
}

.keyboardShortcuts strong {
  color: var(--text-secondary);
}

.shortcutKey {
  color: var(--ship-a-color);
}

.loadingContainer {
  padding: 40px;
  text-align: center;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-lg);
  margin: 20px;
}

.loadingSpinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-primary);
  border-top: 4px solid var(--ship-a-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

.loadingText {
  color: var(--text-secondary);
  font-size: 16px;
}

/* ... rest of styles ... */
```

**Update `ReplayViewer.jsx`:**
```jsx
import React from 'react';
import styles from './ReplayViewer.module.css';
import { useReplayData } from '../hooks/useReplayData';
// ... other imports ...

const ReplayViewer = ({ matchId }) => {
  // ... hooks ...

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingSpinner} />
        <p className={styles.loadingText}>Loading replay...</p>
      </div>
    );
  }

  // ... rest of component ...

  return (
    <div className={styles.container}>
      {/* Match Summary */}
      {showSummary && (
        <MatchSummary
          matchInfo={{...}}
          totalTurns={totalTurns}
          finalTurn={currentTurn}
          onWatchAgain={() => {
            setShowSummary(false);
            jumpToTurn(0);
          }}
        />
      )}

      {/* Match Info Header */}
      <div className={styles.matchInfoHeader}>
        <div>
          <h3>Match: {replay.match_id}</h3>
          <div className={styles.matchInfoDetails}>
            <div>
              <span className={`${styles.shipLabel} ${styles.shipLabelA}`}>Ship A:</span> {modelA}
            </div>
            <div>
              <span className={`${styles.shipLabel} ${styles.shipLabelB}`}>Ship B:</span> {modelB}
            </div>
          </div>
        </div>

        {/* Toggle Thinking Button */}
        <button
          onClick={() => setShowThinking(!showThinking)}
          className={`${styles.toggleButton} ${!showThinking && styles.toggleButtonInactive}`}
          title="Toggle thinking tokens (T key)"
        >
          {showThinking ? '🧠 Hide Thinking' : '🧠 Show Thinking'}
        </button>
      </div>

      {/* ... rest of JSX with CSS classes ... */}
    </div>
  );
};
```

### Step 4: Extract Other Component Styles (0.5 days)

Repeat the same process for:
- `ThinkingPanel.jsx` / `ThinkingPanel.module.css`
- `PlaybackControls.jsx` / `PlaybackControls.module.css`
- `StateOverlay.jsx` / `StateOverlay.module.css`
- `MatchSummary.jsx` / `MatchSummary.module.css`
- `MatchSelector.jsx` / `MatchSelector.module.css`

**Note:** `ThinkingPanel` already has some styles in `App.css` (lines 88-262). These should be moved to `ThinkingPanel.module.css`.

### Step 5: Visual Regression Testing (0.2 days)

```bash
# After all CSS extraction complete
npm start

# Take same screenshots as baseline
# Save to: docs/screenshots/epic-007-after/

# Compare visually:
# - All components should look identical
# - No layout shifts or broken styles
# - Colors, spacing, borders all correct
# - Responsive layout still works
```

Use a screenshot diff tool or manual comparison.

---

## Testing Requirements

### Visual Regression Tests

**Manual testing checklist:**

1. **Match Selector**
   - [ ] Layout unchanged
   - [ ] Colors correct
   - [ ] Hover states work
   - [ ] Responsive (shrink window)

2. **Replay Viewer**
   - [ ] Match info header styled correctly
   - [ ] Toggle button works and has proper styles
   - [ ] Keyboard shortcuts panel styled
   - [ ] Loading state looks correct

3. **Thinking Panel**
   - [ ] Split-screen layout preserved
   - [ ] Ship A (blue) and Ship B (red) colors correct
   - [ ] Scrollable text areas work
   - [ ] Responsive (vertical stacking at <1024px)

4. **Playback Controls**
   - [ ] Button styles correct
   - [ ] Slider styled properly
   - [ ] Speed selector correct

5. **State Overlay**
   - [ ] Ship stats displayed correctly
   - [ ] Events log styled
   - [ ] Colors and spacing preserved

6. **Match Summary**
   - [ ] Winner announcement styled
   - [ ] Statistics table correct
   - [ ] Buttons styled properly

### Responsive Testing

Test at breakpoints:
- 1024px (minimum supported width)
- 1440px (common laptop)
- 1920px (Full HD)
- 2560px (2K/4K)

### Hot Reload Test

```bash
# Start dev server
npm start

# Edit a CSS module file
echo ".test { color: red; }" >> src/components/ReplayViewer.module.css

# Verify:
# - Changes appear immediately (no page refresh)
# - No console errors
```

---

## Files to Create

### CSS Module Files (6 files):
1. `frontend/src/components/ReplayViewer.module.css`
2. `frontend/src/components/ThinkingPanel.module.css`
3. `frontend/src/components/PlaybackControls.module.css`
4. `frontend/src/components/StateOverlay.module.css`
5. `frontend/src/components/MatchSummary.module.css`
6. `frontend/src/components/MatchSelector.module.css`

### Shared Style Files (2 files):
7. `frontend/src/styles/colors.css`
8. `frontend/src/styles/animations.css`

---

## Files to Modify

### Component Files (6 files):
1. `frontend/src/components/ReplayViewer.jsx` - Remove inline styles, use CSS modules
2. `frontend/src/components/ThinkingPanel.jsx` - Remove inline styles
3. `frontend/src/components/PlaybackControls.jsx` - Remove inline styles
4. `frontend/src/components/StateOverlay.jsx` - Remove inline styles
5. `frontend/src/components/MatchSummary.jsx` - Remove inline styles
6. `frontend/src/components/MatchSelector.jsx` - Remove inline styles

### Global Styles:
7. `frontend/src/App.css` - Import shared styles, remove component-specific styles

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] No inline `style={{}}` in any component
- [ ] All CSS module files created
- [ ] Shared styles (colors, animations) in separate files
- [ ] Visual regression tests pass (screenshots match)
- [ ] Responsive layout works at all breakpoints
- [ ] Hot reload works
- [ ] No console warnings/errors
- [ ] Code reviewed
- [ ] Documentation updated (if needed)

---

## Dependencies

**Blocks:**
- Story 046 (Canvas Refactor) - rendering constants will be extracted

**Blocked By:**
- None (independent work)

---

## Notes

### Design Decisions

- **CSS Modules over styled-components**: Simpler, no runtime overhead, native CSS
- **CSS custom properties**: Enable theming, easier color management
- **Shared styles directory**: Centralize colors and animations
- **BEM-like naming**: Clear, maintainable class names

### Benefits

After this story:
- ✅ Better performance (no inline object creation)
- ✅ Maintainable styling system
- ✅ Full CSS feature support (pseudo-classes, animations, media queries)
- ✅ Easy theming via CSS variables
- ✅ Separation of concerns (styles vs logic)
- ✅ Better developer experience (CSS syntax highlighting, autocomplete)

### Risks

**Risk:** Visual regression (layout breaks)
**Mitigation:** Screenshot comparison, manual testing at each step

**Risk:** CSS specificity issues
**Mitigation:** CSS modules provide automatic scoping, avoid global selectors
