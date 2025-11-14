import { worldToScreen, getScale } from './coordinateTransform';

/**
 * Renders a ship as a triangle (heading) with velocity vector (movement arrow)
 * @param {CanvasRenderingContext2D} ctx - Canvas context
 * @param {Object} ship - Ship state {position, velocity, heading, shields, ae}
 * @param {string} color - Ship color (e.g., '#4A90E2')
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries
 * @param {string} label - Ship label (e.g., 'Ship A')
 */
export function renderShip(ctx, ship, color, canvasSize, worldBounds, label) {
  const screenPos = worldToScreen(ship.position, canvasSize, worldBounds);
  const scale = getScale(canvasSize, worldBounds);

  // Ship size in screen pixels
  const shipSize = 15;

  // Render velocity arrow first (so it appears behind the ship)
  renderVelocityVector(ctx, ship, screenPos, color, scale);

  // Render ship triangle (heading indicator)
  renderShipTriangle(ctx, ship, screenPos, shipSize, color);

  // Render ship label and stats
  renderShipStats(ctx, ship, screenPos, label, color);
}

/**
 * Renders the ship as a triangle pointing in the heading direction
 */
function renderShipTriangle(ctx, ship, screenPos, size, color) {
  ctx.save();

  // Move to ship position
  ctx.translate(screenPos.x, screenPos.y);

  // Rotate to heading (negative because canvas Y is flipped)
  // heading: 0 = east, π/2 = north, π = west, 3π/2 = south
  ctx.rotate(-ship.heading);

  // Draw triangle
  ctx.beginPath();
  ctx.moveTo(size, 0);                    // Nose (pointing right/east when heading=0)
  ctx.lineTo(-size, size * 0.6);          // Bottom-right
  ctx.lineTo(-size, -size * 0.6);         // Bottom-left
  ctx.closePath();

  // Fill
  ctx.fillStyle = color;
  ctx.fill();

  // Stroke
  ctx.strokeStyle = '#fff';
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.restore();
}

/**
 * Renders velocity vector as an arrow showing movement direction
 */
function renderVelocityVector(ctx, ship, screenPos, color, scale) {
  const velocity = ship.velocity;

  // Calculate velocity magnitude
  const velMag = Math.sqrt(velocity.x ** 2 + velocity.y ** 2);

  // Don't draw if velocity is too small
  if (velMag < 0.1) return;

  // Calculate velocity angle
  const velAngle = Math.atan2(velocity.y, velocity.x);

  // Arrow length (scaled based on velocity magnitude, with min/max bounds)
  const baseLength = 40;
  const arrowLength = Math.min(Math.max(baseLength, velMag * scale * 0.3), 80);

  ctx.save();

  // Move to ship position
  ctx.translate(screenPos.x, screenPos.y);

  // Rotate to velocity direction (negative because canvas Y is flipped)
  ctx.rotate(-velAngle);

  // Draw arrow shaft
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 2;
  ctx.globalAlpha = 0.7;

  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(arrowLength, 0);
  ctx.stroke();

  // Draw arrowhead
  const headSize = 8;
  ctx.beginPath();
  ctx.moveTo(arrowLength, 0);
  ctx.lineTo(arrowLength - headSize, -headSize * 0.5);
  ctx.lineTo(arrowLength - headSize, headSize * 0.5);
  ctx.closePath();
  ctx.fill();

  ctx.restore();
}

/**
 * Renders ship label and stats (shields, AE)
 */
function renderShipStats(ctx, ship, screenPos, label, color) {
  ctx.save();

  // Label above ship
  ctx.fillStyle = color;
  ctx.font = 'bold 14px monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'bottom';
  ctx.fillText(label, screenPos.x, screenPos.y - 25);

  // Stats below ship
  ctx.fillStyle = '#fff';
  ctx.font = '12px monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  const stats = `SH:${Math.round(ship.shields)} AE:${Math.round(ship.ae)}`;
  ctx.fillText(stats, screenPos.x, screenPos.y + 25);

  ctx.restore();
}
