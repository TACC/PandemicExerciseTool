import React, { useState } from 'react';
import './Header.css';
import epiengage_logo_darkblue from './epiengage_logo_darkblue.jpg';
import GalleryView from '../GalleryView';
import UserGuideView from '../UserGuideView';
import HomeView from '../HomeView';
import ChartView from '../ChartView';


const Header = ({ currentIndex, setCurrentIndex }) => {
  const [activeTab, setActiveTab] = useState('home');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'home':
        return <HomeView currentIndex={currentIndex} setCurrentIndex={setCurrentIndex}/>;
      case 'chart':
        return <ChartView />;
      case 'gallery':
        return <GalleryView />;
      case 'userguide':
        return <UserGuideView />;
      default:
        return <HomeView currentIndex={currentIndex} setCurrentIndex={setCurrentIndex}/>;
    }
  };

  return (
    <div className="container">
      <div className="header">
        <div className="logo-container">
          <img src={epiengage_logo_darkblue} alt="EpiEngage Logo" className="logo" />
        </div>
        <div className="text-container">
          <h1>epiENGAGE</h1>
        </div>
        <div className="tabs">
          <button
            className={`tab-button ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            Home
          </button>
          <button
            className={`tab-button ${activeTab === 'chart' ? 'active' : ''}`}
            onClick={() => setActiveTab('chart')}
          >
            Chart View
          </button>
          <button
            className={`tab-button ${activeTab === 'gallery' ? 'active' : ''}`}
            onClick={() => setActiveTab('gallery')}
          >
            Gallery
          </button>
          <button
            className={`tab-button ${activeTab === 'userguide' ? 'active' : ''}`}
            onClick={() => setActiveTab('userguide')}
          >
            User Guide
          </button>
        </div>
        <div className="text-container">
          <h1>Flu Simulator</h1>
        </div>
      </div>
      <div className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default Header;
