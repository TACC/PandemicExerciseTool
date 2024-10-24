// Provides a resizable grid layout that allows users to resize components
// NOTE: still in development
import React, { useState, useEffect, useRef } from 'react';
import texasCounties from '../../data/texasCounties';
import TimelineSlider from '../Home/TimelineSlider';
import SetScenario from '../Home/SetScenario';
import Interventions from '../Home/Interventions';
import './ChartView.css';
import { Responsive, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import PlayPauseButton from '../Home/PlayPauseButton';
import '../Home/leaflet-overrides.css';
// import './left-panel.css';


const ResponsiveGridLayout = WidthProvider(Responsive);
const layout = [
  { i: 'timeline', x: 0, y: 5, w: 8, h: 3 },
  { i: 'chart', x: 0, y: 0, w: 8, h: 5 },
  { i: 'map', x: 0, y: 8, w: 5, h: 13 },
  { i: 'table', x: 8, y: 0, w: 3, h: 24 },
];

const ChartView = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [eventData, setEventData] = useState([]);
  const [outputFiles] = useState([
    OUTPUT_0
  ]);
  const intervalRef = useRef(null);

  const [isRunning, setIsRunning] = useState(false);
  const handleToggleScenario = () => {
    if (isRunning) {
      setIsRunning(false);
      handlePauseScenario();
    } else {
      setIsRunning(true);
      handleRunScenario();
    }
  };
  
  const [currentLayout, setCurrentLayout] = useState(layout);

  const handleLayoutChange = (newLayout) => {
    setCurrentLayout(newLayout);
  };
 
  const handleDayChange = (index) => {
    console.log(`Day changed to: ${index}`);
    setCurrentIndex(index);
  };

  const handleRunScenario = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    intervalRef.current = setInterval(() => {
      setCurrentIndex((prevIndex) => {
        if (prevIndex < outputFiles.length - 1) {
          return prevIndex + 1;
        } else {
          clearInterval(intervalRef.current);
          return prevIndex;
        }
      });
    }, 1000);
  };
 
  const handlePauseScenario = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  }; 
  
  useEffect(() => {
    if (outputFiles[currentIndex]) {
      console.log('Output Data:', outputFiles[currentIndex]);

      // Calculate deceased count for the current day
      const deceasedCount = outputFiles[currentIndex].data.reduce((acc, county) => {
        const { D } = county.compartments;
        const totalDeceased = [
          ...D.U.L,
          ...D.U.H,
          ...D.V.L,
          ...D.V.H,
        ].reduce((sum, value) => sum + value, 0);
        return acc + totalDeceased;
      }, 0);

      // Update eventData to include only data up to the current day
      setEventData((prevData) => {
        const newData = [...prevData];
        // Ensure we're only adding data for the current day and not duplicating
        if (!newData[currentIndex]) {
          newData[currentIndex] = { day: currentIndex, deceased: Math.round(deceasedCount) };
        } else {
          newData[currentIndex].deceased = Math.round(deceasedCount);
        }
        return newData.slice(0, currentIndex + 1); // Keep only up to currentIndex
      });
    }
  }, [currentIndex, outputFiles]);

  useEffect(() => {
    const delay = 500; // Delay in milliseconds
    const timer = setTimeout(() => {
      console.log('Data processed for day:', currentIndex);
    }, delay);

    return () => clearTimeout(timer);
  }, [currentIndex]);

  return (
    <div className="chart-view">
      <div className="left-panel">
        <SetScenario counties={texasCounties} />
        <div className="interventions-container">
        <Interventions />
      </div>
      <div className="play-pause-container">
        <PlayPauseButton isRunning={isRunning} onToggle={handleToggleScenario} />
      </div>
      </div>
      
      <ResponsiveGridLayout
        className="grid-layout"
        layouts={{ lg: layout }}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={30}
        onLayoutChange={handleLayoutChange}
        draggableCancel=".search-input,.sort-button"
      >
        <div key="timeline">
        {<TimelineSlider
            totalDays={outputFiles.length}
            selectedDay={currentIndex}
            onDayChange={handleDayChange}
            onScenarioRun={handleRunScenario}
            onScenarioPause={handlePauseScenario}
          />}
        </div>  
        <div key="chart">
        </div>
        <div key="map">
        </div>
      </ResponsiveGridLayout>
    </div>
  );
  
};

export default ChartView;
