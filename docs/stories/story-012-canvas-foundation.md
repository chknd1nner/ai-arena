# Story 012: Canvas Foundation & Coordinate System

**Epic:** [Epic 003: Canvas-Based Match Replay Viewer](../epic-003-canvas-replay-viewer.md)
**Status:** Not Started
**Size:** Small (~1-1.5 hours)
**Priority:** P0

---

## User Story

**As a** developer
**I want** a canvas component with proper coordinate transformation
**So that** I can render game objects in world coordinates on screen coordinates

## Context

This is the foundation story for Epic 003. Before we can render ships, weapons, or replays, we need:
1. A React component with an HTML5 Canvas element
2. World-to-screen coordinate transformation
3. Arena boundary rendering
4. Proper canvas sizing and responsiveness

The game uses world coordinates (e.g., ship at position x=100, y=50) but the canvas uses screen pixels. We need a transformation layer that:
- Centers the arena on the canvas
- Maintains aspect ratio
- Flips Y-axis (world: Y+ is up, canvas: Y+ is down)
- Scales appropriately to fit the canvas

## Acceptance Criteria

- [ ] React component `CanvasRenderer` exists in `frontend/src/components/`
- [ ] Canvas element renders with proper dimensions
- [ ] Canvas resizes responsively to container
- [ ] Coordinate transformation functions implemented:
  - `worldToScreen(worldPos)` - Convert world coords to canvas pixels
  - `screenToWorld(screenPos)` - Convert canvas pixels to world coords (for future interactivity)
- [ ] Arena boundaries render as a rectangle
- [ ] Coordinate system verified with test markers at known world positions
- [ ] Canvas maintains 16:9 or similar aspect ratio
- [ ] No console errors

## Technical Requirements

### Canvas Component Structure

**File:** `frontend/src/components/CanvasRenderer.jsx`

```jsx
import React, { useRef, useEffect, useState } from 'react';

const CanvasRenderer = ({ width = 1200, height = 800, children }) => {
  const canvasRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width, height });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    renderFrame(ctx, dimensions);
  }, [dimensions]);

  const renderFrame = (ctx, dims) => {
    // Clear canvas
    ctx.clearRect(0, 0, dims.width, dims.height);

    // Render arena boundaries
    renderArena(ctx, dims);

    // TODO: Render game objects (future stories)
  };

  const renderArena = (ctx, dims) => {
    // Draw arena boundary
    const worldBounds = {
      minX: -500,
      maxX: 500,
      minY: -400,
      maxY: 400
    };

    const topLeft = worldToScreen({ x: worldBounds.minX, y: worldBounds.maxY }, dims, worldBounds);
    const bottomRight = worldToScreen({ x: worldBounds.maxX, y: worldBounds.minY }, dims, worldBounds);

    ctx.strokeStyle = '#444';
    ctx.lineWidth = 2;
    ctx.strokeRect(
      topLeft.x,
      topLeft.y,
      bottomRight.x - topLeft.x,
      bottomRight.y - topLeft.y
    );
  };

  const worldToScreen = (worldPos, canvasDims, worldBounds) => {
    const worldWidth = worldBounds.maxX - worldBounds.minX;
    const worldHeight = worldBounds.maxY - worldBounds.minY;

    // Calculate scale to fit world into canvas
    const scaleX = canvasDims.width / worldWidth;
    const scaleY = canvasDims.height / worldHeight;
    const scale = Math.min(scaleX, scaleY) * 0.9; // 90% to leave padding

    // Transform: world origin (0,0) → canvas center
    // Flip Y axis: world Y+ is up, canvas Y+ is down
    return {
      x: (worldPos.x - worldBounds.minX) * scale + (canvasDims.width - worldWidth * scale) / 2,
      y: (worldBounds.maxY - worldPos.y) * scale + (canvasDims.height - worldHeight * scale) / 2
    };
  };

  return (
    <div style={{ width: '100%', display: 'flex', justifyContent: 'center' }}>
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        style={{
          border: '1px solid #333',
          backgroundColor: '#000',
          maxWidth: '100%',
          height: 'auto'
        }}
      />
    </div>
  );
};

export default CanvasRenderer;
```

### Coordinate Transformation Utility

**File:** `frontend/src/utils/coordinateTransform.js`

