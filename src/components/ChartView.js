import React, { useState, useEffect, useRef } from 'react';
import texasCounties from './counties';
import TimelineSlider from './TimelineSlider';
import DeceasedLineChart from './DeceasedLineChart';
import StateCountyDropdowns from './StateCountyDropdown';
import CountyPercentageTable from './CountyPercentageTable';
import InitialMapPercent from './InitialMapPercent';
import SetParametersDropdown from './SetParametersDropdown';
import Interventions from './Interventions';
import './ChartView.css';
import { Responsive, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';


import OUTPUT_0 from './OUTPUT_0.json';
import OUTPUT_1 from './OUTPUT_1.json';
import OUTPUT_2 from './OUTPUT_2.json';
import OUTPUT_3 from './OUTPUT_3.json';
import OUTPUT_4 from './OUTPUT_4.json';
import OUTPUT_5 from './OUTPUT_5.json';
import OUTPUT_6 from './OUTPUT_6.json';
import OUTPUT_7 from './OUTPUT_7.json';
import OUTPUT_8 from './OUTPUT_8.json';
import OUTPUT_9 from './OUTPUT_9.json';

const ChartView = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [eventData, setEventData] = useState([]);
  const [outputFiles] = useState([
    OUTPUT_0, OUTPUT_1, OUTPUT_2, OUTPUT_3, OUTPUT_4, OUTPUT_5,
    OUTPUT_6, OUTPUT_7, OUTPUT_8, OUTPUT_9
  ]);
  const intervalRef = useRef(null);

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

  const [isLoading, setIsLoading] = useState(false);

  const LoadingSpinner = () => (
    <div className="loading-spinner">Loading...</div>
  );  

  const preloadData = (currentDay) => {
    const daysToPreload = [-1, 0, 1];
    daysToPreload.forEach(offset => {
      const dayToLoad = currentDay + offset;
      // Fetch and cache data for dayToLoad
    });
  };
 
  const handlePauseScenario = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };

  const ResponsiveGridLayout = WidthProvider(Responsive);
  const layout = [
    { i: 'timeline', x: 0, y: 6, w: 10, h: 6 },
    { i: 'chart', x: 6, y: 0, w: 10, h: 7 },
    { i: 'map', x: 0, y: 0, w: 6, h: 12 },
    { i: 'table', x: 6, y: 6, w: 3, h: 12 },
  ];
  
  
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
        <SetParametersDropdown counties={texasCounties} />
        <div className="interventions-container">
        <Interventions />
      </div>
      <div className="state-county-dropdowns-container">
        <StateCountyDropdowns />
      </div>
      </div>
      
      <ResponsiveGridLayout
        className="grid-layout"
        layouts={{ lg: layout }}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={30}
      >
        <div key="timeline">
        {isLoading ? <LoadingSpinner /> :<TimelineSlider
            totalDays={outputFiles.length}
            selectedDay={currentIndex}
            onDayChange={handleDayChange}
            onScenarioRun={handleRunScenario}
            onScenarioPause={handlePauseScenario}
          />}
        </div>  
        <div key="chart">
        {isLoading ? <LoadingSpinner /> :<DeceasedLineChart eventData={eventData} />}
        </div>
        <div key="map">
          {isLoading ? <LoadingSpinner /> :<InitialMapPercent outputData={outputFiles[currentIndex]} />}
        </div>
        <div key="table">
          {isLoading ? <LoadingSpinner /> :<CountyPercentageTable className="percentage-table" outputData={outputFiles[currentIndex]} />}
        </div>
      </ResponsiveGridLayout>
    </div>
  );
  
};

export default ChartView;
