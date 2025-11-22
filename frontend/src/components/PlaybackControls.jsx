import React from 'react';
import styles from './PlaybackControls.module.css';

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
    <div className={styles.container}>
      {/* Top Row: Play/Pause and Speed Controls */}
      <div className={styles.topRow}>
        {/* Play/Pause Button */}
        <button
          onClick={onTogglePlayPause}
          title={playing ? 'Pause replay (Space)' : 'Play replay (Space)'}
          className={`${styles.playPauseButton} ${playing ? styles.playing : styles.paused}`}
        >
          {playing ? '⏸ Pause' : '▶ Play'}
        </button>

        {/* Speed Controls */}
        <div className={styles.speedControls}>
          <span className={styles.speedLabel}>Speed:</span>
          {speedOptions.map(speedOption => (
            <button
              key={speedOption}
              onClick={() => onChangeSpeed(speedOption)}
              title={`Set playback speed to ${speedOption}x`}
              className={`${styles.speedButton} ${speed === speedOption ? styles.active : styles.inactive}`}
            >
              {speedOption}x
            </button>
          ))}
        </div>
      </div>

      {/* Timeline Scrubber */}
      <div className={styles.timeline}>
        <div className={styles.timelineHeader}>
          <span className={styles.turnLabel}>Turn:</span>
          <span className={styles.turnCounter}>
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
          title="Scrub through replay timeline (← → arrow keys)"
          className={styles.slider}
        />

        {/* Progress Bar Visuals */}
        <div className={styles.progressBarContainer}>
          <div
            className={styles.progressBarFill}
            style={{ width: `${((currentTurn + 1) / maxTurns) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default PlaybackControls;
