import React, { useState, useEffect } from 'react';
import '../App.css'; // Adjust CSS as needed
import search from './search.png'; // Assuming you have this image
import { csv } from 'd3-fetch'; // Assuming you use d3-fetch for CSV parsing

// Function to load county names from CSV (Example, adjust as per your actual CSV loading mechanism)
const loadCountyNames = async () => {
  const data = await csv('/data/fips_county_names_HSRs.csv'); // Adjust filename as per your CSV file
  const lookup = {};

  data.forEach(row => {
    lookup[row.fips] = row.county;
  });

  return lookup;
};

// Function to parse data and calculate deceased counts
const parseData = (jsonData, countyNameLookup) => {
  return jsonData.data.map((county) => {
    const { fips_id, compartments } = county;
    const { D } = compartments;
    const totalDeceased = [
      ...D.U.L,
      ...D.U.H,
      ...D.V.L,
      ...D.V.H
    ].reduce((sum, value) => sum + value, 0);

    const countyName = countyNameLookup[fips_id] || 'Unknown';

    return {
      county: countyName,
      fips: fips_id,
      deceased: Math.round(totalDeceased),
    };
  });
};

function CountyDeceasedTable({ outputData }) {
  const [sortedData, setSortedData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortDirection, setSortDirection] = useState({
    county: 'asc',
    deceased: 'desc', // Set default sort direction for deceased to descending
  });

  useEffect(() => {
    const fetchAndParseData = async () => {
      const countyNameLookup = await loadCountyNames();
      const parsedData = parseData(outputData, countyNameLookup);

      // Sort data by deceased count in descending order by default
      const sortedByDeceased = parsedData.sort((a, b) => b.deceased - a.deceased);
      setSortedData(sortedByDeceased);
    };

    fetchAndParseData();
  }, [outputData]);

  // Function to handle sorting by county name or deceased count
  const sortData = (key) => {
    const sorted = [...sortedData];
    sorted.sort((a, b) => {
      const valueA = a[key];
      const valueB = b[key];
      if (valueA < valueB) {
        return sortDirection[key] === 'asc' ? -1 : 1;
      }
      if (valueA > valueB) {
        return sortDirection[key] === 'asc' ? 1 : -1;
      }
      return 0;
    });
    setSortedData(sorted);
    setSortDirection({
      ...sortDirection,
      [key]: sortDirection[key] === 'asc' ? 'desc' : 'asc',
    });
  };

  // Function to filter data based on search term
  const filteredData = sortedData.filter((county) =>
    county.county.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="table-container">
      <div className="search-container">
        <img src={search} alt="Search" className="search-icon" />
        <input
          type="text"
          className="search-input"
          placeholder="Search County..."
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
                <button className="sort-button" onClick={() => sortData('county')}>
                  {sortDirection.county === 'asc' ? '↓' : '↑'}
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
            {filteredData.map((county, index) => (
              <tr key={index} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
                <td>{county.county}</td>
                <td>{county.deceased}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default CountyDeceasedTable;
