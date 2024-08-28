// App.js

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './HomePage'; // Adjust the import path as needed
import ChatComponent from './ChatComponent'; // Import ChatComponent if needed in other routes

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat/:chatroomName" element={<ChatComponent />} />
        {/* Add other routes as needed */}
      </Routes>
    </Router>
  );
}

export default App;
