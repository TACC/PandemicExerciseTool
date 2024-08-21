import React, { useState, useEffect } from 'react';
import '../App.css'; // Adjust CSS as needed
import search from './search.png'; // Assuming you have this image
import { csv } from 'd3-fetch'; // Assuming you use d3-fetch for CSV parsing
import Papa from 'papaparse';

// Function to load county names from CSV
const loadCountyNames = async () => {
  const data = await csv('/data/fips_county_names_HSRs.csv'); // Adjust filename as per your CSV file
  const lookup = {};

  data.forEach(row => {
    lookup[row.fips] = row.county;
  });

  return lookup;
};

// Function to parse infection/deceased data
const parseInfectionData = (jsonData, countyNameLookup) => {
  return jsonData.data.map((county) => {
    const { fips_id, compartments } = county;
    const { I, D } = compartments;
    const totalInfected = [
      ...I.U.L,
      ...I.U.H,
      ...I.V.L,
      ...I.V.H
    ].reduce((sum, value) => sum + value, 0);
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
      infected: Math.round(totalInfected),
      deceased: Math.round(totalDeceased),
    };
  });
};

// Function to load population data
const loadPopulationData = async () => {
  const response = await fetch('/data/SVI_2020_US_County.csv');
  const csvData = await response.text();
  const populationData = {};

  Papa.parse(csvData, {
    header: true,
    complete: (result) => {
      result.data.forEach(row => {
        populationData[row.FIPS] = row.E_TOTPOP;
      });
    },
  });

  return populationData;
};

function CountyPercentageTableDraft({ outputData }) {
  const [mergedData, setMergedData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortDirection, setSortDirection] = useState({
    county: 'asc',
    population: 'asc',
    infected: 'desc',
    deceased: 'desc',
  });

  useEffect(() => {
    const fetchData = async () => {
      const countyNameLookup = await loadCountyNames();
      const parsedInfectionData = parseInfectionData(outputData, countyNameLookup);
      const populationData = await loadPopulationData();

      const merged = parsedInfectionData.map(data => ({
        ...data,
        population: populationData[data.fips] || 0,
      }));

      setMergedData(merged);
    };

    fetchData();
  }, [outputData]);

  // Function to handle sorting
  const sortData = (key) => {
    const sorted = [...mergedData];
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
    setMergedData(sorted);
    setSortDirection({
      ...sortDirection,
      [key]: sortDirection[key] === 'asc' ? 'desc' : 'asc',
    });
  };

  // Function to filter data based on search term
  const filteredData = mergedData.filter((county) =>
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
                Population
                <button className="sort-button" onClick={() => sortData('population')}>
                  {sortDirection.population === 'asc' ? '↓' : '↑'}
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
            {filteredData.map((county, index) => (
              <tr key={index} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
                <td>{county.county}</td>
                <td>{county.population}</td>
                <td>{county.infected}</td>
                <td>{county.deceased}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default CountyPercentageTableDraft;
