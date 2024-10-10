import React, { useState } from 'react';
import './Header.css';
import epiengage_logo_darkblue from './epiengage_logo_darkblue.jpg';
import GalleryView from '../GalleryView';
import UserGuideView from '../UserGuideView';
import HomeView from '../HomeView';
import ChartView from '../ChartView';
import "../../node_modules/bootstrap/dist/css/bootstrap.min.css";
import "../../node_modules/bootstrap/dist/js/bootstrap.bundle.min.js";

const Header = ({ currentIndex, setCurrentIndex }) => {
  const [activeTab, setActiveTab] = useState('home');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'home':
        return <HomeView currentIndex={currentIndex} setCurrentIndex={setCurrentIndex} />;
      /* case 'chart':
         return <ChartView />;
       case 'gallery':
         return <GalleryView />;*/
      case 'userguide':
        return <UserGuideView />;
      default:
        return <HomeView currentIndex={currentIndex} setCurrentIndex={setCurrentIndex} />;
    }
  };

  return (
    <div>
      <nav class="navbar navbar-expand-lg bg-body-tertiary fixed-top">
        <div class="container-fluid" style={{ backgroundColor: "#102c41" }}>
          <img
            src={require('./epiengage_logo_darkblue.jpg')}
            width="70"
            height="70"
            className="d-inline-block align-top"
            alt="EpiEngage Logo"
          />
          <a class="navbar-brand" className='header-name'>epiENGAGE</a>

          <button class="navbar-toggler custom-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarTogglerDemo02" aria-controls="navbarTogglerDemo02" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>

          <div class="collapse navbar-collapse" id="navbarTogglerDemo02">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li class="nav-item" >
                <a class="nav-link" aria-current="page"
                  className={`tab-button ${activeTab === 'home' ? 'active' : ''}`}
                  onClick={() => setActiveTab('home')}>Home</a>
              </li>
              <li class="nav-item" >
                <a class="nav-link"
                  className={`tab-button ${activeTab === 'userguide' ? 'active' : ''}`}
                  onClick={() => setActiveTab('userguide')}>User Guide</a>
              </li>
            </ul>
            <ul class="nav navbar-nav navbar-right">
              <li><a className='header-right'><span class="glyphicon glyphicon-user"></span> Interactive Outbreak Simulator</a></li>            
            </ul>

            {/* <li class="nav-item">
              <p class="nav-link" className='header-right'>Interactive Outbreak Simulator</p>
            </li> */}
          </div>
        </div>
      </nav>
      <div class="container-fluid" className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
};


export default Header;



