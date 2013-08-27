#!/usr/bin/python
###########################################################
#######  A LINUX DRIVER FOR THE NINTENDO WII REMOTE  ######             
##*********************************************************
##      ___           ___                            
##     /\  \         /\  \         _____             
##    _\:\  \       |::\  \       /::\  \            
##   /\ \:\  \      |:|:\  \     /:/\:\  \           
##  _\:\ \:\  \   __|:|\:\  \   /:/  \:\__\          
## /\ \:\ \:\__\ /::::|_\:\__\ /:/__/ \:|__|         
## \:\ \:\/:/  / \:\~~\  \/__/ \:\  \ /:/  /         
##  \:\ \::/  /   \:\  \        \:\  /:/  /          
##   \:\/:/  /     \:\  \        \:\/:/  /           
##    \::/  /       \:\__\        \::/  /            
##     \/__/         \/__/         \/__/             
##
##     WMD v0.0.4: Wiiwanna Motte Dammiit!
##     by Francois A. Bradet, aka e-Hernick#wiili@freenode
##     coded from 2006-12-04 to 2006-12-11 00:10 EDT
##     with code by Micah Dowty and Marcan
##     with algorithms by Ian Rickard
##     share use modify as you wish; CC-PD+GPL2
##
##   WMD is a Linux Driver for the Nintendo Wii Remote
##
##   WMD lets you use the Wiimote as a mouse
##
##   WMD lets you use the Wiimote as a keyboard
##   WMD lets you use the Wiimote as a vibrator
##
##   WMD is dangerous and experimental
##   WMD could make your Wii explode!
##   WMD has no warranty other than the CC-PD+GPL2
##
############################################################
#######  I. INTRODUCTION:   READ ME FIRST OR ELSE  #########
##**********************************************************
## It is important that you read this before
## trying to use WMD, or else you will fail miserably.
##
## You need technical knowledge and Linux experience
## if you are to succeed in installing WMD without help.
##
## But more than that, you need to install the following:
##
##  **  BlueZ (MUST!)
##
##  **  PyBluez 0.9.1 (MUST!)     # aka python-bluez? on ubuntu
##      http://org.csail.mit.edu/pybluez/release/pybluez-src-0.9.1.tar.gz
##
##      To use Xlib event mode   (GOOD)
##  ++  python-xlib 0.12
##  ++    with buffer overflow patch (READ SECTION: XLIB)
##
##      To use uinput event mode (GOOD)
##  ++  Linux 2.6 kernel with evdev and uinput modules
##
##      To use the OSD (GOOD)
##  ++  PyOSD 0.2.14 http://repose.cx/pyosd/
##
##      To use uinput events to move the mouse (BAD!)
##  ++  Xorg 7.0 with evdev
##
## 
###############
## SECTION XLIB
###############
##
##   You must used a PATCHED python-xlib 0.12 because the original
##   has a terrible bug that prevents it from starting with modern Xorg
##   python-xlib hasn't been maintained in years, but the patch is simple.
##
##   First you install python-xlib 0.12
##
##   Then you find the file protocol/display.py
#### locate protocol/display.py | grep -v pyc
##   /usr/lib/python2.4/site-packages/Xlib/protocol/display.py
##
##
##   Then you check if it's already patched
#### grep self.socket.recv /usr/lib/python2.4/site-packages/Xlib/protocol/display.py
##   recv = self.socket.recv(4096)
##
##   If the value is 4096, all is good
##   If the value is 2048, you need to edit the file and change the value to 4096
##
##   It's THAT EASY!
##
##   On Gentoo, dev-python/python-xlib-0.12-r2 is already patched.
##
################
####
#### PREFLIGHT CHECK - IF YOU'RE HAVING ANY TROUBLE
#### RUN THE FOLLOWING COMMANDS AND COMPARE THE OUTPUT
#### YOU GET TO THE OUTPUT I GOT
##
#### gzcat /proc/config.gz | grep -iE "evdev|uinput"
##   CONFIG_INPUT_EVDEV=y
##   CONFIG_INPUT_UINPUT=m
##
#modprobe uinput
#modprobe evdev
#### lsmod | grep uinput
##   uinput	8832	0
##
#### find /dev -name uinput
##   /dev/uinput
##   /dev/misc/uinput
##
#### locate evdev_drv
##   /usr/lib/xorg/modules/input/evdev_drv.so
##
#### locate bluetooth.py
##   /usr/lib/python2.4/site-packages/bluetooth.py
##
#### grep PyBluez /usr/lib/python2.4/site-packages/bluetooth.py | wc -l
##   2
##
#### hcitool scan | grep Nintendo
##   00:19:1D:25:16:43       Nintendo RVL-CNT-01
##


############################################################
#######     II. BASIC CONFIGURATION: DO IT NOW     #########
##**********************************************************
##
## lorgo!
## This is the address of my Wiimote.
##
MY_WIIMOTE_ADDR="00:19:1D:25:16:43"
## 
## Or, if I'm lazy, I'll just comment it out and uncomment
## An empty address: it will force autodetection:
##
#MY_WIIMOTE_ADDR=""
##
##
## Next, I will choose which IO Modes I want to use
## for sending keypresses, clicks, mouse movements and gestures
## *ATTENTION YOU SHOULD NOT EXPECT ANYTHING TO WORK IF YOU CHANGE IO_MODES OR IO_CHANNELS SETTINGS IN ANY WAY
IO_MODES = {          # SET TO TRUE IF YOU HAVE:
  'UINPUT': True,     ## the uinput kernel module loaded.
  'XLIB': True,       ## python-xlib with the buffer overflow patch.
  'X_EVDEV': False,    ## evdev_drv and a customized xorg.conf.
  'PYOSD': True
}
##
##
## If I'm using IO_MODES['UINPUT'] I'll need to
## Set the path of my uinput device
##
UINPUT_DEV = "/dev/misc/uinput"
#UINPUT_DEV = "/dev/input/uinput"  ##ubuntu - you need to modprobe uinput first
#UINPUT_DEV = "/dev/uinput"
##
## I'll also check that I have the right UNIX rights for it
##
##
## If I changed the default IO modes
## I'll need to choose new IO channels for them
## Changing the default IO channels is risky and poorly tested
## The only channel I'd consider changing for now is 'EV_ABS' to 'X_EVDEV'
##
IO_CHANNELS = { 
  'EV_ABS': 'XLIB',
  'EV_KEY': 'UINPUT',
  'EV_REL': 'UINPUT'
}
##
##
## Now, this is the fun part, when you can assign
## Actions to Buttons
##
commandMap = {
  'A': ['click', 'BTN_RIGHT' ],  # A key: right mouse button click
  'B': ['click', 'BTN_LEFT' ],   # B key: left mouse button click

  'H': ['quit'],                 # Home key: quits WMD

  '-': ['vibrate', 'toggle' ],       # Minus key: starts vibrator toggle
  '+': ['vibrate', 'off' ],      # Plus key: stops vibrator and resets IR

# '1': ['guess', 'status' ],
  '2': ['guess', 'orien' ],      # 2 key: guess orientation of the Wiimote
  '1': ['key', 'KEY_1' ],        # 1 key: press the '1' key like a keyboard
# '2': ['key', 'KEY_2' ],

  'U': ['led', 'toggle', 1 ],    # Toggles LED 1
  'D': ['led', 'toggle', 2 ],    #         LED 2
  'L': ['led', 'toggle', 3 ],    #         LED 3
  'R': ['led', 'toggle', 4 ]     #         LED 4
}
##
##
## This will enable IR sensing by default
IR_ENABLE = 1
##
##
## If you having trouble reaching the edges of your screen with the IR mouse
## You want to raise the Dead-Zone values at the most 0.50
XDZ = 0.15
YDZ = 0.15
##
##
## If for some reason WMD isn't detecting your screen size correctly
## Set these to the right values. If 0, WMD will autodetect.
SCREEN_WIDTH = 0     #1600 
SCREEN_HEIGHT = 0
##
##
## These values influence motion sensing in unknown ways
##
force_log_maxlen = 20
force_disturbance = 200
quash = { 'duration': 5, 'age': 0 }
HYST = 0
##
##
## These influence IR pointer behaviour in unknown ways
dots_fifo_len = 2
dots_quash = { 'duration': 2, 'age': 0 }
##
##

