import React, { useRef, useEffect, useState, useCallback } from 'react';
import { worldToScreen, DEFAULT_WORLD_BOUNDS } from '../utils/coordinateTransform';
import { renderShip } from '../utils/shipRenderer';

const CanvasRenderer = ({ width = 1200, height = 800, turnState = null }) => {
  const canvasRef = useRef(null);
  // eslint-disable-next-line no-unused-vars
  const [dimensions, setDimensions] = useState({ width, height });

  // Mock ship data for testing (used when no turnState provided)
  const mockShipData = {
    ship_a: {
      position: { x: -200, y: 100 },
      velocity: { x: 15, y: 5 },
      heading: Math.PI / 4,  // 45 degrees - northeast
      shields: 85,
      ae: 67
    },
    ship_b: {
      position: { x: 200, y: -100 },
      velocity: { x: -10, y: 8 },
      heading: Math.PI * 0.75,  // 135 degrees - northwest
      shields: 92,
      ae: 54
    }
  };

  const renderArena = useCallback((ctx, dims) => {
    const worldBounds = DEFAULT_WORLD_BOUNDS;

    // Convert world boundary corners to screen coordinates
    const topLeft = worldToScreen(
      { x: worldBounds.minX, y: worldBounds.maxY },
      dims,
      worldBounds
    );
    const bottomRight = worldToScreen(
      { x: worldBounds.maxX, y: worldBounds.minY },
      dims,
      worldBounds
    );

    // Draw arena boundary rectangle
    ctx.strokeStyle = '#444';
    ctx.lineWidth = 2;
    ctx.strokeRect(
      topLeft.x,
      topLeft.y,
      bottomRight.x - topLeft.x,
      bottomRight.y - topLeft.y
    );

    // Add subtle grid lines
    ctx.strokeStyle = '#222';
    ctx.lineWidth = 1;

    // Vertical grid lines (every 100 world units)
    for (let x = -400; x <= 400; x += 100) {
      const top = worldToScreen({ x, y: worldBounds.maxY }, dims, worldBounds);
      const bottom = worldToScreen({ x, y: worldBounds.minY }, dims, worldBounds);
      ctx.beginPath();
      ctx.moveTo(top.x, top.y);
      ctx.lineTo(bottom.x, bottom.y);
      ctx.stroke();
    }

    // Horizontal grid lines (every 100 world units)
    for (let y = -300; y <= 300; y += 100) {
      const left = worldToScreen({ x: worldBounds.minX, y }, dims, worldBounds);
      const right = worldToScreen({ x: worldBounds.maxX, y }, dims, worldBounds);
      ctx.beginPath();
      ctx.moveTo(left.x, left.y);
      ctx.lineTo(right.x, right.y);
      ctx.stroke();
    }
  }, []);

  const renderShips = useCallback((ctx, dims) => {
    const worldBounds = DEFAULT_WORLD_BOUNDS;

    // Use turnState if provided, otherwise use mock data
    const shipData = turnState || mockShipData;

    // Define ship colors
    const SHIP_A_COLOR = '#4A90E2';  // Blue
    const SHIP_B_COLOR = '#E24A4A';  // Red

    // Render Ship A
    if (shipData.ship_a) {
      renderShip(
        ctx,
        shipData.ship_a,
        SHIP_A_COLOR,
        dims,
        worldBounds,
        'Ship A'
      );
    }

    // Render Ship B
    if (shipData.ship_b) {
      renderShip(
        ctx,
        shipData.ship_b,
        SHIP_B_COLOR,
        dims,
        worldBounds,
        'Ship B'
      );
    }
  }, [turnState, mockShipData]);

  const renderFrame = useCallback((ctx, dims) => {
    // Clear canvas with black background
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, dims.width, dims.height);

    // Render arena boundaries
    renderArena(ctx, dims);

    // Render ships (from turnState or mock data)
    renderShips(ctx, dims);
  }, [renderArena, renderShips]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    renderFrame(ctx, dimensions);

    // Handle window resize for responsive canvas
    const handleResize = () => {
      // Keep the canvas responsive while maintaining the specified dimensions
      // This allows the canvas to scale with the container via CSS
      if (canvas) {
        renderFrame(ctx, dimensions);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [dimensions, renderFrame]);

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
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
      <div style={{ marginTop: '10px', color: '#666', fontSize: '14px' }}>
        Arena: {DEFAULT_WORLD_BOUNDS.minX} to {DEFAULT_WORLD_BOUNDS.maxX} (X), {DEFAULT_WORLD_BOUNDS.minY} to {DEFAULT_WORLD_BOUNDS.maxY} (Y)
      </div>
    </div>
  );
};

export default CanvasRenderer;
