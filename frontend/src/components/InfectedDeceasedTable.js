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

function InfectedDeceasedTable({ eventData, currentIndex }) {
  const [mergedData, setMergedData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortDirection, setSortDirection] = useState({
    county: 'asc',
    infected: 'desc',
    deceased: 'desc',
  });

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
      }));

      console.log(`Day Data (index ${currentIndex}):`, dayData); // Debugging output

      setMergedData(dayData);
      setFilteredData(dayData); // Initialize filtered data to current day's data
    };

    fetchData();
  }, [eventData, currentIndex]); // Rerun the effect when eventData changes


  // Function to handle sorting
  const sortData = (key) => {
    const sorted = [...filteredData];
    sorted.sort((a, b) => {
      const valueA = key === 'county' ? a[key].toLowerCase() : parseFloat(a[key]);
      const valueB = key === 'county' ? b[key].toLowerCase() : parseFloat(b[key]);

      if (valueA < valueB) {
        return sortDirection[key] === 'asc' ? -1 : 1;
      }
      if (valueA > valueB) {
        return sortDirection[key] === 'asc' ? 1 : -1;
      }
      return 0;
    });

    setFilteredData(sorted);
    setSortDirection({
      ...sortDirection,
      [key]: sortDirection[key] === 'asc' ? 'desc' : 'asc',
    });
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
        <table style={{width: "96%"}}>
          <thead>
            <tr>
              <th>
                County
                <button className="sort-button" onClick={() => sortData('county')}>
                  {sortDirection.county === 'asc' ? '↓' : '↑'}
                </button>
              </th>
              <th>
                Infected
                <button className="sort-button" onClick={() => sortData('infected')}>
                  {sortDirection.infected === 'asc' ? '↓' : '↑'}
                </button>
              </th>
              <th>
                Deceased
                <button className="sort-button" onClick={() => sortData('deceased')}>
                  {sortDirection.deceased === 'asc' ? '↓' : '↑'}
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
                  <td>{county.infected}</td>
                  <td>{county.deceased}</td>
                </tr>
              ))
            )}

          </tbody>
        </table>
      </div>
    </div>
  );
}

export default InfectedDeceasedTable;
