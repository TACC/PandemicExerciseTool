import React, { useState, useEffect } from 'react';
import '../App.css'; // Adjust CSS as needed
import search from './images/search.png'; // Assuming you have this image
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
      deceased: totalDeceased,
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
        populationData[row.FIPS] = parseInt(row.E_TOTPOP, 10);
      });
    },
  });

  return populationData;
};

function CountyPercentageTable({ outputData }) {
  const [mergedData, setMergedData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortDirection, setSortDirection] = useState({
    county: 'asc',
    infectedPercentage: 'desc',
    deceasedPercentage: 'desc',
    infected: 'desc',
    population: 'asc',
  });

  useEffect(() => {
    const fetchData = async () => {
      const countyNameLookup = await loadCountyNames();
      const parsedInfectionData = parseInfectionData(outputData, countyNameLookup);
      const populationData = await loadPopulationData();

      const merged = parsedInfectionData.map(data => {
        const population = populationData[data.fips] || 0;
        const infectedPercentage = population > 0 ? (data.infected / population) * 100 : 0;
        const deceasedPercentage = population > 0 ? (data.deceased / population) * 100 : 0;

        return {
          ...data,
          population: population,
          infectedPercentage: infectedPercentage.toFixed(2),
          deceasedPercentage: deceasedPercentage.toFixed(2),
        };
      });

      setMergedData(merged);
      setFilteredData(merged); // Initialize filtered data
    };

    fetchData();
  }, [outputData]);

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
                Infected (%)
                <button className="sort-button" onClick={() => sortData('infectedPercentage')}>
                  {sortDirection.infectedPercentage === 'asc' ? '↓' : '↑'}
                </button>
              </th>
              <th>
                Deceased (%)
                <button className="sort-button" onClick={() => sortData('deceasedPercentage')}>
                  {sortDirection.deceasedPercentage === 'asc' ? '↓' : '↑'}
                </button>
              </th>
              <th>
                Infected
                <button className="sort-button" onClick={() => sortData('infected')}>
                  {sortDirection.infected === 'asc' ? '↓' : '↑'}
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
                <td>{county.infectedPercentage}</td>
                <td>{county.deceasedPercentage}</td>
                <td>{county.infected}</td>
                <td>{county.population}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default CountyPercentageTable;
