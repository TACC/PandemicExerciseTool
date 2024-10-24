import React from 'react';
import Plot from 'react-plotly.js';
import '../index.css';

const LineChart = ({ eventData, currentIndex }) => {
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

  const layout = {
    autosize: true, // Adjusts the plot to fit the container
    hovermode: 'closest',
    height: 350,
    margin: {
      l: 70, // Left margin
      r: 0, // Right margin
      t: 80, // Top margin
      b: 50, // Bottom margin (increased to provide space for tick labels)
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
      rangemode: 'noraml',
    },

    // Center the legend horizontally and place the legend slightly above the plot area
    showlegend: true,
    legend: {
      font: { size: 16, family: 'GilroyRegular', color: 'black' },
      bgcolor: 'rgba(0, 0, 0, 0)', // Set background color to transparent
      orientation: 'h',
      x: 0.5,
      y: 1.16,
      xanchor: 'center',
    },
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: 'auto' }}>
      <Plot id='Line-Chart' data={traces} layout={layout} style={{ width: '100%', height: '100%', marginTop: '-1em' }} useResizeHandler={true} />
    </div>
  );
};

export default React.memo(LineChart);
