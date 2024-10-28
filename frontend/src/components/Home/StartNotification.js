// displays a notification (a bootstrap Toast to be specific) when the user starts a simulation
import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Toast from 'react-bootstrap/Toast';
import ToastContainer from 'react-bootstrap/ToastContainer';

const StartNotification = ( {isRunning, shouldNotify, changeNotify} ) => {
  const [show, setShow] = useState(false);
  
  useEffect(() => {
    console.log("isRunning?", isRunning);
    if (isRunning) {setShow(true)};
  }, [isRunning])

  const handleClose = () => {
    setShow(false);
    changeNotify(false);
  }

  return (
      <Col xs={6}>
        <ToastContainer 
          className="notification-container" 
          style = {{zIndex: '4', left: '11.6em !important', bottom: '85%', width: '14.2em'}}
        >
          <Toast onClose={handleClose} show={show && shouldNotify} delay={3000} autohide>
            <Toast.Body>Starting simulation...</Toast.Body>
          </Toast>
        </ToastContainer>
      </Col>
  )
}

export default StartNotification;
