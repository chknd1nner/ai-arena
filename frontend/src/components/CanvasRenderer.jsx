import React, { useRef, useEffect, useState, useCallback } from 'react';
import { worldToScreen, DEFAULT_WORLD_BOUNDS } from '../utils/coordinateTransform';

const CanvasRenderer = ({ width = 1200, height = 800 }) => {
  const canvasRef = useRef(null);
  // eslint-disable-next-line no-unused-vars
  const [dimensions, setDimensions] = useState({ width, height });

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

  const renderTestMarkers = useCallback((ctx, dims) => {
    const worldBounds = DEFAULT_WORLD_BOUNDS;

    // Test points to verify coordinate transformation
    const testPoints = [
      { pos: { x: 0, y: 0 }, label: 'Origin (0,0)', color: '#ff0000' },
      { pos: { x: 500, y: 400 }, label: 'Top-Right (500,400)', color: '#ff4444' },
      { pos: { x: -500, y: 400 }, label: 'Top-Left (-500,400)', color: '#ff4444' },
      { pos: { x: 500, y: -400 }, label: 'Bottom-Right (500,-400)', color: '#ff4444' },
      { pos: { x: -500, y: -400 }, label: 'Bottom-Left (-500,-400)', color: '#ff4444' },
      { pos: { x: 0, y: 400 }, label: 'Top (0,400)', color: '#ffaa00' },
      { pos: { x: 0, y: -400 }, label: 'Bottom (0,-400)', color: '#ffaa00' },
      { pos: { x: 500, y: 0 }, label: 'Right (500,0)', color: '#ffaa00' },
      { pos: { x: -500, y: 0 }, label: 'Left (-500,0)', color: '#ffaa00' }
    ];

    testPoints.forEach(({ pos, label, color }) => {
      const screen = worldToScreen(pos, dims, worldBounds);

      // Draw circle marker
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(screen.x, screen.y, 5, 0, Math.PI * 2);
      ctx.fill();

      // Draw label
      ctx.fillStyle = 'white';
      ctx.font = '12px monospace';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(label, screen.x + 10, screen.y);
    });

    // Draw coordinate axes for additional clarity
    ctx.strokeStyle = '#666';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);

    // X-axis (horizontal line through origin)
    const xAxisLeft = worldToScreen({ x: worldBounds.minX, y: 0 }, dims, worldBounds);
    const xAxisRight = worldToScreen({ x: worldBounds.maxX, y: 0 }, dims, worldBounds);
    ctx.beginPath();
    ctx.moveTo(xAxisLeft.x, xAxisLeft.y);
    ctx.lineTo(xAxisRight.x, xAxisRight.y);
    ctx.stroke();

    // Y-axis (vertical line through origin)
    const yAxisTop = worldToScreen({ x: 0, y: worldBounds.maxY }, dims, worldBounds);
    const yAxisBottom = worldToScreen({ x: 0, y: worldBounds.minY }, dims, worldBounds);
    ctx.beginPath();
    ctx.moveTo(yAxisTop.x, yAxisTop.y);
    ctx.lineTo(yAxisBottom.x, yAxisBottom.y);
    ctx.stroke();

    ctx.setLineDash([]);
  }, []);

  const renderFrame = useCallback((ctx, dims) => {
    // Clear canvas with black background
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, dims.width, dims.height);

    // Render arena boundaries
    renderArena(ctx, dims);

    // Render test markers to validate coordinate transformation
    renderTestMarkers(ctx, dims);
  }, [renderArena, renderTestMarkers]);

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
