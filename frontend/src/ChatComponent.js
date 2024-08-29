import React, { useState, useEffect } from 'react';

const ChatComponent = ({ roomName }) => {
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');

    useEffect(() => {
        const socket = new WebSocket(`ws://localhost:8000/ws/chat/${roomName}/`);

        socket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            setMessages([...messages, data.message]);
        };

        return () => socket.close();
    }, [messages, roomName]);

    const sendMessage = () => {
        const socket = new WebSocket(`ws://localhost:8000/ws/chat/${roomName}/`);
        socket.onopen = () => {
            socket.send(JSON.stringify({ 'message': message }));
            setMessage('');
        };
    };

    return (
        <div>
            <div>
                {messages.map((msg, index) => (
                    <div key={index}>{msg}</div>
                ))}
            </div>
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
            />
            <button onClick={sendMessage}>Send</button>
        </div>
    );
};

export default ChatComponent;
