import React, { useState } from 'react';
import Select from 'react-select';
import './CountyDropdown.css'; // Import the CSS file for styling
import texasCounties from './counties'; // Import texasCounties

const CountyDropdown = ({ onCountyChange }) => {
  const [selectedCounty, setSelectedCounty] = useState(null);

  // Convert the list of counties to options format expected by react-select
  const countyOptions = texasCounties.map(county => ({
    value: county,
    label: county
  }));

  // Handler function to update the selected county
  const handleCountyChange = selectedOption => {
    setSelectedCounty(selectedOption);
    onCountyChange(selectedOption); // Notify parent component about the selected county
  };

  return (
    <div className="county-dropdown">
      <label htmlFor="county">Select a County:</label>
      <Select
        id="county"
        value={selectedCounty}
        onChange={handleCountyChange}
        options={countyOptions}
        placeholder="Select a County"
        isClearable
        isSearchable
        className="county-select" // Apply custom className
      />
    </div>
  );
};

export default CountyDropdown;
