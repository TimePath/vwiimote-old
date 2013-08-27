# -*- coding: utf-8 -*-

import common
import hashlib
import os


class WiiMote:
    """"""
    def __init__(self):
        """"""

    class Eeprom:
        """"""

        def __init__(self):
            """"""
            offset = 0x0070
            length = 0x1700
            with open('bin/eeprom.bin', 'rb') as f:
                s = os.fstat(f.fileno()).st_size
                mmap = f.read()
            if s == 0x4000:
                print("Physical EEPROM present")
            elif s == length:
                print("Virtual EEPROM present")
                offset = 0
            else:
                print("Unknown EEPROM present")

            self.eeprom = mmap[offset:][:length]
            print(("EEPROM length: " + hex(len(self.eeprom))))
            print(("EEPROM hash: " + hashlib.md5(self.eeprom).hexdigest()))

        def read(self, offset, length):
            """"""
            print(("Reading " + hex(offset) + ":" + hex(offset + length)))
            l = []
            x = -1
            if (length / 16 > 0):
                for x in range(length / 16):
                    l.append(self.eeprom[offset + x * 16:][:16])
            if length % 16 != 0:
                l.append(self.eeprom[offset + (x + 1) * 16:][:length % 16])
            return l

    eeprom = Eeprom()

    def rumble(self, rumble):
        """"""
        print(("    Rumble: " + str(rumble)))

    leds = [False, False, False, False]

    battery = 50

    report_mode = 0x30
    report_continuous = False

    def report_data(self):
        """"""
        if self.report_mode == 0x30:
            payload = self.buttons_pack()
        elif self.report_mode == 0x31:
            payload = self.buttons_pack() + self.accel_pack()
        elif self.report_mode == 0x32:
            payload = self.buttons_pack() + self.ext8_pack()
        elif self.report_mode == 0x33:
            payload = self.buttons_pack() + self.accel_pack() + self.ir12_pack()
        elif self.report_mode == 0x34:
            payload = self.buttons_pack() + self.ext19_pack()
        elif self.report_mode == 0x35:
            payload = self.buttons_pack() + self.accel_pack() + self.ext16_pack()
        elif self.report_mode == 0x36:
            payload = self.buttons_pack() + self.ir10_pack() + self.ext9_pack()
        elif self.report_mode == 0x37:
            payload = self.buttons_pack() + self.accel_pack() + self.ir10_pack() + self.ext6_pack()
        elif self.report_mode == 0x3d:
            payload = self.ext21_pack()
        elif self.report_mode == 0x3e or self.report_mode == 0x3f:
            print(("*** TODO: report_mode " + hex(self.report_mode)))
        else:
            print(("*** Unhandled report mode: " + self.report_mode))
            return 0
        return chr(0xA1) + chr(self.report_mode) + payload

    def led_unpack(self, strData):
        """"""
        l = common.unpack(strData)[4:]
        self.leds = l
        print(("    LEDs: " + str(self.leds)))

    def mode_unpack(self, strData):
        """"""
        cont = common.unpack(strData[0])
        mode = common.tonum(strData[1])
        print(("    Mode: " + hex(mode)))
        print(("    Continuous: " + str(cont[2])))
        return cont

    def buttons_pack(self):
        """"""
        left = False
        right = False
        up = False
        down = False
        plus = False
        minus = False
        a = False
        b = False
        one = False
        two = False
        home = False
        l = [
            two, one, b, a, minus,
            False, False, home,
            left, right, down, up,
            plus, False, False, False
            ]
        b = common.pack(l)
        return b

    def buttons_unpack(self, strData):
        """"""
        return common.unpack(strData)

    def write(self, payload):
        """"""
        m = common.tonum(payload[0])
        print(("    Space: " + bin(m)))
        off = common.tonum(payload[1:][:3])
        print(("    Start: " + hex(off)))
        size = common.tonum(payload[4:][:2])
        print(("    End: " + hex(off + size)))

    def read(self, payload):
        """"""
        m = common.tonum(payload[0])
        print(("    Space: " + bin(m)))
        off = common.tonum(payload[1:][:3])
        print(("    Start: " + hex(off)))
        size = common.tonum(payload[4])
        print(("    End: " + hex(off + size)))
        data = payload[5:][:size]
        print(("    Data: " + common.tohex(data)))