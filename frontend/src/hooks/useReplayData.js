import { useState, useEffect } from 'react';

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
        setReplay(data);
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
