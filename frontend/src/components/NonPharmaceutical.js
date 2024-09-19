import React, { useState, useEffect } from 'react';
import toggletip from  './images/toggletip.svg';
import './NonPharmaceutical.css';

const NonPharmaceutical = ({ onSubmit }) => {
  const [nonpharmaDay, setNonpharmaDay] = useState(50);
  const [nonpharmaEffectiveness, setNonpharmaEffectiveness] = useState(0.40);
  const [nonpharmaHalflife, setNonpharmaHalflife] = useState(10);
  const [nonpharmaList, setNonpharmaList] = useState(JSON.parse(localStorage.getItem("nonpharma_list")) || []);
  const [nonpharmaCounter, setNonpharmaCounter] = useState(0);


  const handleAddNPI = event => {
    console.log("Adding NPI...");
    event.preventDefault();
    // Ensure all fields are filled out
    if (!nonpharmaDay || !nonpharmaEffectiveness || !nonpharmaHalflife) {
      alert('Please enter all required fields');
      return;
    }
    // Create a new object with the values from the form
    const newNPI = {
      day: nonpharmaDay,
      effectiveness: nonpharmaEffectiveness,
      halflife: nonpharmaHalflife
    };
    // Add the new object to the list
    setNonpharmaList(prevList => [...prevList, newNPI]);
    setNonpharmaCounter(nonpharmaCounter + 1);
  };

  const handleRemove = index => {
    console.log('Removing case at index:', index);
    // Remove the case at the specified index
    setNonpharmaList(nonpharmaList.filter((_, i) => i !== index));
    setNonpharmaCounter(nonpharmaCounter - 1);
  };

  const handleSave = () => {
    console.log('Saving parameters...');
    onSubmit(nonpharmaList);
  };


  useEffect(() => {
    localStorage.setItem("nonpharma_list", JSON.stringify(nonpharmaList));
  }, [nonpharmaCounter]);


  return (
    <div>
      <form className="parameters-form" onSubmit={handleAddNPI}>
        <div className="form-group">
        <label htmlFor="nonpharmaDay">NPI Day
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Specify day that non-pharmaceutical intervention occurs.</span>
          </span>
        </label>
        <input
          type="number"
          id="nonpharmaDay"
          value={nonpharmaDay}
          onChange={e => setNonpharmaDay(e.target.value)}
          min="1"
          max="1000"
          step="1"
          required
        />
        </div>

        <div className="form-group">
        <label htmlFor="nonpharmaEffectiveness">NPI Effectiveness
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Specify effectiveness of non-pharmaceutical intervention (0 = not effective, 1 = completely effective).</span>
          </span>
        </label>
        <input
          type="number"
          id="nonpharmaEffectiveness"
          value={nonpharmaEffectiveness}
          onChange={e => setNonpharmaEffectiveness(e.target.value)}
          min="0"
          max="1"
          step="0.01"
          required
        />
        </div>

        <div className="form-group">
        <label htmlFor="nonpharmaHalflife">NPI Half-life (days)
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Specify half-life of non-pharmaceutical intervention in days (NPI is half as effective after N days).</span>
          </span>
        </label>
        <input
          type="number"
          id="nonpharmaHalflife"
          value={nonpharmaHalflife}
          onChange={e => setNonpharmaHalflife(e.target.value)}
          min="1"
          max="1000"
          step="0.1"
          required
        />
        </div>

        <button type="submit">Add New NPI</button>
      </form>
      <h2>Added NPIs</h2>
      <table className="npi-table">
        <thead>
          <tr>
            <th>Day</th>
            <th>Effectiveness</th>
            <th>Half-life</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {nonpharmaList.map((npiItem, index) => (
            <tr key={index}>
              <td>{npiItem.day}</td>
              <td>{ npiItem.effectiveness}</td>
              <td>{ npiItem.halflife}</td>
              <td>
                <button class="remove-button" onClick={() => handleRemove(index)}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div><button onClick={handleSave}>Save</button></div>
    </div>
  );
};

export default NonPharmaceutical;
