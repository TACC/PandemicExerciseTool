// LineChart.js visualizes SEATIRD data for a given scenario and/or interventions
// Used in Homeview.js
import React from 'react';
import Plot from 'react-plotly.js';
import '../../index.css';

const LineChart = ({ eventData, currentIndex, npiData }) => {
  const createTrace = (name, yData, lineColor) => ({
    x: eventData.map(event => event.day),
    y: yData,
    mode: 'lines+markers',
    name,
    line: { color: lineColor, shape: 'spline' },
    marker: {
      color: eventData.map((_, index) => (index === currentIndex ? 'red' : lineColor)),
      size: eventData.map((_, index) => (index === currentIndex ? 10 : 5)),
    },
  });

  const traces = [
    createTrace('Susceptible', eventData.map(event => event.totalSusceptible), 'rgba(75,192,192,1)'),
    createTrace('Exposed', eventData.map(event => event.totalExposed), 'rgba(255,165,0,1)'),
    createTrace('Asymptomatic', eventData.map(event => event.totalAsymptomaticCount), 'rgba(173,216,230,1)'),
    createTrace('Treatable', eventData.map(event => event.totalTreatableCount), 'rgba(34,139,34,1)'),
    createTrace('Infected', eventData.map(event => event.totalInfectedCount), 'rgba(255,69,0,1)'),
    createTrace('Recovered', eventData.map(event => event.totalRecoveredCount), 'rgba(0,0,255,1)'),
    createTrace('Deceased', eventData.map(event => event.totalDeceased), 'rgba(0,0,0,1)'),
  ];

  const maxPopulationCount = Math.max(
    ...eventData.flatMap(event =>
      [
        event.totalSusceptible, event.totalExposed, event.totalAsymptomaticCount,
        event.totalTreatableCount, event.totalInfectedCount, event.totalRecoveredCount,
        event.totalDeceased,
      ]
    )
  );

  const shapes = [];
  const annotations = [];

  if (npiData) {
    npiData.forEach(npi => {
      const startDay = parseInt(npi.day, 10);
      const endDay = startDay + parseInt(npi.duration, 10);

      shapes.push(
        {
          type: 'rect',
          x0: startDay,
          y0: 0,
          x1: endDay,
          y1: maxPopulationCount,
          fillcolor: 'rgba(255, 192, 203, 0.2)',
          line: { width: 0 },
        },
        {
          type: 'line',
          x0: startDay,
          y0: 0,
          x1: startDay,
          y1: maxPopulationCount,
          line: { color: 'rgba(255,0,0,0.5)', width: 2, dash: 'dot' },
        },
        {
          type: 'line',
          x0: endDay,
          y0: 0,
          x1: endDay,
          y1: maxPopulationCount,
          line: { color: 'rgba(0,0,255,0.5)', width: 2, dash: 'dot' },
        }
      );

      annotations.push(
        {
          x: startDay,
          y: -10,
          xref: 'x',
          yref: 'y',
          text: `Start: ${npi.name}`,
          showarrow: true,
          arrowhead: 2,
          ax: 0,
          ay: -40,
          font: { size: 12, color: 'rgba(255,0,0,1)' },
        },
        {
          x: endDay,
          y: -10,
          xref: 'x',
          yref: 'y',
          text: `End: ${npi.name}`,
          showarrow: true,
          arrowhead: 2,
          ax: 0,
          ay: -40,
          font: { size: 12, color: 'rgba(0,0,255,1)' },
        }
      );
    });
  }

  const layout = {
    autosize: true,
    hovermode: 'closest',
    height: 365,
    margin: { l: 70, r: 0, t: 80, b: 50, pad: 4 },
    title: { text: 'Statewide Trends', font: { size: 25, family: 'GilroyBold', color: 'black' } },
    xaxis: {
      title: { text: 'Day', font: { size: 20, family: 'GilroyRegular', color: 'black' } },
      tickfont: { size: 16, family: 'GilroyRegular', color: 'black' },
      rangemode: 'nonnegative',
    },
    yaxis: {
      title: { text: 'Population Count', font: { size: 20, family: 'GilroyRegular', color: 'black' } },
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
    shapes,
    annotations,
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: 'auto' }}>
      <Plot id='Line-Chart' data={traces} layout={layout} style={{ width: '100%', height: '100%', marginTop: '-1em' }} useResizeHandler={true} />
    </div>
  );
};

export default React.memo(LineChart);
