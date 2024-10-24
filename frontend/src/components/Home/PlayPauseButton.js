// a button responsible for starting and stopping the simulation
// PlayPauseButton only changes the STATE of whether the simulation is running, the logic for
// controlling the simulation occurs in the parent component, <Home />
import React from 'react';
import './PlayPauseButton.css';
import play_button from '../images/play_button.png';
import pause from '../images/pause.png';

const checkForScenario = () => {
  if (localStorage.length > 2) {
    return [false, false];
  }
  let parametersSet = false;
  let initialCasesSet = false;
  // check if user has set disease parameters
  localStorage.getItem('parameters') ? parametersSet = true : parametersSet = false;
  // check if user has set initial cases
  localStorage.getItem('initial_infected') ? (
    initialCasesSet = JSON.parse(localStorage.getItem('initial_infected')).length > 0
  ) : (
    initialCasesSet = false);
  console.log("parametersSet:", parametersSet);
  console.log("initialCasesSet:", initialCasesSet);
  return [parametersSet, initialCasesSet];
};

const PlayPauseButton = ({ isRunning, onToggle }) => {
  const hasSetParameters = checkForScenario();
  if (hasSetParameters[0] && hasSetParameters[1]) {
    return (
      <button className={isRunning ? "pause-button" : "scenario-button"} onClick={onToggle}>
        <img src={isRunning ? pause : play_button} alt={isRunning ? "Pause" : "Play"} className="icon" />
        {isRunning ? "Pause" : "Play"}
      </button>
    );
  } else {
    return (
      <button className="scenario-button-disabled">
        <img src={play_button} alt="Play button disabled, missing parameters" className="icon" />
        Play
      </button>
    )
  }
};
  
  export default PlayPauseButton;
