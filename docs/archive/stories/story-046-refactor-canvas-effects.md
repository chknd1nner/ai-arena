# Story 046: Refactor Canvas Rendering Effects

**Epic:** [Epic 007: Technical Debt Reduction & Code Quality](../epic-007-technical-debt-reduction.md)
**Status:** ⏸️ Not Started
**Size:** Medium (~1.5 days)
**Priority:** P1

---

## Dev Agent Record

**Implementation Date:** _Pending_
**Agent:** _TBD_
**Status:** ⏸️ Not Started

### Instructions for Dev Agent

When implementing this story:

1. **Create rendering constants file** to extract magic numbers
2. **Remove mock data** from production component
3. **Extract animation hook** (`useAnimationLoop`) for cleaner effects
4. **Consolidate useEffect logic** to prevent dependency issues
5. **Test canvas rendering** to ensure no visual glitches

**After implementation, update this section with:**
- Implementation date and your agent name
- Summary of work completed
- Constants extracted
- Animation hook implementation
- File paths for all created/modified files
- Any issues encountered and resolutions

---

## QA Agent Record

**Validation Date:** _Pending_
**Validator:** _TBD_
**Verdict:** ⏸️ Awaiting Implementation

### QA Checklist

- [ ] All magic numbers moved to `constants/rendering.js`
- [ ] No mock data in `CanvasRenderer.jsx`
- [ ] `useAnimationLoop` hook working correctly
- [ ] useEffect dependencies simplified
- [ ] Canvas rendering performance unchanged or improved
- [ ] No visual glitches (trails, interpolation, effects)
- [ ] Ship colors, sizes consistent
- [ ] Torpedo trails render correctly

**After validation, update this section with:**
- QA date and validator name
- Test results for each criterion
- Performance comparison (before/after)
- Visual verification results
- Final verdict

---

## User Story

**As a** frontend developer working on canvas rendering
**I want** rendering constants extracted and effects logic simplified
**So that** the code is maintainable, testable, and free of production test code

### Context

`CanvasRenderer.jsx` has several issues:

1. **Magic Numbers Everywhere:**
   - `TURN_TRANSITION_DURATION = 300` (line 39)
   - `FLASH_DURATION = 200` (line 43)
   - `TRAIL_LENGTH = 10` (line 24)
   - Ship colors, sizes, arc angles hardcoded throughout

2. **Mock Data in Production:**
   ```javascript
   const mockShipData = useMemo(() => ({
     ship_a: { position: { x: -200, y: 100 }, ... },
     ship_b: { position: { x: 200, y: -100 }, ... }
   }), []);
   ```
   Test data mixed with production code.

3. **Complex useEffect Chains:**
   - Two overlapping useEffects (lines 258-283)
   - Confusing dependency arrays
   - Risk of infinite re-render loops

### Goal

- Extract constants to dedicated file
- Remove mock data
- Simplify animation logic with custom hook
- Clean up useEffect dependencies

---

## Acceptance Criteria

### Must Have:

- [ ] All constants in `frontend/src/constants/rendering.js`
- [ ] No mock data in production components
- [ ] `useAnimationLoop` custom hook created
- [ ] Simplified useEffect logic (single animation effect)
- [ ] Canvas rendering performance unchanged or improved
- [ ] No visual glitches

### Should Have:

- [ ] Clear comments explaining constants
- [ ] Type definitions for constants (JSDoc or TypeScript)

### Nice to Have:

- [ ] Animation hook reusable for other components
- [ ] Performance metrics logged

---

## Technical Specification

### Current Issues

**Issue 1: Magic Numbers** (CanvasRenderer.jsx)
```javascript
const TURN_TRANSITION_DURATION = 300; // line 39
const FLASH_DURATION = 200; // line 43
const TRAIL_LENGTH = 10; // line 24
const SHIP_A_COLOR = '#4A90E2'; // line 210
const SHIP_B_COLOR = '#E24A4A'; // line 211
```

**Issue 2: Mock Data** (lines 46-65)
```javascript
const mockShipData = useMemo(() => ({
  ship_a: {
    position: { x: -200, y: 100 },
    // ... mock test data
  },
  ship_b: { ... }
}), []);

// Used as fallback
displayState = turnState || mockShipData;
```

