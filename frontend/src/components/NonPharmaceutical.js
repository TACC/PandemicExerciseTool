import React, { useState } from 'react';
import './NonPharmaceutical.css';

const NonPharmaceutical = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    duration: 0,
    effectiveness: {
      '0-4 years': 0,
      '5-24 years': 0,
      '25-49 years': 0,
      '50-64 years': 0,
      '65+ years': 0
    },
    location: ''
  });

  const handleSubmit = event => {
    event.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (field, value) => {
    setFormData(prevState => ({
      ...prevState,
      [field]: value
    }));
  };

  const handleEffectivenessChange = (ageGroup, value) => {
    setFormData(prevState => ({
      ...prevState,
      effectiveness: {
        ...prevState.effectiveness,
        [ageGroup]: value
      }
    }));
  };

  return (
    <form className="parameters-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="name">Name:</label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={e => handleChange('name', e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="duration">Duration (days):</label>
        <input
          type="number"
          id="duration"
          value={formData.duration}
          onChange={e => handleChange('duration', parseInt(e.target.value, 10))}
          min="0"
          required
        />
      </div>

      <div className="form-group">
        <label>Age-Specific Effectiveness:</label>
        {Object.keys(formData.effectiveness).map(ageGroup => (
          <div key={ageGroup} className="form-group">
            <label htmlFor={`effectiveness-${ageGroup}`}>{ageGroup}:</label>
            <input
              type="number"
              id={`effectiveness-${ageGroup}`}
              value={formData.effectiveness[ageGroup]}
              onChange={e => handleEffectivenessChange(ageGroup, parseFloat(e.target.value))}
              min="0"
              max="100"
              step="0.1"
              required
            />
          </div>
        ))}
      </div>

      <div className="form-group">
        <label htmlFor="location">Location:</label>
        <select
          id="location"
          value={formData.location}
          onChange={e => handleChange('location', e.target.value)}
          required
        >
          <option value="" disabled>Select a location</option>
          <option value="By County">By County</option>
          <option value="Statewide">Statewide</option>
          <option value="By Region">By Region</option>
        </select>
      </div>

      <button type="submit">Submit Data</button>
    </form>
  );
};

export default NonPharmaceutical;
