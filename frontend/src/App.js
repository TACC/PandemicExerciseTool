import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header/Header'
import "./index.css"


const App = () => {
  const [showInitialCases, setShowInitialCases] = useState(true);
  const [showParameters, setShowParameters] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [data, setData] = useState([]); // State to store fetched data
  const totalDays = 30; // Total number of days
  const [isRunning, setIsRunning] = useState(false);

  const handleToggleInitialCases = () => {
    setShowInitialCases(true);
    setShowParameters(false);
  };

  const handleToggleParameters = () => {
    setShowInitialCases(false);
    setShowParameters(true);
  };


  return (
    <div className="App">
      <Header currentIndex={currentIndex} setCurrentIndex={setCurrentIndex} />
      <div>
      </div>
    </div>
  );
};

export default App;