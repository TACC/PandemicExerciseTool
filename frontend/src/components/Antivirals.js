import React, { useState, useEffect } from 'react';
import toggletip from  './images/toggletip.svg';


const Antivirals = ({ onSubmit }) => {
  const [antiviralEffectiveness, setAntiviralEffectiveness] = useState(localStorage.getItem('antiviral_effectiveness') || 0.15);
  const [antiviralWastageFactor, setAntiviralWastageFactor] = useState(localStorage.getItem('antiviral_wastage_factor') || 60);
  const [antiviralStockpileDay, setAntiviralStockpileDay] = useState(50);
  const [antiviralStockpileAmount, setAntiviralStockpileAmount] = useState(10000);
  const [antiviralStockpileList, setAntiviralStockpileList] = useState([]);

  const handleSubmit = event => {
    event.preventDefault();
    localStorage.setItem('antiviral_effectiveness', antiviralEffectiveness);
    localStorage.setItem('antiviral_wastage_factor', antiviralWastageFactor);
  };

  const handleSubmitStockpile = event => {
    event.preventDefault();

    // Ensure both fields are filled out
    if (!antiviralStockpileDay || !antiviralStockpileAmount){
      alert('Please enter all required fields');
      return;
    }

    // Create a new object with the values from the form
    const newAVS = {
      day: antiviralStockpileDay,
      amount: antiviralStockpileAmount
    };

    // Add the new object to the list
    setAntiviralStockpileList(prevList => [...prevList, newAVS]);

    // Reset the form fields
    setAntiviralStockpileDay(50);
    setAntiviralStockpileAmount(10000);
  };

  const handleRemove = index => {
    // Remove the case at the specified index
    setAntiviralStockpileList(antiviralStockpileList.filter((_, i) => i !== index));
  };


  // Load saved stockpiles from localStorage on component mount
  useEffect(() => {
    const savedAntiviralStockpile = localStorage.getItem('antiviral_stockpile');
    if (savedAntiviralStockpile) {
      const parsedAntiviralStockpile = JSON.parse(savedAntiviralStockpile);
      console.log('Loaded cases from localStorage:', parsedAntiviralStockpile); // Log loaded cases
      setAntiviralStockpileList(parsedAntiviralStockpile);
    }
  }, []);

  // Save cases to localStorage whenever the cases list changes
  useEffect(() => {
    if (antiviralStockpileList.length > 0) {
      localStorage.setItem('antiviral_stockpile', JSON.stringify(antiviralStockpileList));
      console.log('Saved antiviral stockpile to localStorage:', antiviralStockpileList); // Log saved cases
    }
  }, [antiviralStockpileList]);



  return (
    <div>
      <form className="parameters-form" onSubmit={handleSubmit}>

        <div className="form-group">
          <label htmlFor="antiviralEffectiveness">Antiviral Effectiveness
            <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltip-text">The probability that an individual treated within the treatment window will recover.</span>
            </span>
          </label>
          <input
            type="number"
            id="antiviralEffectiveness"
            value={antiviralEffectiveness}
            onChange={e => setAntiviralEffectiveness(e.target.value)}
            min="0"
            max="1"
            step="0.01"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="antiviralWastageFactor">Antiviral Wastage Factor (days)
            <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltip-text">Half of the antiviral stockpile will be wasted after N days.</span>
            </span>
          </label>
          <input
            type="number"
            id="antiviralWastageFactor"
            value={antiviralWastageFactor}
            onChange={e => setAntiviralWastageFactor(e.target.value)}
            min="0"
            max="100"
            step="1"
            required
          />
        </div>

        <button type="submit">Save Antiviral Parameters</button>
      </form>

        <form className="parameters-form" onSubmit={handleSubmitStockpile}>
          <div className="form-group">
          <label htmlFor="antiviralStockpileDay">New Stockpile Day
          <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltip-text">Specify day that new antiviral stockpile becomes available.</span>
            </span>
          </label>
          <input
            type="number"
            id="antiviralStockpileDay"
            value={antiviralStockpileDay}
            onChange={e => setAntiviralStockpileDay(e.target.value)}
            min="1"
            required
          />
          </div>
          <div className="form-group">
          <label htmlFor="antiviralStockpileAmount">New Stockpile Amount
          <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltip-text">Specify number of antivirals in new stockpile.</span>
            </span>
          </label>
          <input
            type="number"
            id="antiviralStockpileAmount"
            value={antiviralStockpileAmount}
            onChange={e => setAntiviralStockpileAmount(e.target.value)}
            min="0"
            required
          />
          </div>
          <button type="submit">Add New Antiviral Stockpile</button>
        </form>

        <h3>Added Stockpiles</h3>
        <table className="avs-table">
          <thead>
            <tr>
              <th>Day</th>
              <th>Amount</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {antiviralStockpileList.map((avsItem, index) => (
              <tr key={index}>
                <td>{avsItem.day}</td>
                <td>{avsItem.amount}</td>
                <td>
                  <button onClick={() => handleRemove(index)}>Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
  );
};

export default Antivirals;
