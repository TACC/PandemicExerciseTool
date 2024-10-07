import React, { useState } from 'react';
// import './Parameters.css'; // Import the CSS file for styling
import AddInitialCases from './AddInitialCases';
import texasCounties from './counties';
import editIcon from './images/edit.svg'
import './SavedParameters.css';
import { createPortal } from 'react-dom';


const SavedParameters = () => {
  const [isModalOpen, setModalOpen] = useState(false); // State for modal visibility
  const [hovered, setHovered] = useState(false); // State for hover effect
  const [view, setView] = useState('scenario'); // State to manage toggle between 'scenario' and 'interventions'


  // Retrieve parameters from localStorage
  const parameters = {
    DiseaseName: localStorage.getItem('diseaseName') || 'N/A',
    ReproductionNumber: localStorage.getItem('reproductionNumber') || 'N/A',
    Tau: localStorage.getItem('tau') || 'N/A',
    Kappa: localStorage.getItem('kappa') || 'N/A',
    Gamma: localStorage.getItem('gamma') || 'N/A',
    Chi: localStorage.getItem('chi') || 'N/A',
    //Nu: localStorage.getItem('nu') || 'N/A',
  };

  const paramNu = localStorage.getItem('nu') || 'N/A';
  const paramNuList = paramNu.match(/[^,]+/g);

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

  const nonpharmaList = JSON.parse(localStorage.getItem('nonpharma_list')) || [];


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
              <div className="parameter-value"><span className="light-text"> 0-4:</span>   {paramNuList[0]?.toString()}</div>
              <div className="parameter-value"><span className="light-text"> 5-24:</span>  {paramNuList[1]?.toString()}</div>
              <div className="parameter-value"><span className="light-text"> 25-49:</span> {paramNuList[2]?.toString()}</div>
              <div className="parameter-value"><span className="light-text"> 50-64:</span> {paramNuList[3]?.toString()}</div>
              <div className="parameter-value"><span className="light-text"> 65+: </span>  {paramNuList[4]?.toString()}</div>
          </div>
          <hr className="section-separator" />
          <div
            className={`initial-cases-section ${hovered ? 'hovered' : ''}`}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
          >
           <div><h3>Initial Cases</h3></div>
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
          <div><h3>Antivirals</h3></div>
          {Object.keys(antiviralParams).map((key, index) => (
            <div key={key} className="parameter-item">
              <div className="parameter-label">{antiviralLabels[key]}</div>
              <div className="parameter-value">{antiviralParams[key]}</div>
              {index < Object.keys(antiviralParams).length && (
                <hr className="parameter-separator" />
              )}
            </div>
          ))}

          <div className="section-label">Antiviral Stockpile</div>
          {antiviralStockpileList.map((item, index) => (
            <div key={index} className="initial-case-item">
              <div className="initial-case-info">
                Day: <strong>{item.day}</strong>, {' '}
                Antivirals: <strong>{item.amount}</strong>
              </div>
            </div>
          ))}

          <hr className="section-separator" />


          <div><h3>Vaccines</h3></div>
          {Object.keys(vaccineParams).map((key, index) => (
            <div key={key} className="parameter-item">
              <div className="parameter-label">{vaccineLabels[key]}</div>
              <div className="parameter-value">{vaccineParams[key]}</div>
              {index < Object.keys(vaccineParams).length && (
                <hr className="parameter-separator" />
              )}
            </div>
          ))}

          <div className="section-label">Vaccine Stockpile</div>
          {vaccineStockpileList.map((item, index) => (
            <div key={index} className="initial-case-item">
              <div className="initial-case-info">
                Day: <strong>{item.day}</strong>, {' '}
                Vaccines: <strong>{item.amount}</strong>
              </div>
            </div>
          ))}

          <hr className="section-separator" />

          <div><h3>NPI</h3></div>
          <div className="section-label"></div>
          {nonpharmaList.map((item, index) => (
            <div key={index} className="initial-case-item">
              <div className="initial-case-info">
                NPI on day <strong>{item.day}</strong> with {' '}
                <strong>{item.effectiveness}</strong> effectiveness {' '}
                and half-life of <strong>{item.halflife}</strong> days
              </div>
            </div>
          ))}
        </div>
      )}

      {isModalOpen && (
        <div>
          {createPortal(
          <div className="modal-overlay" onClick={closeModal}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h2>Add Initial Cases</h2>
              <AddInitialCases counties={texasCounties} onClose={closeModal} />
            </div>
          </div>,
          document.body
          )}
        </div>
      )}
    </div>
  );
};

export default SavedParameters;
