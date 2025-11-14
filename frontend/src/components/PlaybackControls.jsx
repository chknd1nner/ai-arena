import React from 'react';

const PlaybackControls = ({
  playing,
  speed,
  currentTurn,
  maxTurns,
  onTogglePlayPause,
  onChangeSpeed,
  onJumpToTurn
}) => {
  const speedOptions = [0.5, 1, 2, 4];

  const handleSliderChange = (e) => {
    const turnIndex = parseInt(e.target.value, 10);
    onJumpToTurn(turnIndex);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '15px',
      padding: '20px',
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      color: '#fff'
    }}>
      {/* Top Row: Play/Pause and Speed Controls */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '20px'
      }}>
        {/* Play/Pause Button */}
        <button
          onClick={onTogglePlayPause}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: 'bold',
            backgroundColor: playing ? '#E24A4A' : '#4CAF50',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            minWidth: '100px'
          }}
        >
          {playing ? '⏸ Pause' : '▶ Play'}
        </button>

        {/* Speed Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '14px', color: '#aaa' }}>Speed:</span>
          {speedOptions.map(speedOption => (
            <button
              key={speedOption}
              onClick={() => onChangeSpeed(speedOption)}
              style={{
                padding: '8px 12px',
                fontSize: '14px',
                backgroundColor: speed === speedOption ? '#4A90E2' : '#333',
                color: '#fff',
                border: speed === speedOption ? '2px solid #4A90E2' : '2px solid #333',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: speed === speedOption ? 'bold' : 'normal'
              }}
            >
              {speedOption}x
            </button>
          ))}
        </div>
      </div>

      {/* Timeline Scrubber */}
      <div style={{ width: '100%' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '8px'
        }}>
          <span style={{ fontSize: '14px', color: '#aaa' }}>Turn:</span>
          <span style={{ fontSize: '16px', fontWeight: 'bold' }}>
            {currentTurn + 1} / {maxTurns}
          </span>
        </div>

        {/* Slider */}
        <input
          type="range"
          min="0"
          max={maxTurns - 1}
          value={currentTurn}
          onChange={handleSliderChange}
          style={{
            width: '100%',
            height: '8px',
            borderRadius: '4px',
            outline: 'none',
            cursor: 'pointer',
            accentColor: '#4A90E2'
          }}
        />

        {/* Progress Bar Visuals */}
        <div style={{
          width: '100%',
          height: '4px',
          backgroundColor: '#333',
          borderRadius: '2px',
          marginTop: '8px',
          overflow: 'hidden'
        }}>
          <div style={{
            width: `${((currentTurn + 1) / maxTurns) * 100}%`,
            height: '100%',
            backgroundColor: '#4A90E2',
            transition: 'width 0.2s ease'
          }} />
        </div>
      </div>
    </div>
  );
};

export default PlaybackControls;
