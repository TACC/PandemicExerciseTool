// an information panel summarizing disease parameters, initial cases, and interventions the user has inputted
// <DisplayedParameters /> should update dynamically as user input is added/changed; we use state variables in <Home />
// and pass change handlers as props to <DisplayedParameters /> to provoke re-renders
// this component is rendered on the left-hand information pane of Home view, below the Interventions dropdown
import React, { useState, useEffect } from 'react';
import InitialCasesForm from './InitialCasesForm';
import texasCounties from '../../data/texasCounties';
import editIcon from '../images/edit.svg'
import './DisplayedParameters.css';
import { createPortal } from 'react-dom';
import NewSimulationButton from './NewSimulationButton'

const NPIInfo = ({ NPIList }) => {
  let ageGroups = [
    "0-4",
    "5-24",
    "25-29",
    "50-64",
    "65+"
  ];

  const [nonpharmaCount, setNonpharmaCount] = useState(NPIList.length);

    return (
    <>
      {NPIList.map((npi, index) => (
        <div key={index} className="initial-case-item">
          <div className="initial-case-info">
            <div className="parameter-label"><span className="light-text"> Name</span></div>
            <div className="parameter-value"><strong>{npi.name}</strong></div>
            <hr className="parameter-separator" /> 
          
            <div className="parameter-label"><span className="light-text"> Begins on</span></div>
            <div className="parameter-value"><strong> Day {npi.day} </strong> </div>
            <hr className="parameter-separator" />

            <div className="parameter-label"><span className="light-text"> Location:</span></div>
            <div className="parameter-value">{npi.location === 0 || npi.location === '' ? <strong>All</strong> : 
              npi.location.split(",").map((county, index) => 
                (<span key={index}><strong>{county}</strong>{index < npi.location.split(",").length - 1 ? ", " : ""}</span>))}
            </div>
            <hr className="parameter-separator" />
            
            <div className="parameter-label"><span className="light-text"> Effectiveness:</span> 
            </div> {npi.effectiveness.split(",").map((effect, index) =>
                            <div key={index} className="parameter-value"><span className="light-text"> {ageGroups[index]}: </span><strong>{effect}</strong></div>)}
          </div>
          {index < NPIList.length - 1 && (
            <hr className="section-separator" />
          )}
        </div>
      ))}
    </>
  )
};

