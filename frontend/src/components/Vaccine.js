import React, { useState } from 'react';

const Vaccine = ({ onSubmit }) => {
  const [vaccineData, setVaccineData] = useState({
    effectivenessLag: 0,
    adherence: 0,
    capacity: 0
  });

  const handleSubmit = event => {
    event.preventDefault();
    onSubmit(vaccineData);
  };

  const handleVaccineChange = (field, value) => {
    setVaccineData(prevState => ({
      ...prevState,
      [field]: value
    }));
  };

  return (
    <form className="parameters-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="vaccineEffectivenessLag">Vaccine Effectiveness Lag (days):</label>
        <input
          type="number"
          id="vaccineEffectivenessLag"
          value={vaccineData.effectivenessLag}
          onChange={e => handleVaccineChange('effectivenessLag', parseInt(e.target.value, 10))}
          min="0"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="vaccineAdherence">Vaccine Adherence:</label>
        <input
          type="number"
          id="vaccineAdherence"
          value={vaccineData.adherence}
          onChange={e => handleVaccineChange('adherence', parseFloat(e.target.value))}
          min="0"
          max="100"
          step="1"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="vaccineCapacity">Vaccine Capacity:</label>
        <input
          type="number"
          id="vaccineCapacity"
          value={vaccineData.capacity}
          onChange={e => handleVaccineChange('capacity', parseInt(e.target.value, 10))}
          min="0"
          required
        />
      </div>

      <button type="submit">Submit Vaccine Data</button>
    </form>
  );
};

export default Vaccine;
