#!/usr/bin/env python3
"""
Motor Controller for Adafruit 16-Channel PWM/Servo HAT (PCA9685)
Supports DC motors via TB6612 or L298N motor drivers
"""

try:
    from adafruit_servokit import ServoKit
    SERVOKIT_AVAILABLE = True
except ImportError:
    SERVOKIT_AVAILABLE = False
    print("⚠ ServoKit not available, install: pip3 install adafruit-circuitpython-servokit")

try:
    from adafruit_motorkit import MotorKit
    from adafruit_motor import motor
    MOTORKIT_AVAILABLE = True
except ImportError:
    MOTORKIT_AVAILABLE = False


class AdafruitMotorController:
    """
    Motor Controller for Adafruit Motor HAT
    
    Configuration options:
    1. Using Adafruit Motor HAT/Bonnet (has built-in TB6612 drivers)
    2. Using PCA9685 HAT with external motor drivers
    """
    
    def __init__(self, use_motor_hat=True):
        """
        Initialize motor controller
        
        Args:
            use_motor_hat: True for Adafruit Motor HAT, False for PCA9685 with external drivers
        """
        self.use_motor_hat = use_motor_hat
        
        if use_motor_hat:
            self._init_motor_hat()
        else:
            self._init_pwm_hat()
        
        print("✓ Adafruit Motor Controller initialized")
    
    def _init_motor_hat(self):
        """Initialize Adafruit Motor HAT/Bonnet"""
        if not MOTORKIT_AVAILABLE:
            raise RuntimeError(
                "MotorKit not available. Install: "
                "pip3 install adafruit-circuitpython-motorkit"
            )
        
        try:
            self.kit = MotorKit()
            
            # Map motor objects for easy access
            self.motors = {
                'front_right': self.kit.motor1,
                'rear_right': self.kit.motor2,
                'front_left': self.kit.motor3,
                'rear_left': self.kit.motor4
            }
            
            print("✓ Using Adafruit Motor HAT")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Motor HAT: {e}")
    
    def _init_pwm_hat(self):
        """Initialize PCA9685 HAT with external motor drivers"""
        if not SERVOKIT_AVAILABLE:
            raise RuntimeError(
                "ServoKit not available. Install: "
                "pip3 install adafruit-circuitpython-servokit"
            )
        
        try:
            # Initialize PCA9685 with 16 channels
            self.kit = ServoKit(channels=16)
            
            # Map PWM channels to motors
            # Assumes external motor driver with 2 pins per motor (IN1, IN2 or PWM, DIR)
            self.motor_channels = {
                'front_left': {'pwm': 0, 'dir': 1},
                'front_right': {'pwm': 2, 'dir': 3},
                'rear_left': {'pwm': 4, 'dir': 5},
                'rear_right': {'pwm': 6, 'dir': 7}
            }
            
            print("✓ Using PCA9685 PWM HAT with external drivers")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PCA9685: {e}")
    
    def set_motor(self, motor_name, speed):
        """
        Set motor speed
        
        Args:
            motor_name: 'front_left', 'front_right', 'rear_left', 'rear_right'
            speed: -100 (full backward) to 100 (full forward)
        """

        # Motors are wired in reverse
        speed = -speed

        # Clamp speed to valid range
        speed = max(-100, min(100, speed))
        
        if self.use_motor_hat:
            self._set_motor_hat(motor_name, speed)
        else:
            self._set_pwm_motor(motor_name, speed)
    
    def _set_motor_hat(self, motor_name, speed):
        """Set motor speed using Motor HAT"""
        if motor_name not in self.motors:
            print(f"Warning: Unknown motor '{motor_name}'")
            return
        
        motor_obj = self.motors[motor_name]
        
        # Convert -100 to 100 range to Motor HAT's -1.0 to 1.0 range
        throttle = speed / 100.0
        
        motor_obj.throttle = throttle
    
    def _set_pwm_motor(self, motor_name, speed):
        """Set motor speed using PCA9685 PWM channels"""
        if motor_name not in self.motor_channels:
            print(f"Warning: Unknown motor '{motor_name}'")
            return
        
        channels = self.motor_channels[motor_name]
        pwm_channel = channels['pwm']
        dir_channel = channels['dir']
        
        # Determine direction
        if speed > 0:
            # Forward
            self.kit.continuous_servo[pwm_channel].throttle = speed / 100.0
            self.kit.continuous_servo[dir_channel].throttle = 1.0
        elif speed < 0:
            # Backward
            self.kit.continuous_servo[pwm_channel].throttle = abs(speed) / 100.0
            self.kit.continuous_servo[dir_channel].throttle = -1.0
        else:
            # Stop
            self.kit.continuous_servo[pwm_channel].throttle = 0
            self.kit.continuous_servo[dir_channel].throttle = 0
    
    def move(self, x, y):
        """
        Move car based on joystick input
        
        Args:
            x: -1.0 (left) to 1.0 (right)
            y: -1.0 (backward) to 1.0 (forward)
        """
        # Convert to speed percentage
        forward_speed = y * 100
        turn_speed = x * -100
        
        # Calculate individual motor speeds using differential steering
        left_speed = forward_speed - turn_speed
        right_speed = forward_speed + turn_speed
        
        # Clamp values to -100 to 100
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        # Apply to motors
        self.set_motor('front_left', left_speed)
        self.set_motor('rear_left', left_speed)
        self.set_motor('front_right', right_speed)
        self.set_motor('rear_right', right_speed)
    
    def stop(self):
        """Stop all motors"""
        for motor_name in ['front_left', 'front_right', 'rear_left', 'rear_right']:
            self.set_motor(motor_name, 0)
    
    def cleanup(self):
        """Cleanup and stop all motors"""
        self.stop()
        print("✓ Motor controller cleaned up")


