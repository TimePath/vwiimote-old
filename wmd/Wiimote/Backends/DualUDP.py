import socket
import time


class WiimoteBT_DualUDP:
    """Simple Dual UDP Wiimote BT Bridge"""
    def __init__(self, cf):
        """"""
        self.receive_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def connect(self, addr):
        """"""
        host = "127.0.0.1"
        receive_port = 9202
        control_port = 9203

        self.receive_addr = (host, receive_port)
        self.control_addr = (host, control_port)

        self.receive_sock.bind((host, receive_port))
        self.control_sock.bind((host, control_port))

        receive_dest_port = 9102
        control_dest_port = 9103

        self.receive_dest_addr = (host, receive_dest_port)
        self.control_dest_addr = (host, control_dest_port)

        cc = "0"
        self.receive_sock.sendto(cc, self.receive_dest_addr)
        self.control_sock.sendto(cc, self.control_dest_addr)

    def disconnect(self):
        """"""
        self.control_sock.close()
        self.receive_sock.close()

    def get_addr(self):
        """"""
        return 1

       # if MY_WIIMOTE_ADDR:
       #   return MY_WIIMOTE_ADDR
       # else:
       #   print "You must manually specify a Wiimote address"

    def receive(self):
        """"""
        data, addr = self.receive_sock.recvfrom(64)
        print((len(data)))
        return data

    def send_command(self, commandcode):
        """"""
        fs = ''
        for b in commandcode:
            fs += str(b).encode("hex").upper() + " "
        log(DEBUG_BT_SEND, "sending " + str(len (commandcode)) + " bytes: " + fs)
        self.control_sock.sendto(commandcode, self.control_dest_addr)
        time.sleep(0.01)