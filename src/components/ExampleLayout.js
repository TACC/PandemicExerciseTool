import React from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import TexasChoropleth from './TexasChoropleth'; // Import TexasChoropleth component
import './ExampleLayout.css'; // Import custom CSS for styling

const ResponsiveGridLayout = WidthProvider(Responsive);

class ExampleLayout extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      layout: [
        { i: 'map', x: 0, y: 0, w: 6, h: 6 }, // Layout for TexasChoropleth
        { i: 'cell1', x: 6, y: 0, w: 6, h: 6 }, // Additional cell 1
        { i: 'cell2', x: 0, y: 6, w: 6, h: 6 }, // Additional cell 2
        { i: 'cell3', x: 6, y: 6, w: 6, h: 6 }, // Additional cell 3
      ],
      countyData: [] // Initialize county data state
    };
    this.onLayoutChange = this.onLayoutChange.bind(this);
  }

  componentDidMount() {
    // Simulate fetching county data (replace with your actual data fetching logic)
    setTimeout(() => {
      const mockCountyData = [
        { county: 'County A', infected: 100 },
        { county: 'County B', infected: 250 },
        // Add more counties as needed
      ];
      this.setState({ countyData: mockCountyData });
    }, 1000);
  }

  onLayoutChange(layout) {
    this.setState({ layout });
  }

  render() {
    const { countyData } = this.state;

    return (
      <div className="exampleLayoutContainer">
        <ResponsiveGridLayout
          className="layout"
          layouts={{ lg: this.state.layout }}
          breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
          cols={{ lg: 12, md: 12, sm: 12, xs: 12, xxs: 12 }}
          rowHeight={window.innerHeight / 12}
          width={window.innerWidth}
          onLayoutChange={this.onLayoutChange}
        >
          {this.state.layout.map((item) => (
            <div key={item.i} data-grid={item} className="layoutItem">
              {item.i === 'map' && (
                <div className="mapContainer">
                  <TexasChoropleth countyData={countyData} />
                </div>
              )}
              {item.i !== 'map' && (
                <div className="placeholder">
                  <h3>{`Cell ${item.i}`}</h3>
                </div>
              )}
            </div>
          ))}
        </ResponsiveGridLayout>
      </div>
    );
  }
}

export default ExampleLayout;
