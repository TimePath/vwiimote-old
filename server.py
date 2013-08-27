#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# http://wiibrew.org/wiki/Wiimote
from socket import *
import threading
import common
import os
import time
from wiimote import WiiMote

host = "127.0.0.1"
data_port = 9102
control_port = 9103
OUTPUT_PREFIX = 0xA2  # HID BT DATA_request (0xA0) | Report Type (Output 0x02). The wii sends this
INPUT_PREFIX = 0xA1  # HID BT DATA_request (0xA0) | Report Type (Input 0x01). The wiimote sends this
running = True

di = {
    0x11: "Set LEDs",
    0x12: "Data reporting mode",
    0x13: "IR camera enable",
    0x14: "Speaker enable",
    0x15: "Status information request",
    0x16: "Write memory",
    0x17: "Read memory",
    0x18: "Speaker data",
    0x19: "Speaker mute",
    0x1a: "IR camera enable 2",

    0x20: "Status information",
    0x21: "Return memory data",
    0x22: "ACK",

    # The wiimote sends these

    0x30: "Data 1",
    0x31: "Data 2",
    0x32: "Data 3",
    0x33: "Data 4",
    0x34: "Data 5",
    0x35: "Data 6",
    0x36: "Data 7",
    0x37: "Data 8",
    0x38: "Data 9",
    0x39: "Data 10",
    0x3a: "Data 11",
    0x3b: "Data 12",
    0x3c: "Data 13",
    0x3d: "Data 14",
    0x3e: "Data 15",
    0x3f: "Data 16"
}


class Server:
    """"""

    def listen(self, serversock, port):
        """"""
        serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serversock.bind((host, port))
        serversock.listen(1)
        while running:
            print("waiting for connection")
            sock, addr = serversock.accept()
            print("connected")
            sending = self.wm.report_data()
            print((common.tohex(sending)))
            sock.send(sending)
            time.sleep(0.001)
            while running:
                data = sock.recv(32)
                if not data:
                    break
                self.handle(data[0], data[1:])
            sock.shutdown()
            sock.close()
        serversock.close()

    def handle(self, kind, data):
        """"""
        op = ord(data[0])
        payload = data[1:]
        arrows = "<<<"
        if kind == INPUT_PREFIX:
            arrows = ">>>"
        name = "0x" + common.tohex(data[0])
        if op in di:
            name = name + " (" + di.get(op) + ")"
        print((arrows + " " + name + ": " + common.tohex(data[1:])))
        self.wm.rumble(common.unpack(payload[0])[0])
        if op == 0x11:
            self.wm.led_unpack(payload)
        elif op == 0x12:
            self.wm.mode_unpack(payload)
        elif op == 0x16:
            self.wm.write(payload)

    def __init__(self):
        """"""
        self.wm = WiiMote()
        data_sock = socket(AF_INET, SOCK_STREAM)
        data_thread = threading.Thread(target=self.listen, args=(data_sock, data_port))
        data_thread.daemon = False
        control_sock = socket(AF_INET, SOCK_STREAM)
        control_thread = threading.Thread(target=self.listen, args=(control_sock, control_port))
        control_thread.daemon = False
        data_thread.start()
        control_thread.start()
        try:
            while True:
                time.sleep(6)
        except KeyboardInterrupt:
            print("")
            print("Exiting...")
            data_sock.close()
            control_sock.close()
            os._exit(0)

if __name__ == '__main__':
    wmd = Server()