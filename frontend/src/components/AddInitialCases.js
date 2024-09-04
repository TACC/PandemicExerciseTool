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

const AddInitialCases = ({ counties, onClose }) => {
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

  const handleSaveToLocalStorage = () => {
    // Build the array of objects directly from casesList
    const jsonData = casesList.map(({ county, infected, age_group }) => ({
      county,
      infected,
      age_group
    }));
  
    // Convert the JSON object to a JSON string with proper formatting
    const jsonString = JSON.stringify(jsonData);
  
    // Save the JSON string to localStorage
    localStorage.setItem('initial_infected', jsonString);

    // close the dialog
    onClose();
  };
  

  /*
  const handleDownload = () => {
    // Build the array of objects directly from casesList
    const jsonData = casesList.map(({ county, infected, age_group }) => ({
      county,
      infected,
      age_group
    }));
  
    // Convert the JSON object to a JSON string with proper formatting
    const jsonString = JSON.stringify(jsonData, null, 2);
  
    // Trigger the download of the JSON file
    const blob = new Blob([jsonString], { type: "application/json;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "initial_infected.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };*/
  

  const handleRemove = index => {
    // Remove the case at the specified index
    setCasesList(casesList.filter((_, i) => i !== index));
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
          <label htmlFor="county">Location</label>
          <Select
            id="county"
            value={selectedCounty}
            onChange={setSelectedCounty}
            options={countyOptions}
            placeholder="Select a county"
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

      <h3>Added Cases</h3>
      <table className="cases-table">
        <thead>
          <tr>
            <th>County</th>
            <th>Infected</th>
            <th>Age Group</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {casesList.map((caseItem, index) => (
            <tr key={index}>
              <td>{caseItem.county_display}</td>
              <td>{caseItem.infected}</td>
              <td>{caseItem.age_group_display}</td>
              <td>
                <button onClick={() => handleRemove(index)}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div><button onClick={handleSaveToLocalStorage}>Save</button></div>
    </div>
  );
};

export default AddInitialCases;
