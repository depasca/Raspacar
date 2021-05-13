#!/usr/bin/python3

import sys
import socket
import time
from adafruit_motorkit import MotorKit
import cam_streamer

hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname)
PORT = 11111    # Port to listen on (non-privileged ports are > 1023)
DEBUG = False


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


if len(sys.argv) > 1 and sys.argv[1] == '--debug':
    print('debug mode')
    DEBUG = True
else:
    print('working mode')

# start the camera streaming server
cam_streamer.start_camera_server()

# start the socket server to receive commands
cc = CarController()
while True:
    try:
        print('opening socket')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen(5)
        print('listening on ' + HOST + ':' + str(PORT))
        reset = False
        while reset == False:
            conn, addr = sock.accept()
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                cmd = data.decode('utf8')
                print('received ' + cmd)
                words = cmd.split(':')
                print(words)
                # motor:fsx:0.5
                if words[0] == 'motor':
                    resp = cc.setMotorThrottle(words[1], float(words[2]))
                    conn.sendall(bytes(resp + ' - ' + cmd, 'utf8'))
                elif words[0] == 'allmotors':
                    resp = cc.setAllMotorThrottle(float(words[2]))
                # rhotheta:0.8:3.14214
                elif words[0] == 'rhotheta':
                    resp = cc.setSpeedRhoTheta(
                        float(words[1]), float(words[2]))
                    conn.sendall(bytes(resp + ' - ' + cmd, 'utf8'))
                elif words[0] == 'move':
                    resp = cc.move(float(words[1]))
                    conn.sendall(bytes(resp + ' - ' + cmd, 'utf8'))
                elif words[0] == 'turn':
                    resp = cc.turn(float(words[1]))
                    conn.sendall(bytes(resp + ' - ' + cmd, 'utf8'))
                elif words[0] == 'stop':
                    resp = cc.stop()
                    conn.sendall(bytes(resp + ' - ' + cmd, 'utf8'))
                else:
                    conn.sendall(bytes('NO ACTION' + ' - ' + cmd, 'utf8'))

    except:
        print('closing socket')
        sock.close()
        time.sleep(5)
