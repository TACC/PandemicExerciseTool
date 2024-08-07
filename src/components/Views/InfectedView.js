import React from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import texasOutline from '../texasOutline.json';

class InfectedView extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        countyData: props.countyData || [] // Initialize countyData state with props or an empty array
      };
    }
  
    componentDidUpdate(prevProps) {
      // Update state if props change
      if (this.props.countyData !== prevProps.countyData) {
        this.setState({ countyData: this.props.countyData });
      }
    }
  
    getColor = (infectedCount) => {
      // Function to determine color based on infected count
      // You can customize this function as needed
      return infectedCount > 500 ? '#800026' :
        infectedCount > 200 ? '#BD0026' :
          infectedCount > 100 ? '#E31A1C' :
            infectedCount > 50 ? '#FC4E2A' :
              infectedCount > 20 ? '#FD8D3C' :
                infectedCount > 10 ? '#FEB24C' :
                  infectedCount > 5 ? '#FED976' :
                    '#FFEDA0';
    };
  
    onEachCounty = (county, layer) => {
      const name = county.properties.name; // Assuming county names are stored in the "name" property
      const { countyData } = this.state;
      const countyInfo = countyData.find(item => item.county === name);
  
      if (countyInfo) {
        layer.bindTooltip(`${name}: ${countyInfo.infected} infected`, { permanent: false, direction: 'auto' });
      }
    };
  
    render() {
      return (
        <MapContainer center={[31.0, -100.0]} zoom={6} style={{ height: '500px', width: '800px' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <GeoJSON
            data={texasOutline}
            style={(feature) => ({
              fillColor: this.getColor(this.state.countyData.find(item => item.county === feature.properties.name)?.infected || 0),
              weight: 1,
              color: 'white',
              fillOpacity: 0.7
            })}
            onEachFeature={this.onEachCounty}
          />
        </MapContainer>
      );
    }
  }

export default InfectedView;