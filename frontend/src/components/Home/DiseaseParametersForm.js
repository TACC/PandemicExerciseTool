// a form for gathering user specifications for disease parameters with the option to use preset scenarios
// clicking the "Disease Parameters" button in the <SetScenario /> dropdown will render this component

import React, { useState, useEffect } from 'react';
import './InitialCases.css'; // Import the CSS file for styling
import toggletip from  '../images/toggletip.svg';
import scenarios from '../../data/scenarios.js';

const DiseaseParametersForm = ({ onClose, scenarioChange }) => {
  // Load initial state from localStorage or set default values
  const [selectedScenario, setSelectedScenario] = useState('');
  const [diseaseName, setDiseaseName] = useState(localStorage.getItem('diseaseName') || '');
  const [reproductionNumber, setReproductionNumber] = useState(parseFloat(localStorage.getItem('reproductionNumber')) || 1.2);
  const [beta_scale, setBetaScale] = useState(parseFloat(localStorage.getItem('beta_scale'), 10) || 10);
  const [tau, setTau] = useState(parseFloat(localStorage.getItem('tau')) || 1.2);
  const [kappa, setKappa] = useState(parseFloat(localStorage.getItem('kappa')) || 1.9);
  const [gamma, setGamma] = useState(parseFloat(localStorage.getItem('gamma')) || 4.1);
  const [chi, setChi] = useState(parseFloat(localStorage.getItem('chi')) || 1.0);
  const [rho, setRho] = useState(parseFloat(localStorage.getItem('rho')) || 0.39);
  // const [nu, setNu] = useState(localStorage.getItem('nu') || [0.000022319,0.000040975,0.000083729,0.000061809,0.000008978]);
  const [nuText, setNuText] = useState(localStorage.getItem('nu') || "0.000022319,0.000040975,0.000083729,0.000061809,0.000008978");
  const [nu, setNu] = useState(nuText.split(',') || [0.000022319,0.000040975,0.000083729,0.000061809,0.000008978]);

  const[paramsObject, setParamsObject] = useState({
    diseaseName: localStorage.getItem('diseaseName') || '',
    reproductionNumber: parseFloat(localStorage.getItem('reproductionNumber')) || 1.2,
    beta_scale: parseFloat(localStorage.getItem('beta_scale'), 10) || 10,
    tau: parseFloat(localStorage.getItem('tau')) || 1.2,
    kappa: parseFloat(localStorage.getItem('kappa')) || 1.9,
    gamma: parseFloat(localStorage.getItem('gamma')) || 4.1,
    chi: parseFloat(localStorage.getItem('chi')) || 1.0,
    rho: parseFloat(localStorage.getItem('rho')) || 0.39,
    nuText: localStorage.getItem('nu') || "0.000022319,0.000040975,0.000083729,0.000061809,0.000008978",
    nu: nuText.split(",") || [0.000022319,0.000040975,0.000083729,0.000061809,0.000008978]
  });

  // change handler used to update paramsObject when input fields are changed
  const handleChanges = e => {
    const { name, value } = e.target;
    setParamsObject(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  // State to store values for each age group
  const [ageGroupValues, setAgeGroupValues] = useState({
    '0-4': '0.000022319',
    '5-24': '0.000040975',
    '25-49': '0.000083729',
    '50-64': '0.000061809',
    '65+': '0.000008978'
  });

  // Function to update the form with scenario values
  const handleScenarioChange = (event) => {
    const scenarioName = event.target.value;
    setSelectedScenario(scenarioName);
    const scenario = scenarios[scenarioName];
    if (scenario) {
      setDiseaseName(scenario.disease_name);
      setReproductionNumber(scenario.R0);
      setBetaScale(scenario.beta_scale);
      setTau(scenario.tau);
      setKappa(scenario.kappa);
      setGamma(scenario.gamma);
      setChi(scenario.chi);
      setRho(scenario.rho);
      setNu(scenario.nu);
      setAgeGroupValues({
        '0-4': scenario.nu[0]?.toString() || 0.000022319,
        '5-24': scenario.nu[1]?.toString() || 0.000040975,
        '25-49': scenario.nu[2]?.toString() || 0.000083729,
        '50-64': scenario.nu[3]?.toString() || 0.000061809,
        '65+': scenario.nu[4]?.toString() || 0.000008978
      });
      ///
      setParamsObject({
        diseaseName: scenario.disease_name,
        reproductionNumber: scenario.R0,
        beta_scale: scenario.beta_scale,
        tau: scenario.tau,
        kappa: scenario.kappa,
        gamma: scenario.gamma,
        chi: scenario.chi,
        rho: scenario.rho,
        nu: scenario.nu,
        nuText: scenario.nu.join()
      });
    }
  };

  // Function to handle input change and update nu array
  const handleInputChange = (event, ageGroup, index) => {
    const value = event.target.value;

    // Update age group values without validation
    setAgeGroupValues(prevState => ({
      ...prevState,
      [ageGroup]: value
    }));

    // Update the nu array with the new value for the corresponding age group
    const updatedNu = [...nu];
    updatedNu[index] = value === '' ? null : parseFloat(value); // Convert value to number or null
    setNu(updatedNu)
  };

  const handleCFRChange = (event, index) => {
    const value = event.target.value;
    const oldNuArray = paramsObject.nu;
    const newNuArray = oldNuArray.map((item, idx) => {
      if (idx === index) {
        return value;
      } else {
        return item;
      }
    });

    setParamsObject(prevState => ({
      ...prevState,
      nu: newNuArray,
      nuText: newNuArray.join()
    }));
  }

  // Save state to localStorage when it changes
  const handleSubmit = event => {
    event.preventDefault();
    // Save the parameters to localStorage

    localStorage.setItem("parameters", JSON.stringify(paramsObject));
    console.log("disease name:", paramsObject.diseaseName);

    // Optionally close the form or notify parent component
    if (onClose) {
      onClose(); // Call the onClose function to close the form
    }
    scenarioChange();    // trigger Home to rerender
  };

  return (
    <form className="parameters-form" onSubmit={handleSubmit}>
      {/* Scenario Selection Dropdown */}
      <div className="form-group">
        <label htmlFor="scenarioSelection">Load from Catalog</label>
        <select id="scenarioSelection" value={selectedScenario} onChange={handleScenarioChange}>
          <option value="" className="centered-input">--Select Scenario--</option>
          {Object.keys(scenarios).map((scenarioName) => (
            <option key={scenarioName}
            className="centered-input" 
            value={scenarioName}>
              {scenarioName}
            </option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label htmlFor="diseaseName">Scenario Name</label>
        <input
          type="text"
          id="diseaseName"
          className="centered-input"
          value={paramsObject.diseaseName}
          name="diseaseName"
          onChange={handleChanges}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="reproductionNumber">Reproduction Number (R0)
          <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Average number of secondary infections in a susceptible population</span>
          </span>
        </label>
        <input
          type="number"
          id="reproductionNumber"
          className="centered-input"
          value={paramsObject.reproductionNumber}
          name="reproductionNumber"
          onChange={handleChanges}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="tau">
          Latency period (days)
          <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Average number of days spent asymptomatic immediately after infection</span>
          </span>
        </label>
        <input
          type="number"
          id="tau"
          className="centered-input"
          value={paramsObject.tau}
          name="tau"
          onChange={handleChanges}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="kappa">
          Asymptomatic period (days)
          <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Average number of days spent infectious, but not yet symptomatic</span>
          </span>
        </label>
        <input
          type="number"
          id="kappa"
          className="centered-input"
          value={paramsObject.kappa}
          name="kappa"
          onChange={handleChanges}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="gamma">Symptomatic period (days)
          <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Average number of days spent symptomatic and infectious
            </span>
          </span>
        </label>
        <input
          type="number"
          id="gamma"
          className="centered-input"
          value={paramsObject.gamma}
          name="gamma"
          onChange={handleChanges}
          step="0.1"
          min="0"
          required
        />
      </div>
{/*}
      <div className="form-group">
        <label htmlFor="chi">Therapeutic Window (days)
          <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Period in which treatment can be dispensed</span>
          </span>
        </label>
        <input
          type="number"
          id="chi"
          className="centered-input"
          value={chi}
          onChange={e => setChi(parseFloat(e.target.value, 10))}
          step="0.1"
          min="0"
          required
        />
      </div> 
*/}
      <div className="form-group" style ={{alignItems: 'center'}}>
        <label htmlFor="nu">Infection fatality rate (proportion)
          <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Proportion of infections that lead to death</span>
          </span>
        </label>
    {/* Age group inputs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%' }}>
          <div className = "cfr-form">
            <label style = {{width: '100%'}} htmlFor="ageGroup0-4">0-4 years: </label>
            <input
              type="number"
              id="ageGroup0-4"
              name="ageGroup0-4"
              value={paramsObject.nu[0]}
              onChange={e => handleCFRChange(e, 0)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>
          <div className = "cfr-form">
            <label style = {{width: '100%'}} htmlFor="ageGroup5-24">5-24 years: </label>
            <input
              type="number"
              id="ageGroup5-24"
              name="ageGroup5-24"
              value={paramsObject.nu[1]}
              onChange={e => handleCFRChange(e, 1)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>
          <div className = "cfr-form">
            <label style = {{width: '100%'}} htmlFor="ageGroup25-49">25-49 years: </label>
            <input
              type="number"
              id="ageGroup25-49"
              name="ageGroup25-49"
              value={paramsObject.nu[2]}
              onChange={e => handleCFRChange(e, 2)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>
          <div className = "cfr-form">
            <label style = {{width: '100%'}} htmlFor="ageGroup50-64">50-64 years: </label>
            <input
              type="number"
              id="ageGroup50-64"
              name="ageGroup50-64"
              value={paramsObject.nu[3]}
              onChange={e => handleCFRChange(e, 3)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>
          <div className = "cfr-form">
            <label style = {{width: '100%'}} htmlFor="ageGroup65Plus">65+ years: </label>
            <input
              type="number"
              id="ageGroup65Plus"
              name="ageGroup65Plus"
              value={paramsObject.nu[4]}
              onChange={e => handleCFRChange(e, 4)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>
        </div>
      </div>
      
      <button type="submit" className="save_button">Save</button>
    </form>
  );
};
export default DiseaseParametersForm;





