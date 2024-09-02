import React, { useState } from 'react';
import AddInitialCases from './AddInitialCases';
import SetManually from './SetManually';
import './SetParametersDropdown.css';

const SetParametersDropdown = ({ counties, onSave }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [isInitialCasesOpen, setIsInitialCasesOpen] = useState(false);
  const [isSetManuallyOpen, setIsSetManuallyOpen] = useState(false);

  const toggleDropdown = () => setShowDropdown(!showDropdown);
  const openInitialCases = () => {
    setIsInitialCasesOpen(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeInitialCases = () => setIsInitialCasesOpen(false);
  const openSetManually = () => {
    setIsSetManuallyOpen(true);
    setShowDropdown(false); // Close dropdown when opening modal
  };
  const closeSetManually = () => setIsSetManuallyOpen(false);

  const handleSave = () => {
    onSave(); // Trigger the save action in the parent component
    setShowDropdown(false); // Close the dropdown after saving
  };

  return (
    <div className="dropdown-container">
      <button className="parameters-button" onClick={toggleDropdown}>
        <span className="dropdown-text">Set Parameters</span>
        <span className={`dropdown-arrow ${showDropdown ? 'open' : ''}`}>▾</span>
      </button>
      {showDropdown && (
        <div className="dropdown-menu">
          <button className="dropdown-item" onClick={openSetManually}>Set Manually</button>
          <button className="dropdown-item" onClick={openInitialCases}>Initial Cases</button>
        </div>
      )}
      {isSetManuallyOpen && (
        <div className="modal-overlay" onClick={closeSetManually}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeSetManually}>×</span>
            <h2>Set Manually</h2>
            <SetManually onClose={closeSetManually} onSubmit={(data) => { console.log('Set Manually:', data); handleSave(); }} />
          </div>
        </div>
      )}
      {isInitialCasesOpen && (
        <div className="modal-overlay" onClick={closeInitialCases}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="modal-close" onClick={closeInitialCases}>×</span>
            <h2>Add Initial Cases</h2>
            <AddInitialCases counties={counties} onSubmit={(data) => { console.log('Initial Cases:', data); handleSave(); }} />
          </div>
        </div>
      )}
    </div>
  );
};

export default SetParametersDropdown;