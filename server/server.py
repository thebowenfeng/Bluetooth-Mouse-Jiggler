import logging
import socket

import dbus
import dbus.mainloop.glib
import dbus.service
from bluetooth import *
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

logging.basicConfig(level=logging.DEBUG)

DEVICE_NAME = "BluetoothKeyboardMouse"
P_CTRL = 17  # Service port - must match port configured in SDP record
P_INTR = 19  # Interrupt port - must match port configured in SDP record
SDP_RECORD_PATH = sys.path[0] + "/sdp_record.xml"
UUID = "00001124-0000-1000-8000-00805f9b34fb" # HID UUID

scontrol = None
sinterrupt = None
ccontrol = None
cinterrupt = None

def init_bt_device():
    print("Configuring Device name " + DEVICE_NAME)
    os.system("hciconfig hci0 up")
    os.system("hciconfig hci0 name " + DEVICE_NAME)
    os.system("hciconfig hci0 piscan")

def init_bluez_profile():
    print("Configuring Bluez Profile")
    with open(SDP_RECORD_PATH, "r") as f:
        service_record = f.read()
        opts = {
            "AutoConnect": True,
            "ServiceRecord": service_record
        }
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object(
            "org.bluez", "/org/bluez"), "org.bluez.ProfileManager1")
        manager.RegisterProfile("/org/bluez/hci0", UUID, opts)
        print("Profile registered ")
        os.system("hciconfig hci0 class 0x002580") # Hex code is also CoD, consistent with 0x0202 in sdp_record

def listen():
    global scontrol
    global sinterrupt
    global ccontrol
    global cinterrupt

    print("\033[0;33mWaiting for connections\033[0m")
    scontrol = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)  # BluetoothSocket(L2CAP)
    sinterrupt = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)  # BluetoothSocket(L2CAP)
    scontrol.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sinterrupt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind these sockets to a port - port zero to select next available
    scontrol.bind((socket.BDADDR_ANY, P_CTRL))
    sinterrupt.bind((socket.BDADDR_ANY, P_INTR))

    # Start listening on the server sockets
    scontrol.listen(5)
    sinterrupt.listen(5)

    ccontrol, cinfo = scontrol.accept()
    print (
        "\033[0;32mGot a connection on the control channel from %s \033[0m" % cinfo[0])

    cinterrupt, cinfo = sinterrupt.accept()
    print (
        "\033[0;32mGot a connection on the interrupt channel from %s \033[0m" % cinfo[0])

def send_string(message):
    try:
        cinterrupt.send(bytes(message))
    except OSError as err:
        print(err)


class BluetoothService(dbus.service.Object):
    def __init__(self):
        print("Setting up DBUS service")
        # set up as a dbus service
        bus_name = dbus.service.BusName(
            "org.bowenfeng.bluetoothservice", bus=dbus.SystemBus())
        dbus.service.Object.__init__(
            self, bus_name, "/org/bowenfeng/bluetoothservice")
        init_bt_device()
        init_bluez_profile()
        listen()

    # Look in keyboard

    @dbus.service.method('org.bowenfeng.bluetoothservice', in_signature='yay')
    def send_mouse(self, modifier_byte, keys):
        state = [0xA1, 2, 0, 0, 0, 0]
        count = 2
        for key_code in keys:
            if(count < 6):
                state[count] = int(key_code)
            count += 1
        send_string(state)


if __name__ == "__main__":
    try:
        if not os.geteuid() == 0:
            sys.exit("Run script with: sudo python server.py")

        DBusGMainLoop(set_as_default=True)
        BluetoothService()
        loop = GLib.MainLoop()
        loop.run()
    except KeyboardInterrupt:
        sys.exit()
