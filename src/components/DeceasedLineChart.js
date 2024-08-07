// DeceasedLineChart.js
import React, { useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

const DeceasedLineChart = ({ eventData }) => {
  const chartRef = useRef(null);

  // Prepare data for the chart
  const data = {
    labels: eventData.map(event => `Day ${event.day}`),
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
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return `Deceased: ${context.raw}`;
          },
        },
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Day',
        },
      },
      y: {
        title: {
          display: true,
          text: 'Total Deceased Count',
        },
        beginAtZero: true,
      },
    },
  };

  useEffect(() => {
    // Cleanup code to ensure the chart is destroyed when the component unmounts
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, []);

  return (
    <div className="chart-container">
      <Line ref={chartRef} data={data} options={options} />
    </div>
  );
};

export default DeceasedLineChart;
