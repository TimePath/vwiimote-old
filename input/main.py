#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import evdev
import select
import argparse

keyboard_sigs = [
    [('EV_LED', 17), ('EV_MSC', 4), ('EV_KEY', 1), ('EV_SYN', 0)]
]


def get_devices(signatures):
    """Returns a list of devices based on a list of capabilities"""
    devs = [evdev.InputDevice(dev) for dev in evdev.list_devices()]
    matches = []
    for signature in signatures:
        for dev in devs:
            try:
                if set(dev.capabilities(verbose=True).keys()) == set(signature):
                    matches.append(dev)
            except AttributeError:
                pass
    return matches


keyboards = get_devices(keyboard_sigs)
for kb in keyboards:
    print(("Match: " + str(kb)))
kb = keyboards[0]
if kb is not None:
    print(("Using: " + str(kb)))
else:
    print("Keyboard not found")

parser = argparse.ArgumentParser(description="Maps keyboard and mouse input to a virtual joystick")
parser.add_argument('-c', '--config', action='store', type=str, required=True, help="Python config script.")
args = parser.parse_args()

# Trim .py from config if it was included.
if args.config[-3:] == '.py':
    args.config = args.config[:-3]

config = __import__(args.config)

ui = evdev.UInput(config.CAPABILITIES, name=config.NAME, vendor=config.VENDOR, product=config.PRODUCT, version=config.VERSION, bustype=evdev.ecodes.BUS_USB)

while True:
    r, w, x = select.select([kb.fd], [], [])
    try:
        event = kb.read_one()
        print(event)
    except IOError:
        pass