#!/usr/bin/env python
#
# Copyright (c) 2020, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

import pycom
import machine
import math
import network
import os
import time
import utime
import gc
from machine import RTC
from machine import SD
from L76GNSS import L76GNSS
from pycoproc_1 import Pycoproc
from network import LTE


lte = LTE()
time.sleep(2)
gc.enable()
lte.attach(band=20, apn="telenor.iot")
print("attaching..", end='')
while not lte.isattached():
    time.sleep(0.25)

    print('.', end='')
    print(lte.send_at_cmd('AT!="fsm"'))         # get the System FSM
print("attached!")

lte.connect()
print("connecting [##", end='')
while not lte.isconnected():
    time.sleep(0.25)
    print('#', end='')
    print(lte.send_at_cmd('AT!="fsm"'))
print("] connected!")

# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

py = Pycoproc(Pycoproc.PYTRACK)
l76 = L76GNSS(py, timeout=30)

pybytes_enabled = False
if 'pybytes' in globals():
    if(pybytes.isconnected()):
        print('Pybytes is connected, sending signals to Pybytes')
        pybytes_enabled = True

# sd = SD()
# os.mount(sd, '/sd')
# f = open('/sd/gps-record.txt', 'w')
pycom.heartbeat(False)

while (True):
    pycom.rgbled(0xffff00)
    coord = l76.coordinates()
    #f.write("{} - {}\n".format(coord, rtc.now()))
    if(pybytes_enabled):
        pycom.rgbled(0xff00)           # turn on the RGB LED in green colour

        print("{} - {} - {}".format(coord, rtc.now(), gc.mem_free()))
        pybytes.send_signal(1, coord)
    time.sleep(10)


lte.deinit()
"""
# sleep procedure
time.sleep(3)
py.setup_sleep(10)
py.go_to_sleep()
"""
