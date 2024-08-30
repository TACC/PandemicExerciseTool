import React, { useState } from 'react';

const Antivirals = ({ onSubmit }) => {
  const [antiviralData, setAntiviralData] = useState({
    effectiveness: 0,
    adherence: 0,
    capacity: 0
  });

  const handleSubmit = event => {
    event.preventDefault();
    onSubmit(antiviralData);
  };

  const handleAntiviralChange = (field, value) => {
    setAntiviralData(prevState => ({
      ...prevState,
      [field]: value
    }));
  };

  return (
    <form className="parameters-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="antiviralEffectiveness">Antiviral Effectiveness:</label>
        <input
          type="number"
          id="antiviralEffectiveness"
          value={antiviralData.effectiveness}
          onChange={e => handleAntiviralChange('effectiveness', parseFloat(e.target.value))}
          min="0"
          max="1"
          step="0.01"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="antiviralAdherence">Antiviral Adherence:</label>
        <input
          type="number"
          id="antiviralAdherence"
          value={antiviralData.adherence}
          onChange={e => handleAntiviralChange('adherence', parseFloat(e.target.value))}
          min="0"
          max="100"
          step="1"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="antiviralCapacity">Antiviral Capacity:</label>
        <input
          type="number"
          id="antiviralCapacity"
          value={antiviralData.capacity}
          onChange={e => handleAntiviralChange('capacity', parseInt(e.target.value, 10))}
          min="0"
          required
        />
      </div>

      <button type="submit">Submit Antiviral Data</button>
    </form>
  );
};

export default Antivirals;
