import React, { useState, useEffect } from 'react';
import { saveAs } from 'file-saver'; // Import FileSaver
import Select from 'react-select';
import './ParametersInitialCases.css'; // Ensure correct CSS import

const texasMapping = require('./texasMapping.json'); // Import the Texas mapping JSON

const ageGroupMapping = {
  '0-4 years': '1',
  '5-24 years': '2',
  '25-49 years': '3',
  '50-64 years': '4',
  '65+ years': '5'
};

const ParametersInitialCases = ({ counties }) => {
  // Parameters state
  const [diseaseName, setDiseaseName] = useState(localStorage.getItem('diseaseName') || '');
  const [reproductionNumber, setReproductionNumber] = useState(parseFloat(localStorage.getItem('reproductionNumber')) || 1.8);
  const [beta_scale, setBetaScale] = useState(parseInt(localStorage.getItem('beta_scale'), 10) || 1);
  const [tau, setTau] = useState(parseFloat(localStorage.getItem('tau')) || 1.2);
  const [kappa, setKappa] = useState(parseFloat(localStorage.getItem('kappa')) || 1.9);
  const [gamma, setGamma] = useState(parseFloat(localStorage.getItem('gamma')) || 4.1);
  const [chi, setChi] = useState(parseFloat(localStorage.getItem('chi')) || 1.0);
  const [rho, setRho] = useState(parseFloat(localStorage.getItem('rho')) || 0.39);
  const [nu_high, setNuHigh] = useState(localStorage.getItem('nu_high') || 'no');
  const [vaccine_wastage_factor, setVaccineWastageFactor] = useState(parseFloat(localStorage.getItem('vaccine_wastage_factor')) || 60);
  const [antiviral_effectiveness, setAntiviralEffectiveness] = useState(parseFloat(localStorage.getItem('antiviral_effectiveness')) || 0.8);
  const [antiviral_wastage_factor, setAntiviralWastageFactor] = useState(parseFloat(localStorage.getItem('antiviral_wastage_factor')) || 60);

  // Initial cases state
  const [numberOfCases, setNumberOfCases] = useState(10000);
  const [selectedCounty, setSelectedCounty] = useState(null);
  const [selectedAgeGroup, setSelectedAgeGroup] = useState(null);
  const [casesList, setCasesList] = useState([]);

  // Save parameters to localStorage
  useEffect(() => {
    localStorage.setItem('diseaseName', diseaseName);
  }, [diseaseName]);
  useEffect(() => {
    localStorage.setItem('reproductionNumber', reproductionNumber);
  }, [reproductionNumber]);
  useEffect(() => {
    localStorage.setItem('beta_scale', beta_scale);
  }, [beta_scale]);
  useEffect(() => {
    localStorage.setItem('tau', tau);
  }, [tau]);
  useEffect(() => {
    localStorage.setItem('kappa', kappa);
  }, [kappa]);
  useEffect(() => {
    localStorage.setItem('gamma', gamma);
  }, [gamma]);
  useEffect(() => {
    localStorage.setItem('chi', chi);
  }, [chi]);
  useEffect(() => {
    localStorage.setItem('rho', rho);
  }, [rho]);
  useEffect(() => {
    localStorage.setItem('nu_high', nu_high);
  }, [nu_high]);
  useEffect(() => {
    localStorage.setItem('vaccine_wastage_factor', vaccine_wastage_factor);
  }, [vaccine_wastage_factor]);
  useEffect(() => {
    localStorage.setItem('antiviral_effectiveness', antiviral_effectiveness);
  }, [antiviral_effectiveness]);
  useEffect(() => {
    localStorage.setItem('antiviral_wastage_factor', antiviral_wastage_factor);
  }, [antiviral_wastage_factor]);

  const handleAddCase = event => {
    event.preventDefault();

    const countyName = selectedCounty ? selectedCounty.label : '';
    const countyId = texasMapping[countyName] || '';
    const ageGroupNumber = ageGroupMapping[selectedAgeGroup ? selectedAgeGroup.value : ''] || '';

    const newCase = {
      county: countyId,
      infected: numberOfCases,
      age_group: ageGroupNumber
    };

    setCasesList([...casesList, { ...newCase, county_display: countyName, age_group_display: selectedAgeGroup ? selectedAgeGroup.label : '' }]);

    setNumberOfCases(10000);
    setSelectedCounty(null);
    setSelectedAgeGroup(null);
  };

  const handleDownload = () => {
    const params = {
      disease_name: diseaseName,
      R0: reproductionNumber.toString(),
      beta_scale: beta_scale.toString(),
      tau: tau.toString(),
      kappa: kappa.toString(),
      gamma: gamma.toString(),
      chi: chi.toString(),
      rho: rho.toString(),
      nu_high: nu_high.toString(),
      vaccine_wastage_factor: vaccine_wastage_factor.toString(),
      antiviral_effectiveness: antiviral_effectiveness.toString(),
      antiviral_wastage_factor: antiviral_wastage_factor.toString()
    };

    const initialCases = {
      initial: {
        v: casesList.map(({ county, infected, age_group }) => ({
          county,
          infected,
          age_group
        }))
      }
    };

    const combinedJson = {
      params,
      ...initialCases
    };

    const blob = new Blob([JSON.stringify(combinedJson, null, 2)], { type: 'application/json' });
    saveAs(blob, 'INPUT.json');
  };

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

  return (
    <div className="full-screen-container">
      {/* Left Panel: Add Disease */}
      <div className="left-panel">
        <h2 className="panel-title">Add Parameters</h2>
        <form className="parameters-form" onSubmit={handleAddCase}>
          <div className="form-group">
            <label htmlFor="diseaseName">Disease Name:</label>
            <input
              type="text"
              id="diseaseName"
              value={diseaseName}
              onChange={e => setDiseaseName(e.target.value)}
              required
            />
          </div>
          
          <div className="input-group">
            <div className="form-group">
              <label htmlFor="reproductionNumber">Reproduction Number (R0):</label>
              <input
                type="number"
                id="reproductionNumber"
                value={reproductionNumber}
                onChange={e => setReproductionNumber(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="tau">Latency Period (days):</label>
              <input
                type="number"
                id="tau"
                value={tau}
                onChange={e => setTau(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="kappa">Asymptomatic Period (days):</label>
              <input
                type="number"
                id="kappa"
                value={kappa}
                onChange={e => setKappa(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                required
              />
            </div>
          </div>
  
          <div className="input-group">
            <div className="form-group">
              <label htmlFor="gamma">Infectious Period (days):</label>
              <input
                type="number"
                id="gamma"
                value={gamma}
                onChange={e => setGamma(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="chi">Treatment Window (days):</label>
              <input
                type="number"
                id="chi"
                value={chi}
                onChange={e => setChi(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="rho">Traveler Contact Rate (percent):</label>
              <input
                type="number"
                id="rho"
                value={rho}
                onChange={e => setRho(parseFloat(e.target.value))}
                step="0.01"
                min="0"
                required
              />
            </div>
          </div>
  
          <div className="input-group">
            <div className="form-group">
              <label htmlFor="beta_scale">Beta Scale:</label>
              <input
                type="number"
                id="beta_scale"
                value={beta_scale}
                onChange={e => setBetaScale(parseInt(e.target.value, 10))}
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="nu_high">High Nu:</label>
              <select
                id="nu_high"
                value={nu_high}
                onChange={e => setNuHigh(e.target.value)}
              >
                <option value="no">No</option>
                <option value="yes">Yes</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="vaccine_wastage_factor">Vaccine Wastage Factor (percent):</label>
              <input
                type="number"
                id="vaccine_wastage_factor"
                value={vaccine_wastage_factor}
                onChange={e => setVaccineWastageFactor(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                required
              />
            </div>
          </div>
  
          <div className="input-group">
            <div className="form-group">
              <label htmlFor="antiviral_effectiveness">Antiviral Effectiveness (percent):</label>
              <input
                type="number"
                id="antiviral_effectiveness"
                value={antiviral_effectiveness}
                onChange={e => setAntiviralEffectiveness(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="antiviral_wastage_factor">Antiviral Wastage Factor (percent):</label>
              <input
                type="number"
                id="antiviral_wastage_factor"
                value={antiviral_wastage_factor}
                onChange={e => setAntiviralWastageFactor(parseFloat(e.target.value))}
                step="0.1"
                min="0"
                required
              />
            </div>
          </div>
  
          <div className="form-group">
            <label htmlFor="numberOfCases">Initial Number of Cases:</label>
            <input
              type="number"
              id="numberOfCases"
              value={numberOfCases}
              onChange={e => setNumberOfCases(parseInt(e.target.value, 10))}
              min="0"
              required
            />
          </div>
  
          <div className="form-group">
            <label htmlFor="county">Select County:</label>
            <Select
              id="county"
              options={countyOptions}
              value={selectedCounty}
              onChange={setSelectedCounty}
              placeholder="Select a county"
              isClearable
            />
          </div>
  
          <div className="form-group">
            <label htmlFor="ageGroup">Select Age Group:</label>
            <Select
              id="ageGroup"
              options={ageGroups}
              value={selectedAgeGroup}
              onChange={setSelectedAgeGroup}
              placeholder="Select an age group"
              isClearable
            />
          </div>
  
          <button type="submit">Add Case</button>
        </form>
      </div>
  
      {/* Right Panel: Download Data */}
      <div className="right-panel">
        <h2 className="panel-title">Initial Cases</h2>
        <button onClick={handleDownload}>Download Data</button>
  
        <h3>Added Cases</h3>
        <table className="cases-table">
          <thead>
            <tr>
              <th>County</th>
              <th>Infected</th>
              <th>Age Group</th>
            </tr>
          </thead>
          <tbody>
            {casesList.map((caseItem, index) => (
              <tr key={index}>
                <td>{caseItem.county_display}</td>
                <td>{caseItem.infected}</td>
                <td>{caseItem.age_group_display}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ParametersInitialCases;

