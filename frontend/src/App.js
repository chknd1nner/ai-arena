import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMatches();
  }, []);

  const fetchMatches = async () => {
    try {
      const response = await fetch('/api/matches');
      const data = await response.json();
      setMatches(data.matches || []);
    } catch (error) {
      console.error('Error fetching matches:', error);
    }
  };

  const startMatch = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/match/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_a: 'gpt-4',
          model_b: 'anthropic/claude-3-haiku-20240307',
          max_turns: 20
        })
      });
      const data = await response.json();
      alert(`Match started! ID: ${data.match_id}`);
      setTimeout(fetchMatches, 2000);
    } catch (error) {
      console.error('Error starting match:', error);
      alert('Failed to start match');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Arena</h1>
        <p>Watch LLMs battle in space combat</p>
      </header>

      <main>
        <section className="controls">
          <button onClick={startMatch} disabled={loading}>
            {loading ? 'Starting Match...' : 'Start New Match'}
          </button>
        </section>

        <section className="matches">
          <h2>Recent Matches</h2>
          {matches.length === 0 ? (
            <p>No matches yet. Start one to begin!</p>
          ) : (
            <ul>
              {matches.map(match => (
                <li key={match.match_id}>
                  <strong>{match.models.ship_a}</strong> vs <strong>{match.models.ship_b}</strong>
                  <br />
                  Winner: {match.winner} | Turns: {match.total_turns}
                  <br />
                  <small>{new Date(match.created_at).toLocaleString()}</small>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
