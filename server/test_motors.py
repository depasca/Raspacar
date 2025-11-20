#!/usr/bin/env python3
from adafruit_motorkit import MotorKit
import time

kit = MotorKit()

print("Testing motors individually with longer delays")
print("=" * 50)

try:
    # Test with slower speed (less current draw)
    print("\nTesting M1 (Front Left) - SLOW...")
    kit.motor1.throttle = 0.3  # Reduced from 0.5
    time.sleep(3)
    kit.motor1.throttle = 0
    time.sleep(2)  # Longer pause between motors
    
    print("Testing M2 (Front Right) - SLOW...")
    kit.motor2.throttle = 0.3
    time.sleep(3)
    kit.motor2.throttle = 0
    time.sleep(2)
    
    print("Testing M3 (Rear Left) - SLOW...")
    kit.motor3.throttle = 0.3
    time.sleep(3)
    kit.motor3.throttle = 0
    time.sleep(2)
    
    print("Testing M4 (Rear Right) - SLOW...")
    kit.motor4.throttle = 0.3
    time.sleep(3)
    kit.motor4.throttle = 0
    
    print("\n✓ All motors tested individually!")
    
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    kit.motor1.throttle = 0
    kit.motor2.throttle = 0
    kit.motor3.throttle = 0
    kit.motor4.throttle = 0
    print("✓ Motors stopped")