#from wmd.Wiimote.Backends.PyBlueZ import WiimoteBT_PyBlueZ
from wmd.Wiimote.Backends.DualTCP import WiimoteBT_DualTCP
from wmd.Wiimote.Input import ReportParser, WiimoteState
from wmd.Wiimote.Output import WiimoteMode
from wmd.Common import *


class WMManager:
    """"""
    go = 1

    def __init__(self, cf, ev):
        """"""
        self.cf = cf
        self.ev = ev

        self.wmstate = WiimoteState(self.ev)
        self.parser = ReportParser(self.ev, self.wmstate)
        self.ev.subscribe(EV_SHUTDOWN, self.ev_shutdown)

    def connect(self):
        """"""
    #    self.backend = WiimoteBT_PyBlueZ(self.cf)
        self.backend = WiimoteBT_DualTCP(self.cf)
        self.ev.send(*UI_INFO_CONNECTING)

        addr = self.backend.get_addr()

        if addr and self.backend.connect(addr):
            self.mode = WiimoteMode(self.ev, self.backend)
            self.mode.leds.toggle(0)

            self.ev.send(*UI_INFO_CONNECTED)
            return 1

    def setup(self):
        """"""
        self.mode.ir.on()
        return 1

    def main_loop(self):
        """"""
        cycles = 0

        while self.go:
            data = self.backend.receive()
            if len(data):
                self.parser.parse(data)
            cycles += 1

        return cycles

    def disconnect(self):
        """"""
        self.backend.disconnect()

    def ev_shutdown(self, null):
        """"""
        self.go = 0

    #      led_on(3)
    #      start_time = time.time()
    #      read_flash(1, 0, 0x16, 8)
    #      cycles = main_loop()
    #      end_time = time.time()
    #      WiimoteBT.disconnect()