import Jetson.GPIO as GPIO
import time
import csv

# Setup
RPM_PIN = 27  # Pin GPIO sesuai dengan penomoran BCM
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

# Durasi pengukuran dalam detik
duration = 40
end_time = time.time() + duration

# List untuk menyimpan hasil pengukuran
results = []

try:
    while time.time() < end_time:
        currentMillis = int(time.time() * 1000)
        if currentMillis - previousMillis >= 1000:
            rpm = calculate_rpm(counter)
            results.append(rpm)
            print(f"RPM: {rpm:.2f}")
            counter = 0
            previousMillis += 1000

    # Menyimpan hasil pengukuran ke dalam file CSV
    with open('rpm_measurements.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "RPM"])
        for i, rpm in enumerate(results):
            writer.writerow([i + 1, rpm])

except KeyboardInterrupt:
    print("Pengukuran dihentikan oleh pengguna.")

finally:
    GPIO.cleanup()
    print("Pengukuran selesai. Hasil disimpan dalam rpm_measurements.csv.")
