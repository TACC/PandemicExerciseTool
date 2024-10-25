// displays a notification (a bootstrap Toast to be specific) when the user starts a simulation
// FIXME: since shouldNotify isn't directly tied to the POST request in Home.js, there are some
// instances where starting a simulation will not display the notification, e.g. pausing and
// resuming a simulation without changing the scenario. it would be smarter to pass shouldNotify
// as a prop from Home.js and set it to true every time a simulation is paused
import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Toast from 'react-bootstrap/Toast';
import ToastContainer from 'react-bootstrap/ToastContainer';

const StartNotification = (isRunning) => {
  const [show, setShow] = useState(false);
  const [shouldNotify, setShouldNotify] = useState(false);

  // only display the notification once
  useEffect(() => {
    setShouldNotify(true);
  }, [])

  useEffect(() => {
    console.log("isRunning?", isRunning.isRunning);
    if (isRunning.isRunning) {setShow(true)};
  }, [isRunning])

  const handleClose = () => {
    setShow(false);
    setShouldNotify(false);
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
