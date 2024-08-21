import React, { useState } from 'react';
import Select from 'react-select';

const variableOptions = [
  { value: 'asymptomatic', label: 'Asymptomatic' },
  { value: 'deceased', label: 'Deceased' },
  { value: 'exposed', label: 'Exposed' },
  { value: 'infectious', label: 'Infectious' },
  { value: 'population', label: 'Population' },
  { value: 'recovered', label: 'Recovered' },
  { value: 'susceptible', label: 'Susceptible' },
  { value: 'treatable', label: 'Treatable' },
  { value: 'treated', label: 'Treated' },
  { value: 'treatedDaily', label: 'Treated Daily' },
  { value: 'treatedIneffectiveDaily', label: 'Treated Ineffective Daily' },
  { value: 'vaccinatedDaily', label: 'Vaccinated Daily' },
  { value: 'allInfected', label: 'All Infected' },
  { value: 'ilireports', label: 'ILI Reports' },
  { value: 'vaccinatedEffective', label: 'Vaccinated Effective' },
  { value: 'vaccinatedLagPeriod', label: 'Vaccinated Lag Period' },
];

const stratifyOptions = [
  { value: 'ageGroup', label: 'Age Group' },
  { value: 'riskGroup', label: 'Risk Group' },
  { value: 'vaccinated', label: 'Vaccinated' },
];

const ageFilterOptions = [
  { value: '0-4', label: '0-4 years' },
  { value: '5-24', label: '5-24 years' },
  { value: '25-49', label: '25-49 years' },
  { value: '50-64', label: '50-64 years' },
  { value: '65+', label: '65+ years' },
];

const riskFilterOptions = [
  { value: 'lowRisk', label: 'Low Risk' },
  { value: 'highRisk', label: 'High Risk' },
  { value: 'firstResponder', label: 'First Responder' },
  { value: 'pregnantWomen', label: 'Pregnant Women' },
];

function ChartParameters({ counties }) {
  const countyOptions = counties.map(county => ({
    value: county,
    label: county
  }));

  const [selectedVariable, setSelectedVariable] = useState(null);
  const [selectedCounty, setSelectedCounty] = useState(null);
  const [selectedStratify, setSelectedStratify] = useState(null);
  const [selectedAgeFilter, setSelectedAgeFilter] = useState(null);
  const [selectedRiskFilter, setSelectedRiskFilter] = useState(null);

  return (
    <div>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap' }}>
          <Select
            placeholder="Asymptomatic"
            options={variableOptions}
            value={selectedVariable}
            onChange={setSelectedVariable}
            style={{ minWidth: '200px' }}
          />
          <span> infections in </span>
          <Select
            placeholder="Anderson"
            options={countyOptions}
            value={selectedCounty}
            onChange={setSelectedCounty}
            style={{ minWidth: '200px' }}
          />
          <span> counties. </span>
        </div>
        <div style={{ marginTop: '10px' }}>
          <span>Stratified by:</span>
          <Select
            placeholder="None"
            options={stratifyOptions}
            value={selectedStratify}
            onChange={setSelectedStratify}
            style={{ minWidth: '200px' }}
          />
          <span> Filter by: </span>
          <Select
            placeholder="Age Group"
            options={ageFilterOptions}
            value={selectedAgeFilter}
            onChange={setSelectedAgeFilter}
            style={{ minWidth: '200px' }}
          />
          <span> </span>
          <Select
            placeholder="Risk Group"
            options={riskFilterOptions}
            value={selectedRiskFilter}
            onChange={setSelectedRiskFilter}
            style={{ minWidth: '200px' }}
          />
          <span>.</span>
        </div>
      </div>
    </div>
  );
}
export default ChartParameters;
