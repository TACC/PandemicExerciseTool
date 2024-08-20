import React, { useState, useEffect } from 'react';
import { saveAs } from 'file-saver'; // Import FileSaver
import './Parameters.css'; // Import the CSS file for styling
const SetManually = () => {
  // Load initial state from localStorage or set default values
  const [diseaseName, setDiseaseName] = useState(localStorage.getItem('diseaseName') || '');
  const [reproductionNumber, setReproductionNumber] = useState(parseFloat(localStorage.getItem('reproductionNumber')) || 1.8);
  //const [latencyPeriod, setLatencyPeriod] = useState(parseInt(localStorage.getItem('latencyPeriod'), 10) || 5);
//  const [asymptomaticPeriod, setAsymptomaticPeriod] = useState(parseInt(localStorage.getItem('asymptomaticPeriod'), 10) || 2);
//  const [infectiousPeriod, setInfectiousPeriod] = useState(parseInt(localStorage.getItem('infectiousPeriod'), 10) || 7);
  const [beta_scale, setBetaScale] = useState(parseInt(localStorage.getItem('beta_scale'), 10) || 1);
  const [tau, setTau] = useState(parseFloat(localStorage.getItem('tau')) || 1.2);
  const [kappa, setKappa] = useState(parseFloat(localStorage.getItem('kappa')) || 1.9);
  const [gamma, setGamma] = useState(parseFloat(localStorage.getItem('gamma')) || 4.1);
  const [chi, setChi] = useState(parseFloat(localStorage.getItem('chi')) || 1.0);
  const [rho, setRho] = useState(parseFloat(localStorage.getItem('rho')) || 0.39);
//  const [nu_high, setNuHigh] = useState(localStorage.getItem('nu_high') || 'no');
  const [vaccine_wastage_factor, setVaccineWastageFactor] = useState(parseFloat(localStorage.getItem('vaccine_wastage_factor'), 10) || 60);
  const [antiviral_effectiveness, setAntiviralEffectiveness] = useState(parseFloat(localStorage.getItem('antiviral_effectiveness')) || 0.8);
  const [antiviral_wastage_factor, setAntiviralWastageFactor] = useState(parseFloat(localStorage.getItem('antiviral_wastage_factor'), 10) || 60);
  // Save state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('diseaseName', diseaseName);
  }, [diseaseName]);
  useEffect(() => {
    localStorage.setItem('reproductionNumber', reproductionNumber);
  }, [reproductionNumber]);
//  useEffect(() => {
//    localStorage.setItem('latencyPeriod', latencyPeriod);
//  }, [latencyPeriod]);
//  useEffect(() => {
//    localStorage.setItem('asymptomaticPeriod', asymptomaticPeriod);
//  }, [asymptomaticPeriod]);
//  useEffect(() => {
//    localStorage.setItem('infectiousPeriod', infectiousPeriod);
//  }, [infectiousPeriod]);
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
//  useEffect(() => {
//    localStorage.setItem('nu_high', nu_high);
//  }, [nu_high]);
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
    // Create the JSON object
    const params = {
      disease_name: diseaseName,
      R0: reproductionNumber.toString(),
      beta_scale: beta_scale.toString(),
      tau: tau.toString(),
      kappa: kappa.toString(),
      gamma: gamma.toString(),
      chi: chi,
      //nu_high: nu_high,
      vaccine_wastage_factor: vaccine_wastage_factor.toString(),
      antiviral_effectiveness: antiviral_effectiveness.toString(),
      antiviral_wastage_factor: antiviral_wastage_factor.toString()
    };
    // Convert JSON object to string
    const json = JSON.stringify({ params }, null, 2);
    // Create a blob and save it as a file
    const blob = new Blob([json], { type: 'application/json' });
    saveAs(blob, 'params.json');
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
            <span className="tooltip-text">Average latency period, in days, which corresponds to Tau in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="tau"
          value={tau}
          onChange={e => setTau(parseFloat(e.target.value, 10))}
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="kappa">
          Asymptomatic Period (days):
          <span className="tooltip">?
            <span className="tooltip-text">The time period during which an infected individual shows no symptoms but can still spread the infection, which corresponds to Kappa in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="kappa"
          value={kappa}
          onChange={e => setKappa(parseFloat(e.target.value, 10))}
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="gamma">Infectious Period (days):
          <span className="tooltip">?
            <span className="tooltip-text">Total infectious period in days (asymptomatic/treatable/infectious to recovered), which corresponds to gamma in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="gamma"
          value={gamma}
          onChange={e => setGamma(parseFloat(e.target.value, 10))}
          min="0"
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="chi">Treatment Window (days):
          <span className="tooltip">?
            <span className="tooltip-text">Treatable to infectious rate in days, which corresponds to chi in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="chi"
          value={chi}
          onChange={e => setChi(parseFloat(e.target.value, 10))}
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
          min="0"
          required
        />
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
          min="0"
          required
        />
      </div>
      {/* Add other input fields here */}
      <button type="submit">+ Add Disease</button>
    </form>
  );
};
export default SetManually;





