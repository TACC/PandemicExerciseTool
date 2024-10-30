// <Header /> is invoked in App.js, all other views are rendered here
import React, { useState, useEffect } from 'react';
import './Header.css';
import epiengage_logo_darkblue from './epiengage_logo_darkblue.jpg';
import GalleryView from '../Gallery/Gallery';
import UserGuideView from '../UserGuide/UserGuide';
import Home from '../Home/Home';
import ChartView from '../discontinued/ChartView';
import axios from 'axios';

import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

axios.defaults.baseURL = "http://localhost:8000";

const Header = ({ currentIndex, setCurrentIndex }) => {
  const [activeTab, setActiveTab] = useState('home');

  // add an EventListener that warns the user before leaving the page and wiping parameters/simulation
  useEffect(() => {
    window.addEventListener('beforeunload', alertUser);
    window.addEventListener('unload', handlePageLeave);
    return () => {
      window.removeEventListener('beforeunload', alertUser);
      window.removeEventListener('unload', handlePageLeave);
      handlePageLeave();
    }
  }, [])

  const alertUser = e => {
    e.preventDefault();
    e.returnValue = '';
  }

  const handlePageLeave = async () => {
    localStorage.clear();
    await axios.get('api/reset');
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'home':
        return <Home currentIndex={currentIndex} setCurrentIndex={setCurrentIndex} />;
      /* case 'chart':
         return <ChartView />;
       case 'gallery':
         return <GalleryView />;*/
      case 'userguide':
        return <UserGuideView />;
      default:
        return <Home currentIndex={currentIndex} setCurrentIndex={setCurrentIndex} />;
    }
  };

  return (
    <div>
      <Navbar expand="lg" fixed="top" style={{ backgroundColor: "#102c41" }}>
        <Container fluid>
          <img
            src={require('./epiengage_logo_darkblue.jpg')}
            width="60"
            height="60"
            className="align-top header-logo"
            alt="EpiEngage Logo"
          />
          <Navbar className='header-name'>epiENGAGE</Navbar>
          <Navbar.Toggle aria-controls="navbarScroll" className="custom-toggler" />
          <Navbar.Collapse id="navbarScroll">
            <Nav
              className="mx-auto my-2 my-lg-0"
              style={{ maxHeight: '100px' }}
              navbarScrollx
            >
              <Nav>
                <ul className="navbar-nav mx-auto mb-2 mb-lg-0">
                  <li >
                    <a aria-current="page"
                      className={`tab-button ${activeTab === 'home' ? 'active' : ''}`}
                      onClick={() => setActiveTab('home')}>Home</a>
                  </li>
                  <li>
                    <a
                      className={`tab-button ${activeTab === 'userguide' ? 'active' : ''}`}
                      onClick={() => setActiveTab('userguide')}>User Guide</a>
                  </li>
                  {/* <li> */}
                  {/*   <a aria-current="page" */}
                  {/*     className={`tab-button ${activeTab === 'gallery' ? 'active' : ''}`} */}
                  {/*     onClick={() => setActiveTab('gallery')}>Gallery</a> */}
                  {/* </li> */}
                </ul>
              </Nav>
            </Nav>
            <Nav>
              <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                <li><a className='header-right'> Interactive Outbreak Simulator</a></li>
              </ul>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <div className="container-fluid" className="tab-content">
        {renderTabContent()}
      </div>
    </div>
  );
};
export default Header;


