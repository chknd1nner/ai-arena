import { worldToScreen, getScale } from './coordinateTransform';

/**
 * Render a phaser arc for a ship
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} ship - Ship object with position and heading
 * @param {string} config - Phaser configuration ('WIDE' or 'FOCUSED')
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries
 */
export function renderPhaserArc(ctx, ship, config, canvasSize, worldBounds) {
  const pos = worldToScreen(ship.position, canvasSize, worldBounds);
  const scale = getScale(canvasSize, worldBounds);

  // Phaser arc angles and ranges based on config
  const arcAngle = config === 'WIDE' ? Math.PI / 2 : Math.PI / 18; // 90° or 10°
  const range = config === 'WIDE' ? 30 : 50;

  ctx.save();
  ctx.globalAlpha = 0.2;
  ctx.fillStyle = '#00ff00'; // Green phaser arc
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);

  // Canvas Y axis is inverted, so we negate the heading
  // Ship heading: 0 = East, counterclockwise (math convention)
  // Canvas: Y increases downward, so we flip
  ctx.arc(
    pos.x, pos.y,
    range * scale,
    -ship.heading - arcAngle / 2,
    -ship.heading + arcAngle / 2
  );
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

/**
 * Render a phaser firing effect
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} ship - Ship object with position and heading
 * @param {string} config - Phaser configuration ('WIDE' or 'FOCUSED')
 * @param {Object} targetPos - Target position {x, y}
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries
 */
export function renderPhaserFiring(ctx, ship, config, targetPos, canvasSize, worldBounds) {
  const shipPos = worldToScreen(ship.position, canvasSize, worldBounds);
  const target = worldToScreen(targetPos, canvasSize, worldBounds);

  ctx.save();

  // Bright beam effect
  ctx.strokeStyle = config === 'WIDE' ? '#00ff00' : '#00ffff';
  ctx.lineWidth = config === 'WIDE' ? 3 : 2;
  ctx.globalAlpha = 0.8;

  ctx.beginPath();
  ctx.moveTo(shipPos.x, shipPos.y);
  ctx.lineTo(target.x, target.y);
  ctx.stroke();

  // Add glow effect
  ctx.globalAlpha = 0.3;
  ctx.lineWidth = config === 'WIDE' ? 8 : 6;
  ctx.stroke();

  ctx.restore();
}

/**
 * Render a torpedo
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} torpedo - Torpedo object with position and owner
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries
 */
export function renderTorpedo(ctx, torpedo, canvasSize, worldBounds) {
  const pos = worldToScreen(torpedo.position, canvasSize, worldBounds);

  // Color based on owner (ship_a = blue, ship_b = red)
  const color = torpedo.owner === 'ship_a' ? '#4A90E2' : '#E24A4A';

  ctx.save();

  // Outer glow
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.3;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, 10, 0, Math.PI * 2);
  ctx.fill();

  // Main torpedo body
  ctx.globalAlpha = 1.0;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, 6, 0, Math.PI * 2);
  ctx.fill();

  // White outline
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.restore();
}

/**
 * Render a torpedo's motion trail
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} torpedo - Torpedo object
 * @param {Array} previousPositions - Array of previous positions [{x, y}, ...]
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries
 */
export function renderTorpedoTrail(ctx, torpedo, previousPositions, canvasSize, worldBounds) {
  if (!previousPositions || previousPositions.length === 0) return;

  const color = torpedo.owner === 'ship_a' ? '#4A90E2' : '#E24A4A';

  ctx.save();

  // Draw trail with fading effect
  previousPositions.forEach((pos, index) => {
    const screenPos = worldToScreen(pos, canvasSize, worldBounds);
    const alpha = (index + 1) / previousPositions.length * 0.5; // Fade from 0 to 0.5

    ctx.fillStyle = color;
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(screenPos.x, screenPos.y, 3, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.restore();
}

/**
 * Render an explosion effect
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} position - World position {x, y}
 * @param {number} currentRadius - Current radius of the explosion in world units
 * @param {number} maxRadius - Maximum radius (15.0 units for torpedoes)
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries
 * @param {number} intensity - Intensity of the explosion (0-1), based on time
 */
export function renderExplosion(ctx, position, currentRadius, maxRadius, canvasSize, worldBounds, intensity = 1.0) {
  const pos = worldToScreen(position, canvasSize, worldBounds);
  const scale = getScale(canvasSize, worldBounds);

  ctx.save();

  // Outer blast wave
  ctx.strokeStyle = '#ff6600';
  ctx.lineWidth = 3;
  ctx.globalAlpha = intensity * 0.6;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, currentRadius * scale, 0, Math.PI * 2);
  ctx.stroke();

  // Inner core
  ctx.fillStyle = '#ffaa00';
  ctx.globalAlpha = intensity * 0.3;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, currentRadius * scale * 0.7, 0, Math.PI * 2);
  ctx.fill();

  // Danger zone outline (shows full blast radius)
  if (currentRadius >= maxRadius) {
    ctx.strokeStyle = '#ff0000';
    ctx.lineWidth = 2;
    ctx.globalAlpha = 0.4;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, maxRadius * scale, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  ctx.restore();
}

/**
 * Render a blast zone (persistent damage area)
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} blastZone - Blast zone object with position and radius
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries
 * @param {number} remainingTime - Time remaining in seconds
 * @param {number} totalDuration - Total duration of blast zone
 */
export function renderBlastZone(ctx, blastZone, canvasSize, worldBounds, remainingTime, totalDuration) {
  const pos = worldToScreen(blastZone.position, canvasSize, worldBounds);
  const scale = getScale(canvasSize, worldBounds);
  const intensity = remainingTime / totalDuration; // Fade as time passes

  ctx.save();

  // Danger zone gradient
  const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, blastZone.current_radius * scale);
  gradient.addColorStop(0, `rgba(255, 100, 0, ${0.4 * intensity})`);
  gradient.addColorStop(0.7, `rgba(255, 50, 0, ${0.2 * intensity})`);
  gradient.addColorStop(1, `rgba(255, 0, 0, ${0.05 * intensity})`);

  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, blastZone.current_radius * scale, 0, Math.PI * 2);
  ctx.fill();

  // Pulsing border
  ctx.strokeStyle = `rgba(255, 0, 0, ${0.6 * intensity})`;
  ctx.lineWidth = 2;
  ctx.setLineDash([10, 5]);
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, blastZone.current_radius * scale, 0, Math.PI * 2);
  ctx.stroke();
  ctx.setLineDash([]);

  ctx.restore();
}
