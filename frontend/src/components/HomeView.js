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
import CountyInfectedDeceasedTable from './CountyInfectedDeceasedTable';
import InfectedMap from './InfectedMap';
import InfectedDeceasedTable from './InfectedDeceasedTable';
import LineChart from './LineChart';

import './HomeView.css';
import PlayPauseButton from './PlayPauseButton';
import './leaflet-overrides.css';
import './styles.css';
import axios from 'axios';

const HomeView = () => {

  const [isRunning, setIsRunning] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalRef = useRef(null);
  const [id, setId] = useState([]);
  const [taskId, setTaskId] = useState([]);
  const [eventData, setEventData] = useState([]);
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
    debugger;
    console.log(`Day changed to: ${index}`);
    setCurrentIndex(index);
  };

  const handleRunScenario = () => {

    setEventData([]);
    setCurrentIndex(0);    

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
      initial_infected: localStorage.getItem('initial_infected'),
      phas: localStorage.getItem('nonpharma_list'),
      antiviral_effectiveness: localStorage.getItem('antiviral_effectiveness'),
      antiviral_wastage_factor: localStorage.getItem('antiviral_wastage_factor'),
      antiviral_stockpile: localStorage.getItem('antiviral_stockpile'),
      vaccine_effectiveness: localStorage.getItem('vaccine_effectiveness'),
      vaccine_adherence: localStorage.getItem('vaccine_adherence'),
      vaccine_wastage_factor: localStorage.getItem('vaccine_wastage_factor'),
      vaccine_pro_rata: localStorage.getItem('vaccine_strategy'),
      vaccine_stockpile: localStorage.getItem('vaccine_stockpile'),
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
    debugger;
    const nextAvailable = eventData.length;
    console.log("Length test", eventData.length);
    console.log("next available", nextAvailable)
    
    const fetchData = async (requestedIndex) => {
      debugger;
      try {
        const response = await axios.get(`http://localhost:8000/api/output/${requestedIndex}`);
        
        if (response.status === 200) {
          console.log('Requested Index:', requestedIndex);
          setCurrentIndex(response.data.day);
          console.log('Day:', response.data.day);
          const data_entries = Object.entries(response.data.data);
          const total_counts = response.data.total_summary;
    
          console.log('Total counts:', total_counts);
    
          // Map through data_entries to collect fips_id, infected counts, and deceased counts for each county
          const countyInfectedDeceasedData = data_entries.map(([countyKey, countyData]) => {
            const fips_id = countyData['fips_id'];  // Get the fips_id for the county
         //   const susceptibleCount = countyData['compartment_summary']['S'] || 0;  // Get the susceptible count;
            const infectedCount = countyData['compartment_summary']['I'] || 0;  // Get the infected count
            const deceasedCount = countyData['compartment_summary']['D'] || 0;  // Get the deceased count
      
            return {
              fips: fips_id,        // Store fips_id
         //     susceptible: susceptibleCount, // Store susceptible count
              infected: infectedCount, // Store infected count
              deceased: deceasedCount, // Store deceased count
            };
          });
      
          // Calculate the total deceased count for the current day
          const totalSusceptibleCount = total_counts['S'];
          const totalExposedCount = total_counts['E'];
          const totalAsymptomaticCount = total_counts['A'];
          const totalTreatableCount = total_counts['T'];
          const totalInfectedCount = total_counts['I'];
          const totalRecoveredCount = total_counts['R'];
          const totalDeceasedCount = total_counts['D'];

          console.log('Total Deceased Count:', totalDeceasedCount);
      
          // Update the eventData to include the county-level fips, infected, and deceased information
          setEventData((prevEventData) => [
            ...prevEventData,
            {
              day: response.data.day,
              counties: countyInfectedDeceasedData,  // Store array of county data for the current day
              totalSusceptible: totalSusceptibleCount,
              totalExposed: totalExposedCount,     // Store total exposed count for the day
              totalAsymptomaticCount: totalAsymptomaticCount,     // Store total asymptomatic count for the day
              totalTreatableCount: totalTreatableCount,     // Store total treatable count for the day
              totalInfectedCount: totalInfectedCount,     // Store total infected count for the day
              totalRecoveredCount: totalRecoveredCount,     // Store total recovered count for the day
              totalDeceased: totalDeceasedCount,     // Store total deceased count for the day
            },
          ]);
    
          console.log('Event Data:', eventData);
        }

      } catch (error) {
        console.log('Data not here yet:', error);
        setTimeout(() => {
          fetchData(nextAvailable);
        }, 1000);
      }
    };

    debugger;

    if (isRunning) {
      setTimeout(() => {
        fetchData(nextAvailable);
      }, 1000);
    }
  }, [isRunning, eventData]);
  
  
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true); 
    window.location.reload(); // Refresh the page
  };

  return (
    <div>
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
        <InfectedMap currentIndex={currentIndex} eventData={eventData} className="map-size" />
        <div className="separator"></div> 
        <LineChart currentIndex={currentIndex} eventData={eventData} className="chart-size" />
        </div>
      </div> 

      <div className="right-panel">
        <InfectedDeceasedTable currentIndex={currentIndex} eventData={eventData}/>
      </div>
  
      <div className="footer">
        <div className="play-pause-container">
          <PlayPauseButton isRunning={isRunning} onToggle={handleToggleScenario} />
        </div>
        <div className="timeline-panel">
          <TimelineSlider
            totalDays={eventData.length}
            selectedDay={currentIndex}
            onDayChange={handleDayChange}
            isRunning={isRunning}
          />
        </div>
      </div>
    </div>
  );

};

export default HomeView;
