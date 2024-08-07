import React from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import countiesData from './countiesData.json';
import texasOutline from './texasOutline.json';
import './InfectedChart.css'; // Import your CSS file for styling
import ChartParameters from './ChartParameters';
import texasCounties from './counties';

const InfectedChart = () => {
  const getColor = (density) => {
    return density > 100
      ? '#800026'
      : density > 50
      ? '#BD0026'
      : density > 20
      ? '#E31A1C'
      : density > 10
      ? '#FC4E2A'
      : density > 5
      ? '#FD8D3C'
      : density > 2
      ? '#FEB24C'
      : density > 1
      ? '#FED976'
      : '#FFEDA0';
  };

  const style = (feature) => {
    return {
      fillColor: getColor(feature.properties.density),
      weight: 2,
      opacity: 1,
      color: 'black',
      dashArray: '3',
      fillOpacity: 0.7,
    };
  };

  return (
    <div className="infected-chart-container">
    <ChartParameters counties={texasCounties} />
    <div className="map-container">
      <MapContainer center={[31.0, -100.0]} zoom={6} style={{ height: '500px', width: '800px' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <GeoJSON data={countiesData} style={style} />
      </MapContainer>
    </div>
  </div>
  );
};

export default InfectedChart;