import { useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for managing animation loops with requestAnimationFrame
 *
 * @param {Function} callback - Function to call on each animation frame (receives deltaTime)
 * @param {Array} deps - Dependencies array (like useEffect)
 * @param {boolean} enabled - Whether the animation loop should be active
 * @returns {Object} - { start, stop, isRunning }
 */
export const useAnimationLoop = (callback, deps = [], enabled = true) => {
  const frameIdRef = useRef(null);
  const isRunningRef = useRef(false);
  const lastFrameTimeRef = useRef(Date.now());

  const stop = useCallback(() => {
    if (frameIdRef.current !== null) {
      cancelAnimationFrame(frameIdRef.current);
      frameIdRef.current = null;
      isRunningRef.current = false;
    }
  }, []);

  const animate = useCallback(() => {
    const now = Date.now();
    const deltaTime = now - lastFrameTimeRef.current;

    // Call the callback with deltaTime
    callback(deltaTime);

    lastFrameTimeRef.current = now;
    frameIdRef.current = requestAnimationFrame(animate);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callback, ...deps]);

  const start = useCallback(() => {
    if (!isRunningRef.current) {
      isRunningRef.current = true;
      lastFrameTimeRef.current = Date.now();
      frameIdRef.current = requestAnimationFrame(animate);
    }
  }, [animate]);

  // Start/stop based on enabled flag
  useEffect(() => {
    if (enabled) {
      start();
    } else {
      stop();
    }

    return () => stop();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, start, stop, ...deps]);

  return {
    start,
    stop,
    isRunning: isRunningRef.current
  };
};

/**
 * Hook for managing interpolated state transitions
 *
 * @param {Object} currentState - Current turn state
 * @param {Object} previousState - Previous turn state
 * @param {number} duration - Transition duration in ms
 * @returns {Function} - getProgress function that returns progress value between 0 and 1
 */
export const useStateTransition = (currentState, previousState, duration) => {
  const startTimeRef = useRef(Date.now());

  useEffect(() => {
    if (currentState !== previousState) {
      startTimeRef.current = Date.now();
    }
  }, [currentState, previousState]);

  const getProgress = useCallback(() => {
    const elapsed = Date.now() - startTimeRef.current;
    return Math.min(1, elapsed / duration);
  }, [duration]);

  return getProgress;
};
