import React from 'react';
import ExampleLayout from './ExampleLayout'; // Adjust path as necessary
import './GalleryView.css'; // Import custom CSS for styling
import exampleGalleryImg from './images/example_gallery.png';

import OUTPUT_0 from './OUTPUT_0.json';
import OUTPUT_1 from './OUTPUT_1.json';
import OUTPUT_2 from './OUTPUT_2.json';
import OUTPUT_3 from './OUTPUT_3.json';
import OUTPUT_4 from './OUTPUT_4.json';
import OUTPUT_5 from './OUTPUT_5.json';
import OUTPUT_6 from './OUTPUT_6.json';
import OUTPUT_7 from './OUTPUT_7.json';
import OUTPUT_8 from './OUTPUT_8.json';
import OUTPUT_9 from './OUTPUT_9.json';


const outputs = [
  OUTPUT_0, OUTPUT_1, OUTPUT_2, OUTPUT_3, OUTPUT_4, 
  OUTPUT_5, OUTPUT_6, OUTPUT_7, OUTPUT_8, OUTPUT_9
];

const GalleryView = () => {
  return (
    <div className="galleryViewContainer">
    <h1>Gallery View</h1>
    <div className="imageContainer">
      <img src={exampleGalleryImg} alt="Gallery" className="galleryImage" />
    </div>
  </div>
    
  );
};

export default GalleryView;
