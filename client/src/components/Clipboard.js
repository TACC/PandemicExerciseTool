/* Homeview set to look like the wireframes*/

import React from 'react';
import texasCounties from './counties';
import CountyInfectedTable from './CountyInfectedTable';
import ToggleMapView from './Views/ToggleMapView';
import SetParametersDropdown from './SetParametersDropdown';
import EventMonitor from './EventMonitor';
import InfectedChart from './InfectedChart';
import Interventions from './Interventions';
import OUTPUT_9 from './OUTPUT_9.json'
import TimelineSlider from './TimelineSlider';
import './HomeView.css';

const HomeView = ({ currentIndex, setCurrentIndex }) => {
  return (
    <div className="regular-view-content">
      <SetParametersDropdown counties={texasCounties} />
      <Interventions />
      <div className="divider"></div> {/* Added divider here */}
      <div className="regular-view-collapsible-container">
        <div className="map-and-charts-container">
          <div className="map-and-table-container">
          <div className="medium-chart-wrapper">
            <CountyInfectedTable outputData={OUTPUT_9}/>
            </div>
            <ToggleMapView currentIndex={currentIndex} setCurrentIndex={setCurrentIndex}/>
          </div>
          <div className="charts-container">
            <div className="chart-wrapper">
              <InfectedChart />
            </div>
            <div className="short-chart-wrapper">
              <EventMonitor />
            </div>
          </div>
        </div>
      </div>
      <TimelineSlider totalDays={OUTPUT_9.length} selectedDay={currentIndex} onDayChange={setCurrentIndex} />
    </div>
  );
};
export default HomeView;

/*UserGuide testing view from June - July that has total pop ingected deceased map, graph, and table*/
import texasCounties from './counties';
import React, { useState, useEffect, useRef } from 'react';
import InitialMap from './InitialMap';
import TimelineSlider from './TimelineSlider';
import DeceasedLineChart from './DeceasedLineChart';
import StateCountyDropdowns from './StateCountyDropdown';
import CountyInfectedDeceasedTable from './CountyInfectedDeceasedTable';
import SetParametersDropdown from './SetParametersDropdown'; 
import Interventions from './Interventions'; 
import './ChartView.css';

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

const UserGuideView = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [eventData, setEventData] = useState([]);
  const [outputFiles] = useState([
    OUTPUT_0, OUTPUT_1, OUTPUT_2, OUTPUT_3, OUTPUT_4, OUTPUT_5,
    OUTPUT_6, OUTPUT_7, OUTPUT_8, OUTPUT_9
  ]);
  const [loading, setLoading] = useState(true); // Add loading state
  const intervalRef = useRef(null);

  const handleDayChange = (index) => {
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
      setLoading(true); // Start loading

      // Simulate data processing delay
      setTimeout(() => {
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

        setEventData((prevData) => {
          const newData = [...prevData];
          if (!newData[currentIndex]) {
            newData[currentIndex] = { day: currentIndex, deceased: Math.round(deceasedCount) };
          } else {
            newData[currentIndex].deceased = Math.round(deceasedCount);
          }
          return newData.slice(0, currentIndex + 1);
        });

        setLoading(false); // Data is loaded
      }, 1); // Adjust the delay if needed
    }
  }, [currentIndex, outputFiles]);

  return (
    <div className="user-guide-view">
      <div className="left-panel">
        <SetParametersDropdown counties={texasCounties} />
        <br></br><br></br><br></br><br></br><br></br><br></br><br></br><br></br>
        <div className="interventions-container">
        <Interventions />
      </div>
      <div className="state-county-dropdowns-container">
        <StateCountyDropdowns />
      </div>
      </div>
      <div className="middle-panel">
        <InitialMap outputData={outputFiles[currentIndex]} />
      </div>
      <div className="timeline-panel">
        <TimelineSlider
          totalDays={outputFiles.length}
          selectedDay={currentIndex}
          onDayChange={handleDayChange}
          onScenarioRun={handleRunScenario}
          onScenarioPause={handlePauseScenario}
        />
      </div>
      <div className="chart-panel">
        <DeceasedLineChart eventData={eventData} />
      </div>
      <div className="bottom-panel">
        <CountyInfectedDeceasedTable className="percentage-table" outputData={outputFiles[currentIndex]} />
      </div>
    </div>
  );
};

export default UserGuideView; */