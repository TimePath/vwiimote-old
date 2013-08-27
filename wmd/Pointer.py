import math
from copy import copy
from wmd.Common import *

#constants:
XRANGE = 1024.0
YRANGE = 768.0

HYST = 0
## These influence IR pointer behaviour in unknown ways
dots_fifo = []
dots_fifo_len = 2
dots_quash = { 'duration': 2, 'age': 0 }
click_lock = { 'duration': 10, 'age': 0 }
##
##
## Ah, this here is magic, use it in combination with AUTO_IRP=OFF if you want to force a mode
#IRP_MODE = "1DM"
IRP_MODE = "HDM"
#IRP_MODE = "2DM"

DM_DOT = 0
#1DM_DOT = 1

AUTO_IRP = "ON"
#AUTO_IRP = "OFF"

# This is the threshold of dot separation at which automatic IRP MODE will switch
# Automatic IRP MODE is not very good at this time
AUTOIRP_THRESH = 430                    # 430 pixels is about 2 feet or 60 cm
#AUTOIRP_THRESH = 10370.0 / 24          # We can specify it as 24 inches
#AUTOIRP_THRESH = 26300.0 / 60          # Or as 60 centimeters

#AUTOIRP_2DMLOCK_THRESH = 220            # 220 pixels is about 4 feet or 120 cm
AUTOIRP_2DMLOCK_THRESH = 10370 / 60    # We can specify it as 48 inches
#AUTOIRP_2DMLOCK_THRESH = 26300 / 120   # Or 120 centimeters

# This dampens sudden changes of IRP mode due to a lost dot that could be reacquired soon
# It doesn't seem to be useful, but you could try raising it a little
# It'll be useful in the future I think
AUTOIRP_DAMPTHRESH = 300
# Those two are useless for now
AUTOIRP_WARNTHRESH = 150
AUTOIRP_WARNDIV = 50

# These are the smoothing thresholds
SMOOThreshes = [
  [ 10, 0.90 ],
  [ 20, 0.82 ],
  [ 35, 0.76 ],
  [ 50, 0.70 ],
  [ 70, 0.30 ],
  [ 90, 0.10 ],
]

# These are the smoothing factors for this function:
# SMOOTHING_WEIGHT = SMOO1 / ( SMOO2 + d*d*d * SMOO3 )
SMOO1 = 180
SMOO2 = 200
SMOO3 = 0.001

# This is the mixing factor for the two smoothing functions
# 1.0 will use only threshold smoothing
# 0.0 will use only function smoothing
# 0.5 will split half and half between the two
SMOOMIX = 0.5  #Min=0.0, Max=1.0



