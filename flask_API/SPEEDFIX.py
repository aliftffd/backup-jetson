import Jetson.GPIO as GPIO
import time
import csv
import math
import os

# Setup
RPM_PIN = 17  # Pin GPIO sesuai dengan penomoran BCM
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

def rpm_to_speed(rpm, diameter):
    # Mengubah RPM menjadi kecepatan linier dalam cm/s
    circumference = math.pi * diameter  # Keliling roda dalam cm
    speed_cm_per_s = (rpm * circumference) / 60
    return speed_cm_per_s

# Function to generate a new CSV filename with a counter
def generate_filename(base_name="Pengukuran_odometer_DC"):
    filename = f"{base_name}.csv"
    counter = 1

    while os.path.isfile(filename):
        filename = f"{base_name} {counter}.csv"
        counter += 1

    return filename

# Diameter roda dalam cm
wheel_diameter = 6

# List untuk menyimpan hasil pengukuran
results = []

# Generate filename with counter
filename = generate_filename()

try:
    while True:
        currentMillis = int(time.time() * 1000)
        if currentMillis - previousMillis >= 1000:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            rpm = calculate_rpm(counter)
            speed_cm_per_s = rpm_to_speed(rpm, wheel_diameter)
            results.append((current_time, rpm, speed_cm_per_s))
            print(f"Timestamp: {current_time}, RPM: {rpm:.2f}, Speed: {speed_cm_per_s:.2f} cm/s")
            counter = 0
            previousMillis += 1000

except KeyboardInterrupt:
    print("Pengukuran dihentikan oleh pengguna.")

finally:
    # Menyimpan hasil pengukuran ke dalam file CSV
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "RPM", "Speed (cm/s)"])
        for current_time, rpm, speed_cm_per_s in results:
            writer.writerow([current_time, rpm, speed_cm_per_s])
            print(f"Menulis ke CSV: Timestamp: {current_time}, RPM: {rpm}, Speed: {speed_cm_per_s} cm/s")
    
    GPIO.cleanup()
    print(f"Pengukuran selesai. Hasil disimpan dalam {filename}.")
