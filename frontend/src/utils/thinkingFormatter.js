/**
 * Thinking token formatting and highlighting utilities
 */

/**
 * Format thinking tokens for display
 * - Trim excess whitespace
 * - Preserve line breaks
 * - Handle empty/null gracefully
 */
export function formatThinking(thinking) {
  if (!thinking || thinking.trim() === '') {
    return '(No thinking tokens available for this turn)';
  }

  // Trim leading/trailing whitespace but preserve internal line breaks
  return thinking.trim();
}

/**
 * Detect if thinking token has structured format (e.g., JSON-like)
 */
export function hasStructuredFormat(thinking) {
  if (!thinking) return false;

  // Check for common structured patterns
  const jsonPattern = /^\s*\{.*\}\s*$/s;
  const listPattern = /^(\s*[-*•]\s+.+\n?)+$/m;
  const sectionPattern = /^.+:\n(\s+.+\n?)+$/m;

  return jsonPattern.test(thinking) ||
         listPattern.test(thinking) ||
         sectionPattern.test(thinking);
}

/**
 * Simple syntax highlighting for structured thinking
 * Returns array of {text, className} objects
 */
export function highlightSyntax(thinking) {
  if (!thinking) return [{ text: '', className: '' }];

  // For now, just highlight key phrases
  // Future: Full markdown/JSON syntax highlighting
  const keyPhrases = [
    { pattern: /\b(Distance|Range|Position|Heading|Velocity)\b/g, className: 'syntax-metric' },
    { pattern: /\b(FORWARD|BACKWARD|LEFT|RIGHT|STOP|HARD_LEFT|HARD_RIGHT|SOFT_LEFT|SOFT_RIGHT)\b/g, className: 'syntax-movement' },
    { pattern: /\b(WIDE|FOCUSED)\b/g, className: 'syntax-weapon' },
    { pattern: /\b(torpedo|phaser|blast zone)\b/gi, className: 'syntax-weapon-type' },
    { pattern: /\b(\d+\.?\d*)\s*(units?|seconds?|AE|damage)\b/g, className: 'syntax-number' }
  ];

  // Simple implementation: return original text
  // Future: Implement proper syntax highlighting
  return [{ text: thinking, className: 'thinking-text-content' }];
}

/**
 * Calculate diff between current and previous thinking
 * Returns array of {text, type: 'added'|'removed'|'unchanged'}
 */
export function calculateDiff(currentThinking, previousThinking) {
  if (!currentThinking && !previousThinking) {
    return [];
  }

  if (!previousThinking) {
    return [{ text: currentThinking, type: 'added' }];
  }

  if (!currentThinking) {
    return [{ text: previousThinking, type: 'removed' }];
  }

  // Simple implementation: check if identical
  if (currentThinking === previousThinking) {
    return [{ text: currentThinking, type: 'unchanged' }];
  }

  // For now, just show as changed
  // Future: Use proper diff algorithm (e.g., Myers diff)
  return [
    { text: previousThinking, type: 'removed' },
    { text: currentThinking, type: 'added' }
  ];
}

/**
 * Truncate thinking for preview (e.g., in match summary)
 */
export function truncateThinking(thinking, maxLength = 200) {
  if (!thinking || thinking.length <= maxLength) {
    return thinking;
  }

  return thinking.substring(0, maxLength) + '...';
}
