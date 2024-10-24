// the main component for "User Guide" view, where components inside /UserGuide/ directory are invoked and rendered
// when the user clicks on the "User Guide" button in the header, this file is what they see
import React from 'react';
import { useState, useEffect, useRef } from "react";
import './UserGuide.css'; // Ensure this CSS file is updated
import ModelInfo from './ModelInfo';
import Instructions from './Instructions';
import appendixData from '../../data/appendixData.js';

const UserGuideView = () => {
  const [toggleModelInfo, setToggleModelInfo] = useState(false);
  const [toggleInstructions, setToggleInstructions] = useState(false);
  const [heightInfo, setHeightInfo] = useState();
  const [heightInstructions, setHeightInstructions] = useState();

  const modelInfoToggler = () => {
    setToggleModelInfo(!toggleModelInfo);
  };

  const instructionsToggler = () => {
    setToggleInstructions(!toggleInstructions);
  };

  const AccordionItem = ({ title, children }) => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleAccordion = () => {
      setIsOpen(!isOpen);
    };

    return (
      <div>
        <button onClick={toggleAccordion} style={styles.accordionButton}>
          {title}
        </button>
        {isOpen && (
          <div style={styles.accordionContent}>
            {children}
          </div>
        )}
      </div>
    );
  };

  // styles for accordion and its children
  const styles = {
    accordionButton: {
      width: '100%',
      padding: '25px 16px',
      fontSize: 'larger',
      fontWeight: 'bold',
      borderRadius: '4px',
      textAlign: 'left',
      background: '#f7b13c',
      border: 'none',
      cursor: 'pointer',
      outline: 'none',
    },
    accordionContent: {
      padding: '10px',
      background: 'f9f9f9',
      border: '1px solid #ccc',
      borderRadius: '4px',
    },
  };

  return (
    <div className="user-guide-view">
      <section className="text">
        <h2>Interactive Outbreak Simulator</h2>
        <h3>Updated as of 10/11/2024</h3>
        <a href="https://github.com/TACC/PandemicExerciseSimulator" target="_blank" rel="noopener noreferrer" className="github-link">
        https://github.com/TACC/PandemicExerciseSimulator
        </a>
        <p id="ptag-separator"></p>
        <p className="needed-section">
          <strong>Needed: </strong>This tool is still in development and will benefit from testing and expert review. In particular, we need:
        </p>
        <ul className="bullet-points">
          <li>Review of the Stochastic SEATIRD Disease Model implementation.</li>
          <li>Review of the Binomial Travel Model implementation.</li>
          <li>A range of example input data and parameters, as well as expected outputs for testing and verification.</li>
        </ul>
      </section>
      <div className="accordion">
        <AccordionItem title="Instructions">
          <Instructions />
        </AccordionItem>
        <p style={{ background: "white", padding: "0.75em", marginBottom: "0" }}></p>
        <AccordionItem title="About the Model">
          <ModelInfo />
        </AccordionItem>
      </div>
      {/* <Instructions /> */}
      {/* <ModelInfo /> */}
    </div>
  )
};


export default UserGuideView;