**Issue 3: Complex useEffects** (lines 258-283)
```javascript
// First useEffect - starts animation loop
useEffect(() => {
  const canvas = canvasRef.current;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  renderFrame(ctx, dimensions);
  return () => { ... };
}, [dimensions, renderFrame]);

// Second useEffect - triggers on state change
useEffect(() => {
  const canvas = canvasRef.current;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  renderFrame(ctx, dimensions);
}, [turnState, events, dimensions, renderFrame]);

// Overlapping logic, confusing dependencies
```

---

## Implementation Guidance

### Step 1: Create Rendering Constants (0.3 days)

**Create `frontend/src/constants/rendering.js`:**
```javascript
/**
 * Canvas rendering constants for AI-Arena.
 *
 * All visual parameters for canvas rendering are defined here
 * to enable easy tuning and consistent styling.
 */

// Animation timings (milliseconds)
export const TURN_TRANSITION_DURATION = 300;
export const FLASH_DURATION = 200;
export const TRAIL_LENGTH = 10;

// Ship colors
export const SHIP_A_COLOR = '#4A90E2'; // Blue
export const SHIP_B_COLOR = '#E24A4A'; // Red

// Ship rendering
export const SHIP_RADIUS = 15; // units
export const SHIP_HEADING_LINE_LENGTH = 25; // units

// Phaser rendering
export const PHASER_ARC_OPACITY = 0.15;
export const PHASER_FLASH_OPACITY = 0.5;

// Torpedo rendering
export const TORPEDO_RADIUS = 5; // units
export const TORPEDO_TRAIL_OPACITY = 0.3;
export const TORPEDO_TRAIL_FADE_STEPS = 10;

// Blast zone rendering
export const BLAST_ZONE_OPACITY_EXPANSION = 0.4;
export const BLAST_ZONE_OPACITY_PERSISTENCE = 0.3;
export const BLAST_ZONE_OPACITY_DISSIPATION = 0.2;

// Grid rendering
export const GRID_LINE_COLOR = '#222';
export const GRID_SPACING_UNITS = 100; // world units

// Starfield
export const STARFIELD_COUNT = 150;
export const STARFIELD_COLORS = ['#fff', '#cce', '#eef'];

// World bounds (should match backend config)
export const DEFAULT_WORLD_BOUNDS = {
  minX: 0,
  maxX: 1000,
  minY: 0,
  maxY: 500
};
```

### Step 2: Remove Mock Data (0.2 days)

**Update `CanvasRenderer.jsx`:**
```javascript
import {
  TURN_TRANSITION_DURATION,
  FLASH_DURATION,
  TRAIL_LENGTH,
  SHIP_A_COLOR,
  SHIP_B_COLOR,
  DEFAULT_WORLD_BOUNDS
} from '../constants/rendering';

const CanvasRenderer = ({ width = 1200, height = 800, turnState = null, events = [] }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width, height });

  // Track torpedo trails
  const torpedoTrails = useRef({});

  // Starfield background
  const stars = useRef(null);
  const lastStarDimensions = useRef({ width, height });
  if (!stars.current || lastStarDimensions.current.width !== dimensions.width || lastStarDimensions.current.height !== dimensions.height) {
    stars.current = generateStars(STARFIELD_COUNT, dimensions.width, dimensions.height);
    lastStarDimensions.current = { width: dimensions.width, height: dimensions.height };
  }

  // Interpolation state
  const prevTurnState = useRef(null);
  const turnChangeTime = useRef(Date.now());
  const phaserFlashes = useRef([]);

  // DELETE mockShipData - no longer needed

  const renderFrame = useCallback((ctx, dims) => {
    const now = Date.now();
    const worldBounds = DEFAULT_WORLD_BOUNDS;

    // Calculate interpolation alpha
    const timeSinceChange = now - turnChangeTime.current;
    const alpha = Math.min(1, timeSinceChange / TURN_TRANSITION_DURATION);

    // Interpolate between states
    let displayState;
    if (turnState && prevTurnState.current && alpha < 1) {
      displayState = interpolateState(prevTurnState.current, turnState, alpha);
    } else {
      displayState = turnState; // Use actual state or null
      if (alpha >= 1 && turnState) {
        prevTurnState.current = turnState;
      }
    }

    // If no state, render placeholder
    if (!displayState) {
      ctx.fillStyle = '#000';
      ctx.fillRect(0, 0, dims.width, dims.height);
      ctx.fillStyle = '#888';
      ctx.font = '20px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No replay data - select a replay to begin', dims.width / 2, dims.height / 2);
      return;
    }

    // ... rest of rendering logic ...
  }, [turnState, /* ... */]);

  // ... rest of component
};
```