## Ah, this here is magic, use it in combination with AUTO_IRP=OFF if you want to force a mode
#IRP_MODE = "1DM"
IRP_MODE = "HDM"
#IRP_MODE = "2DM"

DM_DOT = 0
#1DM_DOT = 1

AUTO_IRP = "ON"
#AUTO_IRP = "OFF"

# This is the threshold of dot separation at which automatic IRP MODE will switch
# Automatic IRP MODE is not very good at this time
AUTOIRP_THRESH = 430                    # 430 pixels is about 2 feet or 60 cm
#AUTOIRP_THRESH = 10370.0 / 24          # We can specify it as 24 inches
#AUTOIRP_THRESH = 26300.0 / 60          # Or as 60 centimeters

#AUTOIRP_2DMLOCK_THRESH = 220            # 220 pixels is about 4 feet or 120 cm
AUTOIRP_2DMLOCK_THRESH = 10370 / 60    # We can specify it as 48 inches
#AUTOIRP_2DMLOCK_THRESH = 26300 / 120   # Or 120 centimeters

# This dampens sudden changes of IRP mode due to a lost dot that could be reacquired soon
# It doesn't seem to be useful, but you could try raising it a little
# It'll be useful in the future I think
AUTOIRP_DAMPTHRESH = 300 
# Those two are useless for now
AUTOIRP_WARNTHRESH = 150 
AUTOIRP_WARNDIV = 50

# These are the smoothing thresholds
SMOOThreshes = [
  [ 10, 0.90 ],
  [ 20, 0.82 ],
  [ 35, 0.76 ],
  [ 50, 0.70 ],
  [ 70, 0.30 ],
  [ 90, 0.10 ],
]

# These are the smoothing factors for this function:
# SMOOTHING_WEIGHT = SMOO1 / ( SMOO2 + d*d*d * SMOO3 )
SMOO1 = 180
SMOO2 = 200
SMOO3 = 0.001

# This is the mixing factor for the two smoothing functions
# 1.0 will use only threshold smoothing
# 0.0 will use only function smoothing
# 0.5 will split half and half between the two
SMOOMIX = 0.5  #Min=0.0, Max=1.0

## DON'T TOUCH THOSE TWO LINES: these are constants for debug levels
LOG_ERR = 1; LOG_INFO = 2; LOG_BTN = 4; LOG_FORCE = 8; LOG_IR = 16
DEBUG_FORCE = 32; DEBUG_IR = 64; DEBUG_BT_SEND = 128; DEBUG_BT_RECV = 256
DEBUG_IR2 = 512
##
##
## Here you can choose how much logging you want to see
LOG_LEVEL = LOG_ERR | LOG_INFO | LOG_FORCE 
#LOG_LEVEL = LOG_ERR | LOG_INFO | LOG_FORCE #| LOG_BTN | LOG_IR   #more stuff
#LOG_LEVEL = LOG_ERR | LOG_INFO     # minimal

## If you want do use XEVDEV IO, you need to install evdev_drv for Xorg
## You also need to add this section to your xorg.conf
#
#  Section "InputDevice"
# 	Identifier	"Wiimote"
# 	Driver		"evdev"
# 	Option		"Name"		"Nintendo Wiimote"
#  EndSection
#
## You will also need to modify your ServerLayout section.
## You must have only one CorePointer, but you can have
## many AlwaysCore devices. You don't need a Synaptics
## touchpad, I just have one on my laptop.
## So this is what the beginning of my xorg.conf looks like:
#
#  Section "ServerLayout"
#  	Identifier      "X.org Configured"
#  	Screen  0       "Screen0" 		0 0
# 	InputDevice     "Mouse0"                "CorePointer"
# 	InputDevice     "Keyboard0"             "CoreKeyboard"
# 	InputDevice     "Synaptics Touchpad"    "AlwaysCore"
# 	InputDevice     "Wiimote"               "AlwaysCore"
#  EndSection
#
## Scaling is known to work badly with evdev_drv



# We import PyBluez and other stuff
from bluetooth import *
from copy import copy
import string, pprint
import os, struct, fcntl, time, math, string, random
pp = pprint.PrettyPrinter(indent=4)

# This is what the Wiimote calls itself (Bluetooth Name)
WIIMOTE_NAME = "Nintendo RVL-CNT-01"

status = { 'go':1 }
socket = {}

force_log = []
dots_fifo = []

# These are the button mappings
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

EXTRALOGS = 0
buttonstates = {}
oldbuttonstates = {}
for bt in buttonmap:
  buttonstates[bt] = 0
  oldbuttonstates[bt] = 0

led_state = [0,0,0,0]

# These are commands for the wiimote
commandcodes = {
  "vibrate_on": 0x521305,
  "vibrate_off": 0x521304,
#  "forcerep_on": 0x52120431,
#  "forcerep_off": 0x52120030,
  "leds_off": 0x521100,
  "accept_attachment": 0x52120033,
  'request_0x20_report': 0x521504
}

#constants:
XRANGE = 1024.0
YRANGE = 768.0


# These are the Wiimote control codes
FEATURE_DISABLE = 0x00
FEATURE_ENABLE = 0x04

IR_MODE_OFF = 0
IR_MODE_STD = 1
IR_MODE_EXP = 3
IR_MODE_FULL = 5

CMD_SET_REPORT = 0x52

RID_LEDS = 0x11
RID_MODE = 0x12
RID_IR_EN = 0x13
RID_SPK_EN = 0x14
RID_STATUS = 0x15
RID_WMEM = 0x16
RID_RMEM = 0x17
RID_SPK = 0x18
RID_SPK_MUTE = 0x19
RID_IR_EN2 = 0x1A

MODE_BASIC = 0x30
MODE_ACC = 0x31
MODE_ACC_IR = 0x33
MODE_FULL = 0x3e


# These are uinput control codes
UI_DEV_CREATE  = 0x5501
UI_DEV_DESTROY = 0x5502

UI_SET_EVBIT   = 0x40045564
UI_SET_KEYBIT  = 0x40045565
UI_SET_RELBIT  = 0x40045566
UI_SET_ABSBIT  = 0x40045567

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03

REL_X = 0x00
REL_Y = 0x01

ABS_X = 0x00
ABS_Y = 0x01

BUS_USB = 0x03

BTN_MOUSE = 0x110
BTN_TOUCH = 0x14a
BTN_TOOL_FINGER = 0x145

SYN_REPORT = 0

class EnumDict:
    """A 1:1 mapping from numbers to strings or other objects, for enumerated
       types and other assigned numbers. The mapping can be queried in either
       direction. All values, by default, map to themselves.
       """
    def __init__(self, numberMap):
        self.numberMap = numberMap
        self.nameMap = {}
        for key, value in numberMap.iteritems():
            self.nameMap[value] = key

    def toNumber(self, name):
        return self.nameMap.get(name, name)

    def fromNumber(self, num):
        return self.numberMap.get(num, num)

typeMap = EnumDict({
        0x00: "EV_RST",
        0x01: "EV_KEY",
        0x02: "EV_REL",
        0x03: "EV_ABS",
        0x04: "EV_MSC",
        0x11: "EV_LED",
        0x12: "EV_SND",
        0x14: "EV_REP",
        0x15: "EV_FF",
        })

## ************** ATTENTION USER ****************
#   _  __________     ____  __          _____  
#  | |/ /  ____\ \   / /  \/  |   /\   |  __ \ 
#  | ' /| |__   \ \_/ /| \  / |  /  \  | |__) |
#  |  < |  __|   \   / | |\/| | / /\ \ |  ___/ 
#  | . \| |____   | |  | |  | |/ ____ \| |     
#  |_|\_\______|  |_|  |_|  |_/_/    \_\_|     
## THIS IS THE KEYMAP
## USE THESE KEY_CODES IN THE commandMap

