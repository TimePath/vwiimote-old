from wmd.UI.Logger import *

UI_INFO = "UI_INFO"

UI_INFO_CONNECTED = [UI_INFO, "CONNECTED"]
UI_INFO_CONNECTING = [UI_INFO, "CONNECTING"]

WM_IR = "WM_IR"    # self.ev.send( WM_IR, [pdots, dots_on] )
WM_ACC = "WM_ACC"  # Accelerometer data, { 'x':x, 'y':y, 'z':z }
WM_BT = "WM_BT"    # Button press, [bt, state] where state in ['UP', 'DOWN']

ABS_POS = "ABS_POS"  # [sx, sy]

SET_LED = "SET_LED"  # on|off|toggle, led

EV_SHUTDOWN = "EV_SHUTDOWN"  # Time to quit!

EVBR_KEYUP = "EVBR_KEYUP"      # Send keyup to event bridge
EVBR_KEYDOWN = "EVBR_KEYDOWN"  # Send keydown ...

WMDPOWER = "WMDPOWER"
