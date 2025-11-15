/**
 * Visual effects utilities for enhanced replay rendering
 */

import { worldToScreen, getScale } from './coordinateTransform';

/**
 * Render a starfield background
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Array} stars - Array of star objects [{x, y, brightness}, ...]
 */
export function renderStarfield(ctx, canvasSize, stars) {
  ctx.save();

  stars.forEach(star => {
    ctx.fillStyle = `rgba(255, 255, 255, ${star.brightness})`;
    ctx.beginPath();
    ctx.arc(star.x, star.y, star.size || 1, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.restore();
}

/**
 * Generate random stars for starfield background
 * @param {number} count - Number of stars to generate
 * @param {number} width - Canvas width
 * @param {number} height - Canvas height
 * @returns {Array} Array of star objects
 */
export function generateStars(count, width, height) {
  const stars = [];
  for (let i = 0; i < count; i++) {
    stars.push({
      x: Math.random() * width,
      y: Math.random() * height,
      brightness: 0.3 + Math.random() * 0.7, // 0.3 to 1.0
      size: Math.random() > 0.9 ? 2 : 1 // 10% larger stars
    });
  }
  return stars;
}

/**
 * Render a phaser firing flash effect
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} ship - Ship object with position and heading
 * @param {string} config - Phaser configuration ('WIDE' or 'FOCUSED')
 * @param {Object} canvasSize - Canvas dimensions
 * @param {Object} worldBounds - World boundaries
 * @param {number} intensity - Flash intensity (0 to 1)
 */
export function renderPhaserFlash(ctx, ship, config, canvasSize, worldBounds, intensity = 1.0) {
  const pos = worldToScreen(ship.position, canvasSize, worldBounds);
  const scale = getScale(canvasSize, worldBounds);

  const arcAngle = config === 'WIDE' ? Math.PI / 2 : Math.PI / 18;
  const range = (config === 'WIDE' ? 30 : 50) * scale;

  ctx.save();

  // Bright flash at firing point
  const flashGradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, 15);
  flashGradient.addColorStop(0, `rgba(0, 255, 0, ${0.9 * intensity})`);
  flashGradient.addColorStop(1, `rgba(0, 255, 0, 0)`);

  ctx.fillStyle = flashGradient;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, 15, 0, Math.PI * 2);
  ctx.fill();

  // Bright beam along phaser arc
  ctx.globalAlpha = 0.6 * intensity;
  ctx.fillStyle = config === 'WIDE' ? '#00ff00' : '#00ffff';
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);
  ctx.arc(
    pos.x, pos.y,
    range,
    -ship.heading - arcAngle / 2,
    -ship.heading + arcAngle / 2
  );
  ctx.closePath();
  ctx.fill();

  // Add glowing outline
  ctx.globalAlpha = 0.8 * intensity;
  ctx.strokeStyle = '#ffffff';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(
    pos.x, pos.y,
    range,
    -ship.heading - arcAngle / 2,
    -ship.heading + arcAngle / 2
  );
  ctx.stroke();

  ctx.restore();
}

/**
 * Render a ship with low shields damage indicator (red tint)
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} ship - Ship object with position and shields
 * @param {Object} canvasSize - Canvas dimensions
 * @param {Object} worldBounds - World boundaries
 */
export function renderDamageIndicator(ctx, ship, canvasSize, worldBounds) {
  if (ship.shields >= 30) return; // Only show for low shields

  const pos = worldToScreen(ship.position, canvasSize, worldBounds);
  const intensity = 1 - (ship.shields / 30); // More intense as shields decrease

  ctx.save();

  // Red pulsing glow around damaged ship
  const pulseIntensity = intensity * (0.8 + 0.2 * Math.sin(Date.now() / 200));
  const glowGradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, 30);
  glowGradient.addColorStop(0, `rgba(255, 0, 0, ${0.4 * pulseIntensity})`);
  glowGradient.addColorStop(1, 'rgba(255, 0, 0, 0)');

  ctx.fillStyle = glowGradient;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, 30, 0, Math.PI * 2);
  ctx.fill();

  ctx.restore();
}

/**
 * Render an explosion animation
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} position - World position {x, y}
 * @param {number} progress - Animation progress (0 to 1)
 * @param {Object} canvasSize - Canvas dimensions
 * @param {Object} worldBounds - World boundaries
 */