codeMaps = {
        "EV_KEY": EnumDict({
        0: "KEY_RESERVED",
        1: "KEY_ESC",
        2: "KEY_1",
        3: "KEY_2",
        4: "KEY_3",
        5: "KEY_4",
        6: "KEY_5",
        7: "KEY_6",
        8: "KEY_7",
        9: "KEY_8",
        10: "KEY_9",
        11: "KEY_0",
        12: "KEY_MINUS",
        13: "KEY_EQUAL",
        14: "KEY_BACKSPACE",
        15: "KEY_TAB",
        16: "KEY_Q",
        17: "KEY_W",
        18: "KEY_E",
        19: "KEY_R",
        20: "KEY_T",
        21: "KEY_Y",
        22: "KEY_U",
        23: "KEY_I",
        24: "KEY_O",
        25: "KEY_P",
        26: "KEY_LEFTBRACE",
        27: "KEY_RIGHTBRACE",
        28: "KEY_ENTER",
        29: "KEY_LEFTCTRL",
        30: "KEY_A",
        31: "KEY_S",
        32: "KEY_D",
        33: "KEY_F",
        34: "KEY_G",
        35: "KEY_H",
        36: "KEY_J",
        37: "KEY_K",
        38: "KEY_L",
        39: "KEY_SEMICOLON",
        40: "KEY_APOSTROPHE",
        41: "KEY_GRAVE",
        42: "KEY_LEFTSHIFT",
        43: "KEY_BACKSLASH",
        44: "KEY_Z",
        45: "KEY_X",
        46: "KEY_C",
        47: "KEY_V",
        48: "KEY_B",
        49: "KEY_N",
        50: "KEY_M",
        51: "KEY_COMMA",
        52: "KEY_DOT",
        53: "KEY_SLASH",
        54: "KEY_RIGHTSHIFT",
        55: "KEY_KPASTERISK",
        56: "KEY_LEFTALT",
        57: "KEY_SPACE",
        58: "KEY_CAPSLOCK",
        59: "KEY_F1",
        60: "KEY_F2",
        61: "KEY_F3",
        62: "KEY_F4",
        63: "KEY_F5",
        64: "KEY_F6",
        65: "KEY_F7",
        66: "KEY_F8",
        67: "KEY_F9",
        68: "KEY_F10",
        69: "KEY_NUMLOCK",
        70: "KEY_SCROLLLOCK",
        71: "KEY_KP7",
        72: "KEY_KP8",
        73: "KEY_KP9",
        74: "KEY_KPMINUS",
        75: "KEY_KP4",
        76: "KEY_KP5",
        77: "KEY_KP6",
        78: "KEY_KPPLUS",
        79: "KEY_KP1",
        80: "KEY_KP2",
        81: "KEY_KP3",
        82: "KEY_KP0",
        83: "KEY_KPDOT",
        84: "KEY_103RD",
        85: "KEY_F13",
        86: "KEY_102ND",
        87: "KEY_F11",
        88: "KEY_F12",
        89: "KEY_F14",
        90: "KEY_F15",
        91: "KEY_F16",
        92: "KEY_F17",
        93: "KEY_F18",
        94: "KEY_F19",
        95: "KEY_F20",
        96: "KEY_KPENTER",
        97: "KEY_RIGHTCTRL",
        98: "KEY_KPSLASH",
        99: "KEY_SYSRQ",
        100: "KEY_RIGHTALT",
        101: "KEY_LINEFEED",
        102: "KEY_HOME",
        103: "KEY_UP",
        104: "KEY_PAGEUP",
        105: "KEY_LEFT",
        106: "KEY_RIGHT",
        107: "KEY_END",
        108: "KEY_DOWN",
        109: "KEY_PAGEDOWN",
        110: "KEY_INSERT",
        111: "KEY_DELETE",
        112: "KEY_MACRO",
        113: "KEY_MUTE",
        114: "KEY_VOLUMEDOWN",
        115: "KEY_VOLUMEUP",
        116: "KEY_POWER",
        117: "KEY_KPEQUAL",
        118: "KEY_KPPLUSMINUS",
        119: "KEY_PAUSE",
        120: "KEY_F21",
        121: "KEY_F22",
        122: "KEY_F23",
        123: "KEY_F24",
        124: "KEY_KPCOMMA",
        125: "KEY_LEFTMETA",
        126: "KEY_RIGHTMETA",
        127: "KEY_COMPOSE",
        128: "KEY_STOP",
        129: "KEY_AGAIN",
        130: "KEY_PROPS",
        131: "KEY_UNDO",
        132: "KEY_FRONT",
        133: "KEY_COPY",
        134: "KEY_OPEN",
        135: "KEY_PASTE",
        136: "KEY_FIND",
        137: "KEY_CUT",
        138: "KEY_HELP",
        139: "KEY_MENU",
        140: "KEY_CALC",
        141: "KEY_SETUP",
        142: "KEY_SLEEP",
        143: "KEY_WAKEUP",
        144: "KEY_FILE",
        145: "KEY_SENDFILE",
        146: "KEY_DELETEFILE",
        147: "KEY_XFER",
        148: "KEY_PROG1",
        149: "KEY_PROG2",
        150: "KEY_WWW",
        151: "KEY_MSDOS",
        152: "KEY_COFFEE",
        153: "KEY_DIRECTION",
        154: "KEY_CYCLEWINDOWS",
        155: "KEY_MAIL",
        156: "KEY_BOOKMARKS",
        157: "KEY_COMPUTER",
        158: "KEY_BACK",
        159: "KEY_FORWARD",
        160: "KEY_CLOSECD",
        161: "KEY_EJECTCD",
        162: "KEY_EJECTCLOSECD",
        163: "KEY_NEXTSONG",
        164: "KEY_PLAYPAUSE",
        165: "KEY_PREVIOUSSONG",
        166: "KEY_STOPCD",
        167: "KEY_RECORD",
        168: "KEY_REWIND",
        169: "KEY_PHONE",
        170: "KEY_ISO",
        171: "KEY_CONFIG",
        172: "KEY_HOMEPAGE",
        173: "KEY_REFRESH",
        174: "KEY_EXIT",
        175: "KEY_MOVE",
        176: "KEY_EDIT",
        177: "KEY_SCROLLUP",
        178: "KEY_SCROLLDOWN",
        179: "KEY_KPLEFTPAREN",
        180: "KEY_KPRIGHTPAREN",
        181: "KEY_INTL1",
        182: "KEY_INTL2",
        183: "KEY_INTL3",
        184: "KEY_INTL4",
        185: "KEY_INTL5",
        186: "KEY_INTL6",
        187: "KEY_INTL7",
        188: "KEY_INTL8",
        189: "KEY_INTL9",
        190: "KEY_LANG1",
        191: "KEY_LANG2",
        192: "KEY_LANG3",
        193: "KEY_LANG4",
        194: "KEY_LANG5",
        195: "KEY_LANG6",
        196: "KEY_LANG7",
        197: "KEY_LANG8",
        198: "KEY_LANG9",
        200: "KEY_PLAYCD",
        201: "KEY_PAUSECD",
        202: "KEY_PROG3",
        203: "KEY_PROG4",
        205: "KEY_SUSPEND",
        206: "KEY_CLOSE",
        220: "KEY_UNKNOWN",
        224: "KEY_BRIGHTNESSDOWN",
        225: "KEY_BRIGHTNESSUP",
        0x100: "BTN_0",
        0x101: "BTN_1",
        0x102: "BTN_2",
        0x103: "BTN_3",
        0x104: "BTN_4",
        0x105: "BTN_5",
        0x106: "BTN_6",
        0x107: "BTN_7",
        0x108: "BTN_8",
        0x109: "BTN_9",
        0x110: "BTN_LEFT",
        0x111: "BTN_RIGHT",
        0x112: "BTN_MIDDLE",
        0x113: "BTN_SIDE",
        0x114: "BTN_EXTRA",
        0x115: "BTN_FORWARD",
        0x116: "BTN_BACK",
        0x120: "BTN_TRIGGER",
        0x121: "BTN_THUMB",
        0x122: "BTN_THUMB2",
        0x123: "BTN_TOP",
        0x124: "BTN_TOP2",
        0x125: "BTN_PINKIE",
        0x126: "BTN_BASE",
        0x127: "BTN_BASE2",
        0x128: "BTN_BASE3",
        0x129: "BTN_BASE4",
        0x12a: "BTN_BASE5",
        0x12b: "BTN_BASE6",
        0x12f: "BTN_DEAD",
        0x130: "BTN_A",
        0x131: "BTN_B",
        0x132: "BTN_C",
        0x133: "BTN_X",
        0x134: "BTN_Y",
        0x135: "BTN_Z",
        0x136: "BTN_TL",
        0x137: "BTN_TR",
        0x138: "BTN_TL2",
        0x139: "BTN_TR2",
        0x13a: "BTN_SELECT",
        0x13b: "BTN_START",
        0x13c: "BTN_MODE",
        0x13d: "BTN_THUMBL",
        0x13e: "BTN_THUMBR",
        0x140: "BTN_TOOL_PEN",
        0x141: "BTN_TOOL_RUBBER",
        0x142: "BTN_TOOL_BRUSH",
        0x143: "BTN_TOOL_PENCIL",
        0x144: "BTN_TOOL_AIRBRUSH",
        0x145: "BTN_TOOL_FINGER",
        0x146: "BTN_TOOL_MOUSE",
        0x147: "BTN_TOOL_LENS",
        0x14a: "BTN_TOUCH",
        0x14b: "BTN_STYLUS",
        0x14c: "BTN_STYLUS2",
        }),

        "EV_REL": EnumDict({
        0x00: "REL_X",
        0x01: "REL_Y",
        0x02: "REL_Z",
        0x06: "REL_HWHEEL",
        0x07: "REL_DIAL",
        0x08: "REL_WHEEL",
        0x09: "REL_MISC",
        }),

        "EV_ABS": EnumDict({
        0x00: "ABS_X",
        0x01: "ABS_Y",
        0x02: "ABS_Z",
        0x03: "ABS_RX",
        0x04: "ABS_RY",
        0x05: "ABS_RZ",
        0x06: "ABS_THROTTLE",
        0x07: "ABS_RUDDER",
        0x08: "ABS_WHEEL",
        0x09: "ABS_GAS",
        0x0a: "ABS_BRAKE",
        0x10: "ABS_HAT0X",
        0x11: "ABS_HAT0Y",
        0x12: "ABS_HAT1X",
        0x13: "ABS_HAT1Y",
        0x14: "ABS_HAT2X",
        0x15: "ABS_HAT2Y",
        0x16: "ABS_HAT3X",
        0x17: "ABS_HAT3Y",
        0x18: "ABS_PRESSURE",
        0x19: "ABS_DISTANCE",
        0x1a: "ABS_TILT_X",
        0x1b: "ABS_TILT_Y",
        0x1c: "ABS_MISC",
        }),

        "EV_MSC": EnumDict({
        0x00: "MSC_SERIAL",
        0x01: "MSC_PULSELED",
        }),

        "EV_LED": EnumDict({
        0x00: "LED_NUML",
        0x01: "LED_CAPSL",
        0x02: "LED_SCROLLL",
        0x03: "LED_COMPOSE",
        0x04: "LED_KANA",
        0x05: "LED_SLEEP",
        0x06: "LED_SUSPEND",
        0x07: "LED_MUTE",
        0x08: "LED_MISC",
        }),

        "EV_REP": EnumDict({
        0x00: "REP_DELAY",
        0x01: "REP_PERIOD",
        }),

        "EV_SND": EnumDict({
        0x00: "SND_CLICK",
        0x01: "SND_BELL",
        }),
        }



