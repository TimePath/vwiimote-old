import socket, time

TCP_TIMEOUT = 10

class Event_Driver_SEP:
  """Simple Event Protocol Driver"""

  SEP_version = "V1"
  GREETING_FIELDS = [ "SEP", "RESX", "RESY" ]
  MESSAGE_NAMES = [ "NOP", "ABS", "KEY:DOWN", "KEY:UP", "BTN:DOWN", "BTN:UP" ]

  def __init__( self ):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.settimeout( TCP_TIMEOUT )

  def connect( host, port ):
    log( LOG_INFO, "Connecting to SEP server on %s:%d" % ( host, port ) )
    self.sock.connect( host, port )
    greeting = sock.recv(128)


  def send_message( message ):
    message += "\n"
    messlen, received = sock.send(message), 0
    if messlen != len(message):
      print "Failed to send complete message"
    data = sock.recv(32)
    if data == "OK":
      return 1
    else:
      return 0
