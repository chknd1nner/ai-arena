import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for managing replay playback controls
 * @param {number} maxTurns - Total number of turns in the replay
 * @returns {Object} Playback state and controls
 */
export function usePlaybackControls(maxTurns) {
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1); // 1x speed by default
  const [currentTurn, setCurrentTurn] = useState(0);

  // Auto-advance turns when playing
  useEffect(() => {
    if (!playing) return;

    // Calculate turn duration based on speed (1000ms / speed)
    const turnDuration = 1000 / speed;

    const interval = setInterval(() => {
      setCurrentTurn(prev => {
        // Auto-stop at end of replay
        if (prev >= maxTurns - 1) {
          setPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, turnDuration);

    return () => clearInterval(interval);
  }, [playing, speed, maxTurns]);

  // Control functions
  const togglePlayPause = useCallback(() => {
    setPlaying(prev => !prev);
  }, []);

  const pause = useCallback(() => {
    setPlaying(false);
  }, []);

  const play = useCallback(() => {
    // If at end, restart from beginning
    if (currentTurn >= maxTurns - 1) {
      setCurrentTurn(0);
    }
    setPlaying(true);
  }, [currentTurn, maxTurns]);

  const jumpToTurn = useCallback((turnIndex) => {
    setCurrentTurn(Math.max(0, Math.min(turnIndex, maxTurns - 1)));
    // Pause when manually jumping
    setPlaying(false);
  }, [maxTurns]);

  const changeSpeed = useCallback((newSpeed) => {
    setSpeed(newSpeed);
  }, []);

  const reset = useCallback(() => {
    setCurrentTurn(0);
    setPlaying(false);
  }, []);

  return {
    // State
    playing,
    speed,
    currentTurn,
    maxTurns,

    // Controls
    togglePlayPause,
    play,
    pause,
    jumpToTurn,
    changeSpeed,
    reset
  };
}
