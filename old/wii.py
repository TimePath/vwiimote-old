#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

# http://wiibrew.org/wiki/Wiimote

DEV_NAME = "Nintendo RVL-CNT-01"
DEV_MAC = "00:1A:E9:F7:62:9C"
# http://bluetooth-pentest.narod.ru/software/bluetooth_class_of_device-service_generator.html
DEV_TYPE = "0x002504"  # Limited Discoverability Joystick

PIPE_CONTROL = 0x11
PIPE_DATA = 0x13

HOST_SEND = 0xa1
HOST_RECV = 0xa2

FEATURE_DISABLE = 0x00
FEATURE_ENABLE = 0x04

IR_MODE_OFF = 0
IR_MODE_STD = 1
IR_MODE_EXP = 3
IR_MODE_FULL = 5

buttonmap = {
  '2': 0x0001,
  '1': 0x0002,
  'B': 0x0004,
  'A': 0x0008,
  '-': 0x0010,
  'H': 0x0080,
  'L': 0x0100,
  'R': 0x0200,
  'D': 0x0400,
  'U': 0x0800,
  '+': 0x1000
}

led_state = [0,0,0,0]

# Headers received over data pipe

I_UNKNOWN = 0x10  # 1
I_LED = 0x11  # 1
I_REPORT_MODE = 0x12  # 2
I_IR_CAM_ENABLE1 = 0x13  # 1
I_SPEAKER_ENABLE = 0x14  # 1
I_STATUS_REQUEST = 0x15  # 1
I_WRITE_MEM = 0x16  # 21
I_READ_MEM = 0x17  # 6
I_SPEAKER_DATA = 0x18  # 21
I_SPEAKER_MUTE = 0x19  # 1
I_IR_CAM_ENABLE2 = 0x1a  # 1

# Headers sent
O_STATUS_INFO = 0x20  # 6
O_READ_MEM = 0x21  # 21
O_ACK = 0x22  # 4
O_DATA1 = 0x30  # 2-21
O_DATA2 = 0x31  # 2-21
O_DATA3 = 0x32  # 2-21
O_DATA4 = 0x33  # 2-21
O_DATA5 = 0x34  # 2-21
O_DATA6 = 0x35  # 2-21
O_DATA7 = 0x36  # 2-21
O_DATA8 = 0x37  # 2-21
O_DATA9 = 0x38  # 2-21
O_DATA10 = 0x39  # 2-21
O_DATA11 = 0x30  # 2-21
O_DATA12 = 0x3a  # 2-21
O_DATA13 = 0x3b  # 2-21
O_DATA14 = 0x3c  # 2-21
O_DATA15 = 0x3d  # 2-21
O_DATA16 = 0x3e  # 2-21
O_DATA17 = 0x3f  # 2-21

MODE_BASIC = 0x30
MODE_ACC = 0x31
MODE_ACC_IR = 0x33
MODE_FULL = 0x3e


def send(op, payload):
    """Sends data"""
    HOST_SEND + op + payload


def recv():
    """Received data"""
    packet = 0
    payload = packet - HOST_RECV
    op = 2
    if op == I_LED:
        set_led(payload)
    elif op == 5:
        pass
    else:
        print(("op :" + op))


def get_battery():
    """Returns battery %"""
    return 50


def status(critical=False, extension=False, speaker=False, ir=False, led1=False, led2=False, led3=False, led4=False):
    """Retirns wiimote status"""
    BB = get_buttons()
    LF = (led4 << 7 | led3 << 6 | led2 << 5 | led1 << 4 | ir << 3 | speaker << 2 | extension << 1 | critical)
    VV = get_battery()
    send(op=O_STATUS_INFO, payload=[BB, LF, 00, 00, VV])


def report(mode=O_DATA1):
    """Sets the reporting mode"""
    if mode == O_DATA1:
        send(op=O_DATA1, payload=get_buttons())
    elif mode == O_DATA2:
        send(op=O_DATA2, payload=[get_buttons(), get_accel()])
    elif mode == O_DATA3:
        send(op=O_DATA3, payload=[get_buttons(), get_extension()])
    else:
        print(("Unknown mode: " + mode))


def get_accel():
    """Returns accel"""
    x = 0
    y = 0
    z = 0
    return (x << 16 | y << 8 | z)


def get_buttons(left=False, right=False, down=False, up=False, plus=False, two=False, one=False, b=False, a=False, minus=False, home=False):
    """Current input state"""
    dummy1 = False
    dummy2 = False
    dummy3 = False
    dummy4 = False
    dummy5 = False
    b1 = (left << 7 | right << 6 | down << 5 | up << 4 | plus << 3 | dummy1 << 2 | dummy2 << 1 | dummy3) << 8
    b2 = (two << 7 | one << 6 | b << 5 | a << 4 | minus << 3 | dummy4 << 2 | dummy5 << 1 | home)
    return b1 | b2


def get_extension():
    """Something"""
    return 8  # bytes


def set_led(val):
    """Sets LED value based on a byte"""
    pass

print("Valid")