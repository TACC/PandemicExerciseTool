import React, { useState, useEffect } from 'react';
import './Parameters.css'; // Import the CSS file for styling

const SetManually = ({ onClose }) => {
  // Load initial state from localStorage or set default values
  const [diseaseName, setDiseaseName] = useState(localStorage.getItem('diseaseName') || '');
  const [reproductionNumber, setReproductionNumber] = useState(parseFloat(localStorage.getItem('reproductionNumber')) || 1.8);
  const [beta_scale, setBetaScale] = useState(parseFloat(localStorage.getItem('beta_scale'), 10) || 1);
  const [tau, setTau] = useState(parseFloat(localStorage.getItem('tau')) || 1.2);
  const [kappa, setKappa] = useState(parseFloat(localStorage.getItem('kappa')) || 1.9);
  const [gamma, setGamma] = useState(parseFloat(localStorage.getItem('gamma')) || 4.1);
  const [chi, setChi] = useState(parseFloat(localStorage.getItem('chi')) || 1.0);
  const [rho, setRho] = useState(parseFloat(localStorage.getItem('rho')) || 0.39);
  const [nu, setNuHigh] = useState(localStorage.getItem('nu') || 'high');
  const [vaccine_wastage_factor, setVaccineWastageFactor] = useState(parseFloat(localStorage.getItem('vaccine_wastage_factor')) || 60);
  const [antiviral_effectiveness, setAntiviralEffectiveness] = useState(parseFloat(localStorage.getItem('antiviral_effectiveness')) || 0.8);
  const [antiviral_wastage_factor, setAntiviralWastageFactor] = useState(parseFloat(localStorage.getItem('antiviral_wastage_factor')) || 60);

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
        <label htmlFor="tau">
          Latency Period (days):
          <span className="tooltip">?
            <span className="tooltip-text">Average latency period, in days, which corresponds to 1/tau in the model.</span>
          </span>
        </label>
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
        <label htmlFor="kappa">
          Asymptomatic Period (days):
          <span className="tooltip">?
            <span className="tooltip-text">The time period during which an infected individual shows no symptoms but can still spread the infection, which corresponds to 1/kappa in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="kappa"
          value={kappa}
          onChange={e => setKappa(parseFloat(e.target.value, 10))}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="gamma">Infectious Period (days):
          <span className="tooltip">?
            <span className="tooltip-text">Total infectious period in days (asymptomatic/treatable/infectious to recovered), which corresponds to 1/gamma in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="gamma"
          value={gamma}
          onChange={e => setGamma(parseFloat(e.target.value, 10))}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="chi">Treatment Window (days):
          <span className="tooltip">?
            <span className="tooltip-text">Treatable to infectious rate in days, which corresponds to 1/chi in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="chi"
          value={chi}
          onChange={e => setChi(parseFloat(e.target.value, 10))}
          step="0.1"
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="rho">Traveler contact rate (percent):
          <span className="tooltip">?
            <span className="tooltip-text">Travelers contact residents at a reduced rate, rho, which is a multiplier used to reduce the age-specific mixing rate parameters.</span>
          </span>
        </label>
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

      <div className="form-group" style ={{alignItems: 'center'}}>
        <label htmlFor="nu">High/Low death rate: 
        <span className="tooltip">?
            <span className="tooltip-text"> Asymptomatic/Treatable/Infectious to Deceased, which corresponds to 1/nu in the model</span>
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
            <label htmlFor="nuHighYes">High <br></br>(1918 Influenza) </label>
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
            <label htmlFor="nuHighNo">Low <br></br> (2009 H1N1)</label>
          </div>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="vaccine_wastage_factor">Vaccine Wastage Factor (days):
          <span className="tooltip">?
            <span className="tooltip-text">Half the vaccine stockpile will be wasted every N days.</span>
          </span>
        </label>
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
      <div className="form-group">
        <label htmlFor="antiviral_wastage_factor">Antiviral Wastage Factor (days):
          <span className="tooltip">?
            <span className="tooltip-text">Half the antiviral stockpile will be wasted every N days.</span>
          </span>
        </label>
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
      <div className="form-group">
        <label htmlFor="antiviral_effectiveness">Antiviral Effectiveness (percent):
          <span className="tooltip">?
            <span className="tooltip-text">Antiviral effectiveness is the probability that an individual treated within the treatment window will recover.</span>
          </span>
        </label>
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
      {/* Add other input fields here */}
      <button type="submit">Save</button>
    </form>
  );
};
export default SetManually;





