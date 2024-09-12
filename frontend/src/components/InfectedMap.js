// InfectedMap.js
import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import texasOutline from './texasOutline.json';
import './Legend.css'; // Ensure you have a CSS file for styling

// Function to determine color based on infected count
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

// Function to parse Texas outline GeoJSON
const parseTexasOutline = (texasOutline) => {
  return texasOutline.features.map((feature) => ({
    name: feature.properties.name,
    geoid: feature.properties.geoid
  }));
};

// Component to create a legend for the map
const Legend = () => {
  const map = useMap();

  useEffect(() => {
    const legend = L.control({ position: 'bottomright' });

    legend.onAdd = function () {
      const div = L.DomUtil.create('div', 'info legend');
      const ranges = [
        { min: 5000, max: Infinity },
        { min: 2000, max: 5000 },
        { min: 1000, max: 2000 },
        { min: 500, max: 1000 },
        { min: 200, max: 500 },
        { min: 100, max: 200 },
        { min: 50, max: 100 },
        { min: 0, max: 50 }
      ];
      const labels = [];

      ranges.forEach((range, index) => {
        const color = getColor(range.min);
        labels.push(
          `<div class="legend-item">
            <div class="color-box" style="background:${color};"></div>
            <span>${range.min}${range.max === Infinity ? '+' : `–${range.max}`}</span>
          </div>`
        );
      });

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

// Main component to render the map
const InfectedMap = ({ eventData }) => {
  const [countyData, setCountyData] = useState([]);
  const mapRef = useRef();

  useEffect(() => {
    const texasCounties = parseTexasOutline(texasOutline);
    if (eventData && eventData.length > 0) {
      // Assume we're using the latest day's data
      const latestDayEventData = eventData[eventData.length - 1]?.counties || [];
      const data = texasCounties.map(county => {
        const countyEvent = latestDayEventData.find(event => event.fips === county.geoid);
        return {
          county: county.name,
          fips: county.geoid,
          infected: countyEvent ? countyEvent.infected : 0
        };
      });
      setCountyData(data);
      console.log('County data loaded:', data); // Debug log
    }
  }, [eventData]);

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
    // console.log(`County: ${feature.properties.name}, Infected: ${infectedCount}`); // Debug log
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
  }, [eventData]);

  return (
    <div>
    <MapContainer
      id="map"
      center={[31.0, -100.0]}
      zoom={6}
      style={{ height: '620px', width: '1700px', backgroundColor: 'white' }}
      whenCreated={mapInstance => { mapRef.current = mapInstance; }}
    >
      {countyData.length > 0 && (
        <GeoJSON
          key={JSON.stringify(eventData)}
          data={texasOutline}
          style={geoJsonStyle}
          onEachFeature={onEachCounty}
        />
      )}

      {/* Ref for the black outline layer */}
      <GeoJSON
        data={texasOutline}
        style={{
          color: '#000',  // Black outline color
          weight: 1,      // Thicker outline for visibility
          fillOpacity: 0, // Transparent fill
          interactive: false, // Disable interaction
        }}
        ref={(layer) => {
          if (layer) {
            layer.bringToFront(); // Bring the outline layer to the front
          }
        }}
      />

      <Legend />
    </MapContainer>
  </div>
  );
};

export default InfectedMap;
