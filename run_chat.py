from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, send
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

try:
    with open("messages.json", "r") as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_messages')
def get_messages():
    return jsonify(messages)

@socketio.on('message')
def handle_message(msg):
    print(f'Message: {msg}')
    messages.append(msg)
    with open("messages.json", "w") as f:
        json.dump(messages, f)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='###########your ip #######', port=5000, debug=True)
  #put you ip adreess to make it work on local host 

