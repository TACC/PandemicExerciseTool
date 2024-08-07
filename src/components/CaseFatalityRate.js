import React, { useState } from 'react';

const CaseFatalityRate = ({ onSubmit }) => {
  const [caseFatalityRates, setCaseFatalityRates] = useState({
    '0-4 years': 0,
    '5-24 years': 0,
    '25-49 years': 0,
    '50-64 years': 0,
    '65+ years': 0
  });

  const handleSubmit = event => {
    event.preventDefault();
    onSubmit(caseFatalityRates);
  };

  const handleCaseFatalityRateChange = (ageGroup, value) => {
    setCaseFatalityRates(prevState => ({
      ...prevState,
      [ageGroup]: value
    }));
  };

  return (
    <form className="parameters-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="age0-4">0-4 years:</label>
        <div className="input-group">
          <input
            type="number"
            id="age0-4"
            value={caseFatalityRates['0-4 years']}
            onChange={e => handleCaseFatalityRateChange('0-4 years', parseInt(e.target.value, 10))}
            min="0"
            required
          />
          <span className="input-suffix">%</span>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="age5-24">5-24 years:</label>
        <div className="input-group">
          <input
            type="number"
            id="age5-24"
            value={caseFatalityRates['5-24 years']}
            onChange={e => handleCaseFatalityRateChange('5-24 years', parseInt(e.target.value, 10))}
            min="0"
            required
          />
          <span className="input-suffix">%</span>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="age25-49">25-49 years:</label>
        <div className="input-group">
          <input
            type="number"
            id="age25-49"
            value={caseFatalityRates['25-49 years']}
            onChange={e => handleCaseFatalityRateChange('25-49 years', parseInt(e.target.value, 10))}
            min="0"
            required
          />
          <span className="input-suffix">%</span>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="age50-64">50-64 years:</label>
        <div className="input-group">
          <input
            type="number"
            id="age50-64"
            value={caseFatalityRates['50-64 years']}
            onChange={e => handleCaseFatalityRateChange('50-64 years', parseInt(e.target.value, 10))}
            min="0"
            required
          />
          <span className="input-suffix">%</span>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="age65+">65+ years:</label>
        <div className="input-group">
          <input
            type="number"
            id="age65+"
            value={caseFatalityRates['65+ years']}
            onChange={e => handleCaseFatalityRateChange('65+ years', parseInt(e.target.value, 10))}
            min="0"
            required
          />
          <span className="input-suffix">%</span>
        </div>
      </div>

      <button type="submit">+ Add Case Fatality Rate</button>
    </form>
  );
};

export default CaseFatalityRate;