def get_wiimote_uinput_user_dev():
  STRPK_UINPUT_USER_DEV = "80sHHHHi" + 64*4*'I' 
  WIIMOTE_UUD_STR = [
    "Nintendo Wiimote",   # Device name
    BUS_USB,             # Bus type
    1,                   # Vendor
    1,                   # Product
    1,                   # Version
    0                   # ff_effects_max
  ]

  for f in range(64*1):  #absmin
    WIIMOTE_UUD_STR.append(0x00)
  for f in range(64*1):  #absmax
    WIIMOTE_UUD_STR.append(0x400)
  for f in range(64*2):   #absfuzz,absflat
    WIIMOTE_UUD_STR.append(0x00)

  WIIMOTE_UUD = struct.pack(
    STRPK_UINPUT_USER_DEV,
    *WIIMOTE_UUD_STR
  )

  return WIIMOTE_UUD

def get_wiimote_evbits():
  UINPUT_IO_CHANNELS = []
  for ioc in IO_CHANNELS:
    if IO_CHANNELS[ioc] == 'UINPUT':
      UINPUT_IO_CHANNELS.append(ioc)

  UINPUT_UUD_BITS = {

    'EV_REL': [
      [ UI_SET_EVBIT, EV_REL ],
      [ UI_SET_RELBIT, REL_X ],
      [ UI_SET_RELBIT, REL_Y ]
    ],

    'EV_ABS': [
      [ UI_SET_EVBIT, EV_ABS ],
      [ UI_SET_ABSBIT, ABS_X ],
      [ UI_SET_ABSBIT, ABS_Y ]
    ],

    'EV_KEY': [
      [ UI_SET_EVBIT, EV_KEY ],
      [ UI_SET_EVBIT, EV_SYN ]
    ]

  }

  if IO_CHANNELS['EV_KEY'] == "UINPUT":
    for btn in commandMap:
      com = commandMap[btn]
      type = com[0]
      if type == "click" or type == "key":
        key = com[1]
        code = int(codeMaps["EV_KEY"].toNumber(key))
        if code:
          log( LOG_INFO, "Registering key %s for button %s with code %x" % (key, btn, code) )
	  UINPUT_UUD_BITS['EV_KEY'].append( [UI_SET_KEYBIT, code] )

  UINPUT_UUD = []
  for ioc in UINPUT_IO_CHANNELS:
    for bitset in UINPUT_UUD_BITS[ioc]:
      UINPUT_UUD.append(bitset)
    
  print UINPUT_UUD
  return UINPUT_UUD

def send_led_command():
  command_start = 0x521100
  command_end = 0x00
  if led_state[0]:
    command_end += 0x10
  if led_state[1]:
    command_end += 0x20
  if led_state[2]:
    command_end += 0x40
  if led_state[3]:
    command_end += 0x80
  command = hex(command_start + command_end)
  cmd = command[2:].decode("hex")
  send_command( cmd )

def led_on(led):
  led_state[led] = 1
  send_led_command()

def led_off(led):
  led_state[led] = 0
  send_led_command()

def led_toggle(led):
  if led_state[led] == 0:
    led_state[led] = 1
  elif led_state[led] == 1:
    led_state[led] = 0
  send_led_command()

def log(level, msg):
  if (level & LOG_LEVEL) or ( level & EXTRALOGS ):
    print msg

def find_willing_wiimote():
  log(LOG_INFO, "Now trying to discover a willing Wiimote, please activate your Wiimote within 5 seconds.")
  bt_devs = discover_devices(lookup_names = True)
  if bt_devs:
    log(LOG_INFO, "Found %d Bluetooth Devices!" % len(bt_devs) )
    for bt_dev in bt_devs:
      if bt_dev[1] == WIIMOTE_NAME:
        addr = bt_dev[0]
        log(LOG_INFO, "Found a Wiimote at address " + addr)
	return addr
  else:
    log(LOG_ERR, "FAILURE!")

