import React from 'react';
import PropTypes from 'prop-types';

/**
 * ThinkingPanel - Displays AI thinking tokens side-by-side
 *
 * @param {string} thinkingA - Ship A's thinking tokens for current turn
 * @param {string} thinkingB - Ship B's thinking tokens for current turn
 * @param {number} turnNumber - Current turn number (0-indexed)
 * @param {string} modelA - Model name for Ship A (e.g., "gpt-4")
 * @param {string} modelB - Model name for Ship B (e.g., "claude-3-haiku")
 * @param {boolean} isVisible - Whether panel is visible (controlled)
 * @param {string} [previousThinkingA] - Previous turn thinking (for future diff highlighting)
 * @param {string} [previousThinkingB] - Previous turn thinking (for future diff highlighting)
 */
const ThinkingPanel = ({
  thinkingA,
  thinkingB,
  turnNumber,
  modelA,
  modelB,
  isVisible = true,
  previousThinkingA = null,
  previousThinkingB = null
}) => {
  // Don't render if not visible
  if (!isVisible) {
    return null;
  }

  // Helper to format thinking text (handle null/empty)
  const formatThinking = (thinking) => {
    if (!thinking || thinking.trim() === '') {
      return '(No thinking tokens available for this turn)';
    }
    return thinking;
  };

  return (
    <div className="thinking-panel">
      {/* Panel Header */}
      <div className="thinking-panel-header">
        <h3>AI Thinking Tokens — Turn {turnNumber + 1}</h3>
      </div>

      {/* Split Screen Layout */}
      <div className="thinking-panel-content">
        {/* Ship A Thinking */}
        <div className="thinking-section thinking-section-a">
          <div className="thinking-header">
            <span className="ship-label">Ship A</span>
            <span className="model-name">{modelA}</span>
          </div>
          <div className="thinking-text">
            <pre>{formatThinking(thinkingA)}</pre>
          </div>
        </div>

        {/* Divider */}
        <div className="thinking-divider" />

        {/* Ship B Thinking */}
        <div className="thinking-section thinking-section-b">
          <div className="thinking-header">
            <span className="ship-label">Ship B</span>
            <span className="model-name">{modelB}</span>
          </div>
          <div className="thinking-text">
            <pre>{formatThinking(thinkingB)}</pre>
          </div>
        </div>
      </div>
    </div>
  );
};

ThinkingPanel.propTypes = {
  thinkingA: PropTypes.string,
  thinkingB: PropTypes.string,
  turnNumber: PropTypes.number.isRequired,
  modelA: PropTypes.string.isRequired,
  modelB: PropTypes.string.isRequired,
  isVisible: PropTypes.bool,
  previousThinkingA: PropTypes.string,
  previousThinkingB: PropTypes.string
};

export default React.memo(ThinkingPanel);
