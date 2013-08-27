#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import gi
from gi.repository import Gtk, Gdk, GObject
import sys


BORDER_WIDTH = 5
PIXMAP_SIZE = 22
STAR_PIXMAP = ["22 22 77 1",
"     c None",
".    c #626260",
"+    c #5E5F5C",
"@    c #636461",
"#    c #949492",
"$    c #62625F",
"%    c #6E6E6B",
"&    c #AEAEAC",
"*    c #757673",
"=    c #61625F",
"-    c #9C9C9B",
";    c #ACACAB",
">    c #9F9F9E",
",    c #61635F",
"'    c #656663",
")    c #A5A5A4",
"!    c #ADADAB",
"~    c #646562",
"{    c #61615F",
"]    c #6C6D6A",
"^    c #797977",
"/    c #868684",
"(    c #A0A19E",
"_    c #AAAAA8",
":    c #A3A3A2",
"<    c #AAAAA7",
"[    c #9F9F9F",
"}    c #888887",
"|    c #7E7E7C",
"1    c #6C6C69",
"2    c #626360",
"3    c #A5A5A3",
"4    c #ABABAA",
"5    c #A9A9A7",
"6    c #A2A2A1",
"7    c #A3A3A1",
"8    c #A7A7A6",
"9    c #A8A8A6",
"0    c #686866",
"a    c #A4A4A2",
"b    c #A4A4A3",
"c    c #A1A19F",
"d    c #9D9D9C",
"e    c #9D9D9B",
"f    c #A7A7A5",
"g    c #666664",
"h    c #A1A1A0",
"i    c #9E9E9D",
"j    c #646461",
"k    c #A6A6A4",
"l    c #A0A09F",
"m    c #9F9F9D",
"n    c #A9A9A8",
"o    c #A0A09E",
"p    c #9B9B9A",
"q    c #ACACAA",
"r    c #60615E",
"s    c #ADADAC",
"t    c #A2A2A0",
"u    c #A8A8A7",
"v    c #6E6F6C",
"w    c #787976",
"x    c #969695",
"y    c #8B8B8A",
"z    c #91918F",
"A    c #71716E",
"B    c #636360",
"C    c #686966",
"D    c #999997",
"E    c #71716F",
"F    c #61615E",
"G    c #6C6C6A",
"H    c #616260",
"I    c #5F605E",
"J    c #5D5E5B",
"K    c #565654",
"L    c #5F5F5D",
"                      ",
"                      ",
"          .           ",
"          +           ",
"         @#$          ",
"         %&*          ",
"        =-;>,         ",
"        ';)!'         ",
"  ~{{]^/(_:<[}|*1@,   ",
"   23&4_5367895&80    ",
"    2a4b:7c>def)g     ",
"     2c4:h>id56j      ",
"      {k8lmeln2       ",
"      j8bmoppqr       ",
"      {stusnd4v       ",
"      ws;x@yq;/       ",
"      zfAB {CmD{      ",
"     rE{     FGH      ",
"     IJ       KL      ",
"                      ",
"                      ",
"                      "]

