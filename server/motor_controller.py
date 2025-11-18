try:
    import RPi.GPIO as GPIO
except Exception:
    # Fallback lightweight GPIO shim for development / CI on non-RPi systems.
    # It implements the subset used by this module (setmode, setwarnings, setup, PWM, cleanup).
    class _FakePWM:
        def __init__(self, pin, freq):
            self.pin = pin
            self.freq = freq

        def start(self, duty):
            pass

        def ChangeDutyCycle(self, duty):
            pass

        def stop(self):
            pass

    class _FakeGPIO:
        BCM = 'BCM'
        OUT = 'OUT'

        def setmode(self, mode):
            pass

        def setwarnings(self, flag):
            pass

        def setup(self, pin, mode):
            pass

        def PWM(self, pin, freq):
            return _FakePWM(pin, freq)

        def cleanup(self):
            pass

    GPIO = _FakeGPIO()

PWM_FREQUENCY = 1000  # Hz

# Motor Control Configuration
MOTOR_PINS = {
    'front_left': {'forward': 17, 'backward': 27},
    'front_right': {'forward': 22, 'backward': 23},
    'rear_left': {'forward': 24, 'backward': 25},
    'rear_right': {'forward': 5, 'backward': 6}
}

class MotorController:
    """Controls 4 motors for car movement"""
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.motors = {}
        
        # Setup all motor pins
        for motor_name, pins in MOTOR_PINS.items():
            GPIO.setup(pins['forward'], GPIO.OUT)
            GPIO.setup(pins['backward'], GPIO.OUT)
            
            pwm_fwd = GPIO.PWM(pins['forward'], PWM_FREQUENCY)
            pwm_bwd = GPIO.PWM(pins['backward'], PWM_FREQUENCY)
            pwm_fwd.start(0)
            pwm_bwd.start(0)
            
            self.motors[motor_name] = {
                'forward': pwm_fwd,
                'backward': pwm_bwd
            }
        
        print("✓ Motor controller initialized")
    
    def set_motor(self, motor_name, speed):
        """Set motor speed (-100 to 100)"""
        if motor_name not in self.motors:
            return
        
        motor = self.motors[motor_name]
        
        if speed > 0:
            motor['forward'].ChangeDutyCycle(min(abs(speed), 100))
            motor['backward'].ChangeDutyCycle(0)
        elif speed < 0:
            motor['forward'].ChangeDutyCycle(0)
            motor['backward'].ChangeDutyCycle(min(abs(speed), 100))
        else:
            motor['forward'].ChangeDutyCycle(0)
            motor['backward'].ChangeDutyCycle(0)
    
    def move(self, x, y):
        """Move car based on joystick input"""
        forward_speed = y * 100
        turn_speed = x * 100
        
        left_speed = forward_speed - turn_speed
        right_speed = forward_speed + turn_speed
        
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        self.set_motor('front_left', left_speed)
        self.set_motor('rear_left', left_speed)
        self.set_motor('front_right', right_speed)
        self.set_motor('rear_right', right_speed)
    
    def stop(self):
        """Stop all motors"""
        for motor_name in self.motors:
            self.set_motor(motor_name, 0)
    
    def cleanup(self):
        """Cleanup GPIO"""
        self.stop()
        GPIO.cleanup()

motor_controller = MotorController()