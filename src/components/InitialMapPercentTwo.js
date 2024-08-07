import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import texasOutline from './texasOutline.json';
import Papa from 'papaparse';
import './Legend.css'; // Ensure you have a CSS file for styling

// Load population data from CSV
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

// Color mapping function
const getColor = (infectedPercent) => {
  return infectedPercent > 0.5 ? '#800026' :
         infectedPercent > 0.4 ? '#BD0026' :
         infectedPercent > 0.3 ? '#E31A1C' :
         infectedPercent > 0.2 ? '#FC4E2A' :
         infectedPercent > 0.1 ? '#FD8D3C' :
         infectedPercent > 0.05 ? '#FEB24C' :
                                   '#FED976';
};

// Parsing Texas outline data
const parseTexasOutline = (texasOutline) => {
  return texasOutline.features.map((feature) => ({
    name: feature.properties.name,
    geoid: feature.properties.geoid
  }));
};

// Parsing and calculating infected percentage
const parseData = async (jsonData, texasCounties, populationData) => {
  if (!jsonData || !jsonData.data) {
    console.error('No data or invalid data format:', jsonData);
    return [];
  }

  const rawData = jsonData.data.map((county) => {
    const { fips_id, compartments } = county;
    const { I } = compartments;
    const totalInfected = [
      ...I.U.L,
      ...I.U.H,
      ...I.V.L,
      ...I.V.H
    ].reduce((sum, value) => sum + value, 0);

    const population = populationData[fips_id] || 0;
    const infectedPercent = population > 0 ? (totalInfected / population) * 100 : 0;

    const countyName = texasCounties.find(tc => tc.geoid === fips_id)?.name || 'Unknown';

    return {
      county: countyName,
      fips: fips_id,
      infected: Math.ceil(totalInfected), // Round up the infected count
      infectedPercent: infectedPercent.toFixed(2)
    };
  });

  return rawData;
};

// Legend component integrated into InitialMapPercentTwo
const InitialMapPercentTwo = ({ outputData }) => {
  const [countyData, setCountyData] = useState([]);
  const mapRef = useRef();

  useEffect(() => {
    const fetchData = async () => {
      const texasCounties = parseTexasOutline(texasOutline);
      const populationData = await loadPopulationData();

      if (outputData) {
        const data = await parseData(outputData, texasCounties, populationData);
        setCountyData(data);
        console.log('County data loaded:', data); // Debug log
      }
    };

    fetchData();
  }, [outputData]);

  const onEachCounty = (feature, layer) => {
    const geoid = feature.properties.geoid;
    const countyInfo = countyData.find(item => item.fips === geoid);

    if (countyInfo) {
      const tooltipContent = `${countyInfo.county}: ${countyInfo.infected} infected (${countyInfo.infectedPercent}%)`;
      layer.bindTooltip(tooltipContent, {
        permanent: false,
        direction: 'auto',
        className: 'county-tooltip'
      });
    } else {
      const tooltipContent = `${feature.properties.name}: No data`;
      layer.bindTooltip(tooltipContent, {
        permanent: false,
        direction: 'auto',
        className: 'county-tooltip'
      });
    }
    layer.on('mouseover', function () {
      this.openTooltip();
    });
    layer.on('mouseout', function () {
      this.closeTooltip();
    });
  };

  const geoJsonStyle = (feature) => {
    const countyInfo = countyData.find(item => item.fips === feature.properties.geoid);
    const infectedPercent = countyInfo ? parseFloat(countyInfo.infectedPercent) : 0;
    console.log(`County: ${feature.properties.name}, Infected %: ${infectedPercent}`); // Debug log
    return {
      fillColor: getColor(infectedPercent),
      weight: 1,
      color: 'white',
      fillOpacity: 0.7
    };
  };

  // Clean up layers on outputData change
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.eachLayer(layer => {
        if (layer instanceof L.GeoJSON) {
          layer.clearLayers();
        }
      });
    }
  }, [outputData]);

  // Legend component
  const Legend = () => {
    const map = useMap();

    useEffect(() => {
      const legend = L.control({ position: 'bottomright' });

      legend.onAdd = function () {
        const div = L.DomUtil.create('div', 'info legend');
        const grades = [0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0];
        const labels = [];

        for (let i = 0; i < grades.length; i++) {
          const grade = grades[i];
          const nextGrade = grades[i - 1];
          labels.push(
            `<i style="background:${getColor(grade)}"></i> ${
              grade === 0.5 ? '0.5%+' : `${(grade).toFixed(2)}% - ${nextGrade ? (nextGrade).toFixed(2) : '0%'}`
            }`
          );
        }
        div.innerHTML = `<strong>Infected (%)</strong>${labels.join('<br>')}`;
        return div;
      };

      legend.addTo(map);

      return () => {
        legend.remove();
      };
    }, [map]);

    return null;
  };

  return (
    <div>
      <MapContainer
        id="map"
        center={[31.0, -100.0]}
        zoom={6}
        style={{ height: '500px', width: '800px' }}
        whenCreated={mapInstance => { mapRef.current = mapInstance; }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {countyData.length > 0 && (
          <GeoJSON
            key={JSON.stringify(outputData)}
            data={texasOutline}
            style={geoJsonStyle}
            onEachFeature={onEachCounty}
          />
        )}
        <Legend />
      </MapContainer>
    </div>
  );
};

export default InitialMapPercentTwo;
