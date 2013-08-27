#!/usr/bin/python
#
# wiimote.py - Wii Remote data inspector. This will be used as a learning
# framework until we have enough data to write an actual wiimote driver.
#
# Copyright (C) 2007 Will Woods <wwoods@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# requires pybluez - http://org.csail.mit.edu/pybluez/

import bluetooth
import os
import sys
import math
import time
import fcntl,struct
from time import strftime,localtime
from logging import debug

def i2bs(x):
    '''Convert a (32-bit) int to a list of 4 byte values, e.g.
    i2bs(0xdeadbeef) = [222,173,190,239]
    12bs(0x4)        = [0,0,0,4]'''
    out=[]
    while x or len(out) < 4:
        out = [x & 0xff] + out
        x = x >> 8
    return out 

class WiiDiscoverer(bluetooth.DeviceDiscoverer):
    def __init__(self,maxdevs=1):
        bluetooth.DeviceDiscoverer.__init__(self) # init parent
        self.wiimotes = []
        self.done = False
        self.inprogress = False
        self.maxdevs = maxdevs 

    # We identify wiimotes by their device name at the moment
    def device_discovered(self, address,device_class, name):
        if not name:
            name = bluetooth.lookup_name(address)

        if name.startswith('Nintendo RVL-CNT'):
            debug("Found wiimote at address %s" % address)
            w=Wiimote(address,len(self.wiimotes))
            self.wiimotes.append(w)
            if len(self.wiimotes) == self.maxdevs:
                self.done = True 

    def pre_inquiry(self):
        self.inprogress = True 

    def inquiry_complete(self):
        self.inprogress = False
        self.done = True 

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
    '+': 0x1000,
} 

# BLUH. These should be less C-ish.
CMD_SET_REPORT = 0x52 
RID_LEDS = 0x11
RID_MODE = 0x12
RID_IR_EN = 0x13
RID_SPK_EN = 0x14
RID_STATUS = 0x15
RID_WMEM = 0x16
RID_RMEM = 0x17
RID_SPK = 0x18
RID_SPK_MUTE = 0x19
RID_IR_EN2 = 0x1a 
MODE_BASIC = 0x30
MODE_ACC = 0x31
MODE_IR = 0x32
MODE_FULL = 0x3e 
IR_MODE_OFF =  0
IR_MODE_STD =  1
IR_MODE_EXP =  3
IR_MODE_FULL = 5 
FEATURE_DISABLE = 0x00
FEATURE_ENABLE = 0x04 

# Max value for IR dots
DOT_MAX = 0x3ff  

def rotate(x,y,theta):
    '''Rotates the given (x,y) coordinates by theta radians around the center
    of the dots' view'''

    # Translate dot values so the center is (0,0)
    c=(DOT_MAX/2)
    x = c - x
    y = c - y

    # rotate about the center
    xprime = x*math.cos(theta) - y*math.sin(theta)
    yprime = x*math.sin(theta) + y*math.cos(theta)

    # now retranslate
    xprime = xprime + c
    yprime = yprime + c

    return (int(xprime),int(yprime)) 

