import os
from wmd.Common import *

class EventBridge_PyXlib:
  def __init__( self, ev, cf ):
    try:
      from Xlib import display
    except:
      return 0

    self.ev = ev
    self.ev.subscribe( ABS_POS, self.ev_abs_pos )

    ENV_DISPLAY = os.environ.get("DISPLAY")

    self.d = display.Display( ENV_DISPLAY )
    i = self.d.screen()

    self.w = cf['SCREEN_WIDTH'] or int( i['width_in_pixels'] )
    self.h = cf['SCREEN_HEIGHT'] or int( i['height_in_pixels'] )
    
  def ev_abs_pos( self, pos ):
    x = self.w * pos[0]
    y = self.h * pos[1]

    self.d.screen().root.warp_pointer( x, y )
    self.d.sync()



