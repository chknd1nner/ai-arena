import React from 'react';
import { useReplayData } from '../hooks/useReplayData';
import { usePlaybackControls } from '../hooks/usePlaybackControls';
import CanvasRenderer from './CanvasRenderer';
import PlaybackControls from './PlaybackControls';

const ReplayViewer = ({ matchId }) => {
  const { replay, loading, error } = useReplayData(matchId);

  // Initialize playback controls hook BEFORE conditional returns
  // Use 1 as default to avoid errors when replay is not loaded
  const totalTurns = replay?.turns?.length || 1;
  const {
    playing,
    speed,
    currentTurn: currentTurnIndex,
    togglePlayPause,
    changeSpeed,
    jumpToTurn
  } = usePlaybackControls(totalTurns);

  // Handle loading state
  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#fff' }}>
        <p>Loading replay...</p>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#ff4444' }}>
        <p>Error: {error}</p>
      </div>
    );
  }

  // Handle no replay
  if (!replay) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
        <p>No replay loaded</p>
      </div>
    );
  }

  const currentTurn = replay.turns[currentTurnIndex];

  return (
    <div style={{ width: '100%', padding: '20px' }}>
      {/* Match Info Header */}
      <div style={{
        marginBottom: '20px',
        padding: '15px',
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        color: '#fff'
      }}>
        <h3 style={{ margin: '0 0 10px 0' }}>
          Match: {replay.match_id}
        </h3>
        <div style={{ display: 'flex', gap: '30px', fontSize: '14px', color: '#aaa' }}>
          <div>
            <span style={{ color: '#4A90E2', fontWeight: 'bold' }}>Ship A:</span> {replay.model_a}
          </div>
          <div>
            <span style={{ color: '#E24A4A', fontWeight: 'bold' }}>Ship B:</span> {replay.model_b}
          </div>
        </div>
      </div>

      {/* Canvas Renderer */}
      <div style={{ marginBottom: '20px' }}>
        <CanvasRenderer
          width={1200}
          height={800}
          turnState={currentTurn?.state}
        />
      </div>

      {/* Playback Controls */}
      <div style={{ marginBottom: '20px' }}>
        <PlaybackControls
          playing={playing}
          speed={speed}
          currentTurn={currentTurnIndex}
          maxTurns={totalTurns}
          onTogglePlayPause={togglePlayPause}
          onChangeSpeed={changeSpeed}
          onJumpToTurn={jumpToTurn}
        />
      </div>

      {/* Turn Events */}
      {currentTurn?.events && currentTurn.events.length > 0 && (
        <div style={{
          padding: '15px',
          backgroundColor: '#1a1a1a',
          borderRadius: '8px',
          color: '#fff'
        }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#aaa' }}>Turn Events:</h4>
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {currentTurn.events.map((event, idx) => (
              <li key={idx} style={{ marginBottom: '5px', fontSize: '14px' }}>
                <span style={{ color: '#ffaa00', fontWeight: 'bold' }}>{event.type}</span>
                {event.attacker && ` - Attacker: ${event.attacker}`}
                {event.damage && ` - Damage: ${event.damage}`}
                {event.message && ` - ${event.message}`}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ReplayViewer;
