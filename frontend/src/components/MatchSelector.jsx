import React, { useState, useEffect } from 'react';

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
    <div style={{
      padding: '15px',
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      marginBottom: '20px'
    }}>
      <div style={{ marginBottom: '10px' }}>
        <label
          htmlFor="match-selector"
          style={{
            color: '#fff',
            fontSize: '14px',
            fontWeight: 'bold',
            display: 'block',
            marginBottom: '8px'
          }}
        >
          Select Replay:
        </label>

        {loading && (
          <div style={{ color: '#aaa', fontSize: '14px' }}>
            Loading matches...
          </div>
        )}

        {error && (
          <div style={{ color: '#ff4444', fontSize: '14px', marginBottom: '10px' }}>
            Error: {error}
            <button
              onClick={fetchMatches}
              style={{
                marginLeft: '10px',
                padding: '4px 8px',
                fontSize: '12px',
                backgroundColor: '#4A90E2',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && (
          <select
            id="match-selector"
            value={selectedMatchId || ''}
            onChange={handleChange}
            style={{
              width: '100%',
              padding: '10px',
              fontSize: '14px',
              backgroundColor: '#333',
              color: '#fff',
              border: '1px solid #555',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
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
        <div style={{ color: '#aaa', fontSize: '14px' }}>
          No matches available. Start a new match to create a replay!
        </div>
      )}
    </div>
  );
};

export default MatchSelector;
