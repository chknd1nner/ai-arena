import React from 'react';
import PropTypes from 'prop-types';
import { truncateThinking } from '../utils/thinkingFormatter';

/**
 * MatchSummary - Displays compelling end-of-match summary
 */
const MatchSummary = ({
  matchInfo,
  totalTurns,
  finalTurn,
  onWatchAgain
}) => {
  if (!matchInfo || !finalTurn) return null;

  const winner = matchInfo.winner;
  const winnerShip = winner === 'ship_a' ? 'Ship A' : 'Ship B';
  const winnerModel = winner === 'ship_a' ? matchInfo.model_a : matchInfo.model_b;
  const winnerColor = winner === 'ship_a' ? '#4A90E2' : '#E24A4A';

  // Extract final thinking tokens
  const finalThinkingA = truncateThinking(finalTurn.thinking_a, 300);
  const finalThinkingB = truncateThinking(finalTurn.thinking_b, 300);

  return (
    <div className="match-summary">
      {/* Winner Announcement */}
      <div className="match-summary-header">
        <div className="victory-icon">🏆</div>
        <h1 style={{ color: winnerColor }}>
          {winnerShip} Wins!
        </h1>
        <div className="winner-model">{winnerModel}</div>
      </div>

      {/* Match Statistics */}
      <div className="match-stats">
        <div className="stat">
          <span className="stat-label">Total Turns</span>
          <span className="stat-value">{totalTurns}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Match ID</span>
          <span className="stat-value">{matchInfo.match_id}</span>
        </div>
      </div>

      {/* Final Thinking Tokens */}
      <div className="final-thinking">
        <h3>Final Thoughts</h3>
        <div className="final-thinking-content">
          <div className="final-thinking-ship">
            <div className="final-thinking-header" style={{ borderColor: '#4A90E2' }}>
              Ship A's Final Turn
            </div>
            <div className="final-thinking-text">
              {finalThinkingA || '(No thinking available)'}
            </div>
          </div>
          <div className="final-thinking-ship">
            <div className="final-thinking-header" style={{ borderColor: '#E24A4A' }}>
              Ship B's Final Turn
            </div>
            <div className="final-thinking-text">
              {finalThinkingB || '(No thinking available)'}
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="match-summary-actions">
        <button onClick={onWatchAgain} className="btn-primary">
          ▶️ Watch Again
        </button>
        <button onClick={() => window.location.reload()} className="btn-secondary">
          🏠 Back to Matches
        </button>
      </div>
    </div>
  );
};

MatchSummary.propTypes = {
  matchInfo: PropTypes.shape({
    match_id: PropTypes.string.isRequired,
    model_a: PropTypes.string.isRequired,
    model_b: PropTypes.string.isRequired,
    winner: PropTypes.string.isRequired
  }).isRequired,
  totalTurns: PropTypes.number.isRequired,
  finalTurn: PropTypes.object,
  onWatchAgain: PropTypes.func.isRequired
};

export default MatchSummary;
