import time, random
from copy import deepcopy
from wmd.Common import *

# These are the Wiimote control codes
FEATURE_DISABLE = 0x00
FEATURE_ENABLE = 0x04

IR_MODE_OFF = 0
IR_MODE_STD = 1
IR_MODE_EXP = 3
IR_MODE_FULL = 5

CMD_SET_REPORT = 0xA2

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

class WiimoteMode:
  def __init__( self, ev, backend ):
    self.backend = backend
    self.ir = Mode_IR( self )
    self.leds = LEDs( self, ev )
    self.vibe = Vibrator( self, ev )

  def send( self, cmd, report, data ):
    c = chr(cmd) + chr(report)
    for d in data:
      c += chr(d)
    self.send_command( c )

  def setmode( self, mode, cont, rmbl=0 ):
    aux = 0
    rmbl = 0
    if rmbl:
      aux |= 0x01
    if cont:
      aux |= 0x04
    self.send(CMD_SET_REPORT,RID_MODE,[aux,mode])

  # size here is redundant, since we can just use len(data) if we want.
  def senddata( self, data, offset, size): # see writing to data: [[#On-board Memory].
    of1 = offset >> 24 & 0xFF #extract offset bytes
    of2 = offset >> 16 & 0xFF
    of3 = offset >> 8 & 0xFF
    of4 = offset & 0xFF
    data2 = data + [0]*(16-len(data)) # append zeros to pad data if less than 16 bytes
    if len(data2) > 16:
      data2 = data2[:16] # crop data if we have too much
    # format is [OFFSET (BIGENDIAN),SIZE,DATA (16bytes)]
    self.send(CMD_SET_REPORT,RID_WMEM,[of1,of2,of3,of4,size]+data2)

  def send_command( self, command ):
    self.backend.send_command( command ) 

  def read_flash( callback, addr_high, addr_low, read_len ):
    req = [ 0, 0, addr_high, addr_low, 0, read_len ]
    self.send( CMD_SET_REPORT, 0x17, req )


class LEDs:
  prevstate = [0,0,0,0]
  state = [0,0,0,0]

  def __init__( self, wiimoteMode, ev ):
    self.ev = ev
    self.wiimoteMode = wiimoteMode

    self.ev.subscribe( SET_LED, self.ev_set_led )

  def ev_set_led( self, payload ):
    led = payload[0]
    action = payload[1]

    if action == 'toggle':
      self.toggle(led)
    elif action == 'on':
      self.on(led)
    elif action == 'off':
      self.off(led)

  def send_led_command( self ):
    command_start = 0xA21100
    command_end = 0x00

    if self.wiimoteMode.vibe.state == "on":
      command_end += 1

    for i in range(3):
      if self.state[i]:
        command_end += (i+1) * 0x10

    command = hex(command_start + command_end)
    cmd = command[2:].decode("hex")

    self.wiimoteMode.send_command( cmd )

  def on( self, led ):
    if self.state[led] != 1:
      self.state[led] = 1
      self.refresh()

  def off( self, led ):
    if self.state[led] != 0:
      self.state[led] = 0
      self.refresh()

  def toggle( self, led ):
    if self.state[led] == 0:
      self.on( led )
    elif self.state[led] == 1:
      self.off( led )

  def refresh( self ):
    self.send_led_command()


class Vibrator:
  """OH YEAH"""

  state = "off" 

  def __init__( self, wiimoteMode, ev ):
    self.wiimoteMode = wiimoteMode
    self.ev = ev

  def on( self ):
    if self.state != "on":
      self.cmd_on()
      self.state = "on"

  def off( self ):
      self.cmd_off()
      self.state = "off"

  def toggle( self ):
    if self.state == "on":
      self.off()
    else:
      self.on()

  def cmd_on( self ):
    self.wiimoteMode.send_command(hex2s(commandcodes['vibrate_on']))

  def cmd_off( self ):
    self.wiimoteMode.send_command(hex2s(commandcodes['vibrate_off']))


# These are commands for the wiimote
commandcodes = {
  "vibrate_on": 0xA21305,
  "vibrate_off": 0xA21304,
#  "forcerep_on": 0xA2120431,
#  "forcerep_off": 0xA2120030,
  "leds_off": 0xA21100,
  "accept_attachment": 0xA2120033,
  'request_0x20_report': 0xA21504
}

class Mode_IR:
  def __init__( self, wiimoteMode, sequence="Ian", state="off" ):
    self.sequences = {
      'Ian': self.seq_ian,
      'Cliff': self.seq_cliff,
      'Marcan': self.seq_marcan
    }
    
    self.send = wiimoteMode.send
    self.senddata = wiimoteMode.senddata
    self.setmode = wiimoteMode.setmode

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
    self.setmode(MODE_ACC_IR,0)
    self.send(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])
    self.send(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])
    self.senddata([8],0x04B00030,1) # enable IR data out
    self.senddata([0x90],0x04B00006,1) # sensitivity constants (guessed, Cliff seems to have more data, but this works for me)
    self.senddata([0xC0],0x04B00008,1)
    self.senddata([0x40],0x04B0001A,1)
    self.senddata([IR_MODE_EXP],0x04B00033,1) # enable IR output with specified data format

  def seq_cliff( self ):
    # this is Cliff's version pythonified, probably more accurate as far as sensitivity. Works pretty much the same for me.
    self.setmode(MODE_ACC_IR,0)
    self.send(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])
    self.send(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])
    self.senddata([1],0x04B00030,1) # seems to enable the IR peripheral
    self.senddata([0x02, 0x00, 0x00, 0x71, 0x01, 0x00, 0xaa, 0x00, 0x64],0x04B00000,9)
    self.senddata([0x63, 0x03],0x04B0001A,2)
    # this seems incorrect - for FULL IR mode, we must use FULL wiimote mode (0x3e).
    # otherwise the data is probably garbled.
    self.senddata([IR_MODE_FULL],0x04B00033,1) 
    self.senddata([8],0x04B00030,1) # Enable data output. Can be specified first it seems, we don't really need to be in mode 1.

  def seq_ian( self ):
    for i in range(2): 
      self.setmode(MODE_ACC_IR,0)
      time.sleep(0.005)
      self.send(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])
      time.sleep(0.003)
      self.send(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])

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
	self.senddata( [ d[1] ], d[0], 1 )

    time.sleep(0.05)


