/**
 * Rendering Constants
 *
 * Centralized configuration for canvas rendering, animations, and visual effects.
 */

// Canvas dimensions
export const DEFAULT_CANVAS_WIDTH = 1200;
export const DEFAULT_CANVAS_HEIGHT = 800;

// World bounds (from physics engine)
export const DEFAULT_WORLD_BOUNDS = {
  minX: -500,
  maxX: 500,
  minY: -500,
  maxY: 500
};

// Animation timing
export const TURN_TRANSITION_DURATION = 300; // ms
export const FLASH_DURATION = 200; // ms
export const ANIMATION_FPS = 60;
export const FRAME_TIME = 1000 / ANIMATION_FPS; // ~16.67ms

// Visual effects
export const STARFIELD_STAR_COUNT = 150;
export const TORPEDO_TRAIL_LENGTH = 10; // positions to keep in trail
export const TRAIL_FADE_ALPHA_MIN = 0.1;
export const TRAIL_FADE_ALPHA_MAX = 1.0;

// Ship rendering
export const SHIP_SIZE = 20; // base size in pixels
export const SHIP_GLOW_RADIUS = 5;

// Weapon rendering
export const PHASER_ARC_WIDTH = 2;
export const PHASER_ARC_SEGMENTS = 20;
export const TORPEDO_SIZE = 8;
export const BLAST_ZONE_RADIUS = 100;
export const BLAST_ZONE_LINE_WIDTH = 2;

// Colors (sync with CSS variables)
export const COLORS = {
  shipA: '#4A90E2',
  shipB: '#E24A4A',
  torpedo: '#E2C74A',
  phaser: '#4AE290',
  blastZone: '#ff4444',
  starfield: '#ffffff',
  arena: '#333'
};

// Performance settings
export const ENABLE_ANTIALIASING = true;
export const ENABLE_INTERPOLATION = true;
export const ENABLE_TRAILS = true;
