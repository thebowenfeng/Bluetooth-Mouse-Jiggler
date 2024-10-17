# Bluetooth Mouse Jiggler

Disguise a bluetooth enabled Linux machine as a HID mouse and use it to keep a machine awake.

Tested on Raspberry OS 12 (Debian bookworm)

## Setup

Requires python3.8 or newer

1. Create a Python venv in the root folder
2. Run `setup.sh`.
   1. The script may shutdown your machine at the end.
2. Restart your machine if you haven't already
3. Run `run.sh` to start the bluetooth server
   1. (Optional) Rename `DEVICE_NAME` to change your device name
   2. (Optional) Modify L43's hex code to change [device type (Section2.8)](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/Assigned_Numbers.pdf?v=1729085009656).
   3. (Optional) Modify `0x0100`, `0x0101`, `0x0102` in `sdp_record.xml` to desired string.

### Spoofing vendor ID and product ID

For more rigorous use cases, the default vendor ID and product ID in BlueZ is statically defined.
This will giveaway the fact that the device is likely not a genuine device.

To change the default vendor ID and product ID, manually compile and install BlueZ from source.

1. Uninstall bluez (`sudo apt-get remove bluez`) and then install bluez (`sudo apt-get install bluez`).
2. Clone bluez's [git repository](https://github.com/bluez/bluez/tree/master)
3. Modify `src/main.c` L1196 and L1197 to desired vendor & product ID.
4. Follow instructions on BlueZ's readme to compile and install. At this point do not uninstall bluez.
5. Execute the following 3 commands:
   1. `sudo sed -i '/^ExecStart=/ s/$/ --noplugin=input/' /lib/systemd/system/bluetooth.service`
   2. `sudo systemctl daemon-reload`
   3. `sudo systemctl restart bluetooth.service`
6. Restart machine

## Running

1. Run `run.sh`. This will run the bluetooth server. Note only 1 device can connect at a time.
2. Run `mouse/mouse_jiggler.py` in a separate terminal session. This script will jiggle the cursor.
   1. The `send_mouse(button_num, dx, dy, dz)` API is used to send mouse events. `button_num` represents a button press (0 for none). `dx` and `dy` is the relative movement of the mouse with respect to the X and Y axis. `dz` represents scrolling.
   2. Run this script after the host machine is connected to the bluetooth device.

