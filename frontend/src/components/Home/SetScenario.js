// renders the Set Scenario dropdown menu on the left panel of Home view
import React, { useState } from 'react';
import InitialCasesForm from './InitialCasesForm';
import DiseaseParametersForm from './DiseaseParametersForm';
import './InitialCases.css'; // Import the CSS file for styling
import { createPortal } from 'react-dom';

const SetScenario = ({ counties, onSave, scenarioChange, casesChange }) => {
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
    scenarioChange();    // trigger Home.js to rerender with updated scenario info
    onSave(); // Trigger the save action in the parent component
    setShowDropdown(false); // Close the dropdown after saving
  };

  return (
    <div className="dropdown-container">
      <button className="parameters-button" onClick={toggleDropdown}>
        <span className="dropdown-text">Set Scenario</span>
        <span className={`dropdown-arrow ${showDropdown ? 'open' : ''}`}>▾</span>
      </button>
      {showDropdown && (
        <div className="dropdown--menu">
          <button className="dropdown-items" onClick={openSetManually}>Disease Parameters</button>
          <button className="dropdown-items" onClick={openInitialCases}>Initial Cases</button>
        </div>
      )}
      {isSetManuallyOpen && (
        <div>
          {/* Appending modal window to document.body prevents a rendering bug on Safari */}
          {createPortal(
            <div className="modal-overlay" onClick={closeSetManually}>
              <div className="modal-contents"  style={{ backgroundColor: 'white' }} onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={closeSetManually}>×</span>
                <h2>Disease Parameters</h2>
                <DiseaseParametersForm
                  onClose={closeSetManually} 
                  onSubmit={(data) => { 
                    console.log('Set Manually:', data); 
                    handleSave(); }} 
                  scenarioChange={scenarioChange}
                />
              </div>
            </div>,
            document.body
          )}
        </div>
      )}
      {isInitialCasesOpen && (
        <div>
          {createPortal(
            <div className="modal-overlay" onClick={closeInitialCases}>
              <div className="modal-contents" style={{ backgroundColor: 'white' }} onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={closeInitialCases}>×</span>
                <h2>Add Initial Cases</h2>
                <InitialCasesForm 
                  onClose={closeInitialCases} 
                  counties={counties} 
                  onSubmit={(data) => { console.log('Initial Cases:', data); handleSave(); }} 
                  casesChange={casesChange}
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

export default SetScenario;
