import React from 'react';
import styles from './StateOverlay.module.css';

/**
 * Format an event for display
 * @param {Object} event - Event object
 * @returns {string} Formatted event string
 */
const formatEvent = (event) => {
  if (!event || !event.type) return 'Unknown event';

  switch (event.type) {
    case 'phaser_fired':
      return `${event.attacker || event.ship} fired ${event.config || 'phaser'} at ${event.target || 'target'} (${event.damage || 0} damage)`;

    case 'torpedo_launched':
      return `${event.ship || event.launcher} launched torpedo ${event.torpedo_id || ''}`;

    case 'torpedo_blast':
      return `Torpedo ${event.torpedo_id || ''} detonated (${event.damage || 0} damage, ${event.radius || 15} radius)`;

    case 'blast_zone_damage':
      return `${event.ship || 'Ship'} took ${event.damage || 0} damage from blast zone`;

    case 'ship_destroyed':
      return `${event.ship} was destroyed!`;

    case 'hit':
      return `${event.attacker} hit ${event.target || 'target'} for ${event.damage || 0} damage`;

    default:
      // Generic fallback
      if (event.message) return event.message;
      return `${event.type}: ${JSON.stringify(event)}`;
  }
};

/**
 * Ship stats component showing shields, AE, and phaser config
 * @param {Object} props - Component props
 * @param {Object} props.ship - Ship state object
 * @param {string} props.label - Ship label (e.g., "Ship A")
 * @param {string} props.shipId - Ship ID ('A' or 'B')
 * @param {string} props.model - Ship model name (optional)
 */
const ShipStats = ({ ship, label, shipId, model }) => {
  if (!ship) return null;

  const shields = ship.shields !== undefined ? ship.shields : 100;
  const ae = ship.ae !== undefined ? ship.ae : 100;
  const phaserConfig = ship.phaser_config || 'UNKNOWN';

  // Determine CSS classes based on values
  const shieldsClass = shields > 50 ? styles.shieldsHigh : shields > 25 ? styles.shieldsMedium : styles.shieldsLow;
  const aeClass = ae > 50 ? styles.aeHigh : ae > 25 ? styles.aeMedium : styles.aeLow;
  const phaserClass = phaserConfig === 'WIDE' ? styles.phaserWide : phaserConfig === 'FOCUSED' ? styles.phaserFocused : styles.phaserUnknown;
  const statsClass = shipId === 'A' ? styles.shipStatsA : styles.shipStatsB;
  const labelClass = shipId === 'A' ? styles.shipLabelA : styles.shipLabelB;

  return (
    <div className={statsClass}>
      <div className={labelClass}>
        {label}
      </div>
      {model && (
        <div className={styles.modelName}>
          {model}
        </div>
      )}
      <div className={styles.statRow}>
        <span className={styles.statLabel}>Shields:</span>{' '}
        <span className={shieldsClass}>
          {shields.toFixed(0)}%
        </span>
      </div>
      <div className={styles.statRow}>
        <span className={styles.statLabel}>AE:</span>{' '}
        <span className={aeClass}>
          {ae.toFixed(0)}
        </span>
      </div>
      <div className={styles.statRow}>
        <span className={styles.statLabel}>Phaser:</span>{' '}
        <span className={phaserClass}>
          {phaserConfig}
        </span>
      </div>
    </div>
  );
};

/**
 * State overlay component showing game state information
 * @param {Object} props - Component props
 * @param {Object} props.turnState - Current turn state
 * @param {number} props.turnNumber - Current turn number (0-indexed)
 * @param {number} props.maxTurns - Total number of turns
 * @param {Array} props.events - Events for current turn
 * @param {Object} props.matchInfo - Match information (optional)
 */
const StateOverlay = ({ turnState, turnNumber = 0, maxTurns = 1, events = [], matchInfo = null }) => {
  if (!turnState) return null;

  // Filter to recent/relevant events (last 5)
  const recentEvents = events.slice(-5);

  return (
    <div className={styles.container}>
      {/* Top row: Ship stats and turn counter */}
      <div className={styles.topRow}>
        {/* Ship A Stats */}
        <ShipStats
          ship={turnState.ship_a}
          label="Ship A"
          shipId="A"
          model={matchInfo?.model_a}
        />

        {/* Turn Counter */}
        <div className={styles.turnCounter}>
          <div className={styles.turnCounterText}>
            Turn {turnNumber + 1} / {maxTurns}
          </div>
          <div className={styles.matchId}>
            {matchInfo?.match_id && `Match: ${matchInfo.match_id}`}
          </div>
        </div>

        {/* Ship B Stats */}
        <ShipStats
          ship={turnState.ship_b}
          label="Ship B"
          shipId="B"
          model={matchInfo?.model_b}
        />
      </div>

      {/* Event log */}
      {recentEvents.length > 0 && (
        <div className={styles.eventLog}>
          <div className={styles.eventLogTitle}>
            Recent Events:
          </div>
          <ul className={styles.eventList}>
            {recentEvents.map((event, idx) => (
              <li key={idx} className={styles.eventItem}>
                {formatEvent(event)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Torpedo count (if present) */}
      {(turnState.torpedoes && turnState.torpedoes.length > 0) && (
        <div className={styles.torpedoCount}>
          <strong>Active Torpedoes:</strong> {turnState.torpedoes.length}
          <span className={styles.torpedoBreakdown}>
            Ship A: {turnState.torpedoes.filter(t => t.owner === 'ship_a').length} |{' '}
            Ship B: {turnState.torpedoes.filter(t => t.owner === 'ship_b').length}
          </span>
        </div>
      )}

      {/* Blast zones (if present) */}
      {(turnState.blast_zones && turnState.blast_zones.length > 0) && (
        <div className={styles.blastZones}>
          <strong>⚠ Active Blast Zones:</strong> {turnState.blast_zones.length}
        </div>
      )}
    </div>
  );
};

export default StateOverlay;
