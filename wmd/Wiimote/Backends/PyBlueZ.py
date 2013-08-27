import time
from bluetooth import *
from wmd.Common import *

# This is what the Wiimote calls itself (Bluetooth Name)
WIIMOTE_NAME = "Nintendo RVL-CNT-01"

class WiimoteBT_PyBlueZ:
  def __init__( self, cf ):
    self.receive_sock = BluetoothSocket( L2CAP )
    self.control_sock = BluetoothSocket( L2CAP )
    self.cf = cf

  def connect( self, addr ):
    recv_port = 19
    ctrl_port = 17
    if self.cf['PPC64']:
      recv_port = 19 << 8
      ctrl_port = 17 << 8

    self.receive_sock.connect( ( addr, recv_port ) )
    self.control_sock.connect( ( addr, ctrl_port ) )

    if self.receive_sock and self.control_sock:
      log(LOG_INFO, "We are now connected to Wiimote at address " + addr)
      time.sleep(0.5)
      return 1

  def disconnect( self ):
    self.receive_sock.close()
    self.control_sock.close()
    log(LOG_INFO, "Disconnected")

  def send_command( self, commandcode ):
    fs = ''
    for b in commandcode:
      fs += str(b).encode("hex").upper()  + " "
    log(DEBUG_BT_SEND, "sending " + str(len (commandcode)) + " bytes: " + fs)
    self.control_sock.send( commandcode )
    time.sleep(0.001)

  def get_addr( self ):
    servs = 0
    if len(self.cf['MY_WIIMOTE_ADDR']):
      addr = self.cf['MY_WIIMOTE_ADDR']
      servs = self.find_wiimote_services( addr )
    if servs:
      return addr
    else:
      addr = self.find_willing_wiimote()
      servs = self.find_wiimote_services( addr )
      if servs:
	return addr
      else:
	log(DEBUG_INFO, "No luck finding Wiimote services.")
	return 0

  def receive( self ):
    data = self.receive_sock.recv( 1024)
    return data

  def find_willing_wiimote( self ):
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

  def find_wiimote_services( self, addr ):
    log(LOG_INFO, "Looking for Wiimote services at address " + addr)
    servs = find_service( address = addr )
    if servs:
      log(LOG_INFO, "Victory! We have found that Wiimote!")
      return servs
    if not servs:
      log(LOG_ERR, "Failure. We have not found that Wiimote.")
      return 0


