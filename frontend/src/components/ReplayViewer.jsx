import React from 'react';
import { useReplayData } from '../hooks/useReplayData';
import { usePlaybackControls } from '../hooks/usePlaybackControls';
import CanvasRenderer from './CanvasRenderer';
import PlaybackControls from './PlaybackControls';
import StateOverlay from './StateOverlay';
import ThinkingPanel from './ThinkingPanel';
import MatchSummary from './MatchSummary';
import styles from './ReplayViewer.module.css';

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
    jumpToTurn,
    reset
  } = usePlaybackControls(totalTurns);

  // Thinking panel visibility toggle (default: visible)
  const [showThinking, setShowThinking] = React.useState(true);

  // Match summary state
  const [showSummary, setShowSummary] = React.useState(false);
  const isMatchComplete = currentTurnIndex === totalTurns - 1;

  // Show summary when reaching final turn
  React.useEffect(() => {
    if (isMatchComplete && !playing) {
      const timer = setTimeout(() => setShowSummary(true), 1000);
      return () => clearTimeout(timer);
    } else {
      setShowSummary(false);
    }
  }, [isMatchComplete, playing]);

  // Reset playback controls when matchId changes
  React.useEffect(() => {
    reset();
  }, [matchId, reset]);

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
        case 't':
        case 'T':
          e.preventDefault();
          setShowThinking(prev => !prev);
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
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
        <p className={styles.loadingText}>Loading replay...</p>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className={styles.errorIcon}>⚠️</div>
        <h3 className={styles.errorTitle}>Failed to Load Replay</h3>
        <p className={styles.errorMessage}>{error}</p>
        <p className={styles.errorHint}>
          Please check your network connection and try again.
        </p>
      </div>
    );
  }

  // Handle no replay
  if (!replay) {
    return (
      <div className={styles.noReplayContainer}>
        <div className={styles.noReplayIcon}>📁</div>
        <p className={styles.noReplayText}>No replay selected</p>
        <p className={styles.noReplayHint}>Select a replay from the dropdown above</p>
      </div>
    );
  }

  const currentTurn = replay.turns[currentTurnIndex];
  const previousTurn = currentTurnIndex > 0 ? replay.turns[currentTurnIndex - 1] : null;

  // Extract thinking tokens
  const thinkingA = currentTurn?.thinking_a || '';
  const thinkingB = currentTurn?.thinking_b || '';
  const prevThinkingA = previousTurn?.thinking_a || '';
  const prevThinkingB = previousTurn?.thinking_b || '';

  // Extract model names (handle both old and new replay formats)
  const modelA = replay.model_a || replay.models?.ship_a || 'Unknown Model A';
  const modelB = replay.model_b || replay.models?.ship_b || 'Unknown Model B';

  return (
    <div className={styles.container}>
      {/* Match Summary - Shows at end of match */}
      {showSummary && (
        <MatchSummary
          matchInfo={{
            match_id: replay.match_id,
            model_a: modelA,
            model_b: modelB,
            winner: replay.winner
          }}
          totalTurns={totalTurns}
          finalTurn={currentTurn}
          onWatchAgain={() => {
            setShowSummary(false);
            jumpToTurn(0);
          }}
        />
      )}

      {/* Match Info Header */}
      <div className={styles.matchHeader}>
        <div className={styles.matchInfo}>
          <h3>Match: {replay.match_id}</h3>
          <div className={styles.matchModels}>
            <div>
              <span className={styles.shipLabelA}>Ship A:</span> {modelA}
            </div>
            <div>
              <span className={styles.shipLabelB}>Ship B:</span> {modelB}
            </div>
          </div>
        </div>
        {/* Toggle Thinking Button */}
        <button
          onClick={() => setShowThinking(!showThinking)}
          className={`${styles.toggleThinkingButton} ${showThinking ? styles.active : styles.inactive}`}
          title="Toggle thinking tokens (T key)"
        >
          {showThinking ? '🧠 Hide Thinking' : '🧠 Show Thinking'}
        </button>
      </div>

      {/* Thinking Panel */}
      <ThinkingPanel
        thinkingA={thinkingA}
        thinkingB={thinkingB}
        turnNumber={currentTurnIndex}
        modelA={modelA}
        modelB={modelB}
        isVisible={showThinking}
        previousThinkingA={prevThinkingA}
        previousThinkingB={prevThinkingB}
      />

      {/* Canvas Renderer */}
      <div className={styles.canvasContainer}>
        <CanvasRenderer
          width={1200}
          height={800}
          turnState={currentTurn?.state}
          events={currentTurn?.events || []}
        />
      </div>

      {/* Playback Controls */}
      <div className={styles.controlsContainer}>
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
      <div className={styles.keyboardHelp}>
        <strong>Keyboard Shortcuts:</strong>
        {' '}
        <span className={styles.shortcutKey}>Space</span> = Play/Pause
        {' • '}
        <span className={styles.shortcutKey}>← →</span> = Previous/Next Turn
        {' • '}
        <span className={styles.shortcutKey}>Home/End</span> = First/Last Turn
        {' • '}
        <span className={styles.shortcutKey}>T</span> = Toggle Thinking
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
