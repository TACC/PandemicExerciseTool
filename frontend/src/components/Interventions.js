import React, { useState } from 'react';
import Antivirals from './Antivirals';
import Vaccine from './Vaccine';
import NonPharmaceutical from './NonPharmaceutical';
import './SetParametersDropdown.css';
import { createPortal } from 'react-dom';

const Interventions = ( {counties, npiChange} ) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [isAntiviralsOpen, setIsAntiviralsOpen] = useState(false);
  const [isVaccineOpen, setIsVaccineOpen] = useState(false);
  const [isNonPharmaceuticalOpen, setIsNonPharmaceuticalOpen] = useState(false);
  const [selectedCounty, setSelectedCounty] = useState(null);

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
      <button className="interventions-button" onClick={toggleDropdown}>
        <span className="dropdown-text"> + Add Interventions</span>
        <span className={`dropdown-arrow ${showDropdown ? 'open' : ''}`}>&#x25BE;</span>
      </button>
      {showDropdown && (
        <div className="dropdown-menu">
          <button className="dropdown-item" onClick={openNonPharmaceutical}>Non-Pharmaceutical</button>
          <button className="dropdown-item" onClick={openAntivirals}>Antivirals</button>
          <button className="dropdown-item" onClick={openVaccine}>Vaccines</button>
        </div>
      )}
      {isAntiviralsOpen && (
        <div>
          {createPortal(
            <div className="modal-overlay" onClick={closeAntivirals}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={closeAntivirals}>&times;</span>
                <h2>Antiviral Parameters and Stockpiles</h2>
                <Antivirals onSubmit={(eff, wf, avs) => { console.log("Eff: ", eff, " WF: ", wf, " AVS: ", avs); closeAntivirals(); }} />
              </div>
            </div>,
            document.body
          )}
        </div>
      )}
      {isVaccineOpen && (
        <div>
          {createPortal(
            <div className="modal-overlay" onClick={closeVaccine}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={closeVaccine}>&times;</span>
                <h2>Vaccine Stockpile</h2>
                <Vaccine onSubmit={(ve, va, vwf, vs, vsl) => { console.log("Eff:", ve, " Adh: ", va, " WF: ", vwf, " Strat: ", vs, " VS: ", vsl); closeVaccine(); }} />
              </div>
            </div>,
            document.body
          )}
        </div>
      )}
      {isNonPharmaceuticalOpen && (
        <div>
          {createPortal(
            <div className="modal-overlay" onClick={closeNonPharmaceutical}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={closeNonPharmaceutical}>&times;</span>
                <h2>Non-pharmaceutical intervention</h2>
                <NonPharmaceutical 
                  counties={counties} 
                  onSubmit={(npil) => { console.log('Non-Pharmaceutical:', npil); 
                    npiChange(npil); closeNonPharmaceutical(); }} 
                />
              </div>
            </div>,
            document.body
          )}
        </div>
      )}
    </div>
  );
};

export default Interventions;