export function renderExplosionEffect(ctx, position, progress, canvasSize, worldBounds) {
  const pos = worldToScreen(position, canvasSize, worldBounds);
  const scale = getScale(canvasSize, worldBounds);

  // Explosion expands and fades
  const maxRadius = 15 * scale; // Match torpedo blast radius
  const intensity = 1 - progress; // Fade as it expands

  ctx.save();

  // Multiple expanding rings for more dramatic effect
  for (let i = 0; i < 3; i++) {
    const ringProgress = Math.min(1, progress * 1.5 - i * 0.2);
    if (ringProgress <= 0) continue;

    const ringRadius = maxRadius * ringProgress;
    const ringIntensity = (1 - ringProgress) * intensity;

    // Outer ring
    ctx.strokeStyle = `rgba(255, 100, 0, ${0.6 * ringIntensity})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, ringRadius, 0, Math.PI * 2);
    ctx.stroke();

    // Inner glow
    if (i === 0) {
      const coreGradient = ctx.createRadialGradient(
        pos.x, pos.y, 0,
        pos.x, pos.y, ringRadius * 0.6
      );
      coreGradient.addColorStop(0, `rgba(255, 200, 0, ${0.8 * ringIntensity})`);
      coreGradient.addColorStop(1, `rgba(255, 100, 0, ${0.2 * ringIntensity})`);

      ctx.fillStyle = coreGradient;
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, ringRadius * 0.6, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  ctx.restore();
}

/**
 * Render energy charging effect (for weapons charging up)
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} ship - Ship object
 * @param {Object} canvasSize - Canvas dimensions
 * @param {Object} worldBounds - World boundaries
 * @param {number} progress - Charging progress (0 to 1)
 */
export function renderChargingEffect(ctx, ship, canvasSize, worldBounds, progress) {
  const pos = worldToScreen(ship.position, canvasSize, worldBounds);

  ctx.save();

  // Pulsing glow that intensifies with charge
  const pulseIntensity = progress * (0.7 + 0.3 * Math.sin(Date.now() / 100));
  const glowGradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, 25);
  glowGradient.addColorStop(0, `rgba(0, 200, 255, ${0.5 * pulseIntensity})`);
  glowGradient.addColorStop(1, 'rgba(0, 200, 255, 0)');

  ctx.fillStyle = glowGradient;
  ctx.beginPath();
  ctx.arc(pos.x, pos.y, 25, 0, Math.PI * 2);
  ctx.fill();

  // Energy particles
  const particleCount = Math.floor(progress * 8);
  for (let i = 0; i < particleCount; i++) {
    const angle = (Date.now() / 1000 + i * (Math.PI * 2 / particleCount)) % (Math.PI * 2);
    const radius = 20 + 10 * Math.sin(Date.now() / 200 + i);
    const px = pos.x + Math.cos(angle) * radius;
    const py = pos.y + Math.sin(angle) * radius;

    ctx.fillStyle = `rgba(0, 200, 255, ${0.8 * progress})`;
    ctx.beginPath();
    ctx.arc(px, py, 2, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.restore();
}

/**
 * Render shield impact effect when ship takes damage
 * @param {CanvasRenderingContext2D} ctx - Canvas rendering context
 * @param {Object} ship - Ship object
 * @param {Object} canvasSize - Canvas dimensions
 * @param {Object} worldBounds - World boundaries
 * @param {number} intensity - Impact intensity (0 to 1)
 */
export function renderShieldImpact(ctx, ship, canvasSize, worldBounds, intensity) {
  const pos = worldToScreen(ship.position, canvasSize, worldBounds);

  ctx.save();

  // Hexagonal shield pattern flash
  const radius = 20;
  ctx.strokeStyle = `rgba(0, 150, 255, ${0.8 * intensity})`;
  ctx.lineWidth = 2;

  // Draw hexagon
  ctx.beginPath();
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i;
    const x = pos.x + radius * Math.cos(angle);
    const y = pos.y + radius * Math.sin(angle);
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }
  ctx.closePath();
  ctx.stroke();

  // Shield shimmer gradient
  const shimmerGradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, radius);
  shimmerGradient.addColorStop(0, `rgba(0, 150, 255, ${0.3 * intensity})`);
  shimmerGradient.addColorStop(0.8, `rgba(0, 150, 255, ${0.1 * intensity})`);
  shimmerGradient.addColorStop(1, 'rgba(0, 150, 255, 0)');

  ctx.fillStyle = shimmerGradient;
  ctx.fill();

  ctx.restore();
}
