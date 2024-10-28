// LineChart.js visualizes SEATIRD data for a given scenario and/or interventions
// Used in Homeview.js
import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import '../../index.css';

const LineChart = ({ eventData, currentIndex, npiData }) => {
  // Function to create a trace
  const createTrace = (name, yData, lineColor) => ({
    x: eventData.map(event => event.day),
    y: yData,
    mode: 'lines+markers',
    name,
    line: { color: lineColor, shape: 'spline', width: 2.5 },
    marker: {
      color: eventData.map((_, index) => (index === currentIndex ? 'red' : lineColor)),
      size: new Array(eventData.length).fill(0).map((_, i) => (i === eventData.length - 1 ? 10 : 0)),
    },
    text: eventData.map((event, index) => `<b>Day ${event.day}</b><br>${name}: ${yData[index].toLocaleString()}`),
    hoverinfo: 'text',
    hoverlabel: {
      font: { family: 'GilroyRegular', size: 14, color: 'white' },
    },
  });

  // Memoized traces to avoid unnecessary calculations
  const traces = useMemo(() => [
    createTrace('Susceptible', eventData.map(event => event.totalSusceptible), 'rgba(75,192,192,1)'),
    createTrace('Exposed', eventData.map(event => event.totalExposed), 'rgba(255,165,0,1)'),
    createTrace('Asymptomatic', eventData.map(event => event.totalAsymptomaticCount), 'rgba(173,216,230,1)'),
    createTrace('Treatable', eventData.map(event => event.totalTreatableCount), 'rgba(34,139,34,1)'),
    createTrace('Infected', eventData.map(event => event.totalInfectedCount), 'rgba(255,69,0,1)'),
    createTrace('Recovered', eventData.map(event => event.totalRecoveredCount), 'rgba(0,0,255,1)'),
    createTrace('Deceased', eventData.map(event => event.totalDeceased), 'rgba(0,0,0,1)'),
  ], [eventData, currentIndex]);

  // Calculate max population count
  const maxPopulationCount = Math.max(
    ...eventData.flatMap(event => [
      event.totalSusceptible, event.totalExposed, event.totalAsymptomaticCount,
      event.totalTreatableCount, event.totalInfectedCount, event.totalRecoveredCount, event.totalDeceased,
    ])
  );

  // Generate shapes and annotations for NPIs
  const { shapes, annotations } = useMemo(() => {
    const shapeList = [];
    const annotationList = [];

    npiData?.forEach(npi => {
      const startDay = parseInt(npi.day, 10);
      const endDay = startDay + parseInt(npi.duration, 10);

      shapeList.push(
        { type: 'rect', x0: startDay, y0: 0, x1: endDay, y1: maxPopulationCount, fillcolor: 'rgba(255, 192, 203, 0.2)', line: { width: 0 } },
        { type: 'line', x0: startDay, y0: 0, x1: startDay, y1: maxPopulationCount, line: { color: 'rgba(255,0,0,0.5)', width: 2, dash: 'dot' } },
        { type: 'line', x0: endDay, y0: 0, x1: endDay, y1: maxPopulationCount, line: { color: 'rgba(0,0,255,0.5)', width: 2, dash: 'dot' } }
      );

      annotationList.push(
        { x: startDay, y: -10, xref: 'x', yref: 'y', text: `Start: ${npi.name}`, showarrow: true, arrowhead: 2, ax: 0, ay: -100, font: { size: 12, color: 'rgba(255,0,0,1)' } },
        { x: endDay, y: -10, xref: 'x', yref: 'y', text: `End: ${npi.name}`, showarrow: true, arrowhead: 2, ax: 0, ay: -50, font: { size: 12, color: 'rgba(0,0,255,1)' } }
      );
    });

    return { shapes: shapeList, annotations: annotationList };
  }, [npiData, maxPopulationCount]);

  // Layout configuration
  const commonFont = { family: 'GilroyRegular', color: 'black' };
  const layout = {
    autosize: true,
    hovermode: 'closest',
    height: 365,
    margin: { l: 70, r: 0, t: 80, b: 50, pad: 4 },
    title: { text: 'Statewide Trends', font: { ...commonFont, size: 25, family: 'GilroyBold' } },
    xaxis: {
      title: { text: 'Day', font: { ...commonFont, size: 20 } },
      tickfont: { ...commonFont, size: 16 },
      rangemode: 'nonnegative',
    },
    yaxis: {
      title: { text: 'Population Count', font: { ...commonFont, size: 20 } },
      tickfont: { ...commonFont, size: 16 },
      rangemode: 'normal',
    },
    showlegend: true,
    legend: {
      font: { ...commonFont, size: 16 },
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
      <Plot data={traces} layout={layout} style={{ width: '100%', height: '100%', marginTop: '-1em' }} useResizeHandler={true}/>
    </div>
  );
};

export default React.memo(LineChart);
