
############################################################
#######     II. BASIC CONFIGURATION: DO IT NOW     #########
##**********************************************************
##
## If you touch a line with # !!!! as a comment
## You will experience total failure # !!!!
CFG = {  # !!!!
##
## This is sensitive to syntax, so be careful with the punctuation
##
##
## This is the address of my Wiimote.
## Or, if I'm lazy, I'll just comment it out and uncomment
## An empty address: it will force autodetection:
##
#'MY_WIIMOTE_ADDR': "00:19:1D:25:16:43",
'MY_WIIMOTE_ADDR': "",
##
##
## Next, I will choose which IO Modes I want to use
## for sending keypresses, clicks, mouse movements and gestures
## *ATTENTION YOU SHOULD NOT EXPECT ANYTHING TO WORK IF YOU CHANGE IO_MODES OR IO_CHANNELS SETTINGS IN ANY WAY
'IO_MODES': {          # SET TO TRUE IF YOU HAVE:
  'UINPUT': True,      # the uinput kernel module loaded.
  'XLIB': True,        # python-xlib with the buffer overflow patch.
#  'X_EVDEV': False,    ## evdev_drv and a customized xorg.conf.
#  'PYOSD': True
},
##
##
## If I'm using IO_MODES['UINPUT'] I'll need to
## Set the path of my uinput device
##
#'UINPUT_DEV': "/dev/misc/uinput",
#UINPUT_DEV: "/dev/input/uinput",  ##ubuntu - you need to modprobe uinput first
'UINPUT_DEV': "/dev/uinput",
##
## I'll also check that I have the right UNIX rights for it
##
##
## If I changed the default IO modes
## I'll need to choose new IO channels for them
## Changing the default IO channels is risky and poorly tested
## The only channel I'd consider changing for now is 'EV_ABS' to 'X_EVDEV'
##
'IO_CHANNELS': {
  'EV_ABS': 'XLIB',
  'EV_KEY': 'UINPUT',
  'EV_REL': 'UINPUT'
},
##
##
## Now, this is the fun part, when you can assign
## Actions to Buttons
##
'commandMap': {
  'A': ['click', 'BTN_RIGHT'],  # A key: right mouse button click
  'B': ['click', 'BTN_LEFT'],   # B key: left mouse button click

  'H': ['quit', 1],                 # Home key: quits WMD

  '+': ['WMDPower', 'increase'],      # Plus key: increase WMDPower
  '-': ['WMDPower', 'decrease'],       # Minus key: decrease WMDPower

  '1': ['key', 'KEY_1'],        # 1 key: press the '1' key like a keyboard
  '2': ['key', 'KEY_2'],      # 2 key

  'U': ['key', ['KEY_LEFTCTRL']],    # Toggles LED 1
  'D': ['key', ['KEY_LEFTCTRL', 'KEY_LEFTALT', 'BTN_LEFT']],    # LED 2
  'L': ['key', ['KEY_LEFTALT']],    # LED 3
  'R': ['key', ['KEY_F8']]     # LED 4
},
##
##
## This will enable IR sensing by default
'IR_ENABLE': 1,
##

'DISABLE_PYLAB': 0,
'DISABLE_PYGAME': 0,
'DISABLE_PYOSD': 1,
##
## If you having trouble reaching the edges of your screen with the IR mouse
## You want to raise the Dead-Zone values at the most 0.50
'XDZ': 0.15,
'YDZ': 0.15,
##
##
## If for some reason WMD isn't detecting your screen size correctly
## Set these to the right values. If 0, WMD will autodetect.
'SCREEN_WIDTH': 0,
'SCREEN_HEIGHT': 0,
##
##
'PPC64': 0
}  # !!!
##
##
