#!/usr/bin/python3

import sys
import socket
import time
import threading
import logging
import cam_streamer
from server.old.car_controller import CarController

hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname + ".local")
PORT = 11111    # Port to listen on (non-privileged ports are > 1023)
DEBUG = False


def dbgprint(msg):
    if DEBUG:
        print(msg)


if len(sys.argv) > 1 and sys.argv[1] == '--debug':
    logging.info('debug mode')
    DEBUG = True
else:
    logging.info('working mode')

# start the camera streaming server
camera = cam_streamer.CameraWrapper()
camera_thread = threading.Thread(target=camera.run)
camera_thread.start()
logging.info("Cam streamer started")
print("Cam streamer started")

# start the socket server to receive commands
cc = CarController()
logging.info("Car controller started")
print("Car controller started")
while True:
    try:
        logging.info('opening socket')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen(5)
        logging.info('listening on ' + HOST + ':' + str(PORT))
        reset = False
        while reset == False:
            conn, addr = sock.accept()
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                cmd = data.decode('utf8')
                dbgprint('received ' + cmd)
                words = cmd.split(':')
                dbgprint(words)
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
