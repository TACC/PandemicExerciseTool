// LineChart.js visualizes SEATIRD data for a given scenario and/or interventions
// Used in Homeview.js
import React from 'react';
import Plot from 'react-plotly.js';
import '../../index.css';

const LineChart = ({ eventData, currentIndex, npiData }) => {
  // Prepare data for the chart
  const traces = [
    {
      x: eventData.map(event => event.day),
      y: eventData.map(event => event.totalSusceptible),
      mode: 'lines+markers',
      name: 'Susceptible',
      line: {
        color: 'rgba(75,192,192,1)',
        shape: 'spline',
      },
      marker: {
        color: eventData.map((_, index) => (index === currentIndex ? 'red' : 'rgba(75,192,192,1)')),
        size: eventData.map((_, index) => (index === currentIndex ? 10 : 5)),
      },
    },
    {
      x: eventData.map(event => event.day),
      y: eventData.map(event => event.totalExposed),
      mode: 'lines+markers',
      name: 'Exposed',
      line: {
        color: 'rgba(255,165,0,1)',
        shape: 'spline',
      },
      marker: {
        color: eventData.map((_, index) => (index === currentIndex ? 'red' : 'rgba(255,165,0,1)')),
        size: eventData.map((_, index) => (index === currentIndex ? 10 : 5)),
      },
    },
    {
      x: eventData.map(event => event.day),
      y: eventData.map(event => event.totalAsymptomaticCount),
      mode: 'lines+markers',
      name: 'Asymptomatic',
      line: {
        color: 'rgba(173,216,230,1)',
        shape: 'spline',
      },
      marker: {
        color: eventData.map((_, index) => (index === currentIndex ? 'red' : 'rgba(173,216,230,1)')),
        size: eventData.map((_, index) => (index === currentIndex ? 10 : 5)),
      },
    },
    {
      x: eventData.map(event => event.day),
      y: eventData.map(event => event.totalTreatableCount),
      mode: 'lines+markers',
      name: 'Treatable',
      line: {
        color: 'rgba(34,139,34,1)',
        shape: 'spline',
      },
      marker: {
        color: eventData.map((_, index) => (index === currentIndex ? 'red' : 'rgba(34,139,34,1)')),
        size: eventData.map((_, index) => (index === currentIndex ? 10 : 5)),
      },
    },
    {
      x: eventData.map(event => event.day),
      y: eventData.map(event => event.totalInfectedCount),
      mode: 'lines+markers',
      name: 'Infected',
      line: {
        color: 'rgba(255,69,0,1)',
        shape: 'spline',
      },
      marker: {
        color: eventData.map((_, index) => (index === currentIndex ? 'red' : 'rgba(255,69,0,1)')),
        size: eventData.map((_, index) => (index === currentIndex ? 10 : 5)),
      },
    },
    {
      x: eventData.map(event => event.day),
      y: eventData.map(event => event.totalRecoveredCount),
      mode: 'lines+markers',
      name: 'Recovered',
      line: {
        color: 'rgba(0,0,255,1)',
        shape: 'spline',
      },
      marker: {
        color: eventData.map((_, index) => (index === currentIndex ? 'red' : 'rgba(0,0,255,1)')),
        size: eventData.map((_, index) => (index === currentIndex ? 10 : 5)),
      },
    },
    {
      x: eventData.map(event => event.day),
      y: eventData.map(event => event.totalDeceased),
      mode: 'lines+markers',
      name: 'Deceased',
      line: {
        color: 'rgba(0,0,0,1)',
        shape: 'spline',
      },
      marker: {
        color: eventData.map((_, index) => (index === currentIndex ? 'red' : 'rgba(0,0,0,1)')),
        size: eventData.map((_, index) => (index === currentIndex ? 10 : 5)),
      },
    },
  ];

  // Parse NPI data to get start and end days
  const shapes = [];
  const annotations = [];

  if (npiData && npiData.length > 0) {
    npiData.forEach(npi => {
      const startDay = parseInt(npi.day, 10); // Start day of the NPI
      const duration = parseInt(npi.duration, 10); // Duration of the NPI
      const endDay = startDay + duration; // Calculate the end day

      const maxPopulationCount = Math.max(
        ...eventData.map(event => Math.max(
          event.totalSusceptible, event.totalExposed,
          event.totalAsymptomaticCount, event.totalTreatableCount,
          event.totalInfectedCount, event.totalRecoveredCount,
          event.totalDeceased
        ))
      );

      // Background fill between start and end days
      shapes.push({
        type: 'rect',
        x0: startDay,
        y0: 0,
        x1: endDay,
        y1: maxPopulationCount,
        fillcolor: 'rgba(255, 192, 203, 0.2)', // Light pink background for NPI duration
        line: { width: 0 }, // No border
      });

      // Dotted vertical lines for start and end days
      shapes.push(
        {
          type: 'line',
          x0: startDay,
          y0: 0,
          x1: startDay,
          y1: maxPopulationCount,
          line: {
            color: 'rgba(255,0,0,0.5)', // Color for start day
            width: 2,
            dash: 'dot', // Dotted line
          },
        },
        {
          type: 'line',
          x0: endDay,
          y0: 0,
          x1: endDay,
          y1: maxPopulationCount,
          line: {
            color: 'rgba(0,0,255,0.5)', // Color for end day
            width: 2,
            dash: 'dot', // Dotted line
          },
        }
      );

      // Add annotations for start and end days at the bottom
      annotations.push(
        {
          x: startDay,
          y: -10, // Position below the y-axis
          xref: 'x',
          yref: 'y',
          text: `Start: ${npi.name}`,
          showarrow: true,
          arrowhead: 2,
          ax: 0,
          ay: -40,
          font: {
            size: 12,
            color: 'rgba(255,0,0,1)', // Color for start text
          },
        },
        {
          x: endDay,
          y: -10, // Position below the y-axis
          xref: 'x',
          yref: 'y',
          text: `End: ${npi.name}`,
          showarrow: true,
          arrowhead: 2,
          ax: 0,
          ay: -40,
          font: {
            size: 12,
            color: 'rgba(0,0,255,1)', // Color for end text
          },
        }
      );
    });
  }

  const layout = {
    autosize: true,
    hovermode: 'closest',
    height: 365,
    margin: {
      l: 70,
      r: 0,
      t: 80,
      b: 50,
      pad: 4,
    },
    title: {
      text: 'Statewide Trends',
      font: { size: 25, family: 'GilroyBold', color: 'black' },
    },
    xaxis: {
      title: {
        text: 'Day',
        font: { size: 20, family: 'GilroyRegular', color: 'black' },
      },
      tickfont: { size: 16, family: 'GilroyRegular', color: 'black' },
      rangemode: 'nonnegative',
    },
    yaxis: {
      title: {
        text: 'Population Count',
        font: { size: 20, family: 'GilroyRegular', color: 'black' },
      },
      tickfont: { size: 16, family: 'GilroyRegular', color: 'black' },
      rangemode: 'normal',
    },
    showlegend: true,
    legend: {
      font: { size: 16, family: 'GilroyRegular', color: 'black' },
      bgcolor: 'rgba(0, 0, 0, 0)',
      orientation: 'h',
      x: 0.5,
      y: 1.16,
      xanchor: 'center',
    },
    shapes: shapes,
    annotations: annotations,
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: 'auto' }}>
      <Plot id='Line-Chart' data={traces} layout={layout} style={{ width: '100%', height: '100%', marginTop: '-1em' }} useResizeHandler={true} />
    </div>
  );
};

export default React.memo(LineChart);
