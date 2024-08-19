// App.js

import React from 'react';
import ChatComponent from './ChatComponent';

function App() {
  return (
    <div className="App">
      <h1>React Chat Application</h1>
      <ChatComponent chatroomName="general" />
    </div>
  );
}

export default App;