### Step 3: Extract Animation Hook (0.5 days)

**Create `frontend/src/hooks/useAnimationLoop.js`:**
```javascript
import { useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for managing canvas animation loops.
 *
 * Handles requestAnimationFrame loop with proper cleanup and
 * conditional execution (only runs when shouldRun is true).
 *
 * @param {Function} callback - Function to call on each frame
 * @param {boolean} shouldRun - Whether animation loop should run
 * @returns {Object} - { start, stop, isRunning }
 */
export const useAnimationLoop = (callback, shouldRun = true) => {
  const animationFrameId = useRef(null);
  const callbackRef = useRef(callback);

  // Keep callback ref up to date
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  const stop = useCallback(() => {
    if (animationFrameId.current !== null) {
      cancelAnimationFrame(animationFrameId.current);
      animationFrameId.current = null;
    }
  }, []);

  const start = useCallback(() => {
    const animate = () => {
      callbackRef.current();
      animationFrameId.current = requestAnimationFrame(animate);
    };

    stop(); // Stop any existing animation
    animationFrameId.current = requestAnimationFrame(animate);
  }, [stop]);

  // Auto start/stop based on shouldRun
  useEffect(() => {
    if (shouldRun) {
      start();
    } else {
      stop();
    }

    // Cleanup on unmount
    return () => stop();
  }, [shouldRun, start, stop]);

  return {
    start,
    stop,
    isRunning: animationFrameId.current !== null
  };
};
```

### Step 4: Simplify useEffect Logic (0.5 days)

**Update `CanvasRenderer.jsx` to use animation hook:**
```javascript
import { useAnimationLoop } from '../hooks/useAnimationLoop';

const CanvasRenderer = ({ width = 1200, height = 800, turnState = null, events = [] }) => {
  // ... existing state ...

  // Determine if animation should run
  const shouldAnimate = useMemo(() => {
    const now = Date.now();
    const timeSinceChange = now - turnChangeTime.current;
    const isInterpolating = timeSinceChange < TURN_TRANSITION_DURATION;
    const hasFlashes = phaserFlashes.current.length > 0;

    return isInterpolating || hasFlashes;
  }, [turnState, /* dependencies */]);

  // Animation loop using custom hook
  const animationCallback = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    renderFrame(ctx, dimensions);
  }, [dimensions, renderFrame]);

  useAnimationLoop(animationCallback, shouldAnimate);

  // Detect turn state changes
  useEffect(() => {
    if (turnState && turnState !== prevTurnState.current) {
      turnChangeTime.current = Date.now();
      prevTurnState.current = prevTurnState.current || turnState;

      // Check for phaser firing events
      if (events && Array.isArray(events)) {
        events.forEach(event => {
          if (event.type === 'phaser_fired' || event.event === 'phaser_fired') {
            phaserFlashes.current.push({
              ship: event.ship || event.owner,
              startTime: Date.now(),
              config: event.config || 'WIDE'
            });
          }
        });
      }
    }
  }, [turnState, events]);

  // Handle window resize for responsive canvas
  useEffect(() => {
    const handleResize = () => {
      if (!containerRef.current) return;

      const containerWidth = containerRef.current.clientWidth;
      const aspectRatio = height / width;

      const newWidth = Math.min(containerWidth * 0.95, width);
      const newHeight = newWidth * aspectRatio;

      setDimensions({
        width: Math.floor(newWidth),
        height: Math.floor(newHeight)
      });
    };

    handleResize();
    window.addEventListener('resize', handleResize);

    return () => window.removeEventListener('resize', handleResize);
  }, [width, height]);

  // ... rest of component
};
```

---

## Testing Requirements

### Visual Tests

**Manual testing checklist:**

1. **Canvas Rendering**
   - [ ] Ships render correctly (position, heading, color)
   - [ ] Torpedoes render with trails
   - [ ] Blast zones render with correct phases
   - [ ] Phaser arcs visible
   - [ ] Grid and starfield background

2. **Animations**
   - [ ] Smooth turn transitions (300ms interpolation)
   - [ ] Phaser flash effects work
   - [ ] Torpedo trails fade correctly
   - [ ] No stuttering or lag

3. **No Mock Data**
   - [ ] Loading replay shows actual data (no mock ships)
   - [ ] Empty state shows placeholder message (not mock data)

