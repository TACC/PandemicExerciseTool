import React, { useState } from 'react';
import Select from 'react-select';
import './AddInitialCases.css'; // Import the CSS file for styling

const texasMapping = require('./texasMapping.json'); // Import the Texas mapping JSON

const ageGroupMapping = {
  '0-4 years': '1',
  '5-24 years': '2',
  '25-49 years': '3',
  '50-64 years': '4',
  '65+ years': '5'
};

const AddInitialCases = ({ counties }) => {
  const [numberOfCases, setNumberOfCases] = useState(10000);
  const [selectedCounty, setSelectedCounty] = useState(null);
  const [selectedAgeGroup, setSelectedAgeGroup] = useState(null);
  const [casesList, setCasesList] = useState([]);

  const ageGroups = [
    { value: '0-4 years', label: '0-4 years' },
    { value: '5-24 years', label: '5-24 years' },
    { value: '25-49 years', label: '25-49 years' },
    { value: '50-64 years', label: '50-64 years' },
    { value: '65+ years', label: '65+ years' }
  ];

  const countyOptions = counties.map(county => ({
    value: county,
    label: county
  }));

  const handleSubmit = event => {
    event.preventDefault();

    // Get the county name and ID from the texasMapping.json
    const countyName = selectedCounty ? selectedCounty.label : '';
    const countyId = texasMapping[countyName] || '';

    // Map age group to number
    const ageGroupNumber = ageGroupMapping[selectedAgeGroup ? selectedAgeGroup.value : ''] || '';

    // Create a new case object
    const newCase = {
      county: countyId,
      infected: numberOfCases,
      age_group: ageGroupNumber
    };

    // Update the cases list with county name for display
    setCasesList([...casesList, { ...newCase, county_display: countyName, age_group_display: selectedAgeGroup ? selectedAgeGroup.label : '' }]);

    // Reset form fields
    setNumberOfCases(10000);
    setSelectedCounty(null);
    setSelectedAgeGroup(null);
  };

  const handleDownload = () => {
    // Build the JSON object
    const jsonData = {
      initial: {
        v: casesList.map(({ county, infected, age_group }) => ({
          county,
          infected,
          age_group
        }))
      }
    };

    // Convert JSON object to a Blob
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });

    // Create a link element and trigger the download
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'initial_cases.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <form className="add-initial-cases-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="numberOfCases">Number of Cases</label>
          <input
            type="number"
            id="numberOfCases"
            value={numberOfCases}
            onChange={e => setNumberOfCases(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="county">County</label>
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
          <label htmlFor="ageGroup">Age Group</label>
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

        <button type="submit">+ Add Cases</button>
      </form>

      <button onClick={handleDownload}>Download JSON</button>

      <div className="cases-list">
        <h3>Cases List:</h3>
        <ul>
          {casesList.map((item, index) => (
            <li key={index}>
              County Name: {item.county_display}, Cases: {item.infected}, Age Group: {item.age_group_display}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AddInitialCases;