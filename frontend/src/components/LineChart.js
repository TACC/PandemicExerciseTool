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
        pointRadius: 3,
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
        pointRadius: 3,
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
        pointRadius: 3,
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
        pointRadius: 3,
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
        pointRadius: 3,
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
        pointRadius: 3,
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
        pointRadius: 3,
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(0,0,0,1)'
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1
        ),
      },
    ],
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
      line: {
        tension: 0, // Adjust tension, lower value flattens the line, reducing dips
        cubicInterpolationMode: 'monotone', // Smooths out the line
      },
    },
    plugins: {
      legend: {
        display: true, // Display legend for all datasets
        labels: {
          font: {
            size: 18, // Increase the font size for legend labels
            family: 'GilroyRegular', // You can customize the font family as well
          },
          color: 'black', // Set the color of the labels (optional)
        },
      },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        titleFont: {
          size: 18,
          family: 'GilroyBold',
        },
        bodyFont: {
          size: 20,
          family: 'GilroyBold',
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
        text: 'Total Compartments',
        color: 'black',
        font: {
          size: 30,
          weight: 'bold',
          family: 'GilroyBold',
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
            size: 25,
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
      },
      y: {
        title: {
          display: true,
          text: 'Population Count',
          color: 'black',
          font: {
            size: 25,
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
      },
    },
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '295px' }}>
      <Line data={data} options={options} />
    </div>
  );
};

export default React.memo(LineChart);