```javascript
/**
 * World coordinate system:
 * - Origin (0, 0) at center
 * - X+ is right (east)
 * - Y+ is up (north)
 * - Units: arbitrary (e.g., x=-500 to x=500)
 *
 * Canvas coordinate system:
 * - Origin (0, 0) at top-left
 * - X+ is right
 * - Y+ is down
 * - Units: pixels
 */

const DEFAULT_WORLD_BOUNDS = {
  minX: -500,
  maxX: 500,
  minY: -400,
  maxY: 400
};

export function worldToScreen(worldPos, canvasSize, worldBounds = DEFAULT_WORLD_BOUNDS) {
  const worldWidth = worldBounds.maxX - worldBounds.minX;
  const worldHeight = worldBounds.maxY - worldBounds.minY;

  // Calculate scale factor (maintain aspect ratio)
  const scaleX = canvasSize.width / worldWidth;
  const scaleY = canvasSize.height / worldHeight;
  const scale = Math.min(scaleX, scaleY) * 0.9; // 90% to add padding

  // Calculate centered offset
  const offsetX = (canvasSize.width - worldWidth * scale) / 2;
  const offsetY = (canvasSize.height - worldHeight * scale) / 2;

  // Transform coordinates
  return {
    x: (worldPos.x - worldBounds.minX) * scale + offsetX,
    y: (worldBounds.maxY - worldPos.y) * scale + offsetY  // Flip Y axis
  };
}

export function screenToWorld(screenPos, canvasSize, worldBounds = DEFAULT_WORLD_BOUNDS) {
  const worldWidth = worldBounds.maxX - worldBounds.minX;
  const worldHeight = worldBounds.maxY - worldBounds.minY;

  const scaleX = canvasSize.width / worldWidth;
  const scaleY = canvasSize.height / worldHeight;
  const scale = Math.min(scaleX, scaleY) * 0.9;

  const offsetX = (canvasSize.width - worldWidth * scale) / 2;
  const offsetY = (canvasSize.height - worldHeight * scale) / 2;

  return {
    x: (screenPos.x - offsetX) / scale + worldBounds.minX,
    y: worldBounds.maxY - (screenPos.y - offsetY) / scale  // Flip Y axis
  };
}

export function getScale(canvasSize, worldBounds = DEFAULT_WORLD_BOUNDS) {
  const worldWidth = worldBounds.maxX - worldBounds.minX;
  const worldHeight = worldBounds.maxY - worldBounds.minY;

  const scaleX = canvasSize.width / worldWidth;
  const scaleY = canvasSize.height / worldHeight;
  return Math.min(scaleX, scaleY) * 0.9;
}
```

### Integration with App

**File:** `frontend/src/App.js` (add new route or component)

```javascript
import React, { useState } from 'react';
import CanvasRenderer from './components/CanvasRenderer';

function App() {
  const [showViewer, setShowViewer] = useState(false);

  return (
    <div className="App">
      <h1>AI Arena</h1>

      {/* Existing match controls */}
      {/* ... */}

      {/* New: Canvas viewer */}
      <button onClick={() => setShowViewer(!showViewer)}>
        {showViewer ? 'Hide' : 'Show'} Canvas Viewer
      </button>

      {showViewer && (
        <div style={{ marginTop: '20px' }}>
          <CanvasRenderer width={1200} height={800} />
        </div>
      )}
    </div>
  );
}

export default App;
```

## Testing & Validation

### Manual Testing Checklist

- [ ] Canvas renders with black background and gray boundary
- [ ] Arena boundary is centered on canvas
- [ ] Resizing browser window doesn't break canvas
- [ ] No console errors or warnings

### Visual Validation

Add test markers to verify coordinate transformation:
```javascript
// In renderFrame(), add test markers
const testPoints = [
  { pos: { x: 0, y: 0 }, label: 'Origin' },
  { pos: { x: 500, y: 400 }, label: 'Top-Right' },
  { pos: { x: -500, y: -400 }, label: 'Bottom-Left' },
  { pos: { x: 0, y: 400 }, label: 'Top' },
  { pos: { x: 0, y: -400 }, label: 'Bottom' }
];

testPoints.forEach(({ pos, label }) => {
  const screen = worldToScreen(pos, dims, worldBounds);
  ctx.fillStyle = 'red';
  ctx.beginPath();
  ctx.arc(screen.x, screen.y, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = 'white';
  ctx.fillText(label, screen.x + 10, screen.y);
});
```

Expected result:
- Red dot at canvas center labeled "Origin"
- Red dots at corners labeled correctly
- Arena boundary fits within canvas with padding

## Implementation Checklist

- [ ] Create `frontend/src/components/CanvasRenderer.jsx`
- [ ] Create `frontend/src/utils/coordinateTransform.js`
- [ ] Update `frontend/src/App.js` to import and render CanvasRenderer
- [ ] Test canvas renders
- [ ] Add test markers to validate coordinate transformation
- [ ] Verify arena boundaries render correctly
- [ ] Test responsive sizing
- [ ] Remove test markers (or keep for debugging)
- [ ] Commit changes

## Definition of Done

- [ ] Canvas component renders successfully
- [ ] Arena boundaries visible and centered
- [ ] Coordinate transformation functions work correctly
- [ ] Test markers appear at expected positions
- [ ] No console errors
- [ ] Code committed to feature branch

## Files to Create/Modify

- Create: `frontend/src/components/CanvasRenderer.jsx`
- Create: `frontend/src/utils/coordinateTransform.js`
- Modify: `frontend/src/App.js` (add viewer toggle)

## Dependencies

- **Requires:** None (fully independent)
- **Blocks:** Stories 013-019 (all depend on canvas foundation)

## Notes

**Why This Story is First:**
- Establishes rendering foundation
- Validates coordinate system before adding complexity
- Testable immediately with visual markers
- No external dependencies (no API, no data)

**Coordinate System Clarification:**
- Game engine uses standard math coordinates (Y+ is up)
- Canvas uses computer graphics coordinates (Y+ is down)
- Transformation must flip Y-axis to display correctly

**Arena Bounds:**
- Current bounds: x ∈ [-500, 500], y ∈ [-400, 400]
- May need adjustment based on config.json (future story)
- For now, hardcode reasonable defaults

---

**Ready for Claude Code Web implementation!**
