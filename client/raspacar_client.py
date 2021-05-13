# Based on
# CEF Hello world example. Doesn't depend on any third party GUI framework.
# Tested with CEF Python v57.0+.

from cefpython3 import cefpython as cef
import platform
import sys
import threading
from joystick_handler import JoyHandler
from sock_client import SockClient

DEBUG = True
HOST = '192.168.178.46'
PORT = 11111


def dbgprint(*msg):
    if DEBUG:
        print(msg)
    else:
        pass


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
        cef.CreateBrowserSync(
            url="http://192.168.178.46:8000", window_title="Robot")
        cef.MessageLoop()

    def check_versions(self):
        ver = cef.GetVersion()
        print("[hello_world.py] CEF Python {ver}".format(ver=ver["version"]))
        print("[hello_world.py] Chromium {ver}".format(
            ver=ver["chrome_version"]))
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
