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

/**
 * Convert world coordinates to screen/canvas coordinates
 * @param {Object} worldPos - World position {x, y}
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries (optional)
 * @returns {Object} Screen position {x, y}
 */
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

/**
 * Convert screen/canvas coordinates to world coordinates
 * @param {Object} screenPos - Screen position {x, y}
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries (optional)
 * @returns {Object} World position {x, y}
 */
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

/**
 * Get the current scale factor used for rendering
 * @param {Object} canvasSize - Canvas dimensions {width, height}
 * @param {Object} worldBounds - World boundaries (optional)
 * @returns {number} Scale factor
 */
export function getScale(canvasSize, worldBounds = DEFAULT_WORLD_BOUNDS) {
  const worldWidth = worldBounds.maxX - worldBounds.minX;
  const worldHeight = worldBounds.maxY - worldBounds.minY;

  const scaleX = canvasSize.width / worldWidth;
  const scaleY = canvasSize.height / worldHeight;
  return Math.min(scaleX, scaleY) * 0.9;
}

export { DEFAULT_WORLD_BOUNDS };
