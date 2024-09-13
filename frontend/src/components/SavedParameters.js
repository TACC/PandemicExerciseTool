import React, { useState } from 'react';
import './Parameters.css'; // Import the CSS file for styling
import AddInitialCases from './AddInitialCases';
import texasCounties from './counties';
import editIcon from './images/edit.svg'
import './SavedParameters.css';


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
    Nu: localStorage.getItem('nu') || 'N/A',
  };

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


  const antiviralParams = {
    antiviralEffectiveness: localStorage.getItem('antiviral_effectiveness') || 'N/A',
    antiviralWastageFactor: localStorage.getItem('antiviral_wastage_factor') || 'N/A',
  }

  const antiviralLabels = {
    antiviralEffectiveness: 'Antiviral Effectiveness',
    antiviralWastageFactor: 'Antiviral Wastage Factor',
  }

  const vaccineParams = {
    vaccineEffectiveness: localStorage.getItem('vaccine_effectiveness') || 'N/A',
    vaccineAdherence: localStorage.getItem('vaccine_adherence') || 'N/A',
    vaccineWastageFactor: localStorage.getItem('vaccine_wastage_factor') || 'N/A',
    vaccineStrategy: localStorage.getItem('vaccine_strategy') || 'N/A',
  }

  const vaccineLabels = {
    vaccineEffectiveness: 'Vaccine Effectiveness',
    vaccineAdherence: 'Vaccine Adherence',
    vaccineWastageFactor: 'Vaccine Wastage Factor',
    vaccineStrategy: 'Vaccine Strategy',
  }
  
  // Retrieve initial cases from localStorage
  const initialCases = JSON.parse(localStorage.getItem('initial_infected')) || [];

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
        <>
          {Object.keys(parameters).map((key, index) => (
            <div key={key} className="parameter-item">
              <div className="parameter-label">{labels[key]}</div>
              <div className="parameter-value">{parameters[key]}</div>
              {index < Object.keys(parameters).length - 1 && (
                <hr className="parameter-separator" />
              )}
            </div>
          ))}
          <hr className="section-separator" />
          <div
            className={`initial-cases-section ${hovered ? 'hovered' : ''}`}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
          >
            <div className="section-label">Initial Cases</div>
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
        </>
      ) : (
        <>
          <div><h3>Antiviral</h3></div>
          {Object.keys(antiviralParams).map((key, index) => (
            <div key={key} className="parameter-item">
              <div className="parameter-label">{antiviralLabels[key]}</div>
              <div className="parameter-value">{antiviralParams[key]}</div>
              {index < Object.keys(antiviralParams).length - 1 && (
                <hr className="parameter-separator" />
              )}
            </div>
          ))}
          <hr className="section-separator" />

          <div><h3>Vaccine</h3></div>
          {Object.keys(vaccineParams).map((key, index) => (
            <div key={key} className="parameter-item">
              <div className="parameter-label">{vaccineLabels[key]}</div>
              <div className="parameter-value">{vaccineParams[key]}</div>
              {index < Object.keys(vaccineParams).length - 1 && (
                <hr className="parameter-separator" />
              )}
            </div>
          ))}
          <hr className="section-separator" />

        </>
      )}

      {isModalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Add Initial Cases</h2>
            <AddInitialCases counties={texasCounties} onClose={closeModal} />
          </div>
        </div>
      )}
    </div>
  );
};

export default SavedParameters;
