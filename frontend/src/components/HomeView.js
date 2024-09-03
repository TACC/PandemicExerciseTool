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
//import OUTPUT_1 from './OUTPUT_1.json';
//import OUTPUT_2 from './OUTPUT_2.json';
//import OUTPUT_3 from './OUTPUT_3.json';
//import OUTPUT_4 from './OUTPUT_4.json';
//import OUTPUT_5 from './OUTPUT_5.json';
//import OUTPUT_6 from './OUTPUT_6.json';
//import OUTPUT_7 from './OUTPUT_7.json';
//import OUTPUT_8 from './OUTPUT_8.json';
//import OUTPUT_9 from './OUTPUT_9.json';


const HomeView = () => {

  const [isRunning, setIsRunning] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const intervalRef = useRef(null);
  const [id, setId] = useState([]);
  const [taskId, setTaskId] = useState([]);
  const [data, setData] = useState([]);
  const [eventData, setEventData] = useState([]);

  const [outputFiles] = useState([ OUTPUT_0 ])

  //const [currentIndex, setCurrentIndex] = useState(0);
  //const [outputFiles] = useState([
  //  OUTPUT_0, OUTPUT_1, OUTPUT_2, OUTPUT_3, OUTPUT_4, OUTPUT_5,
  //  OUTPUT_6, OUTPUT_7, OUTPUT_8, OUTPUT_9
  //]);


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

    intervalRef.current = setInterval(() => {
      setCurrentIndex((prevIndex) => {
          return prevIndex + 1;
      });
    }, 1000);
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

///////////////////////

  useEffect(() => {
    const fetchData = async (currentIndex) => {
        try {
            const response = await axios.get(`http://localhost:8000/api/output/${currentIndex}`);
            if (response.status === 200) {
              //setData(prevData => [...prevData, response.data]);
              setData(response.data);
              setCurrentIndex(prevIndex => prevIndex + 1);

              console.log('Data fetched successfully:', data.day);
              console.log('Current Index:', currentIndex);
              //const deceasedCount = data.data.reduce((acc, node_id) => {

              //  const { D } = node_id.compartments;
              //  const totalDeceased = [
              //    ...D.U.L,
              //    ...D.U.H,
              //    ...D.V.L,
              //    ...D.V.H,
              //  ].reduce((sum, value) => sum + value, 0);
              //  return acc + totalDeceased;
              //}, 0);
              
              //const exposedCount = data.data.compartment_summary.E.reduce((acc, value) => acc + value, 0);
              //console.log(('exposedCount:', exposedCount));

             setEventData((data) => {
               const newData = [...data];
               if (!newData[currentIndex]) {
                 newData[currentIndex] = { day: currentIndex, deceased: 1 };
               } else {
                 newData[currentIndex].deceased = 1;
               }
               return newData.slice(0, currentIndex + 1);
             });

            } else {
                console.log('No data available for index:', currentIndex);
            }
        } catch (error) {
            console.log('Error fetching data:', error);
        }
    };

    if (isRunning) {
      intervalRef.current = setInterval(() => {
          fetchData(currentIndex);
      }, 1000); // Check every 1 second
    }

    return () => {
      if (intervalRef.current) {
          clearInterval(intervalRef.current);
      }
    };

  }, [isRunning, currentIndex]);

/////////////////////

//  useEffect(() => {
//    if (outputFiles[currentIndex]) {
//      console.log('Output Data:', outputFiles[currentIndex]);
//
//      const deceasedCount = outputFiles[currentIndex].data.reduce((acc, county) => {
//        const { D } = county.compartments;
//        const totalDeceased = [
//          ...D.U.L,
//          ...D.U.H,
//          ...D.V.L,
//          ...D.V.H,
//        ].reduce((sum, value) => sum + value, 0);
//        return acc + totalDeceased;
//      }, 0);
//
//      setEventData((prevData) => {
//        const newData = [...prevData];
//        if (!newData[currentIndex]) {
//          newData[currentIndex] = { day: currentIndex, deceased: Math.round(deceasedCount) };
//        } else {
//          newData[currentIndex].deceased = Math.round(deceasedCount);
//        }
//        return newData.slice(0, currentIndex + 1);
//      });
//    }
//  }, [currentIndex, outputFiles]);



  useEffect(() => {
    const delay = 500;
    const timer = setTimeout(() => {
      console.log('Data processed for day:', currentIndex);
    }, delay);

    return () => clearTimeout(timer);
  }, [currentIndex]);

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