4. **Performance**
   - [ ] Animation loop stops when not needed (check requestAnimationFrame calls)
   - [ ] No memory leaks (check browser dev tools)
   - [ ] Smooth 60 FPS (check performance)

### Unit Tests

**Create `frontend/src/hooks/__tests__/useAnimationLoop.test.js`:**
```javascript
import { renderHook, act } from '@testing-library/react-hooks';
import { useAnimationLoop } from '../useAnimationLoop';

describe('useAnimationLoop', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should start animation when shouldRun is true', () => {
    const callback = jest.fn();
    const { result } = renderHook(() => useAnimationLoop(callback, true));

    // Animation should be running
    expect(result.current.isRunning).toBe(true);
  });

  it('should not start animation when shouldRun is false', () => {
    const callback = jest.fn();
    const { result } = renderHook(() => useAnimationLoop(callback, false));

    // Animation should not be running
    expect(result.current.isRunning).toBe(false);
  });

  it('should stop animation when shouldRun changes to false', () => {
    const callback = jest.fn();
    const { result, rerender } = renderHook(
      ({ shouldRun }) => useAnimationLoop(callback, shouldRun),
      { initialProps: { shouldRun: true } }
    );

    expect(result.current.isRunning).toBe(true);

    // Change shouldRun to false
    rerender({ shouldRun: false });

    expect(result.current.isRunning).toBe(false);
  });

  it('should cleanup animation on unmount', () => {
    const callback = jest.fn();
    const { unmount } = renderHook(() => useAnimationLoop(callback, true));

    const cancelSpy = jest.spyOn(window, 'cancelAnimationFrame');

    unmount();

    expect(cancelSpy).toHaveBeenCalled();
  });
});
```

### Integration Tests

```bash
# Start frontend
cd frontend
npm start

# Manual tests:
# 1. Load a replay
# 2. Play/pause - verify animation starts/stops
# 3. Change turns - verify smooth interpolation
# 4. Check browser console - no errors
# 5. Open dev tools Performance tab
#    - Record during playback
#    - Verify 60 FPS
#    - Check requestAnimationFrame usage
```

---

## Files to Create

1. **`frontend/src/constants/rendering.js`** - Rendering constants
2. **`frontend/src/hooks/useAnimationLoop.js`** - Animation loop hook
3. **`frontend/src/hooks/__tests__/useAnimationLoop.test.js`** - Hook tests

---

## Files to Modify

1. **`frontend/src/components/CanvasRenderer.jsx`**
   - Import constants from `constants/rendering.js`
   - Remove `mockShipData`
   - Use `useAnimationLoop` hook
   - Simplify useEffect logic
   - Add placeholder for empty state

2. **`frontend/src/utils/shipRenderer.js`** (if exists)
   - Import ship colors from constants

3. **`frontend/src/utils/weaponRenderer.js`** (if exists)
   - Import torpedo/blast constants

---

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Constants extracted to dedicated file
- [ ] No mock data in production code
- [ ] Animation hook created and working
- [ ] useEffect logic simplified
- [ ] All visual tests pass
- [ ] Performance unchanged or improved
- [ ] Hook unit tests pass
- [ ] Code reviewed
- [ ] Documentation updated

---

## Dependencies

**Blocks:**
- Story 047 (Unit Tests) - provides testable hooks

**Blocked By:**
- Story 045 (CSS Modules) - should complete CSS first

**Can Run Parallel With:**
- None (should wait for CSS to avoid conflicts)

---

## Notes

### Design Decisions

- **Constants in separate file**: Easier to tune, find, and maintain
- **Custom animation hook**: Reusable, cleaner component logic
- **Remove mock data**: Production code should be clean
- **Single animation useEffect**: Clearer dependencies, easier to reason about

### Benefits

After this story:
- ✅ All rendering params in one place (easy tuning)
- ✅ No test code in production components
- ✅ Cleaner useEffect dependencies
- ✅ Reusable animation hook
- ✅ Better performance (conditional animation)

### Performance Optimization

The new `useAnimationLoop` hook only runs when needed:
- During turn transitions (300ms)
- When phaser flash effects active (200ms)
- Otherwise, animation loop stops (saves CPU/battery)

**Before:** Animation loop always running
**After:** Animation loop conditional (runs only when needed)

This improves performance, especially on battery-powered devices.
