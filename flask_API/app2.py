# app.py

import serial
import json
from flask import Flask
from flask_socketio import SocketIO, emit

# Define the serial port and baud rate
serial_port = '/dev/ttyTHS1'  # Adjust this to your serial port
baud_rate = 9600  # Adjust this to your baud rate

# Create a serial object
ser = serial.Serial(serial_port, baud_rate)

# Initialize Flask app and Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return "data sent"

def read_from_serial():
    while True:
        try:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()
            
            # Parse the JSON-formatted data
            try:
                data = json.loads(line)
                
                # Emit the parsed data to all connected WebSocket clients
                socketio.emit('serial_data', data)
                
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                continue  # Skip this iteration if JSON decoding fails
                
        except Exception as e:
            print("An error occurred:", e)
            ser.close()
            break

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    # Start the serial reading thread
    app.run()
    socketio.start_background_task(target=read_from_serial)
    
    # Run the Flask app
    socketio.run(app, host='0.0.0.0', port=8080)
