// a form for collecting user specifications for non-pharmaceutical interventions (or NPIs)
// clicking on the Non-Pharmaceutical button in the <Interventions /> dropdown will render this component
import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import toggletip from  '../images/toggletip.svg';
import './InitialCases.css'; // Import the CSS file for styling

const texasMapping = require('../../data/texasMapping.json'); // Import the Texas mapping JSON

const NPIForm = ({ counties, onSubmit }) => {
  const [nonpharmaName, setNonpharmaName] = useState(localStorage.getItem('nonpharma_name') || 'School Closures');
  const [nonpharmaDay, setNonpharmaDay] = useState(40);
  const [nonpharmaDuration, setNonpharmaDuration] = useState(10);
  const [nonpharmaHalflife, setNonpharmaHalflife] = useState(localStorage.getItem('duration') || 10);
  const [nonpharmaList, setNonpharmaList] = useState(JSON.parse(localStorage.getItem("non_pharma_interventions")) || []);
  const [nonpharmaCounter, setNonpharmaCounter] = useState(0);
  const [nonpharmaCounties, setNonpharmaCounties] = useState(localStorage.getItem('location') || "All");
  const [numEffectives, setNumEffectives] = useState(localStorage.getItem('numEffectives') || [0.4, 0.35, 0.2, 0.25, 0.1]);
  const [nonpharmaEffectiveness, setNonpharmaEffectiveness] = useState({
    '0-4': '0.4',
    '5-24': '0.35',
    '25-49': '0.2',
    '50-64': '0.25',
    '65+': '0.1'
  });

  const countyOptions = counties.map(county => ({
    value: county,
    label: county
  }));


  const handleEffectivenessChange = (event, ageGroup, index) => {
    const value = event.target.value;

    setNonpharmaEffectiveness(prevState => ({
      ...prevState,
      [ageGroup]: value
    }));
    
    const updatedVals = [...numEffectives];
    updatedVals[index] = value === '' ? null : parseFloat(value);
    setNumEffectives(updatedVals);
  }

  const handleAddNPI = event => {
    console.log("Adding NPI...");
    event.preventDefault();
    // Ensure all fields are filled out
    if (!nonpharmaName || !nonpharmaDay || !nonpharmaDuration || !nonpharmaEffectiveness) {
      alert('Please enter all required fields');
      return;
    }
    // Create a new object with the values from the form
    const newNPI = {
      name: nonpharmaName,
      day: nonpharmaDay,
      duration: nonpharmaDuration,
      location: nonpharmaCounties.map((county) => county.value).includes("Statewide") ?
                "Statewide" :
                nonpharmaCounties.map((county) => county.value).toString(),
      effectiveness: numEffectives.toString(),
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


  const InfoList = ( {info} ) => {
    return (
      <>
        {info.split(",").map((item, index) => (
          <span key={index}>{item}<br /></span>
        ))}
      </>
    );
  };

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
        <label htmlFor="nonpharmaDay">NPI start (simulation day)
        <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">Day of simulation on which the NPI is initiated</span>
          </span>
        </label>
        <input
          type="number"
          id="nonpharmaDay"
          value={nonpharmaDay}
          onChange={e => setNonpharmaDay(e.target.value)}
          min="0"
          max="1000"
          step="1"
          required
        />
        </div>

        <div className="form-group">
        <label htmlFor="nonpharmaDuration">NPI duration (days)
        <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
            <span className="tooltips-text">The number of days that NPI is active</span>
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

        <div className='form-group' style={{alignItems: 'center'}}>
          <label htmlFor="nonpharmaEffectiveness">NPI effectiveness (proportion):
          <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
              <span className="tooltips-text"> Age-specific reduction in susceptibility (0 = no protection; 1 = complete protection)</span>
            </span>
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', width: '100%'}}>
            <div className="cfr-form">
              <label style={{ width: '100%' }} htmlFor="ageGroup0-4">0-4 years: </label>
              <input
                type="number"
                id="ageGroup0-4"
                value={nonpharmaEffectiveness['0-4']}
                onChange={e => handleEffectivenessChange(e, '0-4', 0)}
                step="0.01"
                min='0'
                max='1'
                placeholder="Enter decimal value"
                required
              />
              </div>
              <div className="cfr-form">
              <label style={{ width: '100%' }} htmlFor="ageGroup5-24">5-24 years: </label>
              <input
                type="number"
                id="ageGroup5-24"
                value={nonpharmaEffectiveness['5-24']}
                onChange={e => handleEffectivenessChange(e, '5-24', 1)}
                step="0.01"
                min='0'
                max='1'
                placeholder="Enter decimal value"
                required
              />
              </div>
              <div className="cfr-form">
              <label style={{ width: '100%' }} htmlFor="ageGroup25-49">25-49 years: </label>
              <input
                type="number"
                id="ageGroup25-49"
                value={nonpharmaEffectiveness['25-49']}
                onChange={e => handleEffectivenessChange(e, '25-49', 2)}
                step="0.01"
                min='0'
                max='1'
                placeholder="Enter decimal value"
                required
              />
              </div>
              <div className="cfr-form">
              <label style={{ width: '100%' }} htmlFor="ageGroup50-64">50-64 years: </label>
              <input
                type="number"
                id="ageGroup50-64"
                value={nonpharmaEffectiveness['50-64']}
                onChange={e => handleEffectivenessChange(e, '50-64', 3)}
                step="0.01"
                min='0'
                max='1'
                placeholder="Enter decimal value"
                required
              />
              </div>
              <div className="cfr-form">
              <label style={{ width: '100%' }} htmlFor="ageGroup65Plus">65+ years: </label>
              <input
                type="number"
                id="ageGroup65Plus"
                value={nonpharmaEffectiveness['65+']}
                onChange={e => handleEffectivenessChange(e, '65+', 4)}
                step="0.01"
                min='0'
                max='1'
                placeholder="Enter decimal value"
                required
              />
            </div>
          </div>
        </div>
        {/* <div className="form-group"> */}
        {/* <label htmlFor="nonpharmaHalflife">NPI Half-life (days) */}
        {/* <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/> */}
        {/*     <span className="tooltips-text">Specify half-life of non-pharmaceutical intervention in days (NPI is half as effective after N days).</span> */}
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

        <label htmlFor="county">Location
        <span className="tooltips"><img src={toggletip} alt="Tooltip" className="toggletip-icon"/>
          <span className="tooltips-text">Select all regions under the NPI</span>
        </span>
        </label>
        <Select
          id="county"
          value={nonpharmaCounties}
          onChange={setNonpharmaCounties}
          isMulti={true}
          options={countyOptions}
          placeholder="Select counties"
          isClearable
          isSearchable
          styles={{
            multiValueLabel: (baseStyles => ({
              ...baseStyles,
              fontSize: "95%",
            })),
          }}
          required
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
            <th>Location</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {nonpharmaList.map((npiItem, index) => (
            <tr key={index}>
              <td style={{ textWrap: "balance" }}>{ npiItem.name }</td>
              <td>{ npiItem.day }</td>
              <td>{ npiItem.effectiveness }</td>
              <td>
                { npiItem.location != 0 ? <InfoList info={npiItem.location} /> : "All" }
              </td>
              <td style={{ display: "table-cell" }}>
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

export default NPIForm;
