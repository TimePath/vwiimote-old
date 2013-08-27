import time
import socket
from wmd.Common import *

TCP_TIMEOUT = 10


class WiimoteBT_DualTCP:
    """Simple Dual TCP Wiimote BT Bridge"""
    def __init__(self, cf):
        """"""
        self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        self.data_sock.settimeout( TCP_TIMEOUT )
#        self.control_sock.settimeout( TCP_TIMEOUT )

    def connect(self, addr):
        """"""
        host = "127.0.0.1"
        receive_port = 9102
        control_port = 9103

        log(LOG_INFO, "Connecting to Wiimote receive server on %s:%d" % (host, receive_port))
        self.data_sock.connect((host, receive_port))

        log(LOG_INFO, "Connecting to Wiimote control server on %s:%d" % (host, control_port))
        self.control_sock.connect((host, control_port))

        return 1

    def disconnect(self):
        """"""
        self.control_sock.close()
        self.data_sock.close()

    def get_addr(self):
        """"""
        return 1

   # if MY_WIIMOTE_ADDR:
   #   return MY_WIIMOTE_ADDR
   # else:
   #   print "You must manually specify a Wiimote address"

    def receive(self):
        """"""
        data = self.data_sock.recv(32)
        return data

    def send_command(self, commandcode):
        """"""
        fs = ''
        for b in commandcode:
            fs += str(b).encode("hex").upper() + " "
        log(DEBUG_BT_SEND, "sending " + str(len(commandcode)) + " bytes: " + fs)
        self.data_sock.send(commandcode)
        time.sleep(0.001)