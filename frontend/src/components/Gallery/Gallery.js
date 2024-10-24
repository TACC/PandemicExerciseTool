// currently unused, the Gallery view allows users to view saved images
import React from 'react';
import './Gallery.css';

// Retrieve saved images from local storage
const getSavedImages = () => {
  return JSON.parse(localStorage.getItem('savedImages')) || [];
};

const GalleryView = () => {
  const savedImages = getSavedImages();

  return (
    <div className="gallery-view-container">
      <div className="gallery-grid">
        {savedImages.map((image, index) => (
          <div key={index} className="gallery-item">
            <div className="image-title">{image.name}</div>
            <img src={image.url} alt={image.name} className="gallery-image" />
            <a href={image.url} download={image.name} className="download-button">Download</a>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GalleryView;
