// one of two main map components that tracks the infections per county as a percentage of that county's population
// this component is invoked in <Home /> and renders in the top-middle of Home view
import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L, { transformation } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import texasOutline from '../../data/texasOutline.json';
import './Legend.css'; // Ensure you have a CSS file for styling
import '../../fonts/fonts.css';
import { IoHomeSharp } from "react-icons/io5";

// Function to determine color based on infected count
const getColor = (infectedPercent) => {
  return infectedPercent >= 40 ? "#BD0026" :
         infectedPercent >= 30 ? "#E31A1B" :
         infectedPercent >= 20 ? "#FC4F2A" :
         infectedPercent >= 10 ? "#FD8D3D" :
         infectedPercent >= 5 ? "#FEB24C" :
         infectedPercent >= 2.5 ? "#FED976" :
         infectedPercent >= 1 ? "#FFEDA0" :
                  "#FFEDA0";
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

const Legend = () => {
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


const SpreadMapPercent = ({ eventData, currentIndex }) => {
  const [countyData, setCountyData] = useState([]);
  const mapRef = useRef();

  useEffect(() => {
    const texasCounties = parseTexasOutline(texasOutline);
    if (eventData && eventData.length > 0 && typeof currentIndex !== "undefined") {
      // get event data for the specific day
      const specificDayEventData = eventData.find(event => event.day === currentIndex)?.counties || [];

      const data = texasCounties.map(county => {
        const countyEvent = specificDayEventData.find(event => event.fips === county.geoid);
        return {
        county: county.name,
        fips: county.geoid,
        infectedPercent: countyEvent ? countyEvent.infectedPercent: 0
        };
      });
      setCountyData(data);
    }
  }, [eventData, currentIndex]);

const onEachCounty = (feature, layer) => {
    const geoid = feature.properties.geoid;
    const countyInfo = countyData.find(item => item.fips === geoid);

    if (countyInfo) {
      const tooltipContent = `${countyInfo.county}: ${countyInfo.infectedPercent}% infected`;
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
    const infectedPercentCount = countyInfo ? countyInfo.infectedPercent: 0;
    return {
      fillColor: getColor(infectedPercentCount),
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
        style={{ height: '35em', backgroundColor: 'transparent'}}
        attributionControl={false}
        whenCreated={mapInstance => {mapRef.current=mapInstance; }}
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

export default SpreadMapPercent;
