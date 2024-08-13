import React, { useState, useEffect, useRef } from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './TimelineSlider.css';

const TimelineSlider = ({ totalDays, selectedDay, onDayChange, onScenarioRun, onScenarioPause }) => {
    const handleChange = (value) => {
    onDayChange(value);
  };

  return (
    <div className="timeline-slider-wrapper">
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
