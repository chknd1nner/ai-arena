/**
 * Interpolation utilities for smooth animation between replay turns
 */

/**
 * Interpolate angle values with proper wrapping around 360 degrees
 * @param {number} prev - Previous angle in radians
 * @param {number} next - Next angle in radians
 * @param {number} alpha - Interpolation factor (0 to 1)
 * @returns {number} Interpolated angle in radians
 */
export function interpolateAngle(prev, next, alpha) {
  // Handle angle wrapping (e.g., 359° to 1° should go through 0°, not 358°)
  let diff = next - prev;
  if (diff > Math.PI) diff -= 2 * Math.PI;
  if (diff < -Math.PI) diff += 2 * Math.PI;
  return prev + diff * alpha;
}

/**
 * Interpolate a single ship's state
 * @param {Object} prev - Previous ship state
 * @param {Object} next - Next ship state
 * @param {number} alpha - Interpolation factor (0 to 1)
 * @returns {Object} Interpolated ship state
 */
export function interpolateShip(prev, next, alpha) {
  if (!prev || !next) return prev || next;

  return {
    position: {
      x: prev.position.x + (next.position.x - prev.position.x) * alpha,
      y: prev.position.y + (next.position.y - prev.position.y) * alpha
    },
    heading: interpolateAngle(prev.heading, next.heading, alpha),
    velocity: {
      x: prev.velocity.x + (next.velocity.x - prev.velocity.x) * alpha,
      y: prev.velocity.y + (next.velocity.y - prev.velocity.y) * alpha
    },
    shields: prev.shields + (next.shields - prev.shields) * alpha,
    ae: prev.ae + (next.ae - prev.ae) * alpha,
    phaser_config: prev.phaser_config, // Don't interpolate config
    torpedo_count: prev.torpedo_count
  };
}

/**
 * Interpolate torpedo positions
 * @param {Array} prevTorpedoes - Previous torpedoes array
 * @param {Array} nextTorpedoes - Next torpedoes array
 * @param {number} alpha - Interpolation factor (0 to 1)
 * @returns {Array} Interpolated torpedoes
 */
export function interpolateTorpedoes(prevTorpedoes, nextTorpedoes, alpha) {
  if (!prevTorpedoes || !nextTorpedoes) return prevTorpedoes || nextTorpedoes || [];

  // Match torpedoes by ID or owner + approximate position
  const interpolated = [];

  nextTorpedoes.forEach((nextTorp) => {
    // Try to find matching torpedo in previous state
    const prevTorp = prevTorpedoes.find(t => {
      if (t.id && nextTorp.id) return t.id === nextTorp.id;
      // If no ID, match by owner and proximity (within 50 units)
      const dx = t.position.x - nextTorp.position.x;
      const dy = t.position.y - nextTorp.position.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      return t.owner === nextTorp.owner && dist < 50;
    });

    if (prevTorp) {
      // Interpolate existing torpedo
      interpolated.push({
        ...nextTorp,
        position: {
          x: prevTorp.position.x + (nextTorp.position.x - prevTorp.position.x) * alpha,
          y: prevTorp.position.y + (nextTorp.position.y - prevTorp.position.y) * alpha
        },
        velocity: {
          x: prevTorp.velocity.x + (nextTorp.velocity.x - prevTorp.velocity.x) * alpha,
          y: prevTorp.velocity.y + (nextTorp.velocity.y - prevTorp.velocity.y) * alpha
        }
      });
    } else {
      // New torpedo - show at current position
      interpolated.push(nextTorp);
    }
  });

  return interpolated;
}

/**
 * Interpolate blast zones
 * @param {Array} prevZones - Previous blast zones
 * @param {Array} nextZones - Next blast zones
 * @param {number} alpha - Interpolation factor (0 to 1)
 * @returns {Array} Interpolated blast zones
 */
export function interpolateBlastZones(prevZones, nextZones, alpha) {
  if (!prevZones || !nextZones) return nextZones || prevZones || [];

  const interpolated = [];

  nextZones.forEach((nextZone) => {
    // Find matching blast zone by position
    const prevZone = prevZones.find(z => {
      const dx = z.position.x - nextZone.position.x;
      const dy = z.position.y - nextZone.position.y;
      return Math.abs(dx) < 1 && Math.abs(dy) < 1;
    });

    if (prevZone) {
      // Interpolate remaining time
      interpolated.push({
        ...nextZone,
        remaining_time: prevZone.remaining_time + (nextZone.remaining_time - prevZone.remaining_time) * alpha
      });
    } else {
      // New blast zone
      interpolated.push(nextZone);
    }
  });

  return interpolated;
}

/**
 * Interpolate complete game state between two turns
 * @param {Object} prevState - Previous turn state
 * @param {Object} nextState - Next turn state
 * @param {number} alpha - Interpolation factor (0 to 1, where 0 = prevState, 1 = nextState)
 * @returns {Object} Interpolated game state
 */
export function interpolateState(prevState, nextState, alpha) {
  if (!prevState || !nextState) return nextState || prevState;
  if (alpha <= 0) return prevState;
  if (alpha >= 1) return nextState;

  return {
    ship_a: interpolateShip(prevState.ship_a, nextState.ship_a, alpha),
    ship_b: interpolateShip(prevState.ship_b, nextState.ship_b, alpha),
    torpedoes: interpolateTorpedoes(
      prevState.torpedoes || [],
      nextState.torpedoes || [],
      alpha
    ),
    blast_zones: interpolateBlastZones(
      prevState.blast_zones || [],
      nextState.blast_zones || [],
      alpha
    )
  };
}
