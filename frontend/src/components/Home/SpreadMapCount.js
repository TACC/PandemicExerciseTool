// one of two main map components that tracks the number of infections per county 
// this component is invoked in <Home /> and renders in the top-middle of Home view
import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L, { transformation } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import texasOutline from '../../data/texasOutline.json';
import '../Home/Legend.css'; // Ensure you have a CSS file for styling
import '../../fonts/fonts.css'
import { IoHomeSharp } from "react-icons/io5";

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

// Reset button component
const ResetButton = () => {
  const map = useMap();
  const handleReset = () => {
    map.setView([31.0, -100.0], 5.4); // Reset to original center and zoom
  };

  return (
    <button onClick={handleReset} className="map-reset-button">
      <IoHomeSharp size={23} />
    </button>
  );
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
const SpreadMapCount = ({ eventData, currentIndex}) => {
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
          infected: countyEvent ? countyEvent.infected : 0
        };
      });
      setCountyData(data);
      // console.log(`County data loaded for day ${currentIndex}:`, data); // Debug log
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

  /*
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.eachLayer(layer => {
        if (layer instanceof L.GeoJSON) {
          layer.clearLayers();
        }
      });
    }
  }, [eventData]);
*/
  /*

  useEffect(() => {
    if (mapRef.current && outlineLayerRef.current) {
      outlineLayerRef.current.bringToFront(); // Keep the black outline on top
    }
  }, []); // Ensure this only runs once when the map is created
  */

  return (
    <div>
      <MapContainer
        id="map"
        center={[31.0, -100.0]}
        zoomSnap={0.2}
        zoom={5.4}
        style={{ height: '35em', backgroundColor: 'transparent'}}
        attributionControl={false}
        whenCreated={mapInstance => { mapRef.current = mapInstance; }}
      >
        <GeoJSON
          key={JSON.stringify(countyData)}
          data={texasOutline}
          style={geoJsonStyle}
          onEachFeature={onEachCounty}
        />
        <Legend />
        <ResetButton/>
      </MapContainer>
    </div>
  );
};

export default SpreadMapCount;
