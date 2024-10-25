// displays a notification when the user starts a simulation
// TODO: more docstrings here
import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Toast from 'react-bootstrap/Toast';
import ToastContainer from 'react-bootstrap/ToastContainer';

const StartNotification = (isRunning) => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    console.log("isRunning?", isRunning.isRunning);
    if (isRunning.isRunning) {setShow(true)};
  }, [isRunning])

  return (
      <Col xs={6}>
        <ToastContainer 
          className="notification-container" 
          // position={'bottom-center'}
          style = {{zIndex: '4', left: '11.6em !important', bottom: '85%', width: '14.2em'}}
        >
          <Toast onClose={() => setShow(false)} show={show} delay={3000} autohide>
            <Toast.Body>Starting simulation...</Toast.Body>
          </Toast>
        </ToastContainer>
      </Col>
  )
}

export default StartNotification;
