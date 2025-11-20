from sock_client import SockClient


def dbgprint(*msg):
    if 1:
        print(msg)
    else:
        pass


class JoyHandler:
    def __init__(self, host, port):
        self.sc = SockClient(host, port)
        self.sc.connect()
        self.moveEnabled = True

    # def on_joyaxis_motion(self, joystick, axis, value):
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
        dbgprint('hat motion ' + str(hat_x), ', ', str(hat_y))

    def on_joybutton_press(self, stickid, buttonid):
        dbgprint('button_down', stickid, buttonid)
        if buttonid == 4:
            self.moveEnabled = True

    def on_joybutton_release(self, stickid, buttonid):
        dbgprint('button_up', stickid, buttonid)
        if buttonid == 4:
            pass
            #self.moveEnabled = False
            # self.notify('stop')

    def notifyJoyCommand(self, command, value=None):
        if(self.sc == None):
            self.sc = SockClient()
        dbgprint(command + ':' + str(value))
        self.sc.sendCommand(command + ':' + str(value))
