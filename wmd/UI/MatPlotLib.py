from Guess import *

class Plotter:

  skiplen = 10 
  skipcount = 0
  ok = 0

  def __init__( self, disable ):
    if not disable:
      self.try_import()

    if self.ok:
      self.start_display()

  def start_display( self ):
    self.pylab.ion()  
    self.mode = 'live'

    fig = self.pylab.figure(1)
    ax = self.pylab.subplot(111)
    ind = self.pylab.arange(1,4)
    px, py, pz = self.pylab.bar(ind, [128,128,128])
    centers = ind + 0.5*px.get_width()
    px.set_facecolor('r')
    py.set_facecolor('g')
    pz.set_facecolor('b')
    ax.set_xlim([0.5,4])
    ax.set_xticks(centers)
    ax.set_ylim([0,255])
    ax.set_xticklabels(['X', 'Y', 'Z'])
    ax.set_ylabel('Value')
    ax.set_title('WMDAccelerometer')

    self.px = px
    self.py = py
    self.pz = pz
    self.ax = ax
    
    self.update(128,128,128)

  def try_import( self ):
    try:
      import pylab
      self.ok = 1
      self.pylab = pylab
    except:
      log(LOG_ERR, "Could not import pylab. Set DISABLE_PYLAB=1")
      self.ok = 0

  def update( self, x, y, z ):
    if not self.ok or self.mode == 'plot':
      return 0

    if self.skipcount == 0:
      self.skipcount = self.skiplen
    else:
      self.skipcount -= 1 
      return 0

    self.px.set_height(x)
    self.py.set_height(y)
    self.pz.set_height(z)
    self.ax.set_ylim([0,255])

    #orien = guess_orientation( force_log )
    orien = "b0rked"
    self.ax.set_title('WMDAccelerometer - orientation %s' % orien )

    self.pylab.draw()

  def OSDHack( self, message ):
    if self.ok:
      self.ax.set_title( "WMD OSD: " + str(message) )

  def plot( self, data ):
#    for i in data:
#      for j in data[i]:
      
    self.pylab.clf()
#    self.pylab.cla()

    xd = []
    yd = []
    zd = []

    for d in data:
      xd.append( d['x'] )
      yd.append( d['y'] )
      zd.append( d['z'] )
      
    self.pylab.plot( zd )
    self.pylab.plot( yd )
    self.pylab.plot( xd )

    self.mode = 'plot'

    self.pylab.draw()


