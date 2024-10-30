// FIXME: antivirals do not appear in the left-hand summary pane (<DisplayedParameters />) until the component
// rerenders! there's a workaround implemented for NPIs by changing a state variable in the parent component
// (<Home />) when an intervention is added.
// changing state re-renders <Home /> and <DisplayedParameters /> updates dynamically

// a form for gathering user specification for antiviral interventions, which are saved to state and localStorage
// clicking the "Antivirals" button in the <Interventions /> dropdown will render this component
// NOTE: specifying antiviral interventions does not currently affect the simulation!

import React, { useState, useEffect } from 'react';
import toggletip from  '../images/toggletip.svg';
import './InitialCases.css';


const AntiviralsForm = ({ onSubmit }) => {
  const [antiviralEffectiveness, setAntiviralEffectiveness] = useState(localStorage.getItem('antiviral_effectiveness') || 0.15);
  const [antiviralWastageFactor, setAntiviralWastageFactor] = useState(localStorage.getItem('antiviral_wastage_factor') || 60);
  const [antiviralStockpileDay, setAntiviralStockpileDay] = useState(50);
  const [antiviralStockpileAmount, setAntiviralStockpileAmount] = useState(10000);
  const [antiviralStockpileList, setAntiviralStockpileList] = useState(JSON.parse(localStorage.getItem('antiviral_stockpile')) || []);
  const [stockpileCounter, setStockpileCounter] = useState(0);

  const handleSetParams = event => {
    console.log('Submitting parameters...');
    event.preventDefault();
    localStorage.setItem('antiviral_effectiveness', antiviralEffectiveness);
    localStorage.setItem('antiviral_wastage_factor', antiviralWastageFactor);
  };

  const handleAddStockpile = event => {
    console.log('Adding stockpile...');
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
    setStockpileCounter(stockpileCounter + 1);
  };

  const handleRemove = index => {
    console.log('Removing case at index:', index);
    // Remove the case at the specified index
    setAntiviralStockpileList(antiviralStockpileList.filter((_, i) => i !== index));
    setStockpileCounter(stockpileCounter - 1);
  };

  const handleSave = () => {
    console.log('Saving parameters...');
    onSubmit(antiviralEffectiveness, antiviralWastageFactor, antiviralStockpileList);
  };


  useEffect(() => {
    localStorage.setItem('antiviral_stockpile', JSON.stringify(antiviralStockpileList));
  }, [stockpileCounter]);


  return (
    <div>
      <form className="intervention-form" onSubmit={handleSetParams}>
        <div className="form-group">
          <label htmlFor="antiviralEffectiveness">Antiviral Effectiveness
            <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltips-text">The probability that an individual treated within the treatment window will recover.</span>
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
            <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltips-text">Half of the antiviral stockpile will be wasted after N days.</span>
            </span>
          </label>
          <input
            type="number"
            id="antiviralWastageFactor"
            value={antiviralWastageFactor}
            onChange={e => setAntiviralWastageFactor(e.target.value)}
            min="0"
            max="1000"
            step="1"
            required
          />
        </div>

        <button type="submit" className="save_button" >Set Antiviral Parameters</button>
      </form>

      <form className="intervention-form" onSubmit={handleAddStockpile}>
        <div className="form-group">
        <label htmlFor="antiviralStockpileDay">New Stockpile Day
        <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Specify day that new antiviral stockpile becomes available.</span>
          </span>
        </label>
        <input
          type="number"
          id="antiviralStockpileDay"
          value={antiviralStockpileDay}
          onChange={e => setAntiviralStockpileDay(e.target.value)}
          min="1"
          max="1000"
          step="1"
          required
        />
        </div>

        <div className="form-group">
        <label htmlFor="antiviralStockpileAmount">New Stockpile Amount
        <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Specify number of antivirals in new stockpile.</span>
          </span>
        </label>
        <input
          type="number"
          id="antiviralStockpileAmount"
          value={antiviralStockpileAmount}
          onChange={e => setAntiviralStockpileAmount(e.target.value)}
          min="0"
          step="1"
          required
        />
        </div>

        <button type="submit" className="save_button">Add New Antiviral Stockpile</button>
      </form>

      <h5>Added Stockpiles</h5>
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
                <button class="remove-button" onClick={() => handleRemove(index)}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div><button onClick={handleSave} className="save_button" >Save</button></div>
    </div>
  );
};

export default AntiviralsForm;
