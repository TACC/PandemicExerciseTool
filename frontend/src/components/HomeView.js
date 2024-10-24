import React, { useState, useEffect, useRef } from 'react';
import texasCounties from '../data/texasCounties.js';
import texasAllCounties from '../data/texasCountiesStatewide.js';
import TimelineSlider from './TimelineSlider';
import SetParametersDropdown from './SetParametersDropdown';
import Interventions from './Interventions';
import SavedParameters from './SavedParameters';
import InfectedMap from './InfectedMap';
import InfectedMapPercent from './InfectedMapPercent';
import InfectedDeceasedTableMerged from './InfectedDeceasedTableMerged';
import InfectedDeceasedTableMergedPercent from './InfectedDeceasedTableMergedPercent.js';
import LineChart from './LineChart';

import PlayPauseButton from './PlayPauseButton';
import './leaflet-overrides.css';
import axios from 'axios';
import './HomeView.css';

const HomeView = () => {
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
    setInitialCasesCount(localStorage.getItem("initial_infected").length || 0);
  }

  // remember how table is sorted between re-renders
  // default sort is flipped when user clicks to sort
  const [sortDirection, setSortDirection] = useState({
    county: 'asc',
    infected: 'asc',
    deceased: 'asc',
    infectedPercent: 'asc',
    deceasedPercent: 'asc',
    lastSorted: 'county',
  });

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

    axios.post('http://localhost:8000/api/pet/', {
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
    // debugger;
    const nextAvailable = eventData.length;
    console.log("Length test", eventData.length);
    console.log("next available", nextAvailable)

    const fetchData = async (requestedIndex) => {
      // debugger;
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
        console.log('Data not here yet:', error);
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
            <SetParametersDropdown
              counties={texasCounties}
              onSave={handleSave}
              casesChange={handleInitialCasesChange}
              scenarioChange={handleScenarioChange}
            />
            <div className="interventions-container">
              <Interventions counties={texasAllCounties} npiChange={handleNPIChange} />
            </div>
            <div className="saved-parameters-panel">
              <SavedParameters
                scenarioChange={handleScenarioChange}
                casesChange={handleInitialCasesChange}
              />
            </div>
          </div>
        </div>

        {/* Middlle Panel - Infected Map (Count and Percentage) and Line Chart */}
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
              <InfectedMapPercent currentIndex={currentIndex} eventData={eventData} className="map-size" />
            ) : (
              <InfectedMap currentIndex={currentIndex} eventData={eventData} className="map-size" />
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
              <InfectedDeceasedTableMergedPercent 
                currentIndex={currentIndex} 
                eventData={eventData} 
                lastSorted={lastSorted} 
                handleSortDirectionChange={handleSortDirectionChange}
              />
            ) : (
              <InfectedDeceasedTableMerged 
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

    </div>

  );
};

export default HomeView;