def find_wiimote_services(addr):
  log(LOG_INFO, "Looking for Wiimote services at address " + addr)
  servs = find_service( address = addr )
  if servs:
    log(LOG_INFO, "Victory! We have found that Wiimote!")
    return servs
  if not servs:
    log(LOG_ERR, "Failure. We have not found that Wiimote.")
    return 0


def toHex(s):
  l = []
  for c in s:
    h = hex(ord(c)).replace('0x', '')
    if len(h) == 1:
      h = '0' + h
    l.append(h)
  return string.join(l, " ")

def hex2s(h):
  return  ('%x' % h).decode("hex")

def send_command_code(cc):
  valid_names = [ 'led', 'leds', 'quit', 'key', 'click', 'vibrate', 'guess' ]
  name = cc[0]
  
  if name == "led" and cc[1] == "toggle":
    led_id = cc[2]-1
    led_toggle( led_id )

  elif name == 'leds' and cc[1] == "off":
    cs = hex2s(commandcodes['leds_off'])
    send_command( cs )

  elif name == 'quit':
    osd_show( "BYE BYE WMD WILL EXIT IN A SECOND" )
    time.sleep(1)
    status['go'] = 0

  elif name == 'guess' and cc[1] == 'orien':
    guess_orientation(force_log)
    if cc[2] == "DOWN":
      globals()["EXTRALOGS"] = DEBUG_IR
    else:
      globals()["EXTRALOGS"] = 0

  elif name == 'click' or name == "key":
    keyname = cc[1]
    presstype = cc[2]
    keycode = codeMaps["EV_KEY"].toNumber( keyname )
   
    if IO_MODES['PYOSD']:
      osd_show( "%s on %s (%s)" % (name, keyname, presstype) )


    if IO_MODES['UINPUT'] and IO_CHANNELS['EV_KEY'] == 'UINPUT':
      if presstype == "DOWN":
        uinput_send_keydown( keycode )
      elif presstype == "UP":
        uinput_send_keyup( keycode )

  elif name == 'vibrate':
    if cc[1] == "toggle" and cc[2] == "DOWN":
      Vibe.step()
    elif cc[1] == "off":
      Vibe.off()
      IR.on()

  else:
    log(LOG_ERR, "COMMAND ERROR FOR COMMAND NAME = " + name)
   
class Vibrator:
  """OH YEAH"""
  def __init__( self ):
    self.state = "off" 
    self.stepn = 0

  def on( self ):
    self.cmd_on()
    self.state = "on"
    self.stepn = 0

  def off( self ):
    self.cmd_off()
    self.state = "off"
    self.stepn = 0

  def step( self, duration=2, stepo=0 ):
    self.stepn += 1.0
    self.stepn *= 1.1

    if stepo:
      self.stepn = stepo

    freq = self.stepn
    n_steps = int(duration * freq)
    step_duration = 1/freq

    self.plm( n_steps, step_duration )

  def plm( self, pulses, length ):
    if self.state == "on":
      self.off()

    for i in range(pulses):
      time.sleep( length )
      self.cmd_on()
      time.sleep( length )
      self.cmd_off()


  def cmd_on( self ):
    send_command(hex2s(commandcodes['vibrate_on']))

  def cmd_off( self ):
    send_command(hex2s(commandcodes['vibrate_off']))


def send_command(commandcode):
  fs = ''
  for b in commandcode:
    fs += str(b).encode("hex").upper()  + " "
  log(DEBUG_BT_SEND, "sending " + str(len (commandcode)) + " bytes: " + fs)
  socket['control'].send( commandcode )
  time.sleep(0.01)

def preprocess_force( force ):
  for ax in force:
    f_raw = force[ax].decode("hex")
    f_val = int(ord(f_raw))
    force[ax] = f_val
  return force

def process_force( force ):
  force = preprocess_force( force )

  if len(force_log) > force_log_maxlen:
    force_log.pop(0)

  force_log.append(force)

  disturbances = {}
  last_axv = {}
  i = 0
  
  axes = ['x','y','z']

  for f in force_log:
    for ax in axes:
      v = f[ax]
      if i == 0:
        last_axv[ax] = v
	disturbances[ax] = 0
      else:
        disturbances[ax] += abs(last_axv[ax]-v)
        last_axv[ax] = v
    i = i + 1

  disturbed_axes = []

  for ax in axes:
    v = disturbances[ax]
    if v > force_disturbance:
      disturbed_axes.append(ax)
  
  if quash['age'] > 0:
    quash['age'] -= 1
  elif disturbed_axes:
    log(LOG_FORCE, "I SENSE A GREAT DISTURBANCE IN THE FORCE..." + str(disturbances))
    quash['age'] = quash['duration']
    log(DEBUG_FORCE, "Force log: " + str(force_log))
    
def guess_orientation_iter( orien, lowX, lowZ, accX, accZ ):
  Wei = 0.95
  lowX = (lowX * Wei) + (accX * (1-Wei))
  lowZ = (lowZ * Wei) + (accZ * (1-Wei))

  absX = abs(lowX - 128)
  absZ = abs(lowZ - 128)

  if orien == 0 or orien == 2:
    absX -= HYST
  elif orien == 1 or orien == 3:
    absZ -= HYST

  if absZ >= absX:
    if absZ > HYST:
      if lowZ > 128:
        orien = 0
      else:
        orien = 2
  elif absX > absZ:
    if absX > HYST:
      if lowX > 128:
        orien = 3
      else:
        orien = 1

  return [orien, lowX, lowZ]

def guess_orientation(force_log):
  orien = 0
  lowX = 128
  lowZ = 160

  for f in force_log:
    (orien, lowX, lowZ) = guess_orientation_iter( orien, lowX, lowZ, f['x'], f['z'] )

  print "orien=%d, lowX=%d, lowZ=%d " % (orien, lowX, lowZ)

  return orien

class bf(object):
    def __init__(self,value=0):
        self._d = value

    def __getitem__(self, index):
        return (self._d >> index) & 1 

    def __setitem__(self,index,value):
        value    = (value&1L)<<index
        mask     = (1L)<<index
        self._d  = (self._d & ~mask) | value

    def __getslice__(self, start, end):
        mask = 2L**(end - start) -1
        return (self._d >> start) & mask

    def __setslice__(self, start, end, value):
        mask = 2L**(end - start) -1
        value = (value & mask) << start
        mask = mask << start
        self._d = (self._d & ~mask) | value
        return (self._d >> start) & mask

    def __int__(self):
        return self._d


