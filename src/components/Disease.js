import React, { useState } from 'react';
import { saveAs } from 'file-saver'; // Import FileSaver
import './Parameters.css'; // Import the CSS file for styling

const Disease = () => {
  const [diseaseName, setDiseaseName] = useState('');
  const [reproductionNumber, setReproductionNumber] = useState(1.8);
  const [latencyPeriod, setLatencyPeriod] = useState(5); // Default in days
  const [asymptomaticPeriod, setAsymptomaticPeriod] = useState(2); // Default in days
  const [infectiousPeriod, setInfectiousPeriod] = useState(7); // Default in days
  const [beta_scale, setBetaScale] = useState(65);
  const [tau, setTau] = useState(0.83333333);
  const [kappa, setKappa] = useState(0.52631579);
  const [chi, setChi] = useState('1.0');
  const [gamma, setGamma] = useState(0.24390244);
  const [nu_high, setNuHigh] = useState('no');
  const [vaccine_wastage_factor, setVaccineWastageFactor] = useState(60);
  const [antiviral_effectiveness, setAntiviralEffectiveness] = useState(0.8);
  const [antiviral_wastage_factor, setAntiviralWastageFactor] = useState(60);

  const handleSubmit = event => {
    event.preventDefault();

    // Create the JSON object
    const params = {
      disease_name: diseaseName,
      R0: reproductionNumber.toString(),
      beta_scale: beta_scale.toString(),
      tau: tau.toString(),
      kappa: kappa.toString(),
      gamma: (1 / infectiousPeriod).toString(),
      chi: chi,
      nu_high: nu_high,
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
        <label htmlFor="latencyPeriod">
          Latency Period (days):
          <span className="tooltip">?
            <span className="tooltip-text"> Average latency period, in days, which corresponds to Tau in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="latencyPeriod"
          value={latencyPeriod}
          onChange={e => setLatencyPeriod(parseInt(e.target.value, 10))}
          min="0"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="asymptomaticPeriod">
          Asymptomatic Period (days):
          <span className="tooltip">?
            <span className="tooltip-text">The time period during which an infected individual shows no symptoms but can still spread the infection, which corresponds to Kappa in the model.</span>
          </span>
        </label>
        <input
          type="number"
          id="asymptomaticPeriod"
          value={asymptomaticPeriod}
          onChange={e => setAsymptomaticPeriod(parseInt(e.target.value, 10))}
          min="0"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="infectiousPeriod">Infectious Period (days):</label>
        <input
          type="number"
          id="infectiousPeriod"
          value={infectiousPeriod}
          onChange={e => setInfectiousPeriod(parseInt(e.target.value, 10))}
          min="0"
          required
        />
      </div>

      {/* Add other input fields here */}

      <button type="submit">+ Add Disease</button>
    </form>
  );
};

export default Disease;
