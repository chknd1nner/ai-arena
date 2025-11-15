import React from 'react';
import { useReplayData } from '../hooks/useReplayData';
import { usePlaybackControls } from '../hooks/usePlaybackControls';
import CanvasRenderer from './CanvasRenderer';
import PlaybackControls from './PlaybackControls';
import StateOverlay from './StateOverlay';

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

  // Keyboard shortcuts
  React.useEffect(() => {
    const handleKeyPress = (e) => {
      // Ignore if user is typing in an input field
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
        return;
      }

      switch (e.key) {
        case ' ':
          e.preventDefault(); // Prevent page scroll
          togglePlayPause();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          jumpToTurn(Math.max(0, currentTurnIndex - 1));
          break;
        case 'ArrowRight':
          e.preventDefault();
          jumpToTurn(Math.min(totalTurns - 1, currentTurnIndex + 1));
          break;
        case 'Home':
          e.preventDefault();
          jumpToTurn(0);
          break;
        case 'End':
          e.preventDefault();
          jumpToTurn(totalTurns - 1);
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [currentTurnIndex, totalTurns, togglePlayPause, jumpToTurn]);

  // Handle loading state
  if (loading) {
    return (
      <div style={{
        padding: '40px',
        textAlign: 'center',
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        margin: '20px'
      }}>
        <div style={{
          display: 'inline-block',
          width: '40px',
          height: '40px',
          border: '4px solid #333',
          borderTop: '4px solid #4A90E2',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '15px'
        }}></div>
        <p style={{ color: '#aaa', fontSize: '16px' }}>Loading replay...</p>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div style={{
        padding: '30px',
        textAlign: 'center',
        backgroundColor: '#2a1a1a',
        borderRadius: '8px',
        border: '2px solid #ff4444',
        margin: '20px'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '10px' }}>⚠️</div>
        <h3 style={{ color: '#ff4444', margin: '0 0 10px 0' }}>Failed to Load Replay</h3>
        <p style={{ color: '#ffaaaa', fontSize: '14px', marginBottom: '15px' }}>{error}</p>
        <p style={{ color: '#888', fontSize: '12px' }}>
          Please check your network connection and try again.
        </p>
      </div>
    );
  }

  // Handle no replay
  if (!replay) {
    return (
      <div style={{
        padding: '30px',
        textAlign: 'center',
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        margin: '20px'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '10px' }}>📁</div>
        <p style={{ color: '#888', fontSize: '16px' }}>No replay selected</p>
        <p style={{ color: '#666', fontSize: '14px' }}>Select a replay from the dropdown above</p>
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
          events={currentTurn?.events || []}
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

      {/* Keyboard Shortcuts Help */}
      <div style={{
        marginBottom: '20px',
        padding: '12px 15px',
        backgroundColor: '#1a1a1a',
        borderRadius: '8px',
        fontSize: '12px',
        color: '#888'
      }}>
        <strong style={{ color: '#aaa' }}>Keyboard Shortcuts:</strong>
        {' '}
        <span style={{ color: '#4A90E2' }}>Space</span> = Play/Pause
        {' • '}
        <span style={{ color: '#4A90E2' }}>← →</span> = Previous/Next Turn
        {' • '}
        <span style={{ color: '#4A90E2' }}>Home/End</span> = First/Last Turn
      </div>

      {/* State Overlay - Shows ship stats, events, and game state */}
      <StateOverlay
        turnState={currentTurn?.state}
        turnNumber={currentTurnIndex}
        maxTurns={totalTurns}
        events={currentTurn?.events || []}
        matchInfo={{
          match_id: replay.match_id,
          model_a: replay.model_a,
          model_b: replay.model_b,
          winner: replay.winner
        }}
      />
    </div>
  );
};

export default ReplayViewer;
