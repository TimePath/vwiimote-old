from wmd.Common import *
import struct, os, fcntl, time

from wmd.EventBridges.uinputKeymap import *

# Right now this is used only for sending key and click events
# It has the code to handle absolute mouse position reports as well, but it is deactivated
# To reactivate it, one would need to use self.ev.subscribe for ABS_POS events

class EventBridge_uinput:
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

  def test_ppc64( self ):
    if self.cf['PPC64']:
      self.UI_DEV_CREATE  = 0x20005501
      self.UI_DEV_DESTROY = 0x20005502
      self.UI_SET_EVBIT   = 0x80045564
      self.UI_SET_KEYBIT  = 0x80045565
      self.UI_SET_RELBIT  = 0x80045566
      self.UI_SET_ABSBIT  = 0x80045567

  def __init__( self, ev, cf ):
    self.cf = cf
    self.ev = ev
    self.test_ppc64()

    WIIMOTE_UUD = self.get_user_dev()
    WIIMOTE_EVBITS = self.get_evbits()

    self.uinput = os.open( self.cf['UINPUT_DEV'], os.O_RDWR )
    os.write( self.uinput, WIIMOTE_UUD )

    for i in WIIMOTE_EVBITS:
      bit = i[0]
      val = i[1]
      fcntl.ioctl( self.uinput, bit, val )
    fcntl.ioctl( self.uinput, self.UI_DEV_CREATE )

    self.ev.subscribe( EVBR_KEYUP, self.send_keyup )
    self.ev.subscribe( EVBR_KEYDOWN, self.send_keydown )

  def send_event( self, evtype, evcode, evval ):
    STRPK_INPUT_EVENT = "LLHHi"
    evstruct = struct.pack(STRPK_INPUT_EVENT, time.time(), 0, evtype, evcode, evval)
    os.write( self.uinput, evstruct )

  def send_key( self, KEY_CONST ):
    log(LOG_BTN, "Send Key: %d" % KEY_CONST)
    self.send_keydown(KEY_CONST)
    self.send_keyup(KEY_CONST)

  def send_keydown( self, KEY_CONST ):
    log(LOG_BTN, "Send Key DOWN: %d" % KEY_CONST)
    self.send_event( self.EV_KEY, KEY_CONST, 1 )
    self.send_event( self.EV_SYN, self.SYN_REPORT, 0 )

  def send_keyup( self, KEY_CONST ):
    log(LOG_BTN, "Send Key UP: %d" % KEY_CONST)
    self.send_event( self.EV_KEY, KEY_CONST, 0 )
    self.send_event( self.EV_SYN, self.SYN_REPORT, 0 )

  def abs_report( self, x_abs, y_abs ):
    self.send_event( self.EV_ABS, self.ABS_X, x_abs )
    self.send_event( self.EV_ABS, self.ABS_Y, y_abs )
    self.send_event( self.EV_SYN, self.SYN_REPORT, 0 )
    time.sleep(0.01)

  def get_user_dev( self ):
    STRPK_UINPUT_USER_DEV = "80sHHHHi" + 64*4*'I' 
    WIIMOTE_UUD_STR = [
      "Nintendo Wiimote",   # Device name
      self.BUS_USB,             # Bus type
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

  def get_evbits( self ):
    UINPUT_IO_CHANNELS = []
    for ioc in self.cf['IO_CHANNELS']:
      if self.cf['IO_CHANNELS'][ioc] == 'UINPUT':
	UINPUT_IO_CHANNELS.append(ioc)

    UINPUT_UUD_BITS = {

      'EV_REL': [
	[ self.UI_SET_EVBIT, self.EV_REL ],
	[ self.UI_SET_RELBIT, self.REL_X ],
	[ self.UI_SET_RELBIT, self.REL_Y ]
      ],

      'EV_ABS': [
	[ self.UI_SET_EVBIT, self.EV_ABS ],
	[ self.UI_SET_ABSBIT, self.ABS_X ],
	[ self.UI_SET_ABSBIT, self.ABS_Y ]
      ],

      'EV_KEY': [
	[ self.UI_SET_EVBIT, self.EV_KEY ],
	[ self.UI_SET_EVBIT, self.EV_SYN ]
      ]

    }

    for btn in self.cf['commandMap']:
      com = self.cf['commandMap'][btn]
      ktype = com[0]
      if ktype == "click" or ktype == "key":
	key = com[1]

	codes = []

	if type(key) == type(codes):
	  for k in key:
	    codes.append( int(codeMaps["EV_KEY"].toNumber(k)) )
	else:
	  codes.append( int(codeMaps["EV_KEY"].toNumber(key)) )

	for kc in codes:
	  log( LOG_INFO, "Registering key %s for button %s with code %x" % (key, btn, kc) )
	  UINPUT_UUD_BITS['EV_KEY'].append( [self.UI_SET_KEYBIT, kc] )

    UINPUT_UUD = []
    for ioc in UINPUT_IO_CHANNELS:
      for bitset in UINPUT_UUD_BITS[ioc]:
	UINPUT_UUD.append(bitset)
      
    print UINPUT_UUD
    return UINPUT_UUD


