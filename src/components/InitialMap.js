import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import texasOutline from './texasOutline.json';
import './Legend.css'; // Ensure you have a CSS file for styling

const getColor = (infectedCount) => {
  return infectedCount > 5000 ? '#800026' :
    infectedCount > 2000 ? '#BD0026' :
      infectedCount > 1000 ? '#E31A1C' :
        infectedCount > 500 ? '#FC4E2A' :
          infectedCount > 200 ? '#FD8D3C' :
            infectedCount > 100 ? '#FEB24C' :
              infectedCount > 50 ? '#FED976' :
                '#FFEDA0';
};

const parseTexasOutline = (texasOutline) => {
  return texasOutline.features.map((feature) => ({
    name: feature.properties.name,
    geoid: feature.properties.geoid
  }));
};

const parseData = (jsonData, texasCounties) => {
  if (!jsonData || !jsonData.data) {
    console.error('No data or invalid data format:', jsonData);
    return [];
  }

  return jsonData.data.map((county) => {
    const { fips_id, compartments } = county;
    const { I } = compartments;
    const totalInfected = [
      ...I.U.L,
      ...I.U.H,
      ...I.V.L,
      ...I.V.H
    ].reduce((sum, value) => sum + value, 0);

    const countyName = texasCounties.find(tc => tc.geoid === fips_id)?.name || 'Unknown';

    return {
      county: countyName,
      fips: fips_id,
      infected: Math.round(totalInfected) // Round the infected count
    };
  });
};

const Legend = () => {
  const map = useMap();

  useEffect(() => {
    const legend = L.control({ position: 'bottomright' });

    legend.onAdd = function () {
      const div = L.DomUtil.create('div', 'info legend');
      const ranges = [
        { min: 0, max: 50 },
        { min: 50, max: 100 },
        { min: 100, max: 200 },
        { min: 200, max: 500 },
        { min: 500, max: 1000 },
        { min: 1000, max: 2000 },
        { min: 2000, max: 5000 },
        { min: 5000, max: Infinity }
      ];
      const labels = [];

      ranges.forEach(range => {
        labels.push(
          `<div class="legend-item">
            <i style="background:${getColor(range.min)}"></i>
            <span>${range.min} &ndash; ${range.max === Infinity ? '5000+' : range.max}</span>
          </div>`
        );
      });

      // Reverse the labels array to display colors from bottom to top
      labels.reverse();

      div.innerHTML = `<strong>Infected Count</strong>${labels.join('')}`;
      return div;
    };

    legend.addTo(map);

    return () => {
      legend.remove();
    };
  }, [map]);

  return null;
};

const InitialMap = ({ outputData }) => {
  const [countyData, setCountyData] = useState([]);
  const mapRef = useRef();

  useEffect(() => {
    const texasCounties = parseTexasOutline(texasOutline);
    if (outputData) {
      const data = parseData(outputData, texasCounties);
      setCountyData(data);
      console.log('County data loaded:', data); // Debug log
    }
  }, [outputData]);

  const onEachCounty = (feature, layer) => {
    const geoid = feature.properties.geoid;
    const countyInfo = countyData.find(item => item.fips === geoid);

    if (countyInfo) {
      const tooltipContent = `${countyInfo.county}: ${countyInfo.infected} infected`;
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
    const infectedCount = countyInfo ? countyInfo.infected : 0;
    console.log(`County: ${feature.properties.name}, Infected: ${infectedCount}`); // Debug log
    return {
      fillColor: getColor(infectedCount),
      weight: 1,
      color: 'white',
      fillOpacity: 0.7
    };
  };

  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.eachLayer(layer => {
        if (layer instanceof L.GeoJSON) {
          layer.clearLayers();
        }
      });
    }
  }, [outputData]);

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

export default InitialMap;
