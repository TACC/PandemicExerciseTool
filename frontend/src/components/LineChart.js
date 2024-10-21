import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';
import '../index.css';

// Register ChartJS components
ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const LineChart = ({ eventData, currentIndex }) => {
  // Prepare data for the chart
  const data = {
    labels: eventData.map(event => event.day), // Only day numbers on the x-axis
    datasets: [
      {
        label: 'Susceptible',
        data: eventData.map(event => event.totalSusceptible),
        fill: false,
        borderColor: 'rgba(75,192,192,1)', // Line color for Susceptible
        backgroundColor: 'rgba(75,192,192,1)', 
        pointRadius: 1,
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(75,192,192,1)'
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1
        ),
      },
      {
        label: 'Exposed',
        data: eventData.map(event => event.totalExposed),
        fill: false,
        borderColor: 'rgba(255,165,0,1)', // Line color for Exposed
        backgroundColor: 'rgba(255,165,0,1)', 
        pointRadius: 1,
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(255,165,0,1)'
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1
        ),
      },
      {
        label: 'Asymptomatic',
        data: eventData.map(event => event.totalAsymptomaticCount),
        fill: false,
        borderColor: 'rgba(173,216,230,1)', // Line color for Asymptomatic
        backgroundColor: 'rgba(173,216,230,1)',
        pointRadius: 1,
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(173,216,230,1)'
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1
        ),
      },
      {
        label: 'Treatable',
        data: eventData.map(event => event.totalTreatableCount),
        fill: false,
        borderColor: 'rgba(34,139,34,1)', // Line color for Treatable
        backgroundColor: 'rgba(34,139,34,1)',
        pointRadius: 1,
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(34,139,34,1)'
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1
        ),
      },
      {
        label: 'Infected',
        data: eventData.map(event => event.totalInfectedCount),
        fill: false,
        borderColor: 'rgba(255,69,0,1)', // Line color for Infected
        backgroundColor: 'rgba(255,69,0,1)',
        pointRadius: 1,
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(255,69,0,1)'
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1
        ),
      },
      {
        label: 'Recovered',
        data: eventData.map(event => event.totalRecoveredCount),
        fill: false,
        borderColor: 'rgba(0,0,255,1)', // Line color for Recovered
        backgroundColor: 'rgba(0,0,255,1)',
        pointRadius: 1,
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(0,0,255,1)'
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1
        ),
      },
      {
        label: 'Deceased',
        data: eventData.map(event => event.totalDeceased),
        fill: false,
        borderColor: 'rgba(0,0,0,1)', // Line color for Deceased
        backgroundColor: 'rgba(0,0,0,1)',
        pointRadius: 1,
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(0,0,0,1)'
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1
        ),
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
      line: {
        tension: 0,
        cubicInterpolationMode: 'monotone',
      },
    },
    plugins: {
      legend: {
        display: true,
        fill: true,
        labels: {
          font: {
            size: 16,
            family: 'GilroyRegular',
          },
          color: 'black',
          boxWidth: 15,
          boxHeight: 15,
          usePointStyle: false,
        },
      },
      tooltip: {
        enabled: true,
        intersect: false, // Makes sure the tooltip follows the cursor vertically
        backgroundColor: 'white',
        titleColor: 'black',
        bodyColor: 'black',
        borderColor: 'black',
        borderWidth: 2,
        padding: 10,
        cornerRadius: 0,
        titleFont: {
          size: 18,
          family: 'GilroyRegular',
        },
        bodyFont: {
          size: 18,
          family: 'GilroyRegular',
        },
        padding: 15,
        callbacks: {
          title: function (context) {
            const day = context[0].label;
            return `Day ${day}`;
          },
          label: function (context) {
            return `${context.dataset.label}: ${context.raw}`;
          },
        },
      },
      title: {
        display: true,
        text: 'Statewide Trends',
        color: 'black',
        font: {
          size: 25,
          weight: 'bold',
          family: 'GilroyBold',
        },
      },
      // Custom plugin to draw the vertical line
      crosshairLine: {
        id: 'crosshairLine',
        afterDraw(chart) {
          if (chart.tooltip._active && chart.tooltip._active.length) {
            const activePoint = chart.tooltip._active[0];
            const ctx = chart.ctx;
            const x = activePoint.element.x; // Get x position of the active point
            const topY = chart.scales.y.top;
            const bottomY = chart.scales.y.bottom;
  
            // Draw the vertical line
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(x, topY);
            ctx.lineTo(x, bottomY);
            ctx.lineWidth = 2;
            ctx.strokeStyle = 'rgba(0,0,0,0.5)';
            ctx.stroke();
            ctx.restore();
          }
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Day',
          color: 'black',
          font: {
            size: 20,
            family: 'GilroyRegular',
          },
        },
        ticks: {
          color: 'black',
          font: {
            size: 20,
            family: 'GilroyRegular',
          },
        },
        grid: {
          display: false,
        },
      },
      y: {
        title: {
          display: true,
          text: 'Population Count',
          color: 'black',
          font: {
            size: 20,
            family: 'GilroyRegular',
          },
        },
        ticks: {
          color: 'black',
          font: {
            size: 16,
            family: 'GilroyRegular',
          },
        },
        beginAtZero: true,
        grid: {
          display: false,
        },
      },
    },
  };
  
  // Register the plugin
  ChartJS.register({
    id: 'crosshairLine',
    afterDraw(chart) {
      if (chart.tooltip._active && chart.tooltip._active.length) {
        const activePoint = chart.tooltip._active[0];
        const ctx = chart.ctx;
        const x = activePoint.element.x; // Get x position of the active point
        const topY = chart.scales.y.top;
        const bottomY = chart.scales.y.bottom;
  
        // Draw the vertical line
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(x, topY);
        ctx.lineTo(x, bottomY);
        ctx.lineWidth = 2;
        ctx.strokeStyle = 'rgba(0,0,0,0.5)';
        ctx.stroke();
        ctx.restore();
      }
    },
  });
  
  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '350px' }}>
      <Line data={data} options={options} />
    </div>
  );
};

export default React.memo(LineChart);