class IR_Pointer:
  """This handles data from the PixArt sensor in the WiiMote: a number of dots,
     each with x and y coordinates and intensity. We use this data to issue
     absolute coordinates positions suitable for a pointer on screen."""

  def __init__( self ):
    pass

  def preprocess_dots( self, dots ):
    """Here, we take an hex string containing the raw bytes with information
       on the dots. We then decode this information into usable variables.
       We're going to do ugly bitfield manipulation here. It seems to be
       reliable, but I wouldn't attempt to modify it.
       
       Here are the variables we're going to extract for each dot:
         lx, ly: least significant bytes of x and y
	 mx, my: most significant two bits of x and y
         x:      horizontal position
	 y:      vertical position
	 s:      dot intensity measurement
         v:      dot validity
       """
    dots_sum = [0,0]
    dots_on = 0
    pdots = [ [0,0,0,0], [0,0,0,0] ]

    for dn in range(2):
      for dax in range(3):
	dotc_raw = dots[dn][dax].decode("hex")
	dotc_val = int(ord(dotc_raw))
	dots[dn][dax] = dotc_val
	dots_sum[dn] += dotc_val

    for dn in range(2):
      lx = dots[dn][0]
      ly = dots[dn][1]
      ib = bf( dots[dn][2] )
      s = ib[0:3]
      mx = bf( ib[4:6] )
      my = bf( ib[6:8] )
      x = bf(lx)
      y = bf(ly)
      x[8] = mx[0]
      x[9] = mx[1]
      y[8] = my[0]
      y[9] = my[1]
      pdots[dn][0] = int(x)
      pdots[dn][1] = int(y)
      if dots_sum[dn] != 255*3:
        v = 1
	dots_on += 1
	log(DEBUG_IR2, "dn = %u, lx = %u, ly = %u, mx = %u, my = %u, s = %u, v = %u, x = %u, y = %u" % (dn, lx, ly, mx, my, s, v, x, y))
        pdots[dn][2] = 1
      pdots[dn][3] = s

    if dots_on:
      return [pdots, dots_on]
    else:
      return [0,0]

  dotswap_fac = 0.0
  dotswap_sen = 0.01
  dotswap_thresh = 0.5
  dotswap_max = 1.0

  def dot_swapper( self, dots, dots_on ):
    if dots_on == 2:
      if dots[0][0] < dots[1][0]:
        self.dotswap_fac += self.dotswap_sen
	if self.dotswap_fac > self.dotswap_max:
	  self.dotswap_fac = self.dotswap_max
      else:
        self.dotswap_fac -= self.dotswap_sen
	if self.dotswap_fac < 0:
	  self.dotswap_fac = 0

    if self.dotswap_fac > self.dotswap_thresh:
      dots = self.swap_dots( dots )

    return dots
        
  def swap_dots( self, dots ):
    tdot = copy( dots[0] )
    dots[0] = copy( dots[1] )
    dots[1] = tdot
    return dots

  def process_dots( self, dots ):
    (dots, dots_on) = self.preprocess_dots( dots )

    if dots_on == 0:
      return 0

    dots = self.dot_swapper( dots, dots_on )

    if IO_MODES['XLIB'] and IO_CHANNELS['EV_ABS'] == 'XLIB':
      abs_xlib = self.abs_report_processor( dots, dots_on, XL['w'], XL['h'], 1, 0)
      xlib_abs_report( *abs_xlib )

# This mode is poorly tested.
    if IO_MODES['UINPUT'] and IO_CHANNELS['EV_ABS'] == 'UINPUT':
      xscale = 1024.0; yscale = 1024
      abs_uinput = self.abs_report_processor( dots, dots_on, xscale, yscale, 0, 1)
      uinput_abs_report( *abs_uinput )

  def abs_report_processor( self, dots, dots_on, xscale, yscale, xinv, yinv ):
    xmin = 0.0; ymin = 0.0
    xrangec = 0.0; yrangec = 0.0
    xdz = XDZ; ydz = YDZ

    if dots_on == 2:
      (d, dx, dy) = self.calc_distance( dots )
      self.upd_distlog( d, dx, dy )
    elif dots_on == 1:
      (d, dx, dy) = self.guess_distance( )
      active_dot = self.get_active_dot( dots )

    processing_mode = self.pick_processing_mode( dots, dots_on, d )
   # processing_mode = "HDM"

    if processing_mode == "1DM":
      if DM_DOT == 0:
        dots[1] = dots[0]
      elif DM_DOT == 1:
        dots[0] = dots[1]
     
    elif processing_mode == "HDM":
      xmin = dx/2; ymin = dy/2
      xrangec = dx; yrangec = dy
      if dots_on == 1:
        if active_dot == 0:
	  dots[1] = self.hdm_guess_dot(dots[0], dx, dy)
	elif active_dot == 1:
	  dots[0] = self.hdm_guess_dot(dots[1], -dx, -dy)

    elif processing_mode == "2DM":
      xdz = dx / XRANGE + xdz
      ydz = dy / YRANGE + ydz

    ndots = self.norm_dots( dots, xmin, XRANGE+xrangec, ymin, YRANGE+yrangec )

    rx = self.avg_dotax ( ndots[0][0], ndots[1][0]  )
    sx = self.norm_seq  ( rx, xdz, xinv, xscale )

    ry = self.avg_dotax ( ndots[0][1], ndots[1][1]  )
    sy = self.norm_seq  ( ry, ydz, yinv, yscale ) 

    (sx, sy) = self.abs_smoothen( sx, sy )

    print "on: %u, d0=(%u, %u), d1=(%u, %u) dis=(%u, %u), a=(%u, %u), s=(%u, %u), dsf=%.2f" % (dots_on, dots[0][0], dots[0][1], dots[1][0], dots[1][1], dx, dy, rx, ry, sx, sy, self.dotswap_fac)
    log(LOG_IR, "averaged and scaled to " + str(sx) + ", " + str(sy) )

    return [sx, sy]

  screenx = 0
  screeny = 0

  irp_mode = IRP_MODE
  irp_m_damping_counter = 0
  autoirp_warndiv = AUTOIRP_WARNDIV
  distlog = []
  distlog_len = 200
  hdm_lock = 0

  def norm_dots( self, dots, xmin, xrange, ymin, yrange ):
    ndots = [ [0,0], [0,0] ]
    ndots[0][0] = self.abs_norm_axis( dots[0][0], xmin, xrange )
    ndots[0][1] = self.abs_norm_axis( dots[0][1], ymin, yrange )
    ndots[1][0] = self.abs_norm_axis( dots[1][0], xmin, xrange )
    ndots[1][1] = self.abs_norm_axis( dots[1][1], ymin, yrange )
    return ndots

  def hdm_guess_dot( self, dot, dx, dy ):
    ndot = [0,0]
    ndot[0] = int( dot[0] - dx )
    ndot[1] = int( dot[1] - dy )
    return ndot

  def get_active_dot( self, dots ):
    if dots[0][2]:
      return 0 
    elif dots[1][2]:
      return 1

  def norm_seq( self, n, dz, inv, scale ):
    n = self.abs_dz_axis    ( n, dz          )
    n = self.abs_inv_axis   ( n, inv         )
    s = self.abs_scale_axis ( n, scale       )
    return s

  def avg_dotax( self, p1, p2 ):
    p = ( p1 + p2 ) / 2
    return p

  def guess_distance( self ):
    gd = 0.0; gdx = 0.0; gdy = 0.0
    for dl in self.distlog:
      gd += dl[0]
      gdx += dl[1]
      gdy += dl[2]
    gd /= self.distlog_len
    gdx /= self.distlog_len
    gdy /= self.distlog_len
    return [gd, gdx, gdy]

  def upd_distlog( self, d, dx, dy ):
    if len(self.distlog) > self.distlog_len:
      self.distlog.pop(0)
    self.distlog.append( [d, dx, dy] )
 
  def calc_distance( self, dots ):
    dx = abs( dots[0][0] - dots[1][0] )
    dy = abs( dots[0][1] - dots[1][1] )
    d = math.sqrt( dx*dx + dy*dy )
    return [d, dx, dy]

  def pick_processing_mode( self, dots, dots_on, d ):
    if AUTO_IRP != "ON":
      return IRP_MODE
      
    irp_mode = "HDM"
    
    # It must be dampened but only in the Z-axis!
    # The X axis is the dot picking in 2DM

    # GUESS_DX is most important

    if d < AUTOIRP_2DMLOCK_THRESH:
      irp_mode = "2DM"
    elif d > AUTOIRP_THRESH:
      # Here I should calculate which dot is closest to the center
      irp_mode = "1DM"

    # Apparently the damping mode is rather useless
    if irp_mode != self.irp_mode:
      self.irp_m_damping_counter += 1.0
      if self.irp_m_damping_counter > AUTOIRP_DAMPTHRESH:
