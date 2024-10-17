import dbus
import dbus.service
import dbus.mainloop.glib
import time

iface = None

def init_service():
    print("Connecting mouse script to bluetooth service")
    global iface
    bus = dbus.SystemBus()
    btkservice = bus.get_object('org.bowenfeng.bluetoothservice'
                                          , '/org/bowenfeng/bluetoothservice')
    iface = dbus.Interface(btkservice,
                                'org.bowenfeng.bluetoothservice')

def send_mouse(num1, num2, num3, num4):
    def sign_int(num):
        return min(127, max(-127, num)) & 255
    try:
        iface.send_mouse(0, bytes([sign_int(num1), sign_int(num2), sign_int(num3), sign_int(num4)]))
    except OSError as err:
        print(err)
    print("Sent mouse event: ", num1, num2, num3, num4)


if __name__ == '__main__':
    init_service()
    movements = [(0, 100, 0, 0), (0, -100, 0, 0)]
    while True:
        for mv in movements:
            send_mouse(mv[0], mv[1], mv[2], mv[3])
            time.sleep(1)


