// the timeline slider automatically updates with each new simulation day from the backend
// rendered at the middle-bottom of Home view below <LineChart />
import React, { useState, useEffect } from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './TimelineSlider.css';

const TimelineSlider = ({ totalDays, selectedDay, onDayChange, isRunning }) => {
  const handleChange = (value) => {
    onDayChange(value);
  };

  const stepForLabels = totalDays > 50 ? 5 : 1;

  return (
    <div className="timeline-container">
      {/* Slider with a step of 1 for precise dragging */}
      <Slider
        min={0}
        max={totalDays}
        step={1} 
        value={selectedDay}
        onChange={handleChange}
        railStyle={{ backgroundColor: '#ccc' }}
        trackStyle={{ backgroundColor: '#007bff' }}
        handleStyle={{ borderColor: '#007bff' }}
        disabled={isRunning}
      />
      <div className="timeline-slider">
        {Array.from({ length: Math.floor(totalDays / stepForLabels) + 1 }).map((_, index) => {
          const day = index * stepForLabels;
          return (
            <div
              key={day}
              className={`timeline-item ${day === selectedDay ? 'active' : ''}`}
              onClick={() => handleChange(day)}
            >
              <span className="timeline-date">{day}</span>
            </div>
          );
        })}
      </div>
      <h6 className='timeline-title'>Days</h6>
    </div>
  );
};

export default React.memo(TimelineSlider);
