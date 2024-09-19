import React, { useState, useEffect } from 'react';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import './TimelineSlider.css';

const TimelineSlider = ({ totalDays, selectedDay, onDayChange, isRunning }) => {
  const [maxDay, setMaxDay] = useState(totalDays);

  useEffect(() => {
    setMaxDay(isRunning ? totalDays : selectedDay);
  }, [isRunning, selectedDay, totalDays]);

  const handleChange = (value) => {
    onDayChange(value);
  };

  return (
    <div className="timeline-container">
      <Slider
        min={0}
        max={maxDay}
        value={Math.min(selectedDay, maxDay)}
        onChange={handleChange}
        railStyle={{ backgroundColor: '#ccc' }}
        trackStyle={{ backgroundColor: '#007bff' }}
        handleStyle={{ borderColor: '#007bff' }}
      />
      <div className="timeline-slider">
        {Array.from({ length: maxDay + 1 }).map((_, index) => (
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
