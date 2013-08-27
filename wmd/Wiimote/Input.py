import string
from wmd.Common import *


class bf(object):
    """"""
    def __init__(self, value=0):
        """"""
        self._d = value

    def __getitem__(self, index):
        """"""
        return (self._d >> index) & 1

    def __setitem__(self, index, value):
        """"""
        value = (value & 1) << index
        mask = 1 << index
        self._d = (self._d & ~mask) | value

    def __getslice__(self, start, end):
        """"""
        mask = 2 ** (end - start) - 1
        return (self._d >> start) & mask

    def __setslice__(self, start, end, value):
        """"""
        mask = 2 ** (end - start) - 1
        value = (value & mask) << start
        mask = mask << start
        self._d = (self._d & ~mask) | value
        return (self._d >> start) & mask

    def __int__(self):
        """"""
        return self._d


def decbyte(byte):
    """Decode byte from two hex chars"""
    d = int(ord(byte.decode("hex")))
    return d


def toHex(s):
    """"""
    l = []
    for c in s:
        h = hex(ord(c)).replace('0x', '')
        if len(h) == 1:
            h = '0' + h
        l.append(h)
    return string.join(l, " ")


def hex2s(h):
    """"""
    return  ('%x' % h).decode("hex")


class ReportParser:
    """
    Receives report packets from the Wiimote
    Classifies and then slices them
    Individually processes and dispatches the slices
    """

    ## SLICE_START and SLICE_END are in number of nibbles
    # SLICE_NAME = [ SLICE_START, SLICE_END, SLICE_HANDLER ]
    SLICE_BTN = [4, 8, "slice_BTN"]
    SLICE_ACC = [8, 14, "slice_ACC"]
    SLICE_IR = [14, 26, "slice_IR"]
    SLICE_IRBTN = [0, 0, "slice_IRBTN"]
    SLICE_STAT = [8, 10, "slice_STAT"]
    SLICE_BAT = [14, 16, "slice_BAT"]
    SLICE_READ = [8, 46, "slice_READ"]
    EV_ATTACH_CHECK = [0, 0, "ev_ATTACH_CHECK"]

    def __init__(self, ev, wmstate):
        """"""
        self.ev = ev
        self.wmstate = wmstate

        self.REPORT_TYPES = {
          4: ["BTN_ONLY",         # Button status only
               [self.SLICE_BTN]
          ],

          6: ["IR_BTN",       # Button status reports sent during IR mode allow for lower latency
               [self.SLICE_IRBTN]
          ],

          7: ["BTN_ACC",          # Buttons+accelerometers status
               [self.SLICE_BTN, self.SLICE_ACC]
          ],

          8: ["STATUS_REP",       # Status Report
               [self.SLICE_BTN, self.SLICE_STAT, self.SLICE_BAT, self.EV_ATTACH_CHECK],
          ],

          19: ["BTN_ACC_IR",        # Buttons+accelerometers+IR sensor status
               [self.SLICE_BTN, self.SLICE_ACC, self.SLICE_IR]
          ],

          23: ["MEM_READ",    # Memory read
               [self.SLICE_READ]
          ]
        }

    def parse(self, report):
        """"""
        log(DEBUG_BT_RECV, "Recv len(" + str(len(report)) + "): " + str(string.split(toHex(report), " ")))

        if len(report) in self.REPORT_TYPES:
            typ = self.REPORT_TYPES[len(report)]
            self.split_report(report, typ)
        else:
            log(LOG_ERR, "Invalid packet size: " + str(len(report)))
            if not LOG_LEVEL & DEBUG_BT_RECV:
                log(LOG_ERR, "Recv len(" + str(len(report)) + "): " + str(string.split(toHex(report), " ")))

    def split_report(self, report, typ):
        """"""
        hex_report = report.encode("hex")

        slicedefs = typ[1]
        for slicedef in slicedefs:
            sta = int(slicedef[0])
            end = int(slicedef[1])
            funcname = slicedef[2]
            slce = hex_report[sta:end]

            func = getattr(self, funcname)
            func(slce)

    def slice_BTN(self, slce):
        """"""
        rawbtd = int(slce, 16)
        self.wmstate.which_buttons(rawbtd)

    def slice_IRBTN(self, slce):
        """"""
        pass

    def slice_READ(self, slce):
        """"""
        print(slce)

    def slice_ACC(self, slce):
        """"""
        force = {
            'x': decbyte(slce[0:2]),
            'y': decbyte(slce[2:4]),
            'z': decbyte(slce[4:6])
        }

        self.ev.send(WM_ACC, force)

    def slice_IR(self, slice):
        """"""
        dots = [
            [slice[0:2], slice[2:4], slice[4:6]],
            [slice[6:8], slice[8:10], slice[10:12]]
        ]

        (pdots, dots_on) = self.preprocess_dots(dots)
        self.ev.send(WM_IR, [pdots, dots_on])

    def slice_STAT(self, slce):
        """"""
        stat = bf(decbyte(slce))
        s = {}
        s['attachment'] = stat[1]
        s['continuous'] = stat[3]
        s['leds'] = stat[4:8]
        self.process_stats(s)

    def slice_BAT(self, slce):
        """"""
        bat = decbyte(slce)
        self.process_bat(bat)

    def ev_ATTACH_CHECK(self, slce):
        """"""
        if not REQ20H:
            send_command(hex2s(commandcodes['accept_attachment']))

    def preprocess_dots(self, dots):  # Probably broken
        """
        Here, we take an hex string containing the raw bytes with information
        on the dots. We then decode this information into usable variables.
        We're going to do ugly bitfield manipulation here. It seems to be
        reliable, but I wouldn't attempt to modify it.

        Here are the variables we're going to extract for each dot:
        lx, ly:  least significant bytes of x and y
        mx, my:  most significant two bits of x and y
        x:       horizontal position
        y:       vertical position
        s:       dot intensity measurement
        v:       dot validity
        """
        dots_sum = [0, 0]
        dots_on = 0
        pdots = [[0, 0, 0, 0], [0, 0, 0, 0]]

        for dn in range(2):
            for dax in range(3):
                dotc_val = decbyte(dots[dn][dax])
                dots[dn][dax] = dotc_val
                dots_sum[dn] += dotc_val

        for dn in range(2):
          lx = dots[dn][0]
          ly = dots[dn][1]
          ib = bf( dots[dn][2] )
          s = ib[0:3]
          mx = bf( ib[4:6] )
          my = bf( ib[6:8] )
          x = bf(lx)
          y = bf(ly)
          x[8] = mx[0]
          x[9] = mx[1]
          y[8] = my[0]
          y[9] = my[1]
          pdots[dn][0] = int(x)
          pdots[dn][1] = int(y)
          if dots_sum[dn] != 255*3:
            v = 1
        dots_on += 1
        log(DEBUG_IR2, "dn = %u, lx = %u, ly = %u, mx = %u, my = %u, s = %u, v = %u, x = %u, y = %u" % (dn, lx, ly, mx, my, s, v, x, y))
        pdots[dn][2] = 1
        pdots[dn][3] = s

        if dots_on:
            return [pdots, dots_on]
        else:
            return [0, 0]

    def process_stats(s):
        """"""
        pass

    def process_bat(b):
        """"""
        pass


