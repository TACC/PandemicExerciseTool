import React, { useState, useEffect, useRef } from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './TimelineSlider.css';
import play_button from './images/play_button.png';
import pause from './images/pause.png';

const TimelineSlider = ({ totalDays, selectedDay, onDayChange, onScenarioRun, onScenarioPause }) => {
  const [isRunning, setIsRunning] = useState(false);

  const handleRunScenario = () => {
    setIsRunning(true);
    onScenarioRun();
  };

  const handlePauseScenario = () => {
    setIsRunning(false);
    onScenarioPause();
  };

  const handleChange = (value) => {
    onDayChange(value);
  };

  return (
    <div className="timeline-slider-wrapper">
      <div className="button-container">
        <button className="scenario-button" onClick={handleRunScenario} disabled={isRunning}>
          <img src={play_button} alt="Play" className="icon" />
          Run Scenario
        </button>
        <button className="pause-button" onClick={handlePauseScenario} disabled={!isRunning}>
          <img src={pause} alt="Pause" className="icon" />
          Pause
        </button>
      </div>
      <div className="timeline-container">
        <Slider
          min={0}
          max={selectedDay}
          value={Math.min(selectedDay, totalDays - 1)}
          onChange={handleChange}
          railStyle={{ backgroundColor: '#ccc' }}
          trackStyle={{ backgroundColor: '#007bff' }}
          handleStyle={{ borderColor: '#007bff' }}
        />
        <div className="timeline-slider">
          {Array.from({ length: selectedDay + 1 }).map((_, index) => (
            <div
              key={index}
              className={`timeline-item ${index === selectedDay ? 'active' : ''}`}
              onClick={() => onDayChange(index)}
            >
              <span className="timeline-date">{index}</span>
            </div>
           ))}
          </div>
      </div>
    </div>
  );
};

export default TimelineSlider;
