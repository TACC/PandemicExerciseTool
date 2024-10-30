// a form for collecting location and age group data for starting cases. The simulation will not
// run if the user doesn't specify initial cases
// clicking the "Initial Cases" button in the <SetScenario /> dropdown or the Edit button when
// hovering over initial cases in <DisplayedParameters /> will render this component
import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import './InitialCases.css'; // Import the CSS file for styling

const texasMapping = require('../../data/texasMapping.json'); // Import the Texas mapping JSON

const ageGroupMapping = {
  '0-4 years': '0',
  '5-24 years': '1',
  '25-49 years': '2',
  '50-64 years': '3',
  '65+ years': '4'
};

const InitialCasesForm = ({ counties, onClose, casesChange }) => {
  const [numberOfCases, setNumberOfCases] = useState(100);
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

  // Load saved cases from localStorage on component mount
  useEffect(() => {
    const savedCases = localStorage.getItem('initial_infected');
    if (savedCases) {
      const parsedCases = JSON.parse(savedCases);
      console.log('Loaded cases from localStorage:', parsedCases); // Log loaded cases
      setCasesList(parsedCases);
    }
  }, []);

  // Save cases to localStorage whenever the cases list changes
  useEffect(() => {
    if (casesList.length > 0) {
      localStorage.setItem('initial_infected', JSON.stringify(casesList));
      console.log('Saved cases to localStorage:', casesList); // Log saved cases
    }
  }, [casesList]);

  const handleSubmit = event => {
    event.preventDefault();

    // Ensure both county and age group are selected before adding
    if (!selectedCounty || !selectedAgeGroup) {
      alert('Please select both a county and an age group.');
      return;
    }

    // Get the county name and ID from the texasMapping.json
    const countyName = selectedCounty.label;
    const countyId = texasMapping[countyName] || '';

    // Map age group to number
    const ageGroupNumber = ageGroupMapping[selectedAgeGroup.value] || '';

    // Create a new case object
    const newCase = {
      county: countyId,
      infected: numberOfCases,
      age_group: ageGroupNumber,
      county_display: countyName, // Store the display name for county
      age_group_display: selectedAgeGroup.label // Store the display name for age group
    };

    // Update the cases list
    setCasesList(prevCasesList => [...prevCasesList, newCase]);

    // Reset form fields
    setNumberOfCases(100);
    setSelectedCounty(null);
    setSelectedAgeGroup(null);
  };

  const handleRemove = index => {
    // Remove the case at the specified index
    setCasesList(casesList.filter((_, i) => i !== index));
  };

  const handleSaveToLocalStorage = () => {
    // Explicitly save the cases and close the dialog
    localStorage.setItem('initial_infected', JSON.stringify(casesList));
    console.log('Explicitly saved cases before closing:', casesList); // Log the save
    casesChange();    // show changes in left-hand summary pane
    onClose();
  };

  return (
    <div>
      <h6>You can add multiple initial cases.</h6>
      <form className="add-initial-cases-form" onSubmit={handleSubmit}>
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
          <label htmlFor="numberOfCases">Number of Cases</label>
          <input
            type="number"
            id="numberOfCases"
            className= "centered-input"

            value={numberOfCases}
            onChange={e => setNumberOfCases(e.target.value)}
            required
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

        <button className="save_button" type="submit">+ Add Cases</button>
      </form>

      <h2>Added Cases</h2>
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
                <button className="remove-button" onClick={() => handleRemove(index)}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div>
        <button onClick={handleSaveToLocalStorage}  className="save_button" >Save and Close</button>
      </div>
    </div>
  );
};

export default InitialCasesForm;
