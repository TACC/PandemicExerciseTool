import React from 'react';
import { useState } from 'react';
import { createPortal } from 'react-dom';

// create a button that spawns a modal window
const NewSimulationButton = ({}) => {
  const [resetModalActive, setResetModalActive] = useState(false);

  const toggleResetModal = () => setResetModalActive(!resetModalActive);

  return (
    <div className="newsim-btn-container">
      <button className="reset-button" onClick={toggleResetModal}>New Simulation</button>
      {resetModalActive && (
      <div>
          {createPortal(
            <div className="modal-overlay" onClick={toggleResetModal}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <span className="modal-close" onClick={toggleResetModal}>×</span>
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
