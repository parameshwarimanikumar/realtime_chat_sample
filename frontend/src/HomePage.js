import React from 'react';
import './HomePage.css'; // Import your CSS file

const HomePage = () => {
  return (
    <div className="home-page">
      {/* Sidebar with user profile and chat list */}
      <div className="sidebar">
        <div className="profile">
          <img src="/static/images/profile-picture.jpg" alt="Profile" className="profile-pic" />
          <h2 className="username">John Doe</h2>
        </div>
        <div className="search">
          <input type="text" className="search-input" placeholder="Search chats..." />
        </div>
        <div className="chat-list">
          <div className="chat-item">
            <img src="/static/images/chat-avatar1.jpg" alt="Chat 1" className="chat-avatar" />
            <div className="chat-info">
              <h3 className="chat-name">Chat Room 1</h3>
              <p className="chat-preview">Last message preview...</p>
            </div>
          </div>
          <div className="chat-item">
            <img src="/static/images/chat-avatar2.jpg" alt="Chat 2" className="chat-avatar" />
            <div className="chat-info">
              <h3 className="chat-name">Chat Room 2</h3>
              <p className="chat-preview">Last message preview...</p>
            </div>
          </div>
          {/* Add more chat items as needed */}
        </div>
      </div>

      {/* Main chat area */}
      <div className="main-chat">
        <div className="chat-header">
          <h2>Chat Room 1</h2>
          <div className="chat-header-actions">
            <button className="chat-action-btn">🔍</button>
            <button className="chat-action-btn">📞</button>
            <button className="chat-action-btn">📹</button>
          </div>
        </div>
        <div className="chat-messages">
          {/* Messages would be dynamically loaded here */}
          <div className="message received">
            <p className="message-text">Hello, how are you?</p>
            <span className="message-time">12:34 PM</span>
          </div>
          <div className="message sent">
            <p className="message-text">I'm good, thanks!</p>
            <span className="message-time">12:35 PM</span>
          </div>
        </div>
        <div className="message-input-container">
          <input
            type="text"
            className="message-input"
            placeholder="Type a message..."
          />
          <button className="send-btn">Send</button>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
