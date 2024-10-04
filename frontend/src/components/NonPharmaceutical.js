import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import toggletip from  './images/toggletip.svg';
import './AddInitialCases.css'; // Import the CSS file for styling

const texasMapping = require('./texasMapping.json'); // Import the Texas mapping JSON

const NonPharmaceutical = ({ counties, onSubmit }) => {
  const [nonpharmaName, setNonpharmaName] = useState(localStorage.getItem('nonpharma_name') || 'School Closures');
  const [nonpharmaDay, setNonpharmaDay] = useState(40);
  const [nonpharmaDuration, setNonpharmaDuration] = useState(10);
  const [nonpharmaEffectiveness, setNonpharmaEffectiveness] = useState(localStorage.getItem('effectiveness') || 0.40);
  const [nonpharmaHalflife, setNonpharmaHalflife] = useState(localStorage.getItem('duration') || 10);
  const [nonpharmaList, setNonpharmaList] = useState(JSON.parse(localStorage.getItem("non_pharma_interventions")) || []);
  const [nonpharmaCounter, setNonpharmaCounter] = useState(0);
  const [nonpharmaCounties, setNonpharmaCounties] = useState(localStorage.getItem('location') || 0);

  const countyOptions = counties.map(county => ({
    value: county,
    label: county
  }));

  const ageGroups = [
    [0, 4],
    [5, 24],
    [25, 49],
    [50, 64],
    [65, Infinity],
  ];

  const handleAddNPI = event => {
    console.log("Adding NPI...");
    event.preventDefault();
    // Ensure all fields are filled out
    if (!nonpharmaName || !nonpharmaDay || !nonpharmaDuration|| !nonpharmaEffectiveness || !nonpharmaHalflife) {
      alert('Please enter all required fields');
      return;
    }
    // Create a new object with the values from the form
    const newNPI = {
      name: nonpharmaName,
      day: nonpharmaDay,
      duration: nonpharmaDuration,
      // halflife: nonpharmaHalflife
      location: nonpharmaCounties.map((county) => (county.value)),    // only pass the value returned from <Select />
      effectiveness: nonpharmaEffectiveness,
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
    localStorage.setItem("non_pharma_interventions", JSON.stringify(nonpharmaList));
  }, [nonpharmaCounter]);


  return (
    <div>
      <form className="intervention-form" onSubmit={handleAddNPI}>
        <div className="form-group">
          <label htmlFor="nonpharmaName">NPI Name</label>
          <input
            type="text"
            id="nonpharmaName"
            className="centered-input"
            value={nonpharmaName}
            onChange={e => setNonpharmaName(e.target.value)}
            required
          />
        </div>
        
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
        <label htmlFor="nonpharmaDuration">NPI Duration (days)
        <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltip-text">Specify the duration for the non-pharmaceutical intervention.</span>
          </span>
        </label>
        <input
          type="number"
          id="nonpharmaDuration"
          value={nonpharmaDuration}
          onChange={e => setNonpharmaDuration(e.target.value)}
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
        {ageGroups.map((group) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100px'}}>
            <div className="cfr-form">
              <label style={{ width: '100%' }} htmlFor={`ageGroup${group[0]}-${group[1]}`}>
                  {group[0]}{group[1] === Infinity ? "+" : `-${group[1]}`}
              </label>
              <input
                type="number"
                id={`ageGroup${group[0]}-${group[1]}`}
                name={`ageGroup${group[0]}-${group[1]}`}
                value='0.4'
                step="0.01"
                min="0"
                max="1"
                placeholder="Enter decimal value"
                required
              />
            </div>
        </div>
        ))}
        {/* <input */}
        {/*   type="number" */}
        {/*   id="nonpharmaEffectiveness" */}
        {/*   value={nonpharmaEffectiveness} */}
        {/*   onChange={e => setNonpharmaEffectiveness(e.target.value)} */}
        {/*   min="0" */}
        {/*   max="1" */}
        {/*   step="0.01" */}
        {/*   required */}
        {/* /> */}
        </div>

        {/* <div className="form-group"> */}
        {/* <label htmlFor="nonpharmaHalflife">NPI Half-life (days) */}
        {/* <span className="tooltip"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/> */}
        {/*     <span className="tooltip-text">Specify half-life of non-pharmaceutical intervention in days (NPI is half as effective after N days).</span> */}
        {/*   </span> */}
        {/* </label> */}
        {/* <input */}
        {/*   type="number" */}
        {/*   id="nonpharmaHalflife" */}
        {/*   value={nonpharmaHalflife} */}
        {/*   onChange={e => setNonpharmaHalflife(e.target.value)} */}
        {/*   min="1" */}
        {/*   max="1000" */}
        {/*   step="0.1" */}
        {/*   required */}
        {/* /> */}
        {/* </div> */}

        <label htmlFor="county">Location</label>
        <Select
          id="county"
          value={nonpharmaCounties}
          onChange={setNonpharmaCounties}
          isMulti={true}
          options={countyOptions}
          placeholder="Select counties"
          isClearable
          isSearchable
        />

        <button type="submit" className="save_button">Add New NPI</button>
      </form>
      <h2>Added NPIs</h2>
      <table className="npi-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Day</th>
            <th>Effectiveness</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {nonpharmaList.map((npiItem, index) => (
            <tr key={index}>
              <td>{npiItem.name}</td>
              <td>{npiItem.day}</td>
              <td>{ npiItem.effectiveness}</td>
              <td>
                <button className="remove-button" onClick={() => handleRemove(index)}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div><button onClick={handleSave} className="save_button">Save</button></div>
    </div>
  );
};

export default NonPharmaceutical;
