class PIDController:
    def __init__(self, kp, ki, kd, setpoint=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.prev_error = 0
        self.integral = 0
        self.min_output = 0
        self.max_output = 1
        self.integral_limit = 20  # Example limit for integral term

    def set_output_limits(self, min_output, max_output):
        self.min_output = min_output
        self.max_output = max_output

    def update(self, feedback):
        error = self.setpoint - feedback
        self.integral += error
        self.integral = max(-self.integral_limit, min(self.integral, self.integral_limit))  # Anti-windup
        derivative = error - self.prev_error

        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error

        return max(self.min_output, min(self.max_output, output))
