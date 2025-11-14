import React, { useState, useEffect } from 'react';
import './App.css';
import CanvasRenderer from './components/CanvasRenderer';
import ReplayViewer from './components/ReplayViewer';

function App() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showViewer, setShowViewer] = useState(false);
  const [selectedReplay, setSelectedReplay] = useState(null);

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
          <button
            onClick={() => setShowViewer(!showViewer)}
            style={{ marginLeft: '10px' }}
          >
            {showViewer ? 'Hide' : 'Show'} Canvas Viewer
          </button>
        </section>

        {/* Test Replay Buttons */}
        <section style={{ marginTop: '20px', padding: '15px', backgroundColor: '#1a1a1a', borderRadius: '8px' }}>
          <h3 style={{ color: '#fff', marginTop: 0 }}>Load Test Replays:</h3>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={() => setSelectedReplay('test_strafing_maneuver')}
              style={{
                padding: '10px 15px',
                backgroundColor: selectedReplay === 'test_strafing_maneuver' ? '#4A90E2' : '#333',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Watch Strafing Maneuver
            </button>
            <button
              onClick={() => setSelectedReplay('test_retreat_coverage')}
              style={{
                padding: '10px 15px',
                backgroundColor: selectedReplay === 'test_retreat_coverage' ? '#4A90E2' : '#333',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Watch Retreat Coverage
            </button>
            <button
              onClick={() => setSelectedReplay('test_epic002_tactical_showcase')}
              style={{
                padding: '10px 15px',
                backgroundColor: selectedReplay === 'test_epic002_tactical_showcase' ? '#4A90E2' : '#333',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Watch Tactical Showcase
            </button>
            {selectedReplay && (
              <button
                onClick={() => setSelectedReplay(null)}
                style={{
                  padding: '10px 15px',
                  backgroundColor: '#E24A4A',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Close Replay
              </button>
            )}
          </div>
        </section>

        {/* Replay Viewer */}
        {selectedReplay && (
          <section style={{ marginTop: '20px' }}>
            <ReplayViewer matchId={selectedReplay} />
          </section>
        )}

        {/* Canvas Viewer (mock data) */}
        {showViewer && !selectedReplay && (
          <section style={{ marginTop: '20px' }}>
            <h2>Canvas Viewer (Mock Data)</h2>
            <CanvasRenderer width={1200} height={800} />
          </section>
        )}

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
