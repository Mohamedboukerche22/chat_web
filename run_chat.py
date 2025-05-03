from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, send, emit
import json
import time
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  
socketio = SocketIO(app, cors_allowed_origins="*")
MESSAGE_FILE = "messages.json"
MAX_MESSAGES = 1000 

def load_messages():
    """Load messages from file with error handling"""
    if not os.path.exists(MESSAGE_FILE):
        return []
    
    try:
        with open(MESSAGE_FILE, "r") as f:
            messages = json.load(f)
            return messages if messages else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_messages(messages):
    """Save messages to file with error handling"""
    try:
        with open(MESSAGE_FILE, "w") as f:
            json.dump(messages[-MAX_MESSAGES:], f)
    except IOError as e:
        print(f"Error saving messages: {e}")
messages = load_messages()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_messages')
def get_messages():
    return jsonify(messages)

@socketio.on('message')
def handle_message(msg):
    """Handle incoming messages"""
    if not msg or not isinstance(msg, str):
        return
    
    # Create message object with timestamp
    message_data = {
        'text': msg,
        'timestamp': datetime.now().isoformat(),
        'sender': request.sid[:8]  
    }
    messages.append(message_data)
    save_messages(messages)
    emit('new_message', message_data, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicators"""
    emit('user_typing', {
        'sender': request.sid[:8],
        'is_typing': data.get('is_typing', False)
    }, broadcast=True, include_self=False)

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
