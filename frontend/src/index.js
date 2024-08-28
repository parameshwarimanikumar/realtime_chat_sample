import React from 'react';
import ReactDOM from 'react-dom';
import HomePage from './HomePage'; // Import your main component
import './index.css'; // Import global CSS

// Render the HomePage component into the DOM
ReactDOM.render(
  <React.StrictMode>
    <HomePage />
  </React.StrictMode>,
  document.getElementById('root') // This should match the id in your index.html
);
