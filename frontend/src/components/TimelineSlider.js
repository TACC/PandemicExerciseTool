import React, { useState, useEffect } from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './TimelineSlider.css';

const TimelineSlider = ({ totalDays, selectedDay, onDayChange, isRunning }) => {
  
  const handleChange = (value) => {
    onDayChange(value);
  };

  return (
    <div className="timeline-container">
      <Slider
        min={0}
        max={totalDays}
        value={selectedDay}
        onChange={handleChange}
        railStyle={{ backgroundColor: '#ccc' }}
        trackStyle={{ backgroundColor: '#007bff' }}
        handleStyle={{ borderColor: '#007bff' }}
        disabled={isRunning}
      />
      <div className="timeline-slider">
        {Array.from({ length: totalDays + 1}).map((_, index) => (
          <div
            key={index}
            className={`timeline-item ${index === selectedDay ? 'active' : ''}`}
            onClick={() => handleChange(index)}
          >
            <span className="timeline-date">{index}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default React.memo(TimelineSlider);
