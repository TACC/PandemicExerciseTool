import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';

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
        borderColor: 'rgba(75,192,192,1)',
        tension: 0.1,
      },
    ],
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 14, // Increase legend font size
            weight: 'bold', // Optional: Make the font bold
          },
        },
      },
      tooltip: {
        callbacks: {
          title: function (context) {
            const day = context[0].label;
            return `Day ${day}`; // Tooltip title showing "Day _: _"
          },
          label: function (context) {
            return `Deceased: ${context.raw}`;
          },
        },
      },
      title: {
        display: true,
        text: 'Total Deaths',
        font: {
          size: 18, // Increase title font size
          weight: 'bold', // Optional: Make the title bold
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
            size: 16, // Increase x-axis title font size
          },
        },
        ticks: {
          color: 'black', // Change x-axis tick labels color to black
          font: {
            size: 14, // Increase x-axis tick labels font size
          },
          callback: function (value, index, values) {
            return `${value}`; // Display only the day number on the x-axis
          },
        },
      },
      y: {
        title: {
          display: true,
          text: 'Total Deceased Count',
          color: 'black', // Change y-axis title color to black
          font: {
            size: 16, // Increase y-axis title font size
          },
        },
        ticks: {
          color: 'black', // Change y-axis tick labels color to black
          font: {
            size: 14, // Increase y-axis tick labels font size
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