#        log(LOG_IR, "Mode switch to " + irp_mode + " at d=%u, x2=%u, y2=%u" % (d,x2,y2) )
#	log(LOG_INFO, "AUTO_IRP mode: " + irp_mode + " at d=" + str(int(26300.0/d)) + "cm" )
        osd_show( "AUTO_IRP mode: " + irp_mode )
        self.irp_mode = irp_mode
	return irp_mode
      elif self.irp_m_damping_counter > AUTOIRP_WARNDIV:
        if self.autoirp_warndiv == 0:
	  self.autoirp_warndiv = AUTOIRP_WARNDIV
	  self.autoirp_warning(self.irp_mode, irp_mode)
	else:
	  self.autoirp_warndiv -= 1
    elif self.irp_m_damping_counter > 0:
      self.irp_m_damping_counter -= 1.0

    return self.irp_mode

  def autoirp_warning( self, nm, om ):
    osd_show( "Imminent IRP change from %s to %s" % (nm, om) )
    Vibe.plm( pulses=1, length=0.1 ) 

  def abs_smoothen( self, x, y ):
    (d, dx, dy) = self.calc_distance( [ [x,y],
					[self.screenx, self.screeny] ] )

    sx = x
    sy = y

    for thresh in SMOOThreshes:
      dMin = thresh[0]
      if d < dMin:
        Wei1 = thresh[1]
	Wei2 = SMOO1 / ( SMOO2 + d*d*d* SMOO3 )

        Wei = ( Wei1 * SMOOMIX ) + (Wei2 * ( 1.0-SMOOMIX ) )
        sx = ( self.screenx * Wei ) + ( x * (1-Wei) )
	sy = ( self.screeny * Wei  ) + ( y * (1-Wei) )
	break

    self.screenx = sx
    self.screeny = sy

    return [sx, sy]

  def abs_norm_axis( self, rp, min, range ):
    rp += min
    np = rp/range
    return np
 
  def abs_scale_axis( self, np, scale ):
    sp = np*scale
    return sp

  def abs_dz_axis( self, sp, dz ):
    nsp = sp*(1+dz) - (dz/2)
    if nsp < 0:
      nsp = 0
    elif nsp > 1:
      nsp = 1
    return nsp

  def abs_inv_axis( self, sp, inv ):
    nsp = sp
    if inv:
      nsp = 1.0 - sp
    return nsp


class Wiimote_Report_Parser:
  """Receives report packets from the Wiimote
     Classifies and then slices them
     Individually processes and dispatches the slices
     """

  ## SLICE_START and SLICE_END are in number of nibbles
  # SLICE_NAME = [ SLICE_START, SLICE_END, SLICE_HANDLER ]
  SLICE_BTN = [ 4, 8, "slice_BTN" ]   
  SLICE_ACC = [ 8, 14, "slice_ACC" ] 
  SLICE_IR = [ 14, 26, "slice_IR" ]
  SLICE_IRBTN = [ 0, 0, "slice_IRBTN" ]
  SLICE_STAT = [ 8, 10 , "slice_STAT" ]
  SLICE_BAT = [ 14, 16, "slice_BAT" ]
  EV_ATTACH_CHECK = [ 0, 0, "ev_ATTACH_CHECK" ]

  def __init__( self ):
    self.REPORT_TYPES = {
      4: [ "BTN_ONLY",         # Button status only
           [ self.SLICE_BTN ]
	 ],

      6: [ "IR_BTN",       # Useless? Button status reports that are sent during IR mode - allows for lower button latency!!
           [ self.SLICE_IRBTN ]
	 ],

      7: [ "BTN_ACC",          # Buttons+accelerometers status
           [ self.SLICE_BTN, self.SLICE_ACC ]
	 ],

      8: [ "STATUS_REP",       # Status Report
           [ self.SLICE_BTN, self.SLICE_STAT, self.SLICE_BAT, self.EV_ATTACH_CHECK ],
	 ],

      19:[ "BTN_ACC_IR",        # Buttons+accelerometers+IR sensor status
           [ self.SLICE_BTN, self.SLICE_ACC, self.SLICE_IR ]
	 ]
    }

  def parse( self, report ):
    log(DEBUG_BT_RECV, "Recv len(" + str(len(report)) + "): " + str(string.split(toHex(report), " ")))

    if self.REPORT_TYPES.has_key( len(report) ):
      type = self.REPORT_TYPES[ len(report) ]
      self.split_report( report, type )
    else:
      log(LOG_ERR, "Invalid packet size: " + str(len(report)))
      if not LOG_LEVEL & DEBUG_BT_RECV:
        log(LOG_ERR, "Recv len(" + str(len(report)) + "): " + str(string.split(toHex(report), " ")))

  def split_report( self, report, type ):
    hex_report = report.encode("hex")

    slicedefs = type[1]
    for slicedef in slicedefs:
      sta = int(slicedef[0])
      end = int(slicedef[1])
      funcname = slicedef[2]
      slice = hex_report[ sta: end ]

      func = getattr(self,funcname)
      func( slice )
    
  def slice_BTN( self, slice ):
    rawbtd = int( slice, 16 )
    which_buttons( rawbtd )

  def slice_IRBTN( self, slice ):
    pass

  def slice_ACC( self, slice ):
    force = {
      'x': slice[0:2],
      'y': slice[2:4],
      'z': slice[4:6]
    }

    process_force(force)

  def slice_IR( self, slice ):
    dots = [
      [ slice[0:2], slice[2:4], slice[4:6] ],
      [ slice[6:8], slice[8:10], slice[10:12] ]
    ]

    IRPointer.process_dots(dots)

  def slice_STAT( self, slice ):
    stat = bf( B_dec( slice ) )
    s = {}
    s['attachment'] = stat[1]
    s['continuous'] = stat[3]
    s['leds'] = stat[4:8]
    process_stats( s )

  def slice_BAT( self, slice ):
    bat = B_dec( slice )
    process_bat( bat )

  def ev_ATTACH_CHECK( self, slice ):
    if not REQ20H:
      send_command(hex2s(commandcodes['accept_attachment']))

REQ20H = 0

def B_dec( byte ):
  """Decode byte from two hex chars"""
  d = int(ord( byte.decode("hex") ))
  return d
    
def process_stats( s ):
  pass

def process_bat( b ):
  pass

def update_button_states(btps):
  bts_up = []
  bts_down = []

  for bt in buttonstates:
    oldbuttonstates[bt] = buttonstates[bt]
    buttonstates[bt] = 0

  for bt in btps:
    buttonstates[bt] = 1
 
  for bt in oldbuttonstates:
    if oldbuttonstates[bt] and not buttonstates[bt]:
      bt_up(bt)
      bts_up.append(bt)
    if not oldbuttonstates[bt] and buttonstates[bt]:
      bt_down(bt)
      bts_down.append(bt)
  
  if bts_down:
    log(LOG_BTN, "Buttons down: " + str(bts_down))
  if bts_up:
    log(LOG_BTN, "Buttons up: " + str(bts_up))

def which_buttons(rawbtd):
  btps = []

  if rawbtd != 0:
    for bt in buttonmap:
      btk = buttonmap[bt]
      if btk & rawbtd:
        btps.append(bt)

  update_button_states( btps )

def bt_down( bt ):
  command = copy( commandMap[bt] )
  command.append( "DOWN" )
  send_command_code( command )
  time.sleep(0.1)

def bt_up( bt ):
  command = copy( commandMap[bt] )
  command.append( "UP" )
  send_command_code( command )
  time.sleep(0.1)

def send(cmd,report,data):
  c = chr(cmd) + chr(report)
  for d in data:
    c += chr(d)
  send_command( c )

def setmode(mode,cont,rmbl=0):
  aux = 0
  rmbl = 0
  if rmbl:
    aux |= 0x01
  if cont:
    aux |= 0x04
  send(CMD_SET_REPORT,RID_MODE,[aux,mode])

# size here is redundant, since we can just use len(data) if we want.
def senddata(data,offset,size): # see writing to data: [[#On-board Memory].
  of1 = offset >> 24 & 0xFF #extract offset bytes
  of2 = offset >> 16 & 0xFF
  of3 = offset >> 8 & 0xFF
  of4 = offset & 0xFF
  data2 = data + [0]*(16-len(data)) # append zeros to pad data if less than 16 bytes
  if len(data2) > 16:
    data2 = data2[:16] # crop data if we have too much
  # format is [OFFSET (BIGENDIAN),SIZE,DATA (16bytes)]
  send(CMD_SET_REPORT,RID_WMEM,[of1,of2,of3,of4,size]+data2)
	

