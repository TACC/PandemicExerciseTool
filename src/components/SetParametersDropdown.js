import React, { useState } from 'react';
import AddInitialCases from './AddInitialCases';
import CaseFatalityRate from './CaseFatalityRate';
import Disease from './Disease';
import './SetParametersDropdown.css';

const SetParametersDropdown = ({ counties }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [isInitialCasesOpen, setIsInitialCasesOpen] = useState(false);
  const [isCaseFatalityRateOpen, setIsCaseFatalityRateOpen] = useState(false);
  const [isDiseaseOpen, setIsDiseaseOpen] = useState(false);

  const toggleDropdown = () => setShowDropdown(!showDropdown);
  const openInitialCases = () => {
    setIsInitialCasesOpen(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeInitialCases = () => setIsInitialCasesOpen(false);
  const openCaseFatalityRate = () => {
    setIsCaseFatalityRateOpen(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeCaseFatalityRate = () => setIsCaseFatalityRateOpen(false);
  const openDisease = () => {
    setIsDiseaseOpen(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeDisease = () => setIsDiseaseOpen(false);

  return (
    <div className="dropdown-container" id="first-drop">
      <button className="orange-button" onClick={toggleDropdown}>
        <span className="dropdown-text">Set Parameters</span>
        <span className={`dropdown-arrow ${showDropdown ? 'open' : ''}`}>&#x25BE;</span>
      </button>
      {showDropdown && (
        <div className="dropdown-menu">
          <button className="dropdown-item" onClick={openDisease}>Disease</button>
          <button className="dropdown-item" onClick={openInitialCases}>Initial Cases</button>
          <button className="dropdown-item" onClick={openCaseFatalityRate}>Case Fatality Rate</button>
        </div>
      )}
      {isDiseaseOpen && (
        <div className="modal-overlay" onClick={closeDisease}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeDisease}>&times;</span>
            <h2>Disease</h2>
            <Disease onSubmit={(data) => { console.log('Disease:', data); closeDisease(); }} />
          </div>
        </div>
      )}
      {isInitialCasesOpen && (
        <div className="modal-overlay" onClick={closeInitialCases}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeInitialCases}>&times;</span>
            <h2>Initial Cases</h2>
            <AddInitialCases counties={counties} onSubmit={(data) => { console.log('Initial Cases:', data); closeInitialCases(); }} />
          </div>
        </div>
      )}
      {isCaseFatalityRateOpen && (
        <div className="modal-overlay" onClick={closeCaseFatalityRate}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeCaseFatalityRate}>&times;</span>
            <h2>Case Fatality Rate</h2>
            <CaseFatalityRate onSubmit={(data) => { console.log('Case Fatality Rate:', data); closeCaseFatalityRate(); }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default SetParametersDropdown;
