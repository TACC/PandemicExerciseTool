// InfectedMap.js
import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, LayersControl, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import texasOutline from './texasOutline.json';
import './Legend.css'; // Ensure you have a CSS file for styling
import '../fonts/fonts.css';

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

      div.innerHTML = `<strong>Count</strong>${labels.join('')}`;
      return div;
    };

    legend.addTo(map);

    return () => {
      legend.remove();
    };
  }, [map]);

  return null;
};


const LegendPercentage = () => {
  const map = useMap();

  useEffect(() => {
    const legend = L.control({ position: 'bottomright' });

    legend.onAdd = function () {
      const div = L.DomUtil.create('div', 'info legend');
      // the spacing of percent buckets looks uneven, but closely matches our counts (assuming max of 5000)
      const ranges = [
        { min: 40, max: Infinity },
        { min: 30, max: 40 },
        { min: 20, max: 30 },
        { min: 10, max: 20 },
        { min: 5, max: 10 },
        { min: 2.5, max: 5 },
        { min: 1, max: 2.5 },
        { min: 0, max: 1 },
      ];
      const labels = [];

      ranges.forEach((range, index) => {
        const color = getColor(range.min);
        labels.push(
          `<div class="legend-item">
            <div class="color-box" style="background:${color};"></div>
            <span>
                ${range.min === 0 ? `< ${range.max}%` :
                  range.min === 40 ? `> ${range.min}%` :
                 `${range.min} -`}
                ${range.max === 1 ? '' :
                  range.max === Infinity ? '' :
                 `${range.max}%`}
            </span>
          </div>`
        );
      });

      div.innerHTML = `<strong>Infected (Percent)</strong>${labels.join('')}`;
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
const InfectedMap = ({ eventData, currentIndex }) => {
  const [countyData, setCountyData] = useState([]);
  const mapRef = useRef();

  useEffect(() => {
    const texasCounties = parseTexasOutline(texasOutline);
    if (eventData && eventData.length > 0 && typeof currentIndex !== 'undefined') {
      // Get the event data for the specific day (currentIndex)
      const specificDayEventData = eventData.find(event => event.day === currentIndex)?.counties || [];

      const data = texasCounties.map(county => {
        const countyEvent = specificDayEventData.find(event => event.fips === county.geoid);
        return {
          county: county.name,
          fips: county.geoid,
          infected: countyEvent ? countyEvent.infected : 0,
          deceased: countyEvent ? countyEvent.deceased : 0
        };
      });
      setCountyData(data);
    }
  }, [eventData, currentIndex]);

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

  const onEachCountyDeceased = (feature, layer) => {
    const geoid = feature.properties.geoid;
    const countyInfo = countyData.find(item => item.fips === geoid);

    if (countyInfo) {
      const tooltipContent = `${countyInfo.county}: ${countyInfo.deceased} deceased`;
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
    return {
      fillColor: getColor(infectedCount),
      weight: 1,
      color: 'black',
      fillOpacity: 0.7
    };
  };

  const geoJsonStyleDeceased = (feature) => {
    const countyInfo = countyData.find(item => item.fips === feature.properties.geoid);
    const deceasedCount = countyInfo ? countyInfo.deceased : 0;
    return {
      fillColor: getColor(deceasedCount),
      weight: 1,
      color: 'black',
      fillOpacity: 0.7
    };
  };

  return (
    <div>
      <MapContainer
        id="map"
        center={[31.0, -100.0]}
        zoomSnap={0.2}
        zoom={5.4}
        style={{ height: '38em', width: '95em', backgroundColor: 'white' }}
        whenCreated={mapInstance => { mapRef.current = mapInstance; }}
      >
        <LayersControl position="topright">
          {/* Base Layers */}
          <LayersControl.BaseLayer checked name="By Infected">
            <GeoJSON
              key={JSON.stringify(countyData)}
              data={texasOutline}
              style={geoJsonStyle}
              onEachFeature={onEachCounty}
            />
            <Legend />
          </LayersControl.BaseLayer>

          <LayersControl.BaseLayer name="By Deceased">
            <GeoJSON
              key={JSON.stringify(countyData)}
              data={texasOutline}
              style={geoJsonStyleDeceased}
              onEachFeature={onEachCountyDeceased}
            />
            {/* <LegendPercentage/> */}
          </LayersControl.BaseLayer>


          {/* Overlay for the GeoJSON Infected Counties */}
          {/* <LayersControl.Overlay checked name="By Count">
            <GeoJSON
              key={JSON.stringify(countyData)}
              data={texasOutline}
              style={geoJsonStyle}
              onEachFeature={onEachCounty}
            />
            <Legend/>
          </LayersControl.Overlay> */}

          {/* <LayersControl.Overlay name="By Deceased">
            <GeoJSON
              key={JSON.stringify(countyData)}
              data={texasOutline}
              style={geoJsonStyleDeceased}
              onEachFeature={onEachCounty}
            />
          </LayersControl.Overlay> */}

        </LayersControl>

      </MapContainer>
    </div>
  );
};

export default InfectedMap;
