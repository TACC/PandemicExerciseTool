import React, { useState } from 'react';
import Select from 'react-select';
import './AddInitialCases.css'; // Import the CSS file for styling

const AddInitialCases = ({ counties, onSubmit }) => {
  const [numberOfCases, setNumberOfCases] = useState(10000);
  const [selectedCounty, setSelectedCounty] = useState(null);
  const [selectedAgeGroup, setSelectedAgeGroup] = useState(null);
  const [selectedRiskGroup, setSelectedRiskGroup] = useState(null);

  const ageGroups = [
    { value: '0-4 years', label: '0-4 years' },
    { value: '5-24 years', label: '5-24 years' },
    { value: '25-49 years', label: '25-49 years' },
    { value: '50-64 years', label: '50-64 years' },
    { value: '65+ years', label: '65+ years' }
  ];

  const riskGroups = [
    { value: 'low risk', label: 'Low Risk' },
    { value: 'high risk', label: 'High Risk' },
    { value: 'first responder', label: 'First Responder' },
    { value: 'pregnant women', label: 'Pregnant Women' }
  ];

  const countyOptions = counties.map(county => ({
    value: county,
    label: county
  }));

  const handleSubmit = event => {
    event.preventDefault();
    onSubmit({
      numberOfCases,
      selectedCounty: selectedCounty ? selectedCounty.value : '',
      selectedAgeGroup: selectedAgeGroup ? selectedAgeGroup.value : '',
      selectedRiskGroup: selectedRiskGroup ? selectedRiskGroup.value : ''
    });
  };

  return (
    <form className="add-initial-cases-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="numberOfCases">Number of Cases:</label>
        <input
          type="number"
          id="numberOfCases"
          value={numberOfCases}
          onChange={e => setNumberOfCases(e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="county">County:</label>
        <Select
          id="county"
          value={selectedCounty}
          onChange={setSelectedCounty}
          options={countyOptions}
          placeholder="Select a County"
          isClearable
          isSearchable
        />
      </div>

      <div className="form-group">
        <label htmlFor="ageGroup">Age Group:</label>
        <Select
          id="ageGroup"
          value={selectedAgeGroup}
          onChange={setSelectedAgeGroup}
          options={ageGroups}
          placeholder="Select Age Group"
          isClearable
          isSearchable
        />
      </div>

      <div className="form-group">
        <label htmlFor="riskGroup">Risk Group:</label>
        <Select
          id="riskGroup"
          value={selectedRiskGroup}
          onChange={setSelectedRiskGroup}
          options={riskGroups}
          placeholder="Select Risk Group"
          isClearable
          isSearchable
        />
      </div>

      <button type="submit">+ Add Cases</button>
    </form>
  );
};

export default AddInitialCases;
