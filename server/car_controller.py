
from adafruit_motorkit import MotorKit


class CarController:
    def __init__(self):
        self.kit = MotorKit()
        self.mFSx = self.kit.motor2
        self.mBSx = self.kit.motor1
        self.mFDx = self.kit.motor4
        self.mBDx = self.kit.motor3

    def setSpeedXY(self, vx, vy):
        ret = 'OK:'
        pass

    def setSpeedRT(self, rho, theta):
        ret = 'OK:'
        if theta > 0 and theta < pi:
            ret = self.setSpeetLeft(rho)
            ret = self.setSpeedRight(rho*(1-2*theta/pi))
        else:
            theta = math.abs(theta % pi)
            ret = self.setSpeetRight(rho)
            ret = self.setSpeedLeft(rho*(1-2*theta/pi))
        return ret

    def setSpeedLeft(self, value):
        ret = 'OK:'
        ret = self.setMotorThrottle('fsx', value)
        ret = self.setMotorThrottle('bsx', value)
        return ret

    def setSpeedRight(self, value):
        ret = 'OK:'
        ret = self.setMotorThrottle('frx', value)
        ret = self.setMotorThrottle('brx', value)
        return ret

    def move(self, value):
        ret = 'OK:'
        self.setMotorThrottle('fsx', value)
        self.setMotorThrottle('fdx', value)
        self.setMotorThrottle('bsx', value)
        self.setMotorThrottle('bdx', value)
        return ret

    def turn(self, value):
        ret = 'OK:'
        ret = self.setMotorThrottle('fsx', value)
        ret = self.setMotorThrottle('fdx', -value)
        ret = self.setMotorThrottle('bsx', value)
        ret = self.setMotorThrottle('bdx', -value)
        return ret

    def stop(self):
        ret = 'OK:'
        ret = self.setMotorThrottle('fsx', 0)
        ret = self.setMotorThrottle('fdx', 0)
        ret = self.setMotorThrottle('bsx', 0)
        ret = self.setMotorThrottle('bdx', 0)
        return ret

    def setMotorThrottle(self, motor, value):
        ret = 'OK:'
        if DEBUG:
            return ret
        try:
            if motor == 'fsx':
                self.mFSx.throttle = value
            elif motor == 'fdx':
                self.mFDx.throttle = value
            elif motor == 'bsx':
                self.mBSx.throttle = value
            elif motor == 'bdx':
                self.mBDx.throttle = value
            else:
                ret = 'WARNING: motor ' + motor + 'not found'
        except Exception as e:
            ret = 'ERROR: ' + motor + ': ' + str(e)
        return ret

    def setAllMotorThrottle(self, value):
        ret = 'OK:'
        print(str(value))
        return ret
        try:
            self.mFSx.throttle = self.mFDx.throttle = self.mBSx.throttle = self.mBDx.throttle = value
        except Exception as e:
            ret = 'ERROR: ' + motor + ': ' + str(e)
        return ret
