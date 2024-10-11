import React from 'react';
import NewSimulationModal from './NewSimulationModal.js';
import { useState } from 'react';
import { createPortal } from 'react-dom';
import axios from 'axios';

// create a button that spawns a modal window
const NewSimulationButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const toggleModal = () => setIsModalOpen(!isModalOpen);

  const handleReset = async () => {
    console.log("clearing local storage");
    localStorage.clear();
    console.log("GETting reset request to Django server")
    // TODO: it might be prudent to wait for a 200 before refreshing the page
    const response = await axios.get(`http://localhost:8000/api/reset`);
    location.reload();
  }

  return (
    <div className="reset-container">
      <a className="reset-button" onClick={toggleModal}>Reset Simulation</a>
      {isModalOpen && (
        <div>
          {createPortal(
            <div className="modal-overlay" onClick={toggleModal}>
              <div className="modal-contents" onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={toggleModal}>×</span>
                <div className='reset-content'>
                  <h2 className="reset-warning">Confirm Reset</h2>
                  <p>Resetting will remove all disase and interventions parameters. Are you sure you want to continue?</p>
                  <div className="confirmation-buttons">
                    <a className="cancel-reset-button" onClick={toggleModal}>Cancel</a>
                    <button className="confirm-reset-button" onClick={handleReset}>Reset</button>
                  </div>
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