class WiimoteState:
    """This contains the present state of the Wiimote; buttons, battery, etc."""

    def __init__(self, ev):
        """"""
        self.ev = ev

    # These are the button mappings
    buttonmap = {
        '2': 0x0001,
        '1': 0x0002,
        'B': 0x0004,
        'A': 0x0008,
        '-': 0x0010,
        'H': 0x0080,
        'L': 0x0100,
        'R': 0x0200,
        'D': 0x0400,
        'U': 0x0800,
        '+': 0x1000
        }

    buttonstates = {}
    prevbuttonstates = {}
    for bt in buttonmap:
        buttonstates[bt] = 0
        prevbuttonstates[bt] = 0

    def which_buttons(self, rawbtd):
        """"""
        btps = []

        for bt in self.buttonmap:
            btk = self.buttonmap[bt]
            if btk & rawbtd:
                btps.append(bt)

        #if rawbtd == 0:
        #    return

        self.update_button_states(btps)

    def update_button_states(self, btps):
        """"""
        bts_up = []
        bts_down = []

        for bt in self.buttonstates:
            self.prevbuttonstates[bt] = self.buttonstates[bt]
            self.buttonstates[bt] = 0

        for bt in btps:
            self.buttonstates[bt] = 1

        for bt in self.prevbuttonstates:
            if self.prevbuttonstates[bt] and not self.buttonstates[bt]:
                self.bt_notify(bt, "UP")
                bts_up.append(bt)
            if not self.prevbuttonstates[bt] and self.buttonstates[bt]:
                self.bt_notify(bt, "DOWN")
                bts_down.append(bt)

        if bts_down:
            log(LOG_BTN, "Buttons down: " + str(bts_down))
        if bts_up:
            log(LOG_BTN, "Buttons up: " + str(bts_up))

    def bt_notify(self, bt, state):
        """"""
        self.ev.send(WM_BT, [bt, state])

    REQ20H = 0