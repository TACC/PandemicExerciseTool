import React, { useState } from 'react';
import './Parameters.css'; // Import the CSS file for styling
import AddInitialCases from './AddInitialCases';
import texasCounties from './counties';
import editIcon from './images/edit.svg'

const SavedParameters = () => {
  const [isModalOpen, setModalOpen] = useState(false); // State for modal visibility
  const [hovered, setHovered] = useState(false); // State for hover effect

  // Retrieve parameters from localStorage
  const parameters = {
    DiseaseName: localStorage.getItem('diseaseName') || 'N/A',
    ReproductionNumber: localStorage.getItem('reproductionNumber') || 'N/A',
    BetaScale: localStorage.getItem('beta_scale') || 'N/A',
    Tau: localStorage.getItem('tau') || 'N/A',
    Kappa: localStorage.getItem('kappa') || 'N/A',
    Gamma: localStorage.getItem('gamma') || 'N/A',
    Chi: localStorage.getItem('chi') || 'N/A',
 //   Rho: localStorage.getItem('rho') || 'N/A',
    Nu: localStorage.getItem('nu') || 'N/A',
    //VaccineWastageFactor: localStorage.getItem('vaccine_wastage_factor') || 'N/A',
    //AntiviralEffectiveness: localStorage.getItem('antiviral_effectiveness') || 'N/A',
    //AntiviralWastageFactor: localStorage.getItem('antiviral_wastage_factor') || 'N/A',
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
  //  Rho: 'Traveler Contact Rate',
    Nu: 'High/Low Death Rate',
    //VaccineWastageFactor: 'Vaccine Wastage Factor',
    //AntiviralEffectiveness: 'Antiviral Effectiveness',
    //AntiviralWastageFactor: 'Antiviral Wastage Factor',
  };

// Retrieve initial cases from localStorage
const initialCases = JSON.parse(localStorage.getItem('initial_infected')) || [];

 // Function to handle modal opening and closing
 const openModal = () => setModalOpen(true);
 const closeModal = () => setModalOpen(false);

  return (
    <div className="saved-parameters-panel">
    {/* Display Parameters */}
    {Object.keys(parameters).map((key, index) => (
      <div key={key} className="parameter-item">
        <div className="parameter-label">{labels[key]}</div>
        <div className="parameter-value">{parameters[key]}</div>
        {index < Object.keys(parameters).length - 1 && <hr className="parameter-separator" />}
      </div>
    ))}

    {/* Separator line between parameters and initial cases */}
    <hr className="section-separator" />

    {/* Section for Initial Cases with hover effect */}
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
          {index < initialCases.length - 1 && <hr className="case-separator" />}
        </div>
      ))}
      {/* Edit button */}
      {hovered && (
        <button className="edit-button" onClick={openModal}>
          Edit <img src={editIcon} alt="Edit Icon" className="edit-icon" />
        </button>
      )}
    </div>

  {/* AddInitialCases modal */}
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
