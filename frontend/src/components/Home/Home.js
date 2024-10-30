// <Home /> acts as a "root" for the default home view of the web interface
// most of our axios requests and state management happen here
// we define change handler functions and pass them as props to components we want to update dynamically,
// but it might be smarter to switch to React Contexts (and avoid prop drilling) as the project gets bigger
import React, { useState, useEffect, useRef } from 'react';
import texasCounties from '../../data/texasCounties.js';
import texasAllCounties from '../../data/texasCountiesStatewide.js';
import TimelineSlider from './TimelineSlider.js';
import SetScenario from './SetScenario.js';
import Interventions from './Interventions.js';
import DisplayedParameters from './DisplayedParameters.js';
import SpreadMapCount from './SpreadMapCount.js';
import SpreadMapPercent from './SpreadMapPercent.js';
import SpreadTableCount from './SpreadTableCount.js';
import SpreadTablePercent from './SpreadTablePercent.js';
import LineChart from './LineChart.js';

import PlayPauseButton from './PlayPauseButton.js';
import './leaflet-overrides.css';
import './Home.css';
import axios from 'axios';
axios.defaults.baseURL = "http://localhost:8000";

const Home = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalRef = useRef(null);
  const [id, setId] = useState([]);
  const [taskId, setTaskId] = useState([]);
  const [eventData, setEventData] = useState([]);

  const [viewType, setViewType] = useState('percent');

  const [npiCount, setNPICount] = useState(localStorage.getItem('non_pharma_interventions') || 0);
  const handleNPIChange = (npiList) => {
    setNPICount(npiList.length);
  }

  const [initialCasesCount, setInitialCasesCount] = useState(localStorage.getItem("initial_infected") || 0);
  const handleInitialCasesChange = () => {
    setInitialCasesCount(localStorage.getItem("initial_infected").length);
    setHasSetCases(localStorage.getItem("initial_infected").length > 0 || false);
    console.log(JSON.parse(localStorage.getItem("initial_infected")).length);
  }

  const [lastSorted, setLastSorted] = useState({
    category: "county",
    order: "asc",
  });

  const handleSortDirectionChange = (category) => {
    if (category === lastSorted.category) {    // flip sort order
      setLastSorted({
        ...lastSorted,
        order: lastSorted.order === 'asc' ? 'desc' : 'asc'
      });
    } else {
      // county defaults to ascending (alphabetical) order, others default to descending
      setLastSorted({
        category: category,
        order: category === "county" ? "asc" : "desc",
      });
    }
  };

  const [scenarioCounter, setScenarioCounter] = useState(0);
  const handleScenarioChange = () => {
    console.log("scenario counter was", scenarioCounter);
    setScenarioCounter(scenarioCounter + 1);
    console.log("scenario counter now", scenarioCounter);
  }

  // used to enable/disable Play button
  const [hasSetScenario, setHasSetScenario] = useState(false);
  const [hasSetCases, setHasSetCases] = useState(false);

  // determine if a notification should be displayed when simulation is ran
  const [shouldNotifyStart, setShouldNotifyStart] = useState(false);
  const handleNotifyChange = (bool) => {
    setShouldNotifyStart(bool);
  }

  // Handle radio button change
  const handleViewChange = (e) => {
    setViewType(e.target.value);
  };

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
    // debugger;
    console.log(`Day changed to: ${index}`);
    setCurrentIndex(index);
  };

  const handleRunScenario = () => {

    setEventData([]);
    setCurrentIndex(0);

    // load parameters object from local storage and POST each property individually
    console.log(JSON.parse(localStorage.getItem('parameters')));
    const paramsObject = JSON.parse(localStorage.getItem('parameters'));
    console.log("loaded params object from local storage");

    axios.post('api/pet/', {
      disease_name: paramsObject.diseaseName,
      R0: paramsObject.reproductionNumber,
      beta_scale: paramsObject.beta_scale,
      tau: paramsObject.tau,
      kappa: paramsObject.kappa,
      gamma: paramsObject.gamma,
      chi: paramsObject.chi,
      rho: paramsObject.rho,
      nu: paramsObject.nuText,
      initial_infected: localStorage.getItem('initial_infected'),
      npis: localStorage.getItem('non_pharma_interventions'),
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
        return axios.get('api/pet/' + newId + '/run');
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

    handleNotifyChange(true);
  };

  const handlePauseScenario = () => {
    axios.get('api/delete/' + taskId)
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
    // debugger;
    const nextAvailable = eventData.length;
    console.log("Length test", eventData.length);
    console.log("next available", nextAvailable)

    const fetchData = async (requestedIndex) => {
      // debugger;
      try {
        const response = await axios.get(`api/output/${requestedIndex}`);

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
            const infectedPercent = countyData['compartment_summary_percent']['I'] || 0;  // Get the infected percent
            const deceasedPercent = countyData['compartment_summary_percent']['D'] || 0;  // Get the deceased percent

            return {
              fips: fips_id,        // Store fips_id
              //     susceptible: susceptibleCount, // Store susceptible count
              infected: infectedCount, // Store infected count
              deceased: deceasedCount, // Store deceased count
              infectedPercent: infectedPercent, // Store infected percent
              deceasedPercent: deceasedPercent, // Store deceased percent
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
        // console.log('Data not here yet:', error);
        setTimeout(() => {
          fetchData(nextAvailable);
        }, 1000);
      }
    };

    // debugger;

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

  // Needs to make sure its picking up data correctly
  const npiData = JSON.parse(localStorage.getItem('non_pharma_interventions'));

  return (
    <div >
      <div className="row">
        <div className="col-lg-2">
          <div className='left-panel'>
            <SetScenario
              counties={texasCounties}
              onSave={handleSave}
              casesChange={handleInitialCasesChange}
              scenarioChange={handleScenarioChange}
            />
            <div className="interventions-container">
              <Interventions counties={texasAllCounties} npiChange={handleNPIChange} />
            </div>
            <div className="saved-parameters-panel">
              <DisplayedParameters
                scenarioChange={handleScenarioChange}
                casesChange={handleInitialCasesChange}
              />
            </div>
          </div>
        </div>

        {/* Middle Panel - Infected Map (Count and Percentage) and Line Chart */}
        <div className="col-lg-7">

          <div className='top-middle-panel'>
            <div className="radio-buttons-container">
              <h6>Show values as:</h6>

              <label className={`radio-button ${viewType === 'percent' ? 'active' : ''}`}>
                <input
                  type="radio"
                  value="percent"
                  checked={viewType === 'percent'}
                  onChange={handleViewChange}
                />
                Percentage
              </label>
              <label className={`radio-button ${viewType === 'count' ? 'active' : ''}`}>
                <input
                  type="radio"
                  value="count"
                  checked={viewType === 'count'}
                  onChange={handleViewChange}
                />
                Count
              </label>
            </div>
          </div>

          <div className="map-and-chart-container">
            {viewType === 'percent' ? (
              <SpreadMapPercent currentIndex={currentIndex} eventData={eventData} className="map-size" />
            ) : (
              <SpreadMapCount currentIndex={currentIndex} eventData={eventData} className="map-size" />
            )}
            <div className="separator"></div>
            {/* <LineChart currentIndex={currentIndex} eventData={eventData} className="chart-size" /> */}
            <LineChart eventData={eventData} currentIndex={currentIndex} npiData={npiData} />

          </div>
        </div>


        {/* Right Panel - Infected Decease Table */}
        <div className="col-lg-3">
          <div className='right-panel'>
            {viewType === 'percent' ? (
              <SpreadTablePercent
                currentIndex={currentIndex} 
                eventData={eventData} 
                lastSorted={lastSorted} 
                handleSortDirectionChange={handleSortDirectionChange}
              />
            ) : (
              <SpreadTableCount
                  currentIndex={currentIndex} 
                  eventData={eventData} 
                  lastSorted={lastSorted}
                  handleSortDirectionChange={handleSortDirectionChange}
              />
            )}
          </div>
        </div>

        {/* Footer - Play & Pause Timeline */}
        <div className="footer">
          <div className="play-pause-container">
            <PlayPauseButton 
              isRunning={isRunning} 
              onToggle={handleToggleScenario}
              shouldNotify={shouldNotifyStart}
              changeNotify={handleNotifyChange}
            />
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

    </div>

  );
};

export default Home;
