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

function InfectedDeceasedTableMergedPercent({ eventData, currentIndex, sortInfo, handleSortDirectionChange }) {
  const [mergedData, setMergedData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  // const [sortDirection, setSortDirection] = useState({
  //   county: 'asc',
  //   infected: 'desc',
  //   deceased: 'desc',
  //   infectedPercent: 'desc',
  //   deceasedPercent: 'desc',
  // });

  const sortManually = (key) => {
    handleSortDirectionChange(key);
    sortData();
  }

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
      debugger;

      setMergedData(dayData);
      setFilteredData(dayData); // Initialize filtered data to current day's data
      // sortData();
      // we map over filteredData to populate the table
      // sortInfo should update filteredData with sorted data, but maybe that isn't happening
      // before the table is populated in the return() statement
      // check here if the filteredData being printed is actually sorted or not
      console.log(`Day data after sorting by ${sortInfo.lastSorted}:`, filteredData);
      debugger;
    };

    fetchData();
    sortData();
    debugger;
  }, [eventData, currentIndex]); // Rerun the effect when eventData changes or timeline is scrubbed


  // Function to handle sorting
  const sortData = () => {
    const key = sortInfo.lastSorted;
    console.log(sortInfo);
    console.log("sorting data by", key);
    const sorted = [...filteredData];
    sorted.sort((a, b) => {
      const valueA = key === 'county' ? a[key].toLowerCase() : parseFloat(a[key]);
      const valueB = key === 'county' ? b[key].toLowerCase() : parseFloat(b[key]);

      if (valueA < valueB) {
        console.log("me when I'm sorting");
        return sortInfo[key] === 'asc' ? -1 : 1;
      }
      if (valueA > valueB) {
        console.log("sortmaxxing rn");
        return sortInfo[key] === 'asc' ? 1 : -1;
      }
      return 0;
    });

    console.log("after sorting by", key, "within sortData scope:", sorted);
    setFilteredData(sorted);
    setMergedData(sorted);
    // setSortDirection({
    //   ...sortDirection,
    //   [key]: sortDirection[key] === 'asc' ? 'desc' : 'asc',
    // });
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
                <button className="sort-button" onClick={() => sortManually('county')}>
                  {sortInfo.county === 'asc' ? '↓' : '↑'}
                </button>
              </th>
              <th>
                Infected 
                <button className="sort-button" onClick={() => sortManually('infectedPercent')}>
                  {sortInfo.infectedPercent === 'asc' ? '↓' : '↑'}
                </button>
              </th>
              <th>
                Deceased
                <button className="sort-button" onClick={() => sortManually('deceasedPercent')}>
                  {sortInfo.deceasedPercent === 'asc' ? '↓' : '↑'}
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
                  <span className="bold-text">{county.infectedPercent}</span>
                  {county.infectedPercent > 0 && (
                    <>
                      <span className="light-text">% ({county.infected})</span>
                    </>
                  )}
                </td>
                <td>
                  <span className="bold-text">{county.deceasedPercent}</span>
                  {county.deceasedPercent > 0 && (
                    <>
                      &nbsp;
                      <span className="light-text">% ({county.deceased})</span>
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

export default InfectedDeceasedTableMergedPercent;
