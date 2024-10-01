import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';
import '../index.css';

// Register ChartJS components
ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const DeceasedLineChart = ({ eventData, currentIndex }) => {
  // Prepare data for the chart
  const data = {
    labels: eventData.map(event => event.day), // Only day numbers on the x-axis
    datasets: [
      {
        label: 'Deceased',
        data: eventData.map(event => event.totalDeceased),
        fill: false,
        borderColor: 'rgba(75,192,192,1)', // Line color
        backgroundColor: 'rgba(75,192,192,0)', // No fill color
        pointRadius: 3, // Optional: Add some radius for data points
        pointBackgroundColor: eventData.map((_, index) =>
          index === currentIndex ? 'red' : 'rgba(75,192,192,1)' // Highlight the current day
        ),
        pointBorderWidth: eventData.map((_, index) =>
          index === currentIndex ? 5 : 1 // Thicker border for the current day's point
        ),
      },
    ],
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // Remove the legend
      },
      tooltip: {
        enabled: true, // Ensure tooltip is enabled
        backgroundColor: 'rgba(0, 0, 0, 0.7)', // Darker background for the tooltip
        titleFont: {
          size: 18, // Larger font for the tooltip title
          family: 'GilroyBold',
        },
        bodyFont: {
          size: 16, // Larger font for the tooltip body
          family: 'GilroyBold',
        },
        padding: 15, // Increase padding inside the tooltip
        callbacks: {
          title: function (context) {
            const day = context[0].label;
            return `Day ${day}`; // Tooltip title showing "Day _"
          },
          label: function (context) {
            return `Deceased: ${context.raw}`; // Tooltip label showing deceased count
          },
        },
      },
      title: {
        display: true,
        text: 'Total Deaths',
        font: {
          size: 30, // Larger title font size
          weight: 'bold',
          family: 'GilroyBold', // Font family
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Day',
          color: 'black', // Change x-axis title color to black
          font: {
            size: 25, // Larger x-axis title font size
            family: 'GilroyRegular', // Font family
          },
        },
        ticks: {
          color: 'black', // Change x-axis tick labels color to black
          font: {
            size: 20, // Larger x-axis tick labels font size
            family: 'GilroyRegular', // Font family

          },
        },
      },
      y: {
        title: {
          display: true,
          text: 'Total Deaths',
          color: 'black', // Change y-axis title color to black
          font: {
            size: 25, // Larger y-axis title font size
            family: 'GilroyRegular', // Font family
          },
        },
        ticks: {
          color: 'black', // Change y-axis tick labels color to black
          font: {
            size: 16, // Larger y-axis tick labels font size
            family: 'GilroyRegular', // Font family
          },
        },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', minHeight: '300px' }}>
      <Line data={data} options={options} />
    </div>
  );
};

export default React.memo(DeceasedLineChart);
