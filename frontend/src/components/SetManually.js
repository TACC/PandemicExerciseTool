import React, { useState, useEffect } from 'react';
import './Parameters.css'; // Import the CSS file for styling
import toggletip from  './images/toggletip.svg';

const SetManually = ({ onClose }) => {

   // Define scenarios with their corresponding values
   const scenarios = {
    "Slow Transmission, Mild Severity (2009 H1N1)": {
      id: 1,
      disease_name: "2009 H1N1",
      R0: 1.2,
      beta_scale: 10.0,
      tau: 1.2,
      kappa: 1.9,
      gamma: 4.1,
      chi: 1.0,
      rho: 0.39,
      nu: "low"
    },
    "Slow Transmission, High Severity (1918 Influenza)": {
      id: 2,
      disease_name: "1918 Influenza",
      R0: 1.2,
      beta_scale: 10.0,
      tau: 1.2,
      kappa: 1.9,
      gamma: 4.1,
      chi: 1.0,
      rho: 0.39,
      nu: "high"
    },
    "Fast Transmission, Mild Severity (2009 H1N1)": {
      id: 3,
      disease_name: "2009 H1N1",
      R0: 1.8,
      beta_scale: 10.0,
      tau: 1.2,
      kappa: 1.9,
      gamma: 4.1,
      chi: 1.0,
      rho: 0.39,
      nu: "low"
    },
    "Fast Transmission, High Severity (1918 Influenza)": {
      id: 4,
      disease_name: "1918 Influenza",
      R0: 1.8,
      beta_scale: 10.0,
      tau: 1.2,
      kappa: 1.9,
      gamma: 4.1,
      chi: 1.0,
      rho: 0.39,
      nu: "high"
    }
  };

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
  const [nu, setNuHigh] = useState(localStorage.getItem('nu') || 'high');
  const [vaccine_wastage_factor, setVaccineWastageFactor] = useState(parseFloat(localStorage.getItem('vaccine_wastage_factor')) || 60);
  const [antiviral_effectiveness, setAntiviralEffectiveness] = useState(parseFloat(localStorage.getItem('antiviral_effectiveness')) || 0.8);
  const [antiviral_wastage_factor, setAntiviralWastageFactor] = useState(parseFloat(localStorage.getItem('antiviral_wastage_factor')) || 60);


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
        setNuHigh(scenario.nu);
      }
    };
  // Save state to localStorage when it changes
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
    localStorage.setItem('nu', nu);
  }, [nu]);

  useEffect(() => {
    localStorage.setItem('vaccine_wastage_factor', vaccine_wastage_factor);
  }, [vaccine_wastage_factor]);

  useEffect(() => {
    localStorage.setItem('antiviral_effectiveness', antiviral_effectiveness);
  }, [antiviral_effectiveness]);

  useEffect(() => {
    localStorage.setItem('antiviral_wastage_factor', antiviral_wastage_factor);
  }, [antiviral_wastage_factor]);

  const handleSubmit = event => {
    event.preventDefault();
    // Save the parameters to localStorage
    const params = {
      disease_name: diseaseName,
      R0: reproductionNumber.toString(),
      beta_scale: beta_scale.toString(),
      tau: tau.toString(),
      kappa: kappa.toString(),
      gamma: gamma.toString(),
      chi: chi.toString(),
      rho: rho.toString(),
      nu: nu.toString(),
      vaccine_wastage_factor: vaccine_wastage_factor.toString(),
      antiviral_effectiveness: antiviral_effectiveness.toString(),
      antiviral_wastage_factor: antiviral_wastage_factor.toString(),
    };

    Object.keys(params).forEach(key => {
      localStorage.setItem(key, params[key]);
    });

    // Optionally close the form or notify parent component
    if (onClose) {
      onClose(); // Call the onClose function to close the form
    }
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
          value={diseaseName}
          onChange={e => setDiseaseName(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="reproductionNumber">Reproduction Number (R0)
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">The contagiousness of the virus at a given point in time and roughly corresponds to the average number of people a typical case will infect</span>
          </span>
        </label>
        <input
          type="number"
          id="reproductionNumber"
          className="centered-input"
          value={reproductionNumber}
          onChange={e => setReproductionNumber(parseFloat(e.target.value))}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="tau">
          Latency Period (days)
          <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Time period in which an exposed individual is not yet infectious</span>
          </span>
        </label>
        <input
          type="number"
          id="tau"
          className="centered-input"
          value={tau}
          onChange={e => setTau(parseFloat(e.target.value))}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="kappa">
          Asymptomatic Period (days)
          <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">The time period during which an infected individual shows no symptoms but can still spread the infection</span>
          </span>
        </label>
        <input
          type="number"
          id="kappa"
          className="centered-input"
          value={kappa}
          onChange={e => setKappa(parseFloat(e.target.value, 10))}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="gamma">Infectious Period (days)
          <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Total time period during which a transmitting individual (asymptomatic, treatable, infectious) can spread the infection before recovery</span>
          </span>
        </label>
        <input
          type="number"
          id="gamma"
          className="centered-input"
          value={gamma}
          onChange={e => setGamma(parseFloat(e.target.value, 10))}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="chi">Therapeutic Window (days)
          <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Period in which treatment can be dispensed</span>
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

      <div className="form-group" style ={{alignItems: 'center'}}>
        <label htmlFor="nu">Case Fatality Rate
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text"> Asymptomatic/Treatable/Infectious to Deceased</span>
          </span>
        </label>
        <div style={{ display: 'flex', gap: '10px'}}>
          <div>
            <input
              type="radio"
              id="nuHighYes"
              name="nu"
              value="high"
              checked={nu === 'high'}
              onChange={e => setNuHigh(e.target.value)}
              required
            />
            <label htmlFor="nuHighYes">1918 Influenza <br></br>(High) </label>
          </div>
          <div>
            <input
              type="radio"
              id="nuHighNo"
              name="nu"
              value="low"
              checked={nu === 'low'}
              onChange={e => setNuHigh(e.target.value)}
              required
            />
            <label htmlFor="nuHighNo">2009 H1N1 <br></br> (Low)</label>
          </div>
        </div>
      </div>
      <button type="submit" className="save-button">Save</button>
    </form>
  );
};
export default SetManually;





