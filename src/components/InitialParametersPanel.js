import React, { useState } from 'react';
import Select from 'react-select';
import './InitialParametersPanel.css';

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

const InitialParametersPanel = ({ counties, onSubmit }) => {
  const [isInitialParamsOpen, setIsInitialParamsOpen] = useState(false);
  const [isInterventionsOpen, setIsInterventionsOpen] = useState(false);

  const [numberOfCases, setNumberOfCases] = useState(10000);
  const [selectedCounty, setSelectedCounty] = useState(null);
  const [selectedAgeGroup, setSelectedAgeGroup] = useState(null);
  const [selectedRiskGroup, setSelectedRiskGroup] = useState(null);

  const countyOptions = counties.map(county => ({
    value: county,
    label: county
  }));

  const openInitialParams = () => setIsInitialParamsOpen(true);
  const closeInitialParams = () => setIsInitialParamsOpen(false);

  const openInterventions = () => setIsInterventionsOpen(true);
  const closeInterventions = () => setIsInterventionsOpen(false);

  const handleInitialParamsSubmit = event => {
    event.preventDefault();
    onSubmit({
      numberOfCases,
      selectedCounty: selectedCounty ? selectedCounty.value : '',
      selectedAgeGroup: selectedAgeGroup ? selectedAgeGroup.value : '',
      selectedRiskGroup: selectedRiskGroup ? selectedRiskGroup.value : ''
    });
    closeInitialParams();
  };

  return (
    <div>
      <div className="panel-container">
        <button className="orange-button" onClick={openInitialParams}>Set Initial Parameters</button>
        <button className="orange-button" onClick={openInterventions}>Add Interventions</button>
      </div>

      {isInitialParamsOpen && (
        <div className="modal-overlay" onClick={closeInitialParams}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Initial Parameters</h2>
            <form className="form" onSubmit={handleInitialParamsSubmit}>
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

              <button type="submit">Add Cases</button>
            </form>
          </div>
        </div>
      )}

      {isInterventionsOpen && (
        <div className="modal-overlay" onClick={closeInterventions}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Interventions</h2>
            <form className="form">
              <label>
                Intervention 1:
                <input type="text" name="intervention1" />
              </label>
              <label>
                Intervention 2:
                <input type="text" name="intervention2" />
              </label>
              <button type="button" onClick={closeInterventions}>Submit</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default InitialParametersPanel;
