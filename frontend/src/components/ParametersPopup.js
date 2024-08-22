import React, { useState } from 'react';
import './ParametersPopup.css'; // Import custom styles for the popup

const ParametersPopup = () => {
  const [isPopupOpen, setIsPopupOpen] = useState(false);

  const togglePopup = () => {
    setIsPopupOpen(!isPopupOpen);
  };

  return (
    <div className="parameters-popup-container">
      <button className="parameters-button" onClick={togglePopup}>
        Set Parameters
      </button>

      {isPopupOpen && (
        <div className="popup">
          <div className="popup-content">
            <h2>Set Initial Parameters</h2>
            <p>Default values from COVID</p>

            <div className="popup-section">
              <h3>Disease</h3>
              {/* Additional content for Disease section */}
            </div>

            <div className="popup-section">
              <h3>Initial Cases</h3>
              {/* Additional content for Initial Cases section */}
            </div>

            <div className="popup-section">
              <h3>Case Fatality Rate</h3>
              {/* Additional content for Case Fatality Rate section */}
            </div>

            <button className="close-button" onClick={togglePopup}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParametersPopup;
