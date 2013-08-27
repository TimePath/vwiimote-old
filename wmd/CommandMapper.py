from wmd.Common import *
import time
from wmd.EventBridges.uinputKeymap import *


# This maps button presses (and possibly other event types, if we subscribe to them as well) to
# commands defined in the config file
class CommandMapper:
    """"""
    valid_commands = ['quit', 'key', 'click', 'WMDPower']

    def __init__(self, cf, ev):
        """"""
        self.cf = cf
        self.ev = ev
        self.cMap = self.cf['commandMap']

        self.ev.subscribe(WM_BT, self.ev_wm_bt)

    def ev_wm_bt(self, ev):
        """"""
        print("BUTTON EVENT!")
        bt = ev[0]
        state = ev[1]

        if bt in self.cMap:
            cmName = self.cMap[bt][0]
            cmParms = self.cMap[bt][1]

            if cmName in self.valid_commands:
                funcname = "do_" + cmName
                func = getattr(self, funcname)
                func(state, cmParms)
            else:
                log(LOG_ERR, "Invalid command for button")
        else:
            log(LOG_ERR, "Button doesn't exist")

    def do_quit( self, state, parms ):
        self.ev.send( UI_INFO, "BYE BYE WMD WILL EXIT IN A SECOND" )
        time.sleep(1)
        self.ev.send( EV_SHUTDOWN, '' )

    def do_key( self, state, parms ):
        keys = parms
        self.command_key( state, keys )

    def do_click( self, state, parms ):
        #click_lock['age'] = int(click_lock['duration'])
        key = parms
        self.command_key( state, key )

    def do_WMDPower( self, state, parms ):
        if parms == 'increase':
            self.ev.send( WMDPOWER, 0.2 )
        if parms == 'decrease':
            self.ev.send( WMDPOWER, -0.2 )

    def command_key( self, evtype, keyname ):
        keycodes = []

        if type(keyname) == type([]):
            for kn in keyname:
              keycodes.append( self.map_keyname( kn ) )
        else:
            keycodes.append( self.map_keyname( keyname ) )

        for kc in keycodes:
            if evtype == "DOWN":
                self.ev.send( EVBR_KEYDOWN, kc )
            elif evtype == "UP":
                self.ev.send( EVBR_KEYUP, kc )

    def map_keyname( self, keyname ):
        keycode = codeMaps["EV_KEY"].toNumber( keyname )
        return keycode
