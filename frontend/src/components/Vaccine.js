import React, { useState, useEffect } from "react";
import toggletip from  "./images/toggletip.svg";
import './AddInitialCases.css';

const Vaccine = ({ onSubmit }) => {
  const [vaccineEffectiveness, setVaccineEffectiveness] = useState(localStorage.getItem('vaccine_effectiveness') || 0.50);
  const [vaccineAdherence, setVaccineAdherence] = useState(localStorage.getItem('vaccine_adherence') || 0.50);
  const [vaccineWastageFactor, setVaccineWastageFactor] = useState(localStorage.getItem('vaccine_wastage_factor') || 60);
  const [vaccineStrategy, setVaccineStrategy] = useState("default");
  const [vaccineStockpileDay, setVaccineStockpileDay] = useState(50);
  const [vaccineStockpileAmount, setVaccineStockpileAmount] = useState(10000);
  const [vaccineStockpileList, setVaccineStockpileList] = useState(JSON.parse(localStorage.getItem("vaccine_stockpile")) || []);
  const [stockpileCounter, setStockpileCounter] = useState(0);

  const handleSetParams = event => {
    console.log("Submitting parameters...");
    event.preventDefault();
    localStorage.setItem("vaccine_effectiveness", vaccineEffectiveness);
    localStorage.setItem("vaccine_adherence", vaccineAdherence);
    localStorage.setItem("vaccine_wastage_factor", vaccineWastageFactor);
    localStorage.setItem("vaccine_strategy", vaccineStrategy);
  };

  const handleAddStockpile = event => {
    console.log("Adding stockpile...");
    event.preventDefault();
    // Ensure both fields are filled out
    if (!vaccineStockpileDay || !vaccineStockpileAmount){
      alert("Please enter all required fields");
      return;
    }
    // Create a new object with the values from the form
    const newVS = {
      day: vaccineStockpileDay,
      amount: vaccineStockpileAmount
    };
    // Add the new object to the list
    setVaccineStockpileList(prevList => [...prevList, newVS]);
    setStockpileCounter(stockpileCounter + 1);
  };

  const handleRemove = index => {
    console.log("Removing case at index:", index);
    // Remove the case at the specified index
    setVaccineStockpileList(vaccineStockpileList.filter((_, i) => i !== index));
    setStockpileCounter(stockpileCounter - 1);
  };

  const handleSave = () => {
    console.log("Saving parameters...");
    onSubmit(vaccineEffectiveness, vaccineAdherence, vaccineWastageFactor, vaccineStrategy, vaccineStockpileList);
  };


  useEffect(() => {
    localStorage.setItem("vaccine_stockpile", JSON.stringify(vaccineStockpileList));
  }, [stockpileCounter]);


  return (
    <div>
      <form className="intervention-form" onSubmit={handleSetParams}>
        <div className="form-group">
          <label htmlFor="vaccineEffectiveness">Vaccine Effectiveness
            <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltip-text">Fraction of vaccinated population protected from infection (0 = no protection, 1 = complete protection).</span>
            </span>
          </label>
          <input
            type="number"
            id="vaccineEffectiveness"
            value={vaccineEffectiveness}
            onChange={e => setVaccineEffectiveness(e.target.value)}
            min="0"
            max="1"
            step="0.01"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="vaccineAdherence">Vaccine Adherence
            <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltip-text">Fraction of population that adhere to the vaccine schedule (0 = none, 1 = all)</span>
            </span>
          </label>
          <input
            type="number"
            id="vaccineAdherence"
            value={vaccineAdherence}
            onChange={e => setVaccineAdherence(e.target.value)}
            min="0"
            max="1"
            step="0.0001"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="vaccineWastageFactor">Vaccine Wastage Factor (days)
            <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltip-text">Half of the vaccine stockpile will be wasted after N days.</span>
            </span>
          </label>
          <input
            type="number"
            id="vaccineWastageFactor"
            value={vaccineWastageFactor}
            onChange={e => setVaccineWastageFactor(e.target.value)}
            min="0"
            max="1000"
            step="1"
            required
          />
        </div>
        <div className="form-group" style ={{alignItems: "center"}}>
          <label htmlFor="nu">Vaccine Strategy
          <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltip-text">"Pro rata" distributes vaccine stockpiles to all age groups equally, "Children" distributes vaccine stockpiles to youngest age groups first.</span>
            </span>
          </label>
          <div> 
            <div style={{ display: "flex", gap: '5em'}}>
              <div>
                <input
                  type="radio"
                  id="prorataAll"
                  name="vaccineStrategy"
                  value="pro_rata"
                  checked={vaccineStrategy === "pro_rata"}
                  onChange={e => setVaccineStrategy(e.target.value)}
                  required
                />
                <label htmlFor="prorataAll">Pro Rata</label>
              </div>
              <div>
                <input
                  type="radio"
                  id="prorataChildren"
                  name="vaccineStrategy"
                  value="children"
                  checked={vaccineStrategy === "children"}
                  onChange={e => setVaccineStrategy(e.target.value)}
                  required
                />
                <label htmlFor="prorataChildren">Children</label>
              </div>
            </div>
          </div>
        </div>
        <button type="submit" className="save_button" >Set Vaccine Parameters</button>
      </form>


      <form className="intervention-form" onSubmit={handleAddStockpile}>
        <div className="form-group">
        <label htmlFor="vaccineStockpileDay">New Stockpile Day
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Specify day that new vaccine stockpile becomes available.</span>
          </span>
        </label>
        <input
          type="number"
          id="vaccineStockpileDay"
          value={vaccineStockpileDay}
          onChange={e => setVaccineStockpileDay(e.target.value)}
          min="1"
          max="1000"
          step="1"
          required
        />
        </div>

        <div className="form-group">
        <label htmlFor="vaccineStockpileAmount">New Stockpile Amount
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Specify number of vaccine doses in new stockpile.</span>
          </span>
        </label>
        <input
          type="number"
          id="vaccineStockpileAmount"
          value={vaccineStockpileAmount}
          onChange={e => setVaccineStockpileAmount(e.target.value)}
          min="0"
          step="1"
          required
        />
        </div>

        <button type="submit" className="save_button" >Add New Vaccine Stockpile</button>
      </form>

      <h3>Added Stockpiles</h3>
      <table className="vs-table">
        <thead>
          <tr>
            <th>Day</th>
            <th>Amount</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {vaccineStockpileList.map((vsItem, index) => (
            <tr key={index}>
              <td>{vsItem.day}</td>
              <td>{vsItem.amount}</td>
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

export default Vaccine;
