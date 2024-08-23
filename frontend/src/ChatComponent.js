import React, { useState, useEffect, useRef } from 'react';
import './app.css'; // Make sure to import the CSS here

const ChatComponent = ({ chatroomName }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [typingUser, setTypingUser] = useState(null);
  const socketUrl = `ws://localhost:8000/ws/chat/${chatroomName}/`;
  const socketRef = useRef(null); // Ref to store WebSocket connection

  useEffect(() => {
    // Initialize WebSocket connection
    socketRef.current = new WebSocket(socketUrl);

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'typing') {
        setTypingUser(data.user);
      } else if (data.type === 'message') {
        setMessages((prevMessages) => [...prevMessages, data]);
        setTypingUser(null); // Clear typing indicator when a new message is received
      }
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [socketUrl]);

  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
    if (socketRef.current) {
      socketRef.current.send(JSON.stringify({ type: 'typing' }));
    }
  };

  const handleSendMessage = () => {
    if (newMessage.trim() && socketRef.current) {
      socketRef.current.send(JSON.stringify({ type: 'message', body: newMessage }));
      setNewMessage('');
    }
  };

  return (
    <div className="App">
      {/* Display typing indicator */}
      {typingUser && <div className="typing-indicator">{typingUser} is typing...</div>}
      
      {/* Chat header */}
      <div className="chat-header">
        <div className="chatroom-name">{chatroomName}</div>
        <div className="chat-status">Online</div>
      </div>
      
      {/* Chat message container */}
      <div className="chat-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message-bubble ${msg.isSentByCurrentUser ? 'message-sent' : 'message-received'}`}
          >
            <p>{msg.body}</p>
            <div className="message-timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</div>
          </div>
        ))}
      </div>
      
      {/* Input area for new messages */}
      <div className="message-input-container">
        <input
          type="text"
          className="message-input"
          value={newMessage}
          onChange={handleInputChange}
          placeholder="Type a message..."
        />
        <button className="message-send-btn" onClick={handleSendMessage}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatComponent;
