import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

const ChatComponent = () => {
  const { chatroomName } = useParams();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [typingUser, setTypingUser] = useState('');
  const socketUrl = `ws://localhost:8000/ws/chat/${chatroomName}/`;

  useEffect(() => {
    const socket = new WebSocket(socketUrl);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'typing') {
        setTypingUser(data.user);
      } else if (data.type === 'message') {
        setMessages((prevMessages) => [...prevMessages, data]);
      }
    };

    return () => {
      socket.close();
    };
  }, [socketUrl]);

  const handleInputChange = (e) => {
    setNewMessage(e.target.value);
    const socket = new WebSocket(socketUrl);
    socket.onopen = () => {
      socket.send(JSON.stringify({ typing: true }));
    };
  };

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      const socket = new WebSocket(socketUrl);
      socket.onopen = () => {
        socket.send(JSON.stringify({ body: newMessage }));
        setNewMessage('');
      };
    }
  };

  return (
    <div className="App">
      {/* Display typing indicator */}
      {typingUser && <div className="typing-indicator">{typingUser} is typing...</div>}
      
      {/* Other components */}
      <div className="chat-header">
        <h1>{chatroomName} Chat</h1>
      </div>
      <div className="chat-container">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message-bubble ${msg.isSentByCurrentUser ? 'message-sent' : 'message-received'}`}
          >
            <p>{msg.text}</p>
            <div className="message-timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</div>
          </div>
        ))}
      </div>
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
