import React from 'react';
import './PlayPauseButton.css';
import play_button from '../images/play_button.png';
import pause from '../images/pause.png';

const PlayPauseButton = ({ isRunning, onToggle }) => {
    return (
      <button className={isRunning ? "pause-button" : "scenario-button"} onClick={onToggle}>
        <img src={isRunning ? pause : play_button} alt={isRunning ? "Pause" : "Play"} className="icon" />
        {isRunning ? "Pause" : "Play"}
      </button>
    );
  };
  
  export default PlayPauseButton;
