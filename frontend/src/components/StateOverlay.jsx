import React from 'react';

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
 * @param {string} props.color - Ship color for border
 * @param {string} props.model - Ship model name (optional)
 */
const ShipStats = ({ ship, label, color, model }) => {
  if (!ship) return null;

  const shields = ship.shields !== undefined ? ship.shields : 100;
  const ae = ship.ae !== undefined ? ship.ae : 100;
  const phaserConfig = ship.phaser_config || 'UNKNOWN';

  return (
    <div style={{
      borderLeft: `4px solid ${color}`,
      paddingLeft: '12px',
      minWidth: '180px'
    }}>
      <div style={{
        fontWeight: 'bold',
        fontSize: '16px',
        marginBottom: '8px',
        color: color
      }}>
        {label}
      </div>
      {model && (
        <div style={{
          fontSize: '12px',
          color: '#888',
          marginBottom: '8px'
        }}>
          {model}
        </div>
      )}
      <div style={{ fontSize: '14px', marginBottom: '4px' }}>
        <span style={{ color: '#aaa' }}>Shields:</span>{' '}
        <span style={{ color: shields > 50 ? '#0f0' : shields > 25 ? '#ff0' : '#f00', fontWeight: 'bold' }}>
          {shields.toFixed(0)}%
        </span>
      </div>
      <div style={{ fontSize: '14px', marginBottom: '4px' }}>
        <span style={{ color: '#aaa' }}>AE:</span>{' '}
        <span style={{ color: ae > 50 ? '#0ff' : ae > 25 ? '#ff0' : '#f00', fontWeight: 'bold' }}>
          {ae.toFixed(0)}
        </span>
      </div>
      <div style={{ fontSize: '14px' }}>
        <span style={{ color: '#aaa' }}>Phaser:</span>{' '}
        <span style={{
          color: phaserConfig === 'WIDE' ? '#0f0' : phaserConfig === 'FOCUSED' ? '#0ff' : '#888',
          fontWeight: 'bold'
        }}>
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
    <div style={{
      marginTop: '10px',
      padding: '15px',
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      color: '#fff'
    }}>
      {/* Top row: Ship stats and turn counter */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '15px'
      }}>
        {/* Ship A Stats */}
        <ShipStats
          ship={turnState.ship_a}
          label="Ship A"
          color="#4A90E2"
          model={matchInfo?.model_a}
        />

        {/* Turn Counter */}
        <div style={{
          textAlign: 'center',
          padding: '0 20px',
          minWidth: '150px'
        }}>
          <div style={{
            fontSize: '18px',
            fontWeight: 'bold',
            marginBottom: '5px'
          }}>
            Turn {turnNumber + 1} / {maxTurns}
          </div>
          <div style={{
            fontSize: '12px',
            color: '#888'
          }}>
            {matchInfo?.match_id && `Match: ${matchInfo.match_id}`}
          </div>
        </div>

        {/* Ship B Stats */}
        <ShipStats
          ship={turnState.ship_b}
          label="Ship B"
          color="#E24A4A"
          model={matchInfo?.model_b}
        />
      </div>

      {/* Event log */}
      {recentEvents.length > 0 && (
        <div style={{
          marginTop: '15px',
          paddingTop: '15px',
          borderTop: '1px solid #333'
        }}>
          <div style={{
            fontWeight: 'bold',
            fontSize: '14px',
            marginBottom: '8px',
            color: '#aaa'
          }}>
            Recent Events:
          </div>
          <ul style={{
            margin: 0,
            paddingLeft: '20px',
            fontSize: '13px',
            color: '#ccc'
          }}>
            {recentEvents.map((event, idx) => (
              <li key={idx} style={{ marginBottom: '4px' }}>
                {formatEvent(event)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Torpedo count (if present) */}
      {(turnState.torpedoes && turnState.torpedoes.length > 0) && (
        <div style={{
          marginTop: '10px',
          paddingTop: '10px',
          borderTop: '1px solid #333',
          fontSize: '13px',
          color: '#aaa'
        }}>
          <strong>Active Torpedoes:</strong> {turnState.torpedoes.length}
          <span style={{ marginLeft: '15px' }}>
            Ship A: {turnState.torpedoes.filter(t => t.owner === 'ship_a').length} |{' '}
            Ship B: {turnState.torpedoes.filter(t => t.owner === 'ship_b').length}
          </span>
        </div>
      )}

      {/* Blast zones (if present) */}
      {(turnState.blast_zones && turnState.blast_zones.length > 0) && (
        <div style={{
          marginTop: '5px',
          fontSize: '13px',
          color: '#ff6600'
        }}>
          <strong>⚠ Active Blast Zones:</strong> {turnState.blast_zones.length}
        </div>
      )}
    </div>
  );
};

export default StateOverlay;
