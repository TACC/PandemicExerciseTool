import React from 'react';
import NewSimulationModal from './NewSimulationModal.js';
import { useState } from 'react';
import { createPortal } from 'react-dom';

// create a button that spawns a modal window
const NewSimulationButton = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const toggleModal = () => setIsModalOpen(!isModalOpen);

  return (
    <div className="reset-container">
      <button className="reset-button" onClick={toggleModal}>New Simulation</button>
      {isModalOpen && (
        <div>
          {createPortal(
            <div className="modal-overlay" onClick={toggleModal}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={toggleModal}>×</span>
                <NewSimulationModal />
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

