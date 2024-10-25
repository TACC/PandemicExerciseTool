// a button responsible for starting and stopping the simulation
// PlayPauseButton only changes the STATE of whether the simulation is running, the logic for
// controlling the simulation occurs in the parent component, <Home />
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
