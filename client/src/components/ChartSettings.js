import React, { useState } from 'react';
import Select from 'react-select';
import './ChartSettings.css';

const ChartSettings = ({ counties, onSubmit }) => {
    const [numberOfCases, setNumberOfCases] = useState(10000);
    const [selectedCounty, setSelectedCounty] = useState(null);
    const [selectedAgeGroup, setSelectedAgeGroup] = useState(null);
    const [selectedRiskGroup, setSelectedRiskGroup] = useState(null);
    const [selectedVaccinationGroup, setVaccinationGroup] = useState(null);
    const [selectedStratificationGroup, setStratificationGroup] = useState(null);
    const [selectedVariableGroup, setVariableGroup] = useState(null);
  
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

    const vaccinationGroups = [
        {value: 'vaccinated', label: 'Vaccinated'},
        {value: 'unvaccinated', label: 'Unvaccinated'}
    ];

    const stratificationGroups = [
        {value: 'agegroup', label: 'Age Group'},
        {value: 'riskgroup', label: 'Risk Group'},
        {value: 'vaccinated', label: 'Vaccinated'}
    ]

    const variableGroups = [
        {value: 'asymptomatic', label:'Asymptomatic'},
        {value: 'deceased', label:'Deceased'},
        {value: 'exposed', label:'Exposed'},
        {value: 'infectious', label:'Infectious'},
        {value: 'population', label:'Population'},
        {value: 'recovered', label:'Recovered'},
        {value: 'susceptible', label:'Susceptible'},
        {value: 'treatable', label:'Treatable'},
        {value: 'treated', label:'Treated'},
        {value: 'treateddaily', label:'Treated (Daily)'},
        {value: 'treatedineffectivedaily', label:'Treated (Ineffective Daily)'},
        {value: 'vaccinateddaily', label:'Vaccinated (Daily)'},
        {value: 'allinfected', label:'All Infected'},
        {value: 'ilireports', label:'ILI reports'},
        {value: 'vaccinatedeffective', label:'Vaccinated effective'},
        {value: 'vaccinatedlagperiod', label:'Vaccinated in lag period'},
    ]
  
    const handleSubmit = event => {
      event.preventDefault();
      onSubmit({
        numberOfCases,
        selectedCounty: selectedCounty ? selectedCounty.value : '',
        selectedAgeGroup: selectedAgeGroup ? selectedAgeGroup.value : '',
        selectedRiskGroup: selectedRiskGroup ? selectedRiskGroup.value : '',
        selectedVaccinationGroup: selectedVaccinationGroup ? selectedVaccinationGroup.value : '',
        selectedStratificationGroup: selectedStratificationGroup ? selectedStratificationGroup.value : ''

      });
    };
  
    return (
      <form className="add-chart-settings-form" onSubmit={handleSubmit}>

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
          <label htmlFor="stratificationGroup">Stratification Groups:</label>
          <Select
            id="stratificationGroup"
            value={selectedStratificationGroup}
            onChange={setStratificationGroup}
            options={stratificationGroups}
            placeholder="Stratify By:"
            isClearable
            isSearchable
          />
        </div>

        <div className="form-group">
          <label htmlFor="variableGroup">Variable Groups:</label>
          <Select
            id="variableGroup"
            value={selectedVariableGroup}
            onChange={setVariableGroup}
            options={variableGroups}
            placeholder="Stratify By:"
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

        <div className="form-group">
          <label htmlFor="vaccinationGroup">Vaccination Status:</label>
          <Select
            id="vaccinationGroup"
            value={selectedVaccinationGroup}
            onChange={setVaccinationGroup}
            options={vaccinationGroups}
            placeholder="Select Vaccination Group"
            isClearable
            isSearchable
          />
        </div>
  
        <button type="submit">Add Settings</button>
      </form>
    );
};

export default ChartSettings;
