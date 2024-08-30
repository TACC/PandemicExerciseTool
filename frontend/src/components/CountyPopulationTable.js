import React, { useState, useEffect } from 'react';
import texasOutline from './texasOutline.json';
import Papa from 'papaparse';
import '../App.css'; // Import the CSS file

function CountyPopulationTable() {
  const [sortedData, setSortedData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortDirection, setSortDirection] = useState({
    county: 'asc',
    population: 'asc',
  });

  useEffect(() => {
    // Load the population data from SVI_2020_US_County.csv and match with geoids from texasOutline.json
    const fetchData = async () => {
      const response = await fetch('/data/SVI_2020_US_County.csv');
      const csvData = await response.text();
      Papa.parse(csvData, {
        header: true,
        complete: (result) => {
          const populationData = result.data.reduce((acc, row) => {
            acc[row.FIPS] = row.E_TOTPOP;
            return acc;
          }, {});

          const matchedData = texasOutline.features.map((feature) => {
            const population = populationData[feature.properties.geoid] || 0;
            return {
              county: feature.properties.name,
              population: population,
            };
          });

          setSortedData(matchedData);
        },
      });
    };

    fetchData();
  }, []);

  // Function to handle sorting by county name or population
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
      <h2>
        Population
        <input
          type="text"
          className="search-input"
          placeholder="Search County..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </h2>
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
                Population
                <button className="sort-button" onClick={() => sortData('population')}>
                  {sortDirection.population === 'asc' ? '↓' : '↑'}
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((county, index) => (
              <tr key={index} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
                <td>{county.county}</td>
                <td>{county.population}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default CountyPopulationTable;