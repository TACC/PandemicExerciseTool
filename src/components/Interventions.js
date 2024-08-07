import React, { useState } from 'react';
import Antivirals from './Antivirals';
import Vaccine from './Vaccine';
import NonPharmaceutical from './NonPharmaceutical';
import './Interventions.css';

const Interventions = () => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [isAntiviralsOpen, setIsAntiviralsOpen] = useState(false);
  const [isVaccineOpen, setIsVaccineOpen] = useState(false);
  const [isNonPharmaceuticalOpen, setIsNonPharmaceuticalOpen] = useState(false);

  const toggleDropdown = () => setShowDropdown(!showDropdown);
  const openAntivirals = () => {
    setIsAntiviralsOpen(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeAntivirals = () => setIsAntiviralsOpen(false);
  const openVaccine = () => {
    setIsVaccineOpen(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeVaccine = () => setIsVaccineOpen(false);
  const openNonPharmaceutical = () => {
    setIsNonPharmaceuticalOpen(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeNonPharmaceutical = () => setIsNonPharmaceuticalOpen(false);

  return (
    <div className="dropdown-container" id="second-drop">
      <button className="grey-button" onClick={toggleDropdown}>
        <span className="dropdown-text"> + Add Interventions</span>
        <span className={`dropdown-arrow ${showDropdown ? 'open' : ''}`}>&#x25BE;</span>
      </button>
      {showDropdown && (
        <div className="dropdown-menu">
          <button className="dropdown-item" onClick={openAntivirals}>Antivirals</button>
          <button className="dropdown-item" onClick={openVaccine}>Vaccine</button>
          <button className="dropdown-item" onClick={openNonPharmaceutical}>Non-Pharmaceutical</button>
        </div>
      )}
      {isAntiviralsOpen && (
        <div className="modal-overlay" onClick={closeAntivirals}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeAntivirals}>&times;</span>
            <h2>Antivirals</h2>
            <Antivirals onSubmit={(data) => { console.log('Antivirals:', data); closeAntivirals(); }} />
          </div>
        </div>
      )}
      {isVaccineOpen && (
        <div className="modal-overlay" onClick={closeVaccine}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeVaccine}>&times;</span>
            <h2>Vaccine</h2>
            <Vaccine onSubmit={(data) => { console.log('Vaccine:', data); closeVaccine(); }} />
          </div>
        </div>
      )}
      {isNonPharmaceuticalOpen && (
        <div className="modal-overlay" onClick={closeNonPharmaceutical}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeNonPharmaceutical}>&times;</span>
            <h2>Non-Pharmaceutical</h2>
            <NonPharmaceutical onSubmit={(data) => { console.log('Non-Pharmaceutical:', data); closeNonPharmaceutical(); }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Interventions;