class StarHScale(Gtk.Widget):
    """A horizontal Scale Widget that attempts to mimic the star
    rating scheme used in iTunes"""

    def __init__(self, max_stars=5, stars=0):
        """Initialization, numstars is the total number
        of stars that may be visible, and stars is the current
        number of stars to draw"""

        #Initialize the Widget
        GObject.GObject.__init__(self)

        self.max_stars = max_stars
        self.stars = stars

        # Init the list to blank
        self.sizes = []
        for count in range(0,self.max_stars):
            self.sizes.append((count * PIXMAP_SIZE) + BORDER_WIDTH)

    def do_realize(self):
        """Called when the widget should create all of its
        windowing resources.  We will create our Gdk.Window
        and load our star pixmap."""

        # First set an internal flag showing that we're realized
        self.realize()

        # Create a new Gdk.Window which we can draw on.
        # Also say that we want to receive exposure events
        # and button click and button press events

        #self.window = Gdk.Window(
            #self.get_parent_window(),
            #width=self.allocation.width,
            #height=self.allocation.height,
            #window_type=Gdk.WINDOW_CHILD,
            #wclass=Gdk.INPUT_OUTPUT,
            #event_mask=self.get_events() | Gdk.EventMask.EXPOSURE_MASK
                #| Gdk.EventMask.BUTTON1_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK
                #| Gdk.EventMask.POINTER_MOTION_MASK
                #| Gdk.EventMask.POINTER_MOTION_HINT_MASK)

        # Associate the Gdk.Window with ourselves, Gtk+ needs a reference
        # between the widget and the gdk window
        #self.window.set_user_data(self)

        # Attach the style to the Gdk.Window, a style contains colors and
        # GC contextes used for drawing
        #self.style.attach(self.window)

        # The default color of the background should be what
        # the style (theme engine) tells us.
        #self.style.set_background(self.window, Gtk.StateType.NORMAL)
        #self.window.move_resize(*self.allocation)

        # load the star xpm
        #self.pixmap, mask = Gdk.pixmap_create_from_xpm_d(
            #self.window
            #, self.style.bg[Gtk.StateType.NORMAL]
            #, STAR_PIXMAP)

        # self.style is a Gtk.Style object, self.style.fg_gc is
        # an array or graphic contexts used for drawing the forground
        # colours
        #self.gc = self.style.fg_gc[Gtk.StateType.NORMAL]

        self.connect("motion_notify_event", self.motion_notify_event)

    def do_unrealize(self):
        # The do_unrealized method is responsible for freeing the GDK resources
        # De-associate the window we created in do_realize with ourselves
        self.window.destroy()

    def do_size_request(self, requisition):
        """From Widget.py: The do_size_request method Gtk+ is calling
         on a widget to ask it the widget how large it wishes to be.
         It's not guaranteed that gtk+ will actually give this size
         to the widget.  So we will send gtk+ the size needed for
         the maximum amount of stars"""

        requisition.height = PIXMAP_SIZE
        requisition.width = (PIXMAP_SIZE * self.max_stars) + (BORDER_WIDTH * 2)


    def do_size_allocate(self, allocation):
        """The do_size_allocate is called by when the actual
        size is known and the widget is told how much space
        could actually be allocated Save the allocated space
        self.allocation = allocation. The following code is
        identical to the widget.py example"""

        if self.get_realized():
            self.window.move_resize(*allocation)

    def do_expose_event(self, event):
        """This is where the widget must draw itself."""

        #Draw the correct number of stars.  Each time you draw another star
        #move over by 22 pixels. which is the size of the star.
        for count in range(0,self.stars):
            self.window.draw_drawable(self.gc, self.pixmap, 0, 0
                                                , self.sizes[count]
                                                , 0,-1, -1)

    def motion_notify_event(self, widget, event):
        # if this is a hint, then let's get all the necessary
        # information, if not it's all we need.
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.get_state()

        new_stars = 0
        if (state & Gdk.ModifierType.BUTTON1_MASK):
            # loop through the sizes and see if the
            # number of stars should change
            self.check_for_new_stars(event.x)

    def do_button_press_event(self, event):
        """The button press event virtual method"""

        # make sure it was the first button
        if event.button == 1:
            #check for new stars
            self.check_for_new_stars(event.x)
        return True

    def check_for_new_stars(self, xPos):
        """This function will determin how many stars
        will be show based on an x coordinate. If the
        number of stars changes the widget will be invalidated
        and the new number drawn"""

        # loop through the sizes and see if the
        # number of stars should change
        new_stars = 0
        for size in self.sizes:
            if (xPos < size):
                # we've reached the star number
                break
            new_stars = new_stars + 1

        #set the new value
        self.set_value(new_stars)

    def set_value(self, value):
        """Sets the current number of stars that will be
        drawn.  If the number is different then the current
        number the widget will be redrawn"""

        if (value >= 0):
            if (self.stars != value):
                self.stars = value
                #check for the maximum
                if (self.stars > self.max_stars):
                    self.stars = self.max_stars
                # redraw the widget
                self.window.invalidate_rect(self.allocation,True)

    def get_value(self):
        """Get the current number of stars displayed"""

        return self.stars

    def set_max_value(self, max_value):
        """set the maximum number of stars"""

        if (self.max_stars != max_value):
            """Save the old max incase it is less then the
            current number of stars, in which case we will
            have to redraw"""

            if (max_value > 0):
                self.max_stars = max_value
                #reinit the sizes list (should really be a sperate function
                self.sizes = []
                for count in range(0,self.max_stars):
                    self.sizes.append((count * PIXMAP_SIZE) + BORDER_WIDTH)
                """do we have to change the current number of
                stars?"""
                if (self.stars > self.max_stars):
                    self.set_value(self.max_stars)

    def get_max_value(self):
        """Get the maximum number of stars that can be shown"""

        return self.max_stars

GObject.type_register(StarHScale)


class UI:
    """"""

    def __init__(self):
        """"""
        builder = Gtk.Builder()
        builder.add_from_file("ui.glade")
        builder.connect_signals(self)
        window = builder.get_object("window")
        window = Gtk.Window()
        window.resize(200, 50)
        starScale = StarHScale(10, 5)
        window.add(starScale)
        window.show_all()
        Gtk.main()

    def on_window_destroy(self, widget):
        """"""
        sys.exit(0)

if __name__ == '__main__':
    wmd = UI()