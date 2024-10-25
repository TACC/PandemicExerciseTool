// displays a notification when the user starts a simulation
// TODO: more docstrings here
import React, { useState, useEffect, useRef } from 'react';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Toast from 'react-bootstrap/Toast';
import Overlay from 'react-bootstrap/Overlay';

const StartNotification = (isRunning, target) => {
  const [show, setShow] = useState(true);
  console.log("ref.current:", target.current);

  useEffect(() => {
    console.log("isRunning?", isRunning.isRunning);
    if (isRunning.isRunning) {setShow(true)};
  }, [isRunning])

  return (
    <>
      <Overlay target={target.current} show={show} placement="right">
        {({
          placement: _placement,
          arrowProps: _arrowProps,
          show: _show,
          popper: _popper,
          hasDoneInitialMeasure: _hasDoneInitialMeasure,
          ...props
        }) => (
          <div
            {...props}
            style={{
              position: 'absolute',
                backgroundColor: 'white',
                padding: '2px 10px',
                color: 'black',
                borderRadius: 4,
                ...props.style,
              }}
          >
            Starting simulation...
          </div>
        )}
      </Overlay>
    </>
  );
}

export default StartNotification;
