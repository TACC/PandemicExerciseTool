import React, { useState, useEffect } from 'react';
import './AddInitialCases.css'; // Import the CSS file for styling
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
      nu: [0.000022319,0.000040975,0.000083729,0.000061809,0.000008978]
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
      nu: [0.002013710,0.000766899,0.001312944,0.000481093,0.000127993]
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
      nu: [0.000022319,0.000040975,0.000083729,0.000061809,0.000008978]
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
      nu: [0.002013710,0.000766899,0.001312944,0.000481093,0.000127993]
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
  const [nu, setNu] = useState(localStorage.getItem('nu') || [0.000022319,0.000040975,0.000083729,0.000061809,0.000008978]);
  const [vaccine_wastage_factor, setVaccineWastageFactor] = useState(parseFloat(localStorage.getItem('vaccine_wastage_factor')) || 60);
  const [antiviral_effectiveness, setAntiviralEffectiveness] = useState(parseFloat(localStorage.getItem('antiviral_effectiveness')) || 0.8);
  const [antiviral_wastage_factor, setAntiviralWastageFactor] = useState(parseFloat(localStorage.getItem('antiviral_wastage_factor')) || 60);

    // State to store values for each age group
    const [ageGroupValues, setAgeGroupValues] = useState({
        '0-4': '0.000022319',
        '5-24': '000040975',
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
    setNu(updatedNu);
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

{/*}
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
      </div> */}

      <div className="form-group" style ={{alignItems: 'center'}}>
        <label htmlFor="nu">Case Fatality Rate
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text"> Asymptomatic/Treatable/Infectious to Deceased</span>
          </span>
        </label>
    {/* Age group inputs */}
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div>
            <label htmlFor="ageGroup0-4">0-4 years: </label>
            <input
              type="number"
              id="ageGroup0-4"
              name="ageGroup0-4"
              value={ageGroupValues['0-4']}
              onChange={e => handleInputChange(e, '0-4', 0)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>
          
          <div>
            <label htmlFor="ageGroup5-24">5-24 years: </label>
            <input
              type="number"
              id="ageGroup5-24"
              name="ageGroup5-24"
              value={ageGroupValues['5-24']}
              onChange={e => handleInputChange(e, '5-24', 1)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>

          <div>
            <label htmlFor="ageGroup25-49">25-49 years: </label>
            <input
              type="number"
              id="ageGroup25-49"
              name="ageGroup25-49"
              value={ageGroupValues['25-49']}
              onChange={e => handleInputChange(e, '25-49', 2)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>

          <div>
            <label htmlFor="ageGroup50-64">50-64 years: </label>
            <input
              type="number"
              id="ageGroup50-64"
              name="ageGroup50-64"
              value={ageGroupValues['50-64']}
              onChange={e => handleInputChange(e, '50-64', 3)}
              step="0.000000001" // 9 decimal places
              min="0"
              max="100"
              placeholder="Enter decimal value"
              required
            />
          </div>

          <div>
            <label htmlFor="ageGroup65Plus">65+ years: </label>
            <input
              type="number"
              id="ageGroup65Plus"
              name="ageGroup65Plus"
              value={ageGroupValues['65+']}
              onChange={e => handleInputChange(e, '65+', 4)}
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
export default SetManually;