const DisplayedParameters = ({ scenarioChange, casesChange }) => {
  const [isModalOpen, setModalOpen] = useState(false); // State for modal visibility
  const [hovered, setHovered] = useState(false); // State for hover effect
  const [view, setView] = useState('scenario'); // State to manage toggle between 'scenario' and 'interventions'
  const [parameters, setParameters] = useState({
    DiseaseName: "N/A",
    ReproductionNumber: "N/A",
    // BetaScale: "N/A",
    Tau: "N/A",
    Kappa: "N/A",
    Gamma: "N/A",
    Chi: "N/A",
  });
  const [nuArray, setNuArray] = useState(["N/A", "N/A", "N/A", "N/A", "N/A"]);

  // we have to use a useEffect hook rather than mirror the logic for showing initial cases/NPI data
  // parsing the params object causes a crash if 'parameters' doesn't yet exist in local storage
  // we wrap the try-catch block in a hook to prevent the crash
  useEffect(() => {
    const params = localStorage.getItem('parameters');

    if (params) {
      try {
        const paramsObject = JSON.parse(params);
        setParameters({
          DiseaseName: paramsObject.diseaseName,
          ReproductionNumber: paramsObject.reproductionNumber,
          // BetaScale: paramsObject.beta_scale,
          Tau: paramsObject.tau,
          Kappa: paramsObject.kappa,
          Gamma: paramsObject.gamma,
          // do we want to include chi in the summary? we currently don't allow users to edit this
          Chi: paramsObject.chi,
        })
        setNuArray(paramsObject.nu);
      } catch (error) {
        console.error("error parsing JSON", error);
      }
    }
  }, [scenarioChange]);
 
  // const paramNu = localStorage.getItem('nu') || 'N/A';
  // const paramNuList = paramNu.match(/[^,]+/g);

  // Map of user-friendly labels
  const labels = {
    DiseaseName: 'Scenario Name',
    ReproductionNumber: 'Reproduction Number',
    BetaScale: 'Beta Scale',
    Tau: 'Latency Period',
    Kappa: 'Asymptomatic Period',
    Gamma: 'Infectious Period',
    Chi: 'Therapeutic Window',
    Nu: 'Case Fatality Rate',
  };

  // Retrieve initial cases from localStorage
  const initialCases = JSON.parse(localStorage.getItem('initial_infected')) || [];
  
  const antiviralParams = {
    antiviralEffectiveness: localStorage.getItem('antiviral_effectiveness') || 'N/A',
    antiviralWastageFactor: localStorage.getItem('antiviral_wastage_factor') || 'N/A',
  }

  const antiviralLabels = {
    antiviralEffectiveness: 'Antiviral Effectiveness',
    antiviralWastageFactor: 'Antiviral Wastage Factor',
  }

  const antiviralStockpileList = JSON.parse(localStorage.getItem('antiviral_stockpile')) || [];

  const vaccineParams = {
    vaccineEffectiveness: localStorage.getItem('vaccine_effectiveness') || 'N/A',
    vaccineAdherence: localStorage.getItem('vaccine_adherence') || 'N/A',
    vaccineWastageFactor: localStorage.getItem('vaccine_wastage_factor') || 'N/A',
    vaccineStrategy: localStorage.getItem('vaccine_strategy') === 'children' ? 'children first' : 'pro rata',
  }

  const vaccineLabels = {
    vaccineEffectiveness: 'Vaccine Effectiveness',
    vaccineAdherence: 'Vaccine Adherence',
    vaccineWastageFactor: 'Vaccine Wastage Factor',
    vaccineStrategy: 'Vaccine Strategy',
  }
  
  const vaccineStockpileList = JSON.parse(localStorage.getItem('vaccine_stockpile')) || [];

  const nonpharmaList = JSON.parse(localStorage.getItem('non_pharma_interventions')) || [];


  // Function to handle modal opening and closing
  const openModal = () => setModalOpen(true);
  const closeModal = () => setModalOpen(false);

  return (
    <div className="saved-parameters-panel">
      {/* Toggle between 'Scenario' and 'Interventions' */}
      <div className="toggle-section">
        <button
          className={`toggle-button ${view === 'scenario' ? 'active' : ''}`}
          onClick={() => setView('scenario')}
        >
          Scenario
        </button>
        <button
          className={`toggle-button ${view === 'interventions' ? 'active' : ''}`}
          onClick={() => setView('interventions')}
        >
          Interventions
        </button>
      </div>

      {/* Conditionally render content based on selected view */}
      {view === 'scenario' ? (
        // Scenario View: Existing content
        <div className = "scenario-section">
          {Object.keys(parameters).map((key, index) => (
            <div key={key} className="parameter-item">
              <div className="parameter-label">{labels[key]}</div>
              <div className="parameter-value">{parameters[key]}</div>
              {index < Object.keys(parameters).length - 1 && (
                <hr className="parameter-separator" />
              )}
            </div>
          ))}
          <hr className="parameter-separator" />
          <div className="parameter-item">
              <div className="parameter-label">Case Fatality Rate</div>
              <div className="parameter-value"><span className="light-text"> 0-4:</span>   {nuArray[0]?.toString()}</div>
              <div className="parameter-value"><span className="light-text"> 5-24:</span>  {nuArray[1]?.toString()}</div>
              <div className="parameter-value"><span className="light-text"> 25-49:</span> {nuArray[2]?.toString()}</div>
              <div className="parameter-value"><span className="light-text"> 50-64:</span> {nuArray[3]?.toString()}</div>
              <div className="parameter-value"><span className="light-text"> 65+: </span>  {nuArray[4]?.toString()}</div>
          </div>
          <hr className="section-separator" />
          <div
            className={`initial-cases-section ${hovered ? 'hovered' : ''}`}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
          >
           <div><h6>Initial Cases</h6></div>
            {initialCases.map((caseItem, index) => (
              <div key={index} className="initial-case-item">
                <div className="initial-case-info">
                  <strong>{caseItem.infected}</strong> aged{' '}
                  <strong>{caseItem.age_group_display}</strong> in{' '}
                  <strong>{caseItem.county_display}</strong>
                </div>
                {index < initialCases.length - 1 && (
                  <hr className="case-separator" />
                )}
              </div>
            ))}
            {hovered && (
              <button className="edit-button" onClick={openModal}>
                Edit <img src={editIcon} alt="Edit Icon" className="edit-icon" />
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="interventions-section">

        <div><h6>NPIs</h6></div>
          <div className="section-label"></div>
          {/* {nonpharmaList.map((item, index) => ( */}
          {/*   <div key={index} className="initial-case-item"> */}
          {/*     <div className="initial-case-info"> */}
          {/*       NPI on day <strong>{item.day}</strong> with {' '} */}
          {/*       <strong>{item.effectiveness}</strong> effectiveness {' '} */}
          {/*       and a duration of <strong>{item.duration}</strong> days */}
          {/*     </div> */}
          {/*   </div> */}
          {/* ))} */}
          <NPIInfo NPIList={ nonpharmaList } />

          <hr className="section-separator" />

          <div><h6>Antivirals</h6></div>
          {Object.keys(antiviralParams).map((key, index) => (
            <div key={key} className="parameter-item">
              <div className="parameter-label">{antiviralLabels[key]}</div>
              <div className="parameter-value">{antiviralParams[key]}</div>
              {index < Object.keys(antiviralParams).length && (
                <hr className="parameter-separator" />
              )}
            </div>
          ))}

          <div className="parameter-label">Antiviral Stockpile</div>
          {antiviralStockpileList.map((item, index) => (
            <div key={index} className="initial-case-item">
              <div className="initial-case-info">
                Day: <strong>{item.day}</strong>, {' '}
                Antivirals: <strong>{item.amount}</strong>
              </div>
            </div>
          ))}

          <hr className="section-separator" />


          <div><h6>Vaccines</h6></div>
          {Object.keys(vaccineParams).map((key, index) => (
            <div key={key} className="parameter-item">
              <div className="parameter-label">{vaccineLabels[key]}</div>
              <div className="parameter-value">{vaccineParams[key]}</div>
              {index < Object.keys(vaccineParams).length && (
                <hr className="parameter-separator" />
              )}
            </div>
          ))}

          <div className="parameter-label">Vaccine Stockpile</div>
          {vaccineStockpileList.map((item, index) => (
            <div key={index} className="initial-case-item">
              <div className="initial-case-info">
                Day: <strong>{item.day}</strong>, {' '}
                Vaccines: <strong>{item.amount}</strong>
              </div>
            </div>
          ))}

          <hr className="section-separator" />
</div>
      )}

      {isModalOpen && (
        <div>
          {createPortal(
          <div className="modal-overlay" onClick={closeModal}>
            <div className="modal-contents" onClick={(e) => e.stopPropagation()}>
              <h2>Add Initial Cases</h2>
              <InitialCasesForm 
                  counties={texasCounties} 
                  onClose={closeModal} 
                  casesChange={casesChange}
                />
            </div>
          </div>,
          document.body
          )}
        </div>
      )}
                    <NewSimulationButton />

    </div>
  );
};

export default DisplayedParameters;
