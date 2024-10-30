// a button responsible for starting and stopping the simulation
// PlayPauseButton only changes the STATE of whether the simulation is running, the logic for
// controlling the simulation occurs in the parent component, <Home />
// NOTE: passing shouldNotify props from Home.js to StartNotification.js is fine for now,
// but any further prop drilling makes the code hard to maintain. Consider using Contexts
// for any deeper prop passes
import React from 'react';
import './PlayPauseButton.css';
import play_button from '../images/play_button.png';
import pause from '../images/pause.png';
import StartNotification from './StartNotification';

const checkForScenario = () => {
  if (localStorage.length < 2) {
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
  return [parametersSet, initialCasesSet];
};

const PlayPauseButton = ({ isRunning, onToggle, shouldNotify, changeNotify }) => {
  const [parametersSet, initialCasesSet]= checkForScenario();

  if (parametersSet && initialCasesSet) {
    return (
      <div>
        <StartNotification isRunning={isRunning} shouldNotify={shouldNotify} changeNotify={changeNotify} />
        <button className={isRunning ? "pause-button" : "scenario-button"} onClick={onToggle}>
          <img src={isRunning ? pause : play_button} alt={isRunning ? "Pause" : "Play"} className="icon" />
          {isRunning ? "Pause" : "Play"}
        </button>
      </div>
    )
  } else {
    return (
      <>
      <button className="scenario-button-disabled">
        <span className="tooltips-text">Scenario parameters and initial cases are required to run a simulation</span>
        <img src={play_button} alt="Play button disabled, missing parameters" className="icon" />
        Play
      </button>
      </>
    )
  }
};
  
  export default PlayPauseButton;
