import React, { useState } from 'react';
import './Header.css';
import epiengage_logo_darkblue from './epiengage_logo_darkblue.jpg';
import GalleryView from '../GalleryView';
import UserGuideView from '../UserGuideView';
import HomeView from '../HomeView';
import ChartView from '../ChartView';

import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';


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
      <Navbar expand="lg" fixed="top" style={{ backgroundColor: "#102c41" }}>
        <Container >
          <img
            src={require('./epiengage_logo_darkblue.jpg')}
            width="60"
            height="60"
            className="align-top header-logo"
            alt="EpiEngage Logo"
          />
          <a class="navbar-brand" className='header-name'>epiENGAGE</a>

          <Navbar.Toggle aria-controls="basic-navbar-nav" className="custom-toggler" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="navbar-nav mx-auto mb-2 mb-lg-0">
              <ul class="navbar-nav mx-auto mb-2 mb-lg-0">
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
            </Nav>
            <ul class="nav navbar-nav navbar-right">
              <li><a className='header-right'> Interactive Outbreak Simulator</a></li>
            </ul>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <div class="container-fluid" className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
};
export default Header;



