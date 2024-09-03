import React from 'react';
import './Parameters.css'; // Import the CSS file for styling

const SavedParameters = () => {
  // Retrieve parameters from localStorage
  const parameters = {
    DiseaseName: localStorage.getItem('diseaseName') || 'N/A',
    ReproductionNumber: localStorage.getItem('reproductionNumber') || 'N/A',
    BetaScale: localStorage.getItem('beta_scale') || 'N/A',
    Tau: localStorage.getItem('tau') || 'N/A',
    Kappa: localStorage.getItem('kappa') || 'N/A',
    Gamma: localStorage.getItem('gamma') || 'N/A',
    Chi: localStorage.getItem('chi') || 'N/A',
    Rho: localStorage.getItem('rho') || 'N/A',
    Nu: localStorage.getItem('nu') || 'N/A',
    //VaccineWastageFactor: localStorage.getItem('vaccine_wastage_factor') || 'N/A',
    //AntiviralEffectiveness: localStorage.getItem('antiviral_effectiveness') || 'N/A',
    //AntiviralWastageFactor: localStorage.getItem('antiviral_wastage_factor') || 'N/A',
  };

  // Map of user-friendly labels
  const labels = {
    DiseaseName: 'Disease Name',
    ReproductionNumber: 'Reproduction Number',
    BetaScale: 'Beta Scale',
    Tau: 'Latency Period',
    Kappa: 'Asymptomatic Period',
    Gamma: 'Infectious Period',
    Chi: 'Treatment Window',
    Rho: 'Traveler Contact Rate',
    Nu: 'High/Low Death Rate',
    //VaccineWastageFactor: 'Vaccine Wastage Factor',
    //AntiviralEffectiveness: 'Antiviral Effectiveness',
    //AntiviralWastageFactor: 'Antiviral Wastage Factor',
  };

  return (
    <div className="saved-parameters-panel">
      <table className="parameters-table">
        <thead>
          <tr>
            <th>Parameter</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.keys(parameters).map(key => (
            <tr key={key}>
              <td>{labels[key]}</td>
              <td>{parameters[key]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SavedParameters;
