# Based on
# CEF Hello world example. Doesn't depend on any third party GUI framework.
# Tested with CEF Python v57.0+.

from cefpython3 import cefpython as cef
import platform
import sys
import socket
import threading

HOST = '192.168.178.46'
PORT = 11111
DEBUG = True

def dbgprint(*msg):
    if DEBUG:
        print(msg)
    else:
        pass

class SockClient:
    def __init__(self):
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
            x = threading.Thread(target=self.connect_thread, args=(HOST, PORT), daemon=True)
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
        
class JoyHandler:
    def __init__(self):
        self.sc = SockClient()
        self.sc.connect()
        self.moveEnabled = True

    #def on_joyaxis_motion(self, joystick, axis, value):
    def on_joyaxis_motion(self, stickid, axisid, value):
        dbgprint('on_joyaxis_motion', axisid, value)
        if self.moveEnabled == True:
            #value = value * 1/32767
            cmd = None
            if abs(value) < 0.5:
                value = 0
            elif value < 0:
                value = -1
            else:
                value = 1
                
            if(axisid == 'y'):
                cmd = 'move'
                value = value
            elif(axisid == 'z'):
                cmd = 'turn'

            if cmd != None:
                self.notifyJoyCommand(cmd, value)

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        dbgprint ('hat motion ' + str(hat_x), ', ', str(hat_y))

    def on_joybutton_press(self, stickid, buttonid):
        dbgprint('button_down', stickid, buttonid)
        if buttonid == 4:
            self.moveEnabled = True

    def on_joybutton_release(self, stickid, buttonid):
        dbgprint('button_up', stickid, buttonid)
        if buttonid == 4:
            pass
            #self.moveEnabled = False
            #self.notify('stop')

    def notifyJoyCommand(self, command, value=None):
        if(self.sc == None):
            self.sc = SockClient()
        dbgprint(command + ':' + str(value))
        self.sc.sendCommand(command + ':' + str(value))

def pyglet_thread():
    import pyglet
    joystick = None
    joysticks = pyglet.input.get_joysticks()
    if joysticks:
        joystick = joysticks[0]
        joystick.open()
        my_controller = JoyHandler()
        joystick.push_handlers(my_controller)
        pyglet.app.run()

class Container:

    def main(self):
        self.check_versions()
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

        x = threading.Thread(target=pyglet_thread, daemon=True)
        x.start()
        
        cef.Initialize()
        cef.CreateBrowserSync(url="http://192.168.178.46:8000", window_title="Robot")
        cef.MessageLoop()

    def check_versions(self):
        ver = cef.GetVersion()
        print("[hello_world.py] CEF Python {ver}".format(ver=ver["version"]))
        print("[hello_world.py] Chromium {ver}".format(ver=ver["chrome_version"]))
        print("[hello_world.py] CEF {ver}".format(ver=ver["cef_version"]))
        print("[hello_world.py] Python {ver} {arch}".format(
            ver=platform.python_version(),
            arch=platform.architecture()[0]))
        assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"

    def close(self):
        print('closing')
        cef.Shutdown()


if __name__ == '__main__':
    c = Container()
    c.main()
    c.close()
