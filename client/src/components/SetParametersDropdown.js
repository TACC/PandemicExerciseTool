import React, { useState } from 'react';
import AddInitialCases from './AddInitialCases';
import CaseFatalityRate from './CaseFatalityRate';
import SetManually from './SetManually';
import './Dropdown.css';

const SetParametersDropdown = ({ counties }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [isInitialCasesOpen, setIsInitialCasesOpen] = useState(false);
  const [isCaseFatalityRateOpen, setIsCaseFatalityRateOpen] = useState(false);
  const [isSetManually, setIsSetManually] = useState(false);

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
  const openSetManually = () => {
    setIsSetManually(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeSetManually = () => setIsSetManually(false);

  return (
    <div className="dropdown-container" id="first-drop">
      <button className="parameters-button" onClick={toggleDropdown}>
        <span className="dropdown-text">Set Parameters</span>
        <span className={`dropdown-arrow ${showDropdown ? 'open' : ''}`}>▾</span>
      </button>
      {showDropdown && (
        <div className="dropdown-menu">
          <button className="dropdown-item" onClick={openSetManually}>Set Manually</button>
          <button className="dropdown-item" onClick={openInitialCases}>Initial Cases</button>
          <button className="dropdown-item" onClick={openCaseFatalityRate}>Case Fatality Rate</button>
        </div>
      )}
      {isSetManually && (
         <div style={{ position: 'relative', zIndex: 20000 }}>
        <div className="modal-overlay" onClick={closeSetManually}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeSetManually}>×</span>
            <h2>Set Manually</h2>
            <SetManually onSubmit={(data) => { console.log('Set Manually:', data); closeSetManually(); }} />
          </div>
        </div>
        </div>
      )}
      {isInitialCasesOpen && (
        <div className="modal-overlay" onClick={closeInitialCases}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeInitialCases}>×</span>
            <h2>Add Initial Cases</h2>
            <AddInitialCases counties={counties} onSubmit={(data) => { console.log('Initial Cases:', data); closeInitialCases(); }} />
          </div>
        </div>
      )}
      {isCaseFatalityRateOpen && (
        <div className="modal-overlay" onClick={closeCaseFatalityRate}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeCaseFatalityRate}>×</span>
            <h2>Case Fatality Rate</h2>
            <CaseFatalityRate onSubmit={(data) => { console.log('Case Fatality Rate:', data); closeCaseFatalityRate(); }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default SetParametersDropdown;