class Wiimote(object):
    def __init__(self,addr,number=0):
        self.connected=False
        self.done=False
        self.addr=addr
        self.number=number
        self.mode       = 0
        self.ledmask    = 0
        self.buttonmask = 0 
        self.force      = [0,0,0]
        self.force_zero = [0,0,0]
        self.force_1g   = [0,0,0]
        self.force_1g_diff = [0,0,0] # Difference between zero and 1g
        self.theta_g    = 0.0 # Angle of the remote with respect to gravity,
                              # calculated from the z-axis force. In radians.

        self.theta_g_x  = 0.0 # Same, but calculated from x-axis. 
        self.dots       = [(DOT_MAX,DOT_MAX),(DOT_MAX,DOT_MAX)]
        self.theta      = 0.0 # dots' angle (again, in rad) from horizontal
        self.dotlist    = []  # a fifo queue of recent dots
        self.maxdots    = 10  # max length for dotlist
        self.pointer = [0,0]  # Location of pointer. range is (0,DOT_MAX) 
        self.rx = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.cx = bluetooth.BluetoothSocket(bluetooth.L2CAP)

    def connect(self):
        debug("Attaching to Wiimote #%i at %s", self.number+1, self.addr)
        self.rx.connect((self.addr,19))
        self.cx.connect((self.addr,17))
        self.setled(self.number)
        self.connected=True

    def disconnect(self):
        debug("Disconnecting from Wiimote #%i", self.number+1)
        self.cx.close()
        self.rx.close()
        self.connected=False

    def mainloop(self):
        debug("Receiving data from Wiimote #%i", self.number+1)

        while not self.done:
            self._getpacket()
            debug("time %f force= %s %s ", time.time(),self.force_str(),self.buttons_str())

    def _handle_button_data(self,data):
        if len(data) != 4: 
            return False

        # XXX: what's byte 1 for?
        newmask = (ord(data[2])<<8) + ord(data[3])

        # TODO: check newmask against current mask and send events?
        if newmask & buttonmap['H'] and not self.buttonmask & buttonmap['H']:
            debug("Re-enabling IR")
            self.enable_IR()

        self.buttonmask = newmask

    def _handle_force_data(self,data):
        if len(data) != 3: 
            return False

        self.force = [ord(d) for d in data]
        return True

    def _handle_IR_data(self,data):
        if len(data) != 6: 
            return False

        if data ==' \xff' * 6:
            self.dots=[(DOT_MAX,DOT_MAX),(DOT_MAX,DOT_MAX)]
        else:
            a,b,c,d,e,f = [ord(d) for d in data]
            # processing dots:
            # each tuple is 3 bytes in the form: x,y,extra
            # extra contains 8 bits of extra data as follows: [yyxxssss]
            # x and y are the high two bits for the full 10-bit x/y values.
            # s is some unknown info (size data?)
            x1=a+((c & 0x30) << 4)
            y1=b+((c & 0xc0) << 2)
            x2=d+((f & 0x30) << 4)
            y2=e+((f & 0xc0) << 2)
            self.dots=[(x1,y1),(x2,y2)]
            self.dotlist.insert(0,self.dots)
            
            if len(self.dotlist) > self.maxdots:
                self.dotlist.pop()
        return True

    def _getpacket(self):
        data=self.rx.recv(1024)
        
        if len(data) == 4:    # button
            self._handle_button_data(data)
            
        elif len(data) == 7:  # button + accelerometer
            self._handle_button_data(data[0:4])
            self._handle_force_data(data[4:7])

        elif len(data) == 19: # button + accel + IR
            self._handle_button_data(data[0:4])
            self._handle_force_data(data[4:7])
            self._handle_IR_data(data[7:13])
            # I think the extra data is emitted if we see more than two dots
            extradata = data[13:19]
            if extradata != "\xff"*len(extradata):
                debug("Interesting extradata: %s\n", extradata.encode("hex"))

        elif len(data) == 0:  # Wiimote went away!
            debug("Lost wiimote #%i",  self.number+1)
            self.done = True
        else:
            debug("Unknown packet len %i: 0x%s" , len(data), data.encode("hex"))

    def setled(self, num):
        debug("setled(%i)", num)

        if num < 4:
            self.ledmask = self.ledmask | (0x10 << num)
            self._led_command()

    def clearled(self,num):
        debug("clearled(%i)", num)

        if num < 4:
            self.ledmask = self.ledmask & ~(0x10 << num)
            self._led_command()

    def buttons_str(self):
        buttonlist='+UDLRH-AB12'
        out=''
        for c in buttonlist:
            if not self.buttonmask & buttonmap[c]:
                c = '.'
            out = out + c
        return out

    def force_gx(self):
        return (self.force[0]-self.force_zero[0])
       
    def force_gy(self):
        return (self.force[1]-self.force_zero[1])
       
    def force_gz(self):
        return (self.force[2]-self.force_zero[2])

    def force_str(self):
        return "% 4i,% 4i,% 4i" % (self.force_gx(), self.force_gy(), self.force_gz())

    def dots_str(self):
        (a,b),(c,d) = self.dots
        return "((%4i,%4i),(%4i,%4i))" % (a,b,c,d)

    def setmode(self,mode):
        self.mode = mode
        # XXX wiimotulator.py has flags for setting 0x01 in the first byte for
        # 'rmbl' and 0x04 for 'cont'. Both of these are always off.
        # No idea why.
        self._send_command(CMD_SET_REPORT,RID_MODE,[0,mode])

    def enable_force(self):
        self.setmode(self.mode | MODE_ACC)
        self.get_force_calibration()

    def enable_IR(self):
        self.setmode(self.mode | MODE_IR)
        self._send_command(CMD_SET_REPORT,RID_IR_EN,[FEATURE_ENABLE])
        self._send_command(CMD_SET_REPORT,RID_IR_EN2,[FEATURE_ENABLE])
        # Enable IR device
        self._write_mem(0x04b00030,[0x01])
        # Set sensitivity constants
        self._write_mem(0x04b00030,[0x08])
        self._write_mem(0x04b00006,[0x90])
        self._write_mem(0x04b00008,[0xc0])
        self._write_mem(0x04b0001a,[0x40])
        self._write_mem(0x04b00033,[0x33])
        # Enable IR data output
        self._write_mem(0x04b00030,[8])

    def get_force_calibration(self):
        data=[ord(b) for b in self._read_mem(0x16,10)]
        self.force_zero = data[0:3]
        self.force_1g   = data[4:7]
        # XXX currently we don't know what data[3], data[7], or data[8:9] are
        debug("Got force calibration data: zero=%s, 1g=%s", self.force_zero, self.force_1g)
        # Calculate the difference between zero and 1g for each axis
        for b in range(0,3):
            self.force_1g_diff[b] = self.force_1g[b] - self.force_zero[b] 

    def _led_command(self):
        self._send_command(CMD_SET_REPORT,RID_LEDS,[self.ledmask])

    def _waitforpacket(self,header,max=32):
        r=''
        n=0
        while (n<max) and not r.startswith(header):
            r = self.rx.recv(1024)
            n = n + 1
        
        debug("Leaving _waitforpacket() after %i packets",  n)
        
        if not r.startswith(header):
            return None
        else:
            return r

    def _waitforok(self):
        self._waitforpacket('\xa1\x22\x00')

    def _read_mem(self,offset,size):
        if size >= 16:
            debug("ERROR: _read_mem can't handle size > 15 yet")
            return None

        # RMEM command wants: [offset,size]
        self._send_command(CMD_SET_REPORT,RID_RMEM,i2bs(offset)+[0,size])
        data = self._waitforpacket('\xa1\x21')
        if data:
            # TODO check error flag, continuation, etc
            return data[7:]
        else:
            return None

    def _write_mem(self,offset,data):
        # WMEM command wants: [offset,size,data]
        # offset = 32-bit, bigendian. data is 0-padded to 16 bytes.
        size = len(data)
        if size > 16: 
            return False # Too much data!

        if size < 16: 
            data = data + [0]*(16-size)

        self._send_command(CMD_SET_REPORT,RID_WMEM,i2bs(offset)+[size]+data)
        self._waitforok()

    def _send_command(self,cmd,report,data):
        debug("_send_command(%#x,%#x,%s)", cmd, report, data)
        self.cx.send(chr(cmd) + chr(report) + "".join([chr(d) for d in data]))

    def calc_theta_g(self):
        '''Use the z and x accelerometer values to figure out the wiimote's
        orientation with respect to gravity.'''

        # sanity - return if we have no calibration data
        if self.force_1g[0] == 0: 
            return self.theta_g

        # rotating from face-up to upside-down, force[2] goes from
        # force_1g[2] to force_zero[2]-force_1g[2]. The normal force of
        # gravity should be force_zero-force_1g - call this 'g'.
        # It seems intuitive that this should map to a cosine wave - we start
        # at 1g for face-up, then zero for a quarter-turn, -1g for half, etc.
        zg = float(self.force[2]-self.force_zero[2])/self.force_1g_diff[2]
        # If we're seeing more than 1g, probably this data isn't reliable
        # for determining orientation, so we ignore it
        if abs(zg) <= 1.0:
            self.theta_g = math.acos(zg)
        # Do the same thing with force[0] - it goes from 0->+/-1g->0, just like
        # a sine wave
        xg = float(self.force[0]-self.force_zero[0])/self.force_1g_diff[0]
        if abs(xg) <= 1.0:
            self.theta_g_x = math.asin(xg)
        # For convenience, return theta_g
        return self.theta_g 


    def calc_pointer(self):
        '''Calculate the position of the pointer, taking into account the
        rotation of the controller.
        Sets self.theta and self.pointer; returns self.pointer.'''

        # Credit for most of the math here goes to my esteemed colleague Mike
        # (mikem@redhat.com). Finally, all those years TA-ing Calc 1 are
        # paying off!
        # One of the dots is bogus/missing. Bail out.
        # TODO: keep track of the previous dot positions and guess instead of
        # immediately bailing out?
        if (DOT_MAX, DOT_MAX) in self.dots:
            return self.pointer

        ((x1,y1),(x2,y2)) = self.dots
        # FIXME: for some reason, py never goes above ~750.
        # Might be my bogus IR emitters (half-power every 15 degrees
        # away from center! Thanks, Radio Shack.)
        # But it might also be that the IR camera is calibrated to
        # assume the sensor bar should be on the bottom of the TV.
        # Since IR calibration is still Black Magick, I am forcing
        # a scale factor for y here.
        y1 = y1 * DOT_MAX / 760
        y2 = y2 * DOT_MAX / 760 
        # Determine rotation angle. SOH CAH TOA ftw.
        if (x1 != x2):
            self.theta = math.atan(float(y2-y1)/float(x1-x2))
        else:
            self.theta = math.pi/2
            if y1 > y2:
                self.theta = -self.theta

        # If the accel. says we are upside-down, add half a turn to theta
        tg = math.degrees(self.calc_theta_g())
        if tg > 90.0:
            self.theta = self.theta+math.pi
        if tg < -90.0:
            self.theta = self.theta-math.pi
        # rotate dots around center by theta.
        (x1,y1) = rotate(x1,y1,self.theta)
        (x2,y2) = rotate(x2,y2,self.theta)
        # They should now be horizontal (y1 should be very close to y2).
        # Average the two X values (find the center between them)
        px = (x1+x2)/2
        # Horizontal means y1 = y2, so there's no need to average them.
        # In fact, let's output an error message if the rotate messed up.
        if y2 != y1:
            debug("post-rotation Y delta=%i", abs(y1-y2))
        # We do need to flip the incoming y data.
        py = DOT_MAX - y1 
        # Do some scaling - ignore the outer edges of the screen
        # FIXME: fix scaling such that the center of the wiimote image
        # maps to the top of the screen
        # Center point of the screen is (c,c)
        c = DOT_MAX/2
        maxd = 0.33 * DOT_MAX # max allowable distance from center
        # If this point is less than (maxd) from the center of the image,
        # draw it.
        if (abs(px-c) <= maxd) and (abs(py-c) <= maxd):
            # px/py are in the range [c-maxd,c+maxd]
            px = px - (c-maxd)
            py = py - (c-maxd)
            # Now they're in the range [0,2*maxd]. Scale to DOT_MAX.
            px = px * (DOT_MAX/(2*maxd))
            py = py * (DOT_MAX/(2*maxd))
            # Hooray! We did it!
            self.pointer = [int(px),int(py)]
        return self.pointer

    def pointer_str(self):
        return "(%4i,%4i)" % (self.pointer[0],self.pointer[1]) 


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s')
                    
    w=Wiimote("00:19:1D:BB:7D:28",0) 
    w.connect()
    print "Enabling accelerometer."
    w.enable_force() 
    #w.enable_IR() 
    try:
        last=time.time()
        while not w.done:
            w._getpacket()
            debug("time %f force= %s %s ", time.time(), w.force_str(), w.buttons_str())
    finally:
        w.disconnect()

