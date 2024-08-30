// src/components/ILIView.js

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import texasOutline from '../texasOutline.json';

const ILIView = ({ day }) => {
  const [outputData, setOutputData] = useState(null);

  useEffect(() => {
    const fetchOutputData = async () => {
      try {
        const response = await fetch(`OUTPUT_${day + 1}.json`);
        const jsonData = await response.json();
        setOutputData(jsonData);
      } catch (error) {
        console.error('Error fetching output data:', error);
      }
    };

    fetchOutputData();
  }, [day]);

  if (!outputData) {
    return <div>Loading...</div>;
  }

  // Modify your map rendering logic here using outputData
  return (
    <MapContainer center={[31.0, -100.0]} zoom={6} style={{ height: '500px', width: '800px' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <GeoJSON
        data={texasOutline}
        style={() => ({
          fillColor: '#238b45',
          weight: 1,
          color: 'white',
          fillOpacity: 0.7
        })}
      />
      {/* Additional layers or GeoJSON based on outputData */}
    </MapContainer>
  );
};

export default ILIView;
