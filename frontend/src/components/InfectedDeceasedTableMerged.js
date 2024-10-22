import React, { useState, useEffect } from 'react';
import searchIcon from './images/search.svg'; // Updated to use search.svg
import { csv } from 'd3-fetch'; // Assuming you use d3-fetch for CSV parsing
import './Table.css';

// Function to load county names from CSV
const loadCountyNames = async () => {
  const data = await csv('/data/fips_county_names_HSRs.csv'); // Adjust filename as per your CSV file
  const lookup = {};

  data.forEach(row => {
    lookup[row.fips] = row.county;
  });

  return lookup;
};

function InfectedDeceasedTableMerged({ eventData, currentIndex, sortInfo, handleSortDirectionChange }) {
  const [mergedData, setMergedData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  
  // invoked when the user clicks on table heading to change sort config
  const sortManually = (data, key) => {
    handleSortDirectionChange(key);
    sortData(data);
  }

  // update dayData when new day is simulated or when user scrubs the timeline
  useEffect(() => {
    const fetchData = async () => {
      const countyNameLookup = await loadCountyNames();

      if (!eventData || eventData.length === 0) {
        console.warn('eventData is empty');
        return;
      }

        // Get the data for the specific day (currentIndex)
        const specificDayEventData = eventData.find(event => event.day === currentIndex)?.counties || [];

      // Map and transform data for display
      const dayData = specificDayEventData.map(county => ({
        county: countyNameLookup[county.fips] || 'Unknown',
        infected: county.infected,
        deceased: county.deceased,
        infectedPercent: county.infectedPercent,
        deceasedPercent: county.deceasedPercent,
      }));

      console.log(`Day Data (index ${currentIndex}):`, dayData); // Debugging output

      const sortedData = sortData(dayData);

      setMergedData(sortedData);
      setFilteredData(sortedData); // Initialize filtered data to current day's data
    };

    fetchData();
  }, [eventData, currentIndex]); // Rerun the effect when eventData changes


  // Function to handle sorting
  const sortData = (sorted) => {
    const key = sortInfo.lastSorted;
    sorted.sort((a, b) => {
      const valueA = key === 'county' ? a[key].toLowerCase() : parseFloat(a[key]);
      const valueB = key === 'county' ? b[key].toLowerCase() : parseFloat(b[key]);

      if (valueA < valueB) {
        return sortInfo[key] === 'asc' ? -1 : 1;
      }
      if (valueA > valueB) {
        return sortInfo[key] === 'asc' ? 1 : -1;
      }
      return 0;
    });

    return sorted;
  };

  // Function to filter data based on search term
  useEffect(() => {
    const lowerCaseSearchTerm = searchTerm.toLowerCase();
    const filtered = mergedData.filter(county =>
      county.county.toLowerCase().includes(lowerCaseSearchTerm)
    );
    setFilteredData(filtered);
  }, [searchTerm, mergedData]);

  return (
    <div className="table-container">
      <div className="search-container">
        <div className="search-icon-box">
          <img src={searchIcon} alt="Search" className="search-icon" />
        </div>
        <input
          type="text"
          className="search-input"
          placeholder="Search Counties..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>
                County
                <button className="sort-button" onClick={() => sortManually(filteredData, 'county')}>
                  {sortInfo.county === 'asc' ? '↓' : '↑'}
                </button>
              </th>
              <th>
                Infected
                <button className="sort-button" onClick={() => sortManually(filteredData, 'infected')}>
                  {sortInfo.infected === 'asc' ? '↓' : '↑'}
                </button>
              </th>
              <th>
                Deceased
                <button className="sort-button" onClick={() => sortManually(filteredData, 'deceased')}>
                  {sortInfo.deceased === 'asc' ? '↓' : '↑'}
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredData.length === 0 ? (
              <tr>
                <td colSpan="3">No data available for the selected day.</td>
              </tr>
            ) : (
              filteredData.map((county, index) => (
                <tr key={index} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
                <td>{county.county}</td>
                <td>
                  <span className="bold-text">{county.infected}</span>
                  {county.infectedPercent > 0 && (
                    <>
                      &nbsp;
                      <span className="light-text">({county.infectedPercent}%)</span>
                    </>
                  )}
                </td>
                <td>
                  <span className="bold-text">{county.deceased}</span>
                  {county.deceasedPercent > 0 && (
                    <>
                      &nbsp;
                      <span className="light-text">({county.deceasedPercent}%)</span>
                    </>
                  )}
                </td>
              </tr>
              ))
            )}

          </tbody>
        </table>
      </div>
    </div>
  );
}

export default InfectedDeceasedTableMerged;
