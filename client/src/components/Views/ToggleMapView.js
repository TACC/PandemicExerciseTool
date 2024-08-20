import React, { useState, useEffect } from 'react';
import ILIView from './ILIView';
import InfectedView from './InfectedView';
import AntiviralsView from './AntiviralsView';
import VaccineView from './VaccineView';
import TexasChoropleth from '../TexasChoropleth';
import './ToggleMapView.css';
import InitialMap from '../InitialMap';
const ToggleMapView = () => {
  const [view, setView] = useState('ili');
  const [selectedDay, setSelectedDay] = useState(1); // Example: Start from day 1
  const [outputData, setOutputData] = useState(null); // State to hold output data

  const handleButtonClick = (selectedView) => {
    setView(selectedView);
  };

  // Function to load output data based on selected day
  const loadOutputData = async (day) => {
    try {
      // Dynamically import the JSON file based on day
      const response = await fetch(`/components/OUTPUT_${day}.json`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setOutputData(data);
    } catch (error) {
      console.error(`Error loading OUTPUT_${day}.json:`, error);
      setOutputData(null); // Reset output data on error
    }
  };

  // Load the output data for the current selected day on initial render
  useEffect(() => {
    loadOutputData(selectedDay);
  }, [selectedDay]);

  return (
    <div>
      <div className="button-group">
        <button className={`view-button ${view === 'ili' ? 'active' : ''}`} onClick={() => handleButtonClick('ili')}>ILI View</button>
        <button className={`view-button ${view === 'infected' ? 'active' : ''}`} onClick={() => handleButtonClick('infected')}>Infected</button>
        <button className={`view-button ${view === 'antivirals' ? 'active' : ''}`} onClick={() => handleButtonClick('antivirals')}>Antivirals Stockpile</button>
        <button className={`view-button ${view === 'vaccines' ? 'active' : ''}`} onClick={() => handleButtonClick('vaccines')}>Vaccines Stockpile</button>
      </div>
      {/* Render the corresponding view based on the selected state */}
      {view === 'ili' && <InitialMap outputData={outputData} />}
      {view === 'infected' && <InfectedView />}
      {view === 'antivirals' && <AntiviralsView />}
      {view === 'vaccines' && <VaccineView />}
    </div>
  );
};

export default ToggleMapView;