class POManager:
  """This handles data from the PixArt sensor in the WiiMote: a number of dots,
     each with x and y coordinates and intensity. We use this data to issue
     absolute coordinates positions suitable for a pointer on screen."""

  def __init__( self, cf, ev ):
    self.cf = cf
    self.ev = ev
    self.ev.subscribe( WM_IR, self.ev_wm_ir )

  dotswap_fac = 0.0
  dotswap_sen = 0.01
  dotswap_thresh = 0.5
  dotswap_max = 1.0

  def dot_swapper( self, dots, dots_on ):
    if dots_on == 2:
      if dots[0][0] < dots[1][0]:
        self.dotswap_fac += self.dotswap_sen
	if self.dotswap_fac > self.dotswap_max:
	  self.dotswap_fac = self.dotswap_max
      else:
        self.dotswap_fac -= self.dotswap_sen
	if self.dotswap_fac < 0:
	  self.dotswap_fac = 0

    if self.dotswap_fac > self.dotswap_thresh:
      dots = self.swap_dots( dots )

    return dots

  def swap_dots( self, dots ):
    tdot = copy( dots[0] )
    dots[0] = copy( dots[1] )
    dots[1] = tdot
    return dots

  def ev_wm_ir( self, payload ):
    dots = payload[0]
    dots_on = payload[1]

    if click_lock['age']:
      click_lock['age'] -= 1
      return 0

    if dots_on == 0:
      self.led_off(0)
      self.led_off(1)
      return 0

    dots = self.dot_swapper( dots, dots_on )
    abs_pos = self.abs_report_processor( dots, dots_on, 1, 0 )
    self.ev.send( ABS_POS, abs_pos )


  def abs_report_processor( self, dots, dots_on, xinv, yinv ):
    xmin = 0.0; ymin = 0.0
    xrangec = 0.0; yrangec = 0.0
    xdz = self.cf['XDZ']; ydz = self.cf['YDZ']

    if dots_on == 2:
      (d, dx, dy) = self.calc_distance( dots )
      self.upd_distlog( d, dx, dy )
    elif dots_on == 1:
      (d, dx, dy) = self.guess_distance( )
      active_dot = self.get_active_dot( dots )

    processing_mode = self.pick_processing_mode( dots, dots_on, d )
    self.set_mode_leds( processing_mode, dots_on )

    if processing_mode == "1DM":
      if DM_DOT == 0:
        dots[1] = dots[0]
      elif DM_DOT == 1:
        dots[0] = dots[1]

    elif processing_mode == "HDM":
      xmin = dx/2; ymin = dy/2
      xrangec = dx; yrangec = dy
      if dots_on == 1:
        if active_dot == 0:
	  dots[1] = self.hdm_guess_dot(dots[0], dx, dy)
	elif active_dot == 1:
	  dots[0] = self.hdm_guess_dot(dots[1], -dx, -dy)

    elif processing_mode == "2DM":
      xdz = dx / XRANGE + xdz
      ydz = dy / YRANGE + ydz

    ndots = self.norm_dots( dots, xmin, XRANGE+xrangec, ymin, YRANGE+yrangec )

    rx = self.avg_dotax ( ndots[0][0], ndots[1][0]  )
    nx = self.norm_seq  ( rx, xdz, xinv )

    ry = self.avg_dotax ( ndots[0][1], ndots[1][1]  )
    ny = self.norm_seq  ( ry, ydz, yinv )

    (sx, sy) = self.abs_smoothen( nx, ny )

    log(LOG_IR, "on: %u, d0=(%u, %u), d1=(%u, %u) dis=(%u, %u), a=(%u, %u), s=(%u, %u), dsf=%.2f" % (dots_on, dots[0][0], dots[0][1], dots[1][0], dots[1][1], dx, dy, rx, ry, sx, sy, self.dotswap_fac) )
    log(LOG_IR, "averaged and smoothened to " + str(sx) + ", " + str(sy) )

    return [sx, sy]

  screenx = 0
  screeny = 0

  irp_mode = IRP_MODE
  irp_m_damping_counter = 0
  autoirp_warndiv = AUTOIRP_WARNDIV
  distlog = []
  distlog_len = 200
  hdm_lock = 0

  hdm_blink_freq = 100
  hdm_blink_count = 0
  hdm_blink_len = -5


  def set_mode_leds( self, mode, dots_on ):
    if mode == "1DM":
      self.led_on(0)
      self.led_off(1)
    elif mode == "2DM":
      self.led_on(0)
      self.led_on(1)
    elif mode == "HDM":
      if self.hdm_blink_count < self.hdm_blink_len:
	self.hdm_blink_count = self.hdm_blink_freq

      if dots_on == 1:
        if self.hdm_blink_count <= 0:
          self.led_on(0)
	  self.led_off(1)
	else:
          self.led_off(0)
          self.led_on(1)

      elif dots_on == 2:
        if self.hdm_blink_count <= 0:
          self.led_off(0)
	  self.led_off(1)
	else:
          self.led_on(0)
          self.led_on(1)

      self.hdm_blink_count -= 1

  def norm_dots( self, dots, xmin, xrange, ymin, yrange ):
    ndots = [ [0,0], [0,0] ]
    ndots[0][0] = self.abs_norm_axis( dots[0][0], xmin, xrange )
    ndots[0][1] = self.abs_norm_axis( dots[0][1], ymin, yrange )
    ndots[1][0] = self.abs_norm_axis( dots[1][0], xmin, xrange )
    ndots[1][1] = self.abs_norm_axis( dots[1][1], ymin, yrange )
    return ndots

  def hdm_guess_dot( self, dot, dx, dy ):
    ndot = [0,0]
    ndot[0] = int( dot[0] - dx )
    ndot[1] = int( dot[1] - dy )
    return ndot

  def get_active_dot( self, dots ):
    if dots[0][2]:
      return 0
    elif dots[1][2]:
      return 1

  def norm_seq( self, n, dz, inv ):
    n = self.abs_dz_axis    ( n, dz          )
    n = self.abs_inv_axis   ( n, inv         )
    return n

  def avg_dotax( self, p1, p2 ):
    p = ( p1 + p2 ) / 2
    return p

  def guess_distance( self ):
    gd = 0.0; gdx = 0.0; gdy = 0.0
    for dl in self.distlog:
      gd += dl[0]
      gdx += dl[1]
      gdy += dl[2]
    gd /= self.distlog_len
    gdx /= self.distlog_len
    gdy /= self.distlog_len
    return [gd, gdx, gdy]

  def upd_distlog( self, d, dx, dy ):
    if len(self.distlog) > self.distlog_len:
      self.distlog.pop(0)
    self.distlog.append( [d, dx, dy] )

  def calc_distance( self, dots ):
    dx = abs( dots[0][0] - dots[1][0] )
    dy = abs( dots[0][1] - dots[1][1] )
    d = math.sqrt( dx*dx + dy*dy )
    return [d, dx, dy]

  def pick_processing_mode( self, dots, dots_on, d ):
    if AUTO_IRP != "ON":
      return IRP_MODE

    irp_mode = "HDM"

    # It must be dampened but only in the Z-axis!
    # The X axis is the dot picking in 2DM

    # GUESS_DX is most important

    if d < AUTOIRP_2DMLOCK_THRESH:
      irp_mode = "2DM"
    elif d > AUTOIRP_THRESH:
      # Here I should calculate which dot is closest to the center
      irp_mode = "1DM"

    # Apparently the damping mode is rather useless
    if irp_mode != self.irp_mode:
      self.irp_m_damping_counter += 1.0
      if self.irp_m_damping_counter > AUTOIRP_DAMPTHRESH:
