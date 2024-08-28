// D:\Realtime_chat\frontend\src\services\websocketservice.js

class WebSocketService {
    constructor() {
      this.socket = null;
      this.callbacks = {};
    }
  
    connect(url) {
      // Create a new WebSocket connection
      this.socket = new WebSocket(url);
  
      // Set up WebSocket event listeners
      this.socket.onopen = () => {
        console.log('WebSocket connection established');
      };
  
      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };
  
      this.socket.onclose = () => {
        console.log('WebSocket connection closed');
      };
  
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    }
  
    // Handle incoming WebSocket messages
    handleMessage(data) {
      if (this.callbacks[data.type]) {
        this.callbacks[data.type](data);
      }
    }
  
    // Send a message over the WebSocket
    sendMessage(type, message) {
      if (this.socket) {
        this.socket.send(JSON.stringify({ type, ...message }));
      } else {
        console.warn('WebSocket is not connected');
      }
    }
  
    // Register a callback for a specific message type
    on(type, callback) {
      this.callbacks[type] = callback;
    }
  
    // Close the WebSocket connection
    close() {
      if (this.socket) {
        this.socket.close();
      }
    }
  }
  
  export default new WebSocketService();
  