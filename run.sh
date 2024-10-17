#!/bin/bash
sudo hciconfig hci0 down
sudo systemctl daemon-reload
sudo /etc/init.d/bluetooth start

source bin/activate
sudo python server/server.py
