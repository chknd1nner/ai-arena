import { useState, useEffect } from 'react';

/**
 * Converts array-based positions and velocities to object format
 * Backend stores as [x, y], frontend expects {x, y}
 * @param {Object} replayData - Raw replay data from API
 * @returns {Object} Transformed replay data
 */
function transformReplayData(replayData) {
  if (!replayData || !replayData.turns) return replayData;

  return {
    ...replayData,
    turns: replayData.turns.map(turn => ({
      ...turn,
      state: {
        ...turn.state,
        ship_a: turn.state.ship_a ? {
          ...turn.state.ship_a,
          position: Array.isArray(turn.state.ship_a.position)
            ? { x: turn.state.ship_a.position[0], y: turn.state.ship_a.position[1] }
            : turn.state.ship_a.position,
          velocity: Array.isArray(turn.state.ship_a.velocity)
            ? { x: turn.state.ship_a.velocity[0], y: turn.state.ship_a.velocity[1] }
            : turn.state.ship_a.velocity
        } : null,
        ship_b: turn.state.ship_b ? {
          ...turn.state.ship_b,
          position: Array.isArray(turn.state.ship_b.position)
            ? { x: turn.state.ship_b.position[0], y: turn.state.ship_b.position[1] }
            : turn.state.ship_b.position,
          velocity: Array.isArray(turn.state.ship_b.velocity)
            ? { x: turn.state.ship_b.velocity[0], y: turn.state.ship_b.velocity[1] }
            : turn.state.ship_b.velocity
        } : null,
        torpedoes: turn.state.torpedoes ? turn.state.torpedoes.map(torpedo => ({
          ...torpedo,
          position: Array.isArray(torpedo.position)
            ? { x: torpedo.position[0], y: torpedo.position[1] }
            : torpedo.position,
          velocity: Array.isArray(torpedo.velocity)
            ? { x: torpedo.velocity[0], y: torpedo.velocity[1] }
            : torpedo.velocity
        })) : [],
        blast_zones: turn.state.blast_zones ? turn.state.blast_zones.map(zone => ({
          ...zone,
          position: Array.isArray(zone.position)
            ? { x: zone.position[0], y: zone.position[1] }
            : zone.position
        })) : []
      }
    }))
  };
}

/**
 * Custom hook to fetch replay data from the backend API
 * @param {string} matchId - The match ID to fetch replay for
 * @returns {Object} { replay, loading, error }
 */
export function useReplayData(matchId) {
  const [replay, setReplay] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Reset state when matchId changes
    if (!matchId) {
      setReplay(null);
      setError(null);
      setLoading(false);
      return;
    }

    const fetchReplay = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/match/${matchId}/replay`);

        if (!response.ok) {
          throw new Error(`Failed to fetch replay: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        const transformedData = transformReplayData(data);
        setReplay(transformedData);
      } catch (err) {
        console.error('Error fetching replay:', err);
        setError(err.message || 'Failed to load replay');
        setReplay(null);
      } finally {
        setLoading(false);
      }
    };

    fetchReplay();
  }, [matchId]);

  return { replay, loading, error };
}
