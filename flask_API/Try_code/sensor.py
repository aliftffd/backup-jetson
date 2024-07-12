# sensor.py untuk menjalankan sensor optik 

import Jetson.GPIO as GPIO
import time
import math

# Setup
RPM_PIN = 17  # Pin GPIO sesuai dengan penomoran BCM

# Periksa apakah mode GPIO sudah diatur
if not GPIO.getmode():
    GPIO.setmode(GPIO.BCM)

GPIO.setup(RPM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variabel untuk menyimpan jumlah pulsa dan waktu
counter = 0
previousMillis = int(time.time() * 1000)

# Callback untuk interrupt dengan debouncing
def pulsecount(channel):
    global counter
    counter += 1

# Event detect untuk input pin dengan debouncing time 5 ms
GPIO.add_event_detect(RPM_PIN, GPIO.RISING, callback=pulsecount, bouncetime=5)

def calculate_rpm(counter):
    # Hitung RPM
    pulses_per_revolution = 20  # Disk memiliki 20 lubang
    rpm = (counter / pulses_per_revolution) * 60
    return rpm

def get_current_rpm():
    global counter, previousMillis
    currentMillis = int(time.time() * 1000)
    if currentMillis - previousMillis >= 1000:
        rpm = calculate_rpm(counter)
        counter = 0
        previousMillis += 1000
        return rpm
    return None
