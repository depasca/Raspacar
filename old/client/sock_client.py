import socket
import threading
import sys


def dbgprint(*msg):
    if 1:
        print(msg)
    else:
        pass


class SockClient:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.s = None
        self.connected = False
        self.connecting = False
        self.connection_lock = threading.Lock()

    def connect_thread(self, host, port):
        self.connection_lock.acquire()
        try:
            print('thread: connecting to robot')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            self.s = sock
            self.connected = True
        except Exception as e:
            print('thread: couldn\'t connect to ' + host + ':' + str(port))
            print("Unexpected error:", sys.exc_info()[0])
            self.s = None
            self.connected = False
        self.connecting = False
        self.connection_lock.release()

    def connect(self):
        if self.connecting == False:
            self.connecting = True
            dbgprint('connect start')
            x = threading.Thread(target=self.connect_thread,
                                 args=(self.HOST, self.PORT), daemon=True)
            x.start()
            x.join()
            dbgprint('connect end')
        else:
            dbgprint('already trying to connect')
        return self.connected

    def sendCommand(self, msg):
        ret = False
        try:
            if self.connected == False:
                print('cannot send. connecting...')
                self.connect()
            else:
                self.s.sendall(bytes(msg, 'utf8'))
                data = self.s.recv(1024)
                msg = data.decode('utf8')
                dbgprint('received back:', msg)
                if msg.startswith('OK:'):
                    ret = True
        except Exception as e:
            print('communication exception: ' + str(e.with_traceback))
            self.connected = False
            ret = False
        return ret

    def close(self):
        print('closing connection to robot')
        if self.s != None:
            self.s.close()
            self.s = None
            self.connected = False
