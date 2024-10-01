import React from 'react';

const NewSimulationModal = ({isModalOpen, setIsModalOpen}) => {
  return (
    <div className="reset-dialog">
      <h2>New Simulation</h2>
      <p>Starting a new simulation will clear all previous parameters and erase previous simulation data. Do you wish to continue?</p>
      <div clasName="confirmation-buttons">
        <button className="cancel-reset-button" onClick={setIsModalOpen(false)}>Cancel</button>
        <button className="confirm-reset-button">Reset</button>
      </div>
    </div>
  )
};

export default NewSimulationModal;
