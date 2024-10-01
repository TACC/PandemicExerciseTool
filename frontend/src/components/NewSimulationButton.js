import React from 'react';
import NewSimulationModal from './NewSimulationModal.js';
import { useState } from 'react';
import { createPortal } from 'react-dom';

// create a button that spawns a modal window
const NewSimulationButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const toggleModal = () => setIsModalOpen(!isModalOpen);

  const handleReset = () => {
    // clear parameters from local storage
    console.log("clearing local storage");
    localStorage.clear();
    // this is where we'll pass the GET request
    console.log("GETting reset request to Django server")
    // refresh the page
    location.reload();
  }

  return (
    <div className="reset-container">
      <button className="reset-button" onClick={toggleModal}>New Simulation</button>
      {isModalOpen && (
        <div>
          {createPortal(
            <div className="modal-overlay" onClick={toggleModal}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={toggleModal}>×</span>
                <h2>Warning!</h2>
                <p>Starting a new simulation will clear all previous parameters and erase previous simulation data. Do you wish to continue?</p>
                <div className="confirmation-buttons">
                  <button className="cancel-reset-button" onClick={toggleModal}>Cancel</button>
                  <button className="confirm-reset-button" onClick={handleReset}>Reset</button>
                </div>
              </div>
            </div>,
            document.body
          )}
        </div>
      )}
    </div>
  )
};

export default NewSimulationButton;