#        log(LOG_IR, "Mode switch to " + irp_mode + " at d=%u, x2=%u, y2=%u" % (d,x2,y2) )
#	log(LOG_INFO, "AUTO_IRP mode: " + irp_mode + " at d=" + str(int(26300.0/d)) + "cm" )
        self.ev.send( UI_INFO, "AUTO_IRP mode: " + irp_mode )
        self.irp_mode = irp_mode
	return irp_mode
      elif self.irp_m_damping_counter > AUTOIRP_WARNDIV:
        if self.autoirp_warndiv == 0:
	  self.autoirp_warndiv = AUTOIRP_WARNDIV
	  self.autoirp_warning(self.irp_mode, irp_mode)
	else:
	  self.autoirp_warndiv -= 1
    elif self.irp_m_damping_counter > 0:
      self.irp_m_damping_counter -= 1.0

    return self.irp_mode

  def led_on( self, led ):
    self.ev.send( SET_LED, [ led, 'on' ] )

  def led_off( self, led ):
    self.ev.send( SET_LED, [ led, 'off' ] )

  def autoirp_warning( self, nm, om ):
    self.led_on(2)
    self.led_off(3)
    self.ev.send( UI_INFO, "Imminent IRP change from %s to %s" % (nm, om) )
    #Vibe.plm( pulses=1, length=0.05 )

  def abs_smoothen( self, x, y ):
    (d, dx, dy) = self.calc_distance( [ [x,y],
					[self.screenx, self.screeny] ] )

    sx = x
    sy = y

    for thresh in SMOOThreshes:
      dMin = thresh[0]
      if d < dMin:
        Wei1 = thresh[1]
	Wei2 = SMOO1 / ( SMOO2 + d*d*d* SMOO3 )

        Wei = ( Wei1 * SMOOMIX ) + (Wei2 * ( 1.0-SMOOMIX ) )
        sx = ( self.screenx * Wei ) + ( x * (1-Wei) )
	sy = ( self.screeny * Wei  ) + ( y * (1-Wei) )
	break

    self.screenx = sx
    self.screeny = sy

    return [sx, sy]

  def abs_norm_axis( self, rp, min, range ):
    rp += min
    np = rp/range
    return np

  def abs_dz_axis( self, sp, dz ):
    nsp = sp*(1+dz) - (dz/2)
    if nsp < 0:
      nsp = 0
    elif nsp > 1:
      nsp = 1
    return nsp

  def abs_inv_axis( self, sp, inv ):
    nsp = sp
    if inv:
      nsp = 1.0 - sp
    return nsp