def bt_connect(addr):
  socket['receive'] = BluetoothSocket( L2CAP )
  socket['control'] = BluetoothSocket( L2CAP )

  socket['receive'].connect( ( addr, 19 ) )
  socket['control'].connect( ( addr, 17 ) )

  if socket['receive'] and socket['control']:
    log(LOG_INFO, "We are now connected to Wiimote at address " + addr)
    return 1

def bt_disconnect():
  socket['receive'].close()
  socket['control'].close()
  log(LOG_INFO, "Disconnected")

class Mode_IR:
  def __init__( self, sequence="Ian", state="off" ):
    self.sequences = {
      'Ian': self.seq_ian,
      'Cliff': self.seq_cliff,
      'Marcan': self.seq_marcan
    }

    if self.sequences.has_key( sequence ):
      self.sequence = self.sequences[sequence]

    self.state = "off"
    if state == "on":
      self.state = "on"
      self.sequence()

  def on( self ):
    self.state = "on"
    self.sequence()

  def off( self ):
    self.state = "off"
 
  def seq_marcan( self ):
    # this seems to be the minimal code to get it to work
    setmode(MODE_ACC_IR,0)
    send(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])
    send(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])
    senddata([8],0x04B00030,1) # enable IR data out
    senddata([0x90],0x04B00006,1) # sensitivity constants (guessed, Cliff seems to have more data, but this works for me)
    senddata([0xC0],0x04B00008,1)
    senddata([0x40],0x04B0001A,1)
    senddata([IR_MODE_EXP],0x04B00033,1) # enable IR output with specified data format

  def seq_cliff( self ):
    # this is Cliff's version pythonified, probably more accurate as far as sensitivity. Works pretty much the same for me.
    setmode(MODE_ACC_IR,0)
    send(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])
    send(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])
    senddata([1],0x04B00030,1) # seems to enable the IR peripheral
    senddata([0x02, 0x00, 0x00, 0x71, 0x01, 0x00, 0xaa, 0x00, 0x64],0x04B00000,9)
    senddata([0x63, 0x03],0x04B0001A,2)
    # this seems incorrect - for FULL IR mode, we must use FULL wiimote mode (0x3e).
    # otherwise the data is probably garbled.
    senddata([IR_MODE_FULL],0x04B00033,1) 
    senddata([8],0x04B00030,1) # Enable data output. Can be specified first it seems, we don't really need to be in mode 1.

  def seq_ian( self ):
    for i in range(3): 
      setmode(MODE_ACC_IR,0)
      time.sleep(0.005)
      send(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])
      time.sleep(0.003)
      send(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])

      dataset = [
	[ 0x04B00030, 0x01 ],
	[ 0x04B00030, 0x08 ],
	[ 0x04B00006, 0x90 ],
	[ 0x04B00008, 0xC0 ],
	[ 0x04B0001A, 0x40 ],
	[ 0x04B00033, 0x33 ],
	[ 0x04B00030, 0x08 ]
      ]

      for d in dataset:
        time.sleep(0.001)
	senddata( [ d[1] ], d[0], 1 )

    time.sleep(0.05)

def start_uinput():
  uinput = os.open(UINPUT_DEV, os.O_RDWR)
  os.write(uinput, WIIMOTE_UUD);
  for i in WIIMOTE_EVBITS:
    bit = i[0]
    val = i[1]
    fcntl.ioctl(uinput, bit, val)
  fcntl.ioctl(uinput, UI_DEV_CREATE)
  return uinput

def ui_send_event(evtype, evcode, evval):
  if IO_MODES['UINPUT'] and socket['uinput']:
    STRPK_INPUT_EVENT = "LLHHi"
    evstruct = struct.pack(STRPK_INPUT_EVENT, time.time(), 0, evtype, evcode, evval)
    os.write( socket['uinput'], evstruct )

def test_uinput(reps):
  theta = 0
  for a in range(reps):
      x_rel = int(math.sin(theta) * 10)
      y_rel = int(math.cos(theta) * 10)
      theta += 0.15
      ui_send_event( EV_REL, REL_X, x_rel )
      ui_send_event( EV_REL, REL_Y, y_rel )
      ui_send_event( EV_SYN, SYN_REPORT, 0 )
      time.sleep(0.01)

def uinput_sendkey(KEY_CONST):
  log(LOG_BTN, "Send Key: %d" % KEY_CONST)
  uinput_send_keydown(KEY_CONST)
  uinput_send_keyup(KEY_CONST)

def uinput_send_keydown(KEY_CONST):
  log(LOG_BTN, "Send Key DOWN: %d" % KEY_CONST)
  ui_send_event( EV_KEY, KEY_CONST, 1 )
  ui_send_event( EV_SYN, SYN_REPORT, 0 )

def uinput_send_keyup(KEY_CONST):
  log(LOG_BTN, "Send Key UP: %d" % KEY_CONST)
  ui_send_event( EV_KEY, KEY_CONST, 0 )
  ui_send_event( EV_SYN, SYN_REPORT, 0 )

def test_uinput3():
  x_abs = random.randint(0,255)
  y_abs = random.randint(0,255)
  uinput_abs_report( x_abs, y_abs )

def uinput_abs_report( x_abs, y_abs ):
  ui_send_event( EV_ABS, ABS_X, x_abs )
  ui_send_event( EV_ABS, ABS_Y, y_abs )
  ui_send_event( EV_SYN, SYN_REPORT, 0 )
  time.sleep(0.01)

OSD = {}

def start_pyosd():
  import pyosd
  font = "-*-helvetica-medium-r-normal-*-*-250-*-*-p-*-*-*"
  OSD['p'] = pyosd.osd( font=font, offset=200, colour="#2222cc" )
  OSD['p'].set_align( pyosd.ALIGN_CENTER )

def osd_show(msg):
  if IO_MODES['PYOSD']:
    OSD['p'].display(msg)

XL = {}

def start_xlib():
  from Xlib import display

  ENV_DISPLAY = os.environ.get("DISPLAY")

  d = display.Display( ENV_DISPLAY )
  i = d.screen()

  XL['d'] = d
  XL['w'] = SCREEN_WIDTH or int( i['width_in_pixels'] )
  XL['h'] = SCREEN_HEIGHT or int( i['height_in_pixels'] )
  
def xlib_abs_report( x_abs, y_abs ):
  d = XL['d']
  d.screen().root.warp_pointer( x_abs, y_abs )
  d.sync()


ReportParser = Wiimote_Report_Parser()

def main_loop():
  while status['go']:
    data = socket['receive'].recv(1024)
    if len(data):
      ReportParser.parse( data )
      

def get_wiimote_addr():
  servs = 0
  if len(MY_WIIMOTE_ADDR):
    addr = MY_WIIMOTE_ADDR
    servs = find_wiimote_services( addr )
  if servs:
    return addr
  else:
    addr = find_willing_wiimote()
    servs = find_wiimote_services( addr )
    if servs:
      return addr
    else:
      log(DEBUG_INFO, "No luck finding Wiimote services.")
      return 0
      
WIIMOTE_UUD = get_wiimote_uinput_user_dev()
WIIMOTE_EVBITS = get_wiimote_evbits()

Vibe = Vibrator()
IR = Mode_IR()
IRPointer = IR_Pointer()

addr = get_wiimote_addr()

if addr:
  bt_connect(addr)
  send_command_code( ['leds', 'off'] )
  if IR_ENABLE:
    IR.on()
  if IO_MODES['UINPUT']:
    socket['uinput'] = start_uinput()
  if IO_MODES['XLIB']:
    start_xlib()
  if IO_MODES['PYOSD']:
    start_pyosd()
  main_loop()
  bt_disconnect()