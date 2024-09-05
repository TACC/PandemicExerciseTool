import React, { useState, useEffect, useRef } from 'react';
import texasCounties from './counties';
import TimelineSlider from './TimelineSlider';
import DeceasedLineChart from './DeceasedLineChart';
import StateCountyDropdowns from './StateCountyDropdown';
import CountyPercentageTable from './CountyPercentageTable';
import InitialMapPercent from './InitialMapPercent';
import SetParametersDropdown from './SetParametersDropdown';
import Interventions from './Interventions';
import SavedParameters from './SavedParameters';
import AddInitialCases from './AddInitialCases';

import './HomeView.css';
import PlayPauseButton from './PlayPauseButton';
import './leaflet-overrides.css';
import './styles.css';
import './left-panel.css';
import axios from 'axios';

import OUTPUT_0 from './OUTPUT_0.json';



const HomeView = () => {

  const [isRunning, setIsRunning] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const intervalRef = useRef(null);
  const [id, setId] = useState([]);
  const [taskId, setTaskId] = useState([]);
  const [data, setData] = useState([]);
  const [eventData, setEventData] = useState([]);

  const [outputFiles] = useState([ OUTPUT_0 ])


  const handleToggleScenario = () => {

    if (isRunning) {
      setIsRunning(false);
      handlePauseScenario();
    } else {
      setIsRunning(true);
      handleRunScenario();
    }
  };

  const handleDayChange = (index) => {
    console.log(`Day changed to: ${index}`);
    setCurrentIndex(index);
  };

  const handleRunScenario = () => {
    axios.post('http://localhost:8000/api/pet/', {
      disease_name: localStorage.getItem('diseaseName'),
      R0: localStorage.getItem('reproductionNumber'),
      beta_scale: localStorage.getItem('beta_scale'),
      tau: localStorage.getItem('tau'),
      kappa: localStorage.getItem('kappa'),
      gamma: localStorage.getItem('gamma'),
      chi: localStorage.getItem('chi'),
      rho: localStorage.getItem('rho'),
      nu: localStorage.getItem('nu'),
      initial_infected: localStorage.getItem('initial_infected')
    })
    .then(response => {
      console.log('Disease parameters updated successfully:', response.data['id']);
      const newId = response.data['id'];
      setId(newId);
      return axios.get('http://localhost:8000/api/pet/' + newId + '/run');
    })
    .then(response => {
      console.log('Job runs successfully:', response.data['task_id']);
      setTaskId(response.data['task_id']);
    })
    .catch(error => {
      console.error('Error running job:', error);
    });

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };

  const handlePauseScenario = () => {
    axios.get('http://localhost:8000/api/delete/' + taskId)
      .then(response => {
        console.log('Simulation stopped successfully:', response.data['task_id']);
      })
      .catch(error => {
        console.error('Error stopping job:', error);
      });

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };


  useEffect(() => {
    const fetchData = async (currentIndex) => {
      try {
        const response = await axios.get(`http://localhost:8000/api/output/${currentIndex}`);
        
        if (response.status === 200) {
          setData(response.data);

          console.log('Current Index before increment:', currentIndex);
          setCurrentIndex((prevIndex) => {
            return prevIndex + 1;
          });
        }

      } catch (error) {
        console.log('Data not here yet:', error);
      }
    };

    if (isRunning) {
      intervalRef.current = setInterval(() => {
          console.log('Fetching data for index:', currentIndex);
          fetchData(currentIndex);
      }, 1000); // Check every 1 second
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, currentIndex]);

  useEffect(() => {
    if (currentIndex !== 0) {
      const data_entries = Object.entries(data.data);
  
      // Use reduce to iterate over counties and accumulate deceased counts
      const totalDeceasedCount = data_entries.reduce((acc, [countyKey, countyData]) => {
        const deceasedCount = countyData['compartment_summary']['D'] || 0;
        return acc + deceasedCount; // Accumulate deceased count
      }, 0); // Initialize accumulator at 0
  
      console.log('Total Deceased Count:', totalDeceasedCount);
  
      // Update event data with the accumulated deceased count for the current day
      setEventData((eventData) => {
        const newData = [...eventData];
        newData.push({ day: currentIndex, deceased: totalDeceasedCount });
        return newData;
      });
    }
  }, [data, currentIndex]);
  
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true); 
    window.location.reload(); // Refresh the page
  };

  return (
    <div className="home-view">
      <div className="left-panel">
        <SetParametersDropdown counties={texasCounties} onSave={handleSave} />
        <div className="interventions-container">
          <Interventions />
        </div>
        <div className="saved-parameters-panel">
          <SavedParameters />
        </div>
      </div>
  
      <div className="middle-panel">
        <div className="map-and-chart-container">
          <InitialMapPercent outputData={outputFiles[0]} className="map-size" />
          <div className="separator"></div> 
          <DeceasedLineChart eventData={eventData} className="chart-size" />
        </div>
      </div> 
      <div className="right-panel">
        <CountyPercentageTable className="percentage-table" outputData={outputFiles[0]} />
      </div>
  
      <div className="footer">
        <div className="play-pause-container">
          <PlayPauseButton isRunning={isRunning} onToggle={handleToggleScenario} />
        </div>
        <div className="timeline-panel">
          <TimelineSlider
            totalDays={currentIndex}
            selectedDay={currentIndex}
            onDayChange={handleDayChange}
            onScenarioRun={handleRunScenario}
            onScenarioPause={handlePauseScenario}
          />
        </div>
      </div>
    </div>
  );

};

export default HomeView;
