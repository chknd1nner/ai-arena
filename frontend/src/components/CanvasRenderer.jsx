import React, { useRef, useEffect, useState, useCallback } from 'react';
import { worldToScreen, DEFAULT_WORLD_BOUNDS } from '../utils/coordinateTransform';
import { renderShip } from '../utils/shipRenderer';
import {
  renderPhaserArc,
  renderTorpedo,
  renderTorpedoTrail,
  renderBlastZone
} from '../utils/weaponRenderer';
import { interpolateState } from '../utils/interpolation';
import {
  renderStarfield,
  generateStars,
  renderPhaserFlash,
  renderDamageIndicator
} from '../utils/visualEffects';
import {
  DEFAULT_CANVAS_WIDTH,
  DEFAULT_CANVAS_HEIGHT,
  STARFIELD_STAR_COUNT,
  TORPEDO_TRAIL_LENGTH,
  TURN_TRANSITION_DURATION,
  FLASH_DURATION
} from '../constants/rendering';

const CanvasRenderer = ({ width = DEFAULT_CANVAS_WIDTH, height = DEFAULT_CANVAS_HEIGHT, turnState = null, events = [] }) => {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width, height });

  // Track torpedo trails (store last N positions for each torpedo)
  const torpedoTrails = useRef({});

  // Starfield background - regenerate when dimensions change
  const stars = useRef(null);
  const lastStarDimensions = useRef({ width, height });
  if (!stars.current || lastStarDimensions.current.width !== dimensions.width || lastStarDimensions.current.height !== dimensions.height) {
    stars.current = generateStars(STARFIELD_STAR_COUNT, dimensions.width, dimensions.height);
    lastStarDimensions.current = { width: dimensions.width, height: dimensions.height };
  }

  // Interpolation state
  const prevTurnState = useRef(null);
  const turnChangeTime = useRef(Date.now());
  const animationFrameId = useRef(null);

  // Track phaser flash effects
  const phaserFlashes = useRef([]);

  // Detect turn state changes and trigger effects
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
    for (let x = 0; x <= 1000; x += 100) {
      const top = worldToScreen({ x, y: worldBounds.maxY }, dims, worldBounds);
      const bottom = worldToScreen({ x, y: worldBounds.minY }, dims, worldBounds);
      ctx.beginPath();
      ctx.moveTo(top.x, top.y);
      ctx.lineTo(bottom.x, bottom.y);
      ctx.stroke();
    }

    // Horizontal grid lines (every 100 world units)
    for (let y = 0; y <= 500; y += 100) {
      const left = worldToScreen({ x: worldBounds.minX, y }, dims, worldBounds);
      const right = worldToScreen({ x: worldBounds.maxX, y }, dims, worldBounds);
      ctx.beginPath();
      ctx.moveTo(left.x, left.y);
      ctx.lineTo(right.x, right.y);
      ctx.stroke();
    }
  }, []);


  const renderFrame = useCallback((ctx, dims) => {
    const now = Date.now();
    const worldBounds = DEFAULT_WORLD_BOUNDS;

    // Calculate interpolation alpha
    const timeSinceChange = now - turnChangeTime.current;
    const alpha = Math.min(1, timeSinceChange / TURN_TRANSITION_DURATION);

    // Handle null turnState (show empty arena)
    if (!turnState) {
      // Just render the arena boundaries, no ships
      renderArena(ctx, dims);
      return;
    }

    // Interpolate between previous and current turn state
    let displayState;
    if (prevTurnState.current && alpha < 1) {
      displayState = interpolateState(prevTurnState.current, turnState, alpha);
    } else {
      displayState = turnState;
      if (alpha >= 1) {
        prevTurnState.current = turnState;
      }
    }

    // Clear canvas with black background
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, dims.width, dims.height);

    // Render starfield background
    if (stars.current) {
      renderStarfield(ctx, dims, stars.current);
    }

    // Render arena boundaries
    renderArena(ctx, dims);

    // Render blast zones (behind everything for danger zones)
    if (displayState.blast_zones && Array.isArray(displayState.blast_zones)) {
      displayState.blast_zones.forEach((blastZone) => {
        const remainingTime = blastZone.remaining_time || 60.0;
        const totalDuration = 60.0;
        renderBlastZone(ctx, blastZone, dims, worldBounds, remainingTime, totalDuration);
      });
    }

    // Render phaser arcs (semi-transparent, behind ships)
    if (displayState.ship_a && displayState.ship_a.phaser_config) {
      renderPhaserArc(ctx, displayState.ship_a, displayState.ship_a.phaser_config, dims, worldBounds);
    }

    if (displayState.ship_b && displayState.ship_b.phaser_config) {
      renderPhaserArc(ctx, displayState.ship_b, displayState.ship_b.phaser_config, dims, worldBounds);
    }

    // Render phaser flash effects
    phaserFlashes.current = phaserFlashes.current.filter(flash => {
      const flashAge = now - flash.startTime;
      if (flashAge > FLASH_DURATION) return false;

      const intensity = 1 - (flashAge / FLASH_DURATION);
      const ship = flash.ship === 'ship_a' ? displayState.ship_a : displayState.ship_b;
      if (ship) {
        renderPhaserFlash(ctx, ship, flash.config, dims, worldBounds, intensity);
      }
      return true;
    });

    // Render damage indicators for low shields
    if (displayState.ship_a) {
      renderDamageIndicator(ctx, displayState.ship_a, dims, worldBounds);
    }
    if (displayState.ship_b) {
      renderDamageIndicator(ctx, displayState.ship_b, dims, worldBounds);
    }

    // Render ships
    const SHIP_A_COLOR = '#4A90E2';  // Blue
    const SHIP_B_COLOR = '#E24A4A';  // Red

    if (displayState.ship_a) {
      renderShip(ctx, displayState.ship_a, SHIP_A_COLOR, dims, worldBounds, 'Ship A');
    }
    if (displayState.ship_b) {
      renderShip(ctx, displayState.ship_b, SHIP_B_COLOR, dims, worldBounds, 'Ship B');
    }

    // Render torpedoes and trails (on top of ships)
    if (displayState.torpedoes && Array.isArray(displayState.torpedoes)) {
      displayState.torpedoes.forEach((torpedo) => {
        const torpId = torpedo.id || `${torpedo.owner}_${torpedo.position.x}_${torpedo.position.y}`;

        if (!torpedoTrails.current[torpId]) {
          torpedoTrails.current[torpId] = [];
        }

        torpedoTrails.current[torpId].push({ ...torpedo.position });

        if (torpedoTrails.current[torpId].length > TORPEDO_TRAIL_LENGTH) {
          torpedoTrails.current[torpId].shift();
        }

        renderTorpedoTrail(ctx, torpedo, torpedoTrails.current[torpId], dims, worldBounds);
        renderTorpedo(ctx, torpedo, dims, worldBounds);
      });

      // Clean up old trails
      const activeTorpIds = displayState.torpedoes.map(t =>
        t.id || `${t.owner}_${t.position.x}_${t.position.y}`
      );
      Object.keys(torpedoTrails.current).forEach(id => {
        if (!activeTorpIds.includes(id)) {
          delete torpedoTrails.current[id];
        }
      });
    }

    // Continue animation loop for smooth interpolation
    if (alpha < 1 || phaserFlashes.current.length > 0) {
      animationFrameId.current = requestAnimationFrame(() => {
        renderFrame(ctx, dims);
      });
    }
  }, [renderArena, turnState]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Start the animation loop
    renderFrame(ctx, dimensions);

    // Cleanup animation frame on unmount
    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [dimensions, renderFrame]);

  // Trigger re-render when turnState or events change
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    renderFrame(ctx, dimensions);
  }, [turnState, events, dimensions, renderFrame]);

  // Handle window resize for responsive canvas
  useEffect(() => {
    const handleResize = () => {
      if (!containerRef.current) return;

      const containerWidth = containerRef.current.clientWidth;
      const aspectRatio = height / width; // Maintain original aspect ratio

      // Calculate new dimensions
      const newWidth = Math.min(containerWidth * 0.95, width); // Max 95% of container, capped at original width
      const newHeight = newWidth * aspectRatio;

      setDimensions({
        width: Math.floor(newWidth),
        height: Math.floor(newHeight)
      });
    };

    // Initial sizing
    handleResize();

    // Add resize listener
    window.addEventListener('resize', handleResize);

    return () => window.removeEventListener('resize', handleResize);
  }, [width, height]);

  return (
    <div ref={containerRef} style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
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
