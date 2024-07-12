import Jetson.GPIO as GPIO
import time
import math
import board
import busio
from adafruit_pca9685 import PCA9685

# sensor.py
# Setup GPIO for RPM sensor
RPM_PIN = 17  # Pin GPIO sesuai dengan penomoran BCM

# Setup GPIO mode dan pin untuk RPM sensor
GPIO.setwarnings(False)
if GPIO.getmode() is None:
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

# motor.py
class MotorController:
    def __init__(self, ena, in1, in2, enb, in3, in4, pwm_frequency=60):
        # Motor control pins
        self.ENA = ena
        self.IN1 = in1
        self.IN2 = in2
        self.ENB = enb
        self.IN3 = in3
        self.IN4 = in4

        # Initialize I2C bus and PCA9685 module
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca = PCA9685(self.i2c)
        self.pca.frequency = pwm_frequency

        self.current_duty_cycle = 0

    def set_motor_duty_cycle(self, duty_cycle):
        self.current_duty_cycle = max(0, min(1.0, duty_cycle))

        # Set PWM duty cycle for motor speed
        self.pca.channels[self.ENA].duty_cycle = int(self.current_duty_cycle * 0xFFFF)
        self.pca.channels[self.ENB].duty_cycle = int(self.current_duty_cycle * 0xFFFF)
        
        if self.current_duty_cycle == 0:
            self.pca.channels[self.IN1].duty_cycle = 0
            self.pca.channels[self.IN2].duty_cycle = 0
            self.pca.channels[self.IN3].duty_cycle = 0
            self.pca.channels[self.IN4].duty_cycle = 0
        else:
            self.pca.channels[self.IN1].duty_cycle = 0xFFFF
            self.pca.channels[self.IN2].duty_cycle = 0
            self.pca.channels[self.IN3].duty_cycle = 0xFFFF
            self.pca.channels[self.IN4].duty_cycle = 0

        print("Motor duty cycle set to:", self.current_duty_cycle)

    def stop(self):
        self.set_motor_duty_cycle(0)
        self.pca.deinit()
        print("Motor control stopped.")

# main.py
class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.previous_error = 0
        self.integral = 0

    def compute(self, setpoint, actual):
        error = setpoint - actual
        self.integral += error
        derivative = error - self.previous_error

        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.previous_error = error

        return output

# Inisialisasi motor controller dan PID controller
motor = MotorController(ena=0, in1=1, in2=2, enb=3, in3=4, in4=5)
pid = PIDController(Kp=0.5, Ki=0.1, Kd=0.05)

setpoint_rpm = 1000  # Kecepatan yang diinginkan dalam RPM

try:
    while True:
        actual_rpm = get_current_rpm()
        if actual_rpm is not None:
            pid_output = pid.compute(setpoint_rpm, actual_rpm)
            new_duty_cycle = motor.current_duty_cycle + (pid_output / 100.0)
            motor.set_motor_duty_cycle(new_duty_cycle)
        time.sleep(0.1)
except KeyboardInterrupt:
    motor.stop()
    GPIO.cleanup()
