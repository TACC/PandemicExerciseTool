import React, { useState, useEffect, useRef } from 'react';
import html2canvas from 'html2canvas';
import texasCounties from './counties';
import TimelineSlider from './TimelineSlider';
import DeceasedLineChart from './DeceasedLineChart';
import StateCountyDropdowns from './StateCountyDropdown';
import CountyPercentageTable from './CountyPercentageTable';
import InitialMapPercent from './InitialMapPercent';
import SetParametersDropdown from './SetParametersDropdown';
import Interventions from './Interventions';
import './ChartView.css';
import { Responsive, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

import OUTPUT_0 from './OUTPUT_0.json';
import OUTPUT_1 from './OUTPUT_1.json';
import OUTPUT_2 from './OUTPUT_2.json';
import OUTPUT_3 from './OUTPUT_3.json';
import OUTPUT_4 from './OUTPUT_4.json';
import OUTPUT_5 from './OUTPUT_5.json';
import OUTPUT_6 from './OUTPUT_6.json';
import OUTPUT_7 from './OUTPUT_7.json';
import OUTPUT_8 from './OUTPUT_8.json';
import OUTPUT_9 from './OUTPUT_9.json';

const ChartView = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [eventData, setEventData] = useState([]);
  const [outputFiles] = useState([
    OUTPUT_0, OUTPUT_1, OUTPUT_2, OUTPUT_3, OUTPUT_4, OUTPUT_5,
    OUTPUT_6, OUTPUT_7, OUTPUT_8, OUTPUT_9
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [fileName, setFileName] = useState('');
  const [imgData, setImgData] = useState(''); // State to store image data URL
  const chartViewRef = useRef();

  const handleDayChange = (index) => {
    console.log(`Day changed to: ${index}`);
    setCurrentIndex(index);
  };

  const handleRunScenario = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    intervalRef.current = setInterval(() => {
      setCurrentIndex((prevIndex) => {
        if (prevIndex < outputFiles.length - 1) {
          return prevIndex + 1;
        } else {
          clearInterval(intervalRef.current);
          return prevIndex;
        }
      });
    }, 1000);
  };

  const handlePauseScenario = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };

  const handleScreenshot = async () => {
    if (chartViewRef.current) {
      try {
        const canvas = await html2canvas(chartViewRef.current);
        const dataUrl = canvas.toDataURL('image/png');
        setImgData(dataUrl); // Store the image data URL
        setModalVisible(true); // Show the modal
        setFileName('screenshot.png'); // Set default file name
      } catch (error) {
        console.error("Error capturing screenshot:", error);
      }
    }
  };

  const handleSaveScreenshot = () => {
    if (fileName && imgData) {
      const storedImages = JSON.parse(localStorage.getItem('savedImages')) || [];
      storedImages.push({ url: imgData, name: fileName });
      localStorage.setItem('savedImages', JSON.stringify(storedImages));

      const link = document.createElement('a');
      link.href = imgData;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      setModalVisible(false);
      setFileName(''); // Reset file name
      setImgData(''); // Clear image data
    }
  };

  const ResponsiveGridLayout = WidthProvider(Responsive);
  const layout = [
    { i: 'timeline', x: 0, y: 6, w: 10, h: 6 },
    { i: 'chart', x: 6, y: 0, w: 10, h: 7 },
    { i: 'map', x: 0, y: 0, w: 6, h: 12 },
    { i: 'table', x: 6, y: 6, w: 3, h: 12 },
  ];

  useEffect(() => {
    if (outputFiles[currentIndex]) {
      console.log('Output Data:', outputFiles[currentIndex]);

      const deceasedCount = outputFiles[currentIndex].data.reduce((acc, county) => {
        const { D } = county.compartments;
        const totalDeceased = [
          ...D.U.L,
          ...D.U.H,
          ...D.V.L,
          ...D.V.H,
        ].reduce((sum, value) => sum + value, 0);
        return acc + totalDeceased;
      }, 0);

      setEventData((prevData) => {
        const newData = [...prevData];
        if (!newData[currentIndex]) {
          newData[currentIndex] = { day: currentIndex, deceased: Math.round(deceasedCount) };
        } else {
          newData[currentIndex].deceased = Math.round(deceasedCount);
        }
        return newData.slice(0, currentIndex + 1);
      });
    }
  }, [currentIndex, outputFiles]);

  return (
    <div className="chart-view" ref={chartViewRef}>
      <div className="left-panel">
        <StateCountyDropdowns />
        <div className="interventions-container">
          <Interventions />
        </div>
        <button onClick={handleScreenshot} className="screenshot-button">Take Screenshot</button>
      </div>
      <ResponsiveGridLayout
        className="grid-layout"
        layouts={{ lg: layout }}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={30}
      >
        <div key="timeline">
          {isLoading ? <LoadingSpinner /> : <TimelineSlider
            totalDays={outputFiles.length}
            selectedDay={currentIndex}
            onDayChange={handleDayChange}
            onScenarioRun={handleRunScenario}
            onScenarioPause={handlePauseScenario}
          />}
        </div>
        <div key="chart">
          {isLoading ? <LoadingSpinner /> : <DeceasedLineChart eventData={eventData} />}
        </div>
        <div key="map">
          {isLoading ? <LoadingSpinner /> : <InitialMapPercent outputData={outputFiles[currentIndex]} />}
        </div>
        <div key="table">
          {isLoading ? <LoadingSpinner /> : <CountyPercentageTable className="percentage-table" outputData={outputFiles[currentIndex]} />}
        </div>
      </ResponsiveGridLayout>

      {/* Modal for file name input */}
      {modalVisible && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Save Screenshot</h2>
            <input
              type="text"
              value={fileName}
              onChange={(e) => setFileName(e.target.value)}
              placeholder="Enter file name"
            />
            <button onClick={handleSaveScreenshot} className="save-button">Save</button>
            <button onClick={() => setModalVisible(false)} className="cancel-button">Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChartView;
