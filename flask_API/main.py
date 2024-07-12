import serial
import threading
import time
import csv
from datetime import datetime

class ReadSpeed:
    def __init__(self, port, baud_rate, callback):
        self.serial_port = serial.Serial(port, baud_rate)
        self.stop_event = threading.Event()
        self.callback = callback

    def read_speed(self):
        while not self.stop_event.is_set():
            line = self.serial_port.readline().decode('utf-8').strip()
            if line:  # Check if line is not empty
                try:
                    # Convert the line to float directly
                    speed = float(line)
                    self.callback(speed)
                except ValueError:
                    print(f"Unable to convert line to float: {line}")
            else:
                print("No data received from the sensor. Continuing read_speed.")

    def stop(self):
        self.stop_event.set()

# Callback function to handle the speed data
def handle_speed(speed):
    print(f"Speed: {speed}")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('speed_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, speed])

# Instantiate the ReadSpeed class
read_speed_instance = ReadSpeed("/dev/ttyACM0", 7600, handle_speed)
read_thread = threading.Thread(target=read_speed_instance.read_speed)

try:
    # Start reading in a separate thread
    read_thread.start()
    print("Reading started. Press Ctrl+C to stop.")
    
    # Keep the main thread running, to catch KeyboardInterrupt
    while read_thread.is_alive():
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping due to user interruption.")
finally:
    # Stop reading and join the thread
    read_speed_instance.stop()
    read_thread.join()

print("Finished reading speed data.")