# Example configurations for different setups
class MotorControllerFactory:
    """Factory to create appropriate motor controller"""
    
    @staticmethod
    def create(controller_type='motor_hat'):
        """
        Create motor controller based on hardware
        
        Args:
            controller_type: 'motor_hat', 'pwm_hat', or 'auto'
        
        Returns:
            AdafruitMotorController instance
        """
        if controller_type == 'auto':
            # Try Motor HAT first, fall back to PWM HAT
            try:
                return AdafruitMotorController(use_motor_hat=True)
            except:
                print("Motor HAT not found, trying PWM HAT...")
                return AdafruitMotorController(use_motor_hat=False)
        elif controller_type == 'motor_hat':
            return AdafruitMotorController(use_motor_hat=True)
        elif controller_type == 'pwm_hat':
            return AdafruitMotorController(use_motor_hat=False)
        else:
            raise ValueError(f"Unknown controller type: {controller_type}")


# Create global motor controller instance
# Change 'motor_hat' to 'pwm_hat' or 'auto' based on your hardware
try:
    motor_controller = MotorControllerFactory.create('motor_hat')
except Exception as e:
    print(f"⚠ Motor controller initialization failed: {e}")
    print("  Running without motor control")
    motor_controller = None


if __name__ == "__main__":
    """Test motor controller"""
    import time
    
    print("\nTesting Motor Controller")
    print("=" * 50)
    
    if motor_controller is None:
        print("Motor controller not available")
        exit(1)
    
    try:
        print("\n1. Testing forward...")
        motor_controller.move(0, 0.8)
        time.sleep(2)
        
        print("2. Testing backward...")
        motor_controller.move(0, -0.8)
        time.sleep(2)
        
        print("3. Testing left turn...")
        motor_controller.move(-0.8, 0.8)
        time.sleep(2)
        
        print("4. Testing right turn...")
        motor_controller.move(0.8, 0.8)
        time.sleep(2)
        
        print("5. Stopping...")
        motor_controller.stop()
        
        print("\n✓ Test complete!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        motor_controller.cleanup()
