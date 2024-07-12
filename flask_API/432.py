import threading
import time
import csv
from datetime import datetime
from motor import MotorController
from pid_controller import PIDController  # Mengubah import PID
from sensor_ir import get_current_rpm

class MotorControlApplication:
    def __init__(self, motor_controller):
        self.motor_controller = motor_controller
        self.csv_file = 'motor_log.csv'
        self._initialize_csv()

        # Initialize PID Controller with appropriate tuning parameters
        self.pid = PIDController(0.1, 0.02, 0.01, setpoint=330)  # Example values for tuning
        self.pid.set_output_limits(0, 1)  # Output as duty cycle (0-1)

        self.previous_rpm = 0  # Variable to store previous RPM value

    def _initialize_csv(self):
        """Initialize CSV file with header if not exist."""
        try:
            with open(self.csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                if file.tell() == 0:
                    writer.writerow(['Timestamp', 'Duty Cycle', 'RPM'])
        except Exception as e:
            print("Error initializing CSV file:", e)

    def log_to_csv(self, duty_cycle, rpm):
        """Log motor data to CSV file."""
        try:
            with open(self.csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([timestamp, duty_cycle, rpm])
        except Exception as e:
            print("Error logging to CSV file:", e)

    def motor_control(self):
        try:
            while True:
                try:
                    current_rpm = get_current_rpm()
                    if current_rpm is not None:
                        # Apply a simple low-pass filter to the RPM readings to smooth out fluctuations
                        current_rpm = 0.8 * self.previous_rpm + 0.2 * current_rpm
                        self.previous_rpm = current_rpm

                        control = self.pid.update(current_rpm)
                        print(f"Setting motor duty cycle to: {control}")
                        self.motor_controller.set_motor_duty_cycle(control)
                        self.log_to_csv(control, current_rpm)
                    time.sleep(0.1)  # Ensure consistent sampling time
                except Exception as e:
                    print("Error in motor control loop:", e)
                    self.motor_controller.set_motor_duty_cycle(0)
                    break
        finally:
            self.motor_controller.stop()

    def main(self):
        try:
            motor_thread = threading.Thread(target=self.motor_control, daemon=True)
            motor_thread.start()
            motor_thread.join()
        except Exception as e:
            print("Error in main thread:", e)
            self.motor_controller.stop()

if __name__ == "__main__":
    motor_controller = MotorController(ena=8, in1=9, in2=10, enb=13, in3=11, in4=12)
    motor_app = MotorControlApplication(motor_controller)
    motor_app.main()
    GPIO.cleanup()
