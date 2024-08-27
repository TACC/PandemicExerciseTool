import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';
import '../fonts/fonts.css';

// Register ChartJS components
ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const DeceasedLineChart = ({ eventData }) => {
  // Prepare data for the chart
  const data = {
    labels: eventData.map(event => event.day), // Only day numbers on the x-axis
    datasets: [
      {
        label: 'Deceased',
        data: eventData.map(event => event.deceased),
        fill: false,
        borderColor: 'rgba(75,192,192,1)', // Line color
        backgroundColor: 'rgba(75,192,192,0)', // No fill color
        tension: 0.1,
        pointRadius: 3, // Optional: Add some radius for data points
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
        callbacks: {
          title: function (context) {
            const day = context[0].label;
            return `Day ${day}`; // Tooltip title showing "Day _: _"
          },
          label: function (context) {
            return `Deceased: ${context.raw}`;
          },
        },
        // Optionally, customize tooltip font style here
        // For the tooltip, add font settings directly within the tooltip callbacks
        // or via global settings if you need it to be applied globally
      },
      title: {
        display: true,
        text: 'Total Deaths',
        font: {
          size: 25, // Larger title font size
          weight: 'bold',
          family: 'Gilroy', // Font family
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
            size: 20, // Larger x-axis title font size
            family: 'Gilroy', // Font family
          },
        },
        ticks: {
          color: 'black', // Change x-axis tick labels color to black
          font: {
            size: 20, // Larger x-axis tick labels font size
            family: 'Gilroy', // Font family
          },
          callback: function (value, index, values) {
            return `${value}`; // Display only the day number on the x-axis
          },
        },
      },
      y: {
        title: {
          display: true,
          text: 'Total Deceased',
          color: 'black', // Change y-axis title color to black
          font: {
            size: 20, // Larger y-axis title font size
            family: 'Gilroy', // Font family
          },
        },
        ticks: {
          color: 'black', // Change y-axis tick labels color to black
          font: {
            size: 16, // Larger y-axis tick labels font size
            family: 'Gilroy', // Font family
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

export default DeceasedLineChart;
