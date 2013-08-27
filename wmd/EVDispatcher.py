from wmd.EventBridges.PyXlib import EventBridge_PyXlib
from wmd.EventBridges.uinput import EventBridge_uinput
from wmd.Common import *


class EVDispatcher:
    """"""
    valid_evtypes = [  # Accept only these event types
        WM_IR, WM_ACC, WM_BT,
        UI_INFO,
        ABS_POS, SET_LED,
        EV_SHUTDOWN,
        EVBR_KEYUP, EVBR_KEYDOWN, WMDPOWER
    ]  # To create a new event type, you must add it to Common.py

    subs = {}

    def __init__(self, cf):
        """"""
        self.cf = cf
        if self.cf['IO_MODES']['XLIB']:
            self.xlib = EventBridge_PyXlib(self, cf)

        if self.cf['IO_MODES']['UINPUT']:
            self.uinput = EventBridge_uinput(self, cf)

    def send(self, evtype, payload):
        """"""
        if evtype in self.valid_evtypes:
            if evtype in self.subs:
                dests = self.subs[evtype]
                for dest in dests:
                    dest(payload)
            else:
                log(LOG_EV, "Event type %s is being ignored" % (evtype))
        else:
            log(LOG_ERR, "%s is not a valid event type" % (evtype))

    def subscribe(self, evtype, callback):
        """"""
        if evtype in self.subs:
            self.subs[evtype].append(callback)
        else:
            self.subs[evtype] = [callback]