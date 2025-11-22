import React, { useState, useEffect } from 'react';
import styles from './MatchSelector.module.css';

/**
 * Match selector dropdown component
 * Fetches available matches from the API and allows user to select one
 */
const MatchSelector = ({ onSelectMatch, selectedMatchId = null }) => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/matches');

      if (!response.ok) {
        throw new Error(`Failed to fetch matches: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setMatches(data.matches || []);
    } catch (err) {
      console.error('Error fetching matches:', err);
      setError(err.message || 'Failed to load matches');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const matchId = e.target.value;
    if (matchId) {
      onSelectMatch(matchId);
    } else {
      onSelectMatch(null);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.formGroup}>
        <label htmlFor="match-selector" className={styles.label}>
          Select Replay:
        </label>

        {loading && (
          <div className={styles.loading}>
            Loading matches...
          </div>
        )}

        {error && (
          <div className={styles.error}>
            Error: {error}
            <button onClick={fetchMatches} className={styles.retryButton}>
              Retry
            </button>
          </div>
        )}

        {!loading && !error && (
          <select
            id="match-selector"
            value={selectedMatchId || ''}
            onChange={handleChange}
            className={styles.select}
          >
            <option value="">-- Select a replay --</option>
            {matches.map(match => {
              const timestamp = match.created_at
                ? new Date(match.created_at).toLocaleString()
                : 'Unknown time';

              const modelA = match.models?.ship_a || 'Unknown';
              const modelB = match.models?.ship_b || 'Unknown';
              const winner = match.winner || 'N/A';
              const turns = match.total_turns || '?';

              return (
                <option key={match.match_id} value={match.match_id}>
                  {modelA} vs {modelB} | Winner: {winner} | Turns: {turns} | {timestamp}
                </option>
              );
            })}
          </select>
        )}
      </div>

      {matches.length === 0 && !loading && !error && (
        <div className={styles.noMatches}>
          No matches available. Start a new match to create a replay!
        </div>
      )}
    </div>
  );
};

export default MatchSelector;
