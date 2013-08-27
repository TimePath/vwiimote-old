from wmd.Common import *
import time


class Grapher:
    """"""

    # These four values sould go into the configuration file
    winheight = 640  # Window height at startup
    width = 480      # Window width at startup

    save_tga = 0   # Set this to 1 if you want to save the force log as a series of TGA files

    bgcolor = (255, 255, 255)                           # Background color for the window
    axcolors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Colors for each axis:  x,y,z
    sepcolor = (190, 190, 190)                          # Color for the separation lines
    mmcolor = (25, 25, 25)                              # Color of the min/max text

                # This is the width in number of pixels to use for every point in the graph.
    tInc = 1.5  # Increase (use value between 1-4 for best results) to have a more faster, more precise graph

    init_ignore = 10  # Number of frames to ignore completely while initializing
    init_skip = 10    # Number of frames to use for calibration, without graphing them

    blank_ahead_width = 80  # How many pixels should be blanked ahead of the new graph when redrawing?
    vsep_period = 1.0       # Draw a vertical separator every how many seconds? Set to 0 to disable

    fontheight = 20
    fontpadding = 5

    # You shouldn't have to touch these
    headerheight = 2 * (fontheight + fontpadding)
    height = winheight - headerheight

    init = init_skip + init_ignore
    ok = 0
    min = 120  # Initial calibration values
    max = 160
    t = 0     # Start graphing at the left side of the graph
    id = 0
    spf = 4  # Split factor
    prev_ui_info_rect = 0

    def __init__(self, ev):
        """"""
        self.ev = ev
        self.try_import()

        if self.ok:
            self.ev.subscribe(WM_ACC, self.ev_wm_acc)      # subscribe to wiimote force/accelerometer reports, handle with ev_wm_acc()
            self.ev.subscribe(UI_INFO, self.ev_ui_info)    # subscribe to UI_INFO messages and display them, handle with ev_ui_info()
            self.ev.subscribe(WMDPOWER, self.ev_wmdpower)  # let's use this to control graphing speed with ev_wmdpower()

            # Initialize pygame screen with selected height, width, background colour; set background colour immediately
            self.pygame.init()
            self.init_font()

            self.screen = self.pygame.display.set_mode((self.width, self.winheight), self.pygame.RESIZABLE)
            self.pygame.display.set_caption("WMD 0.1.2")
            self.screen.fill(self.bgcolor)
            self.draw_separators()
            self.pygame.display.flip()

            # Register for event processing of these event types only. However, other events still seem to get through.
            pgevlist = [self.pygame.VIDEORESIZE, self.pygame.VIDEOEXPOSE]
            self.pygame.event.set_allowed(pgevlist)

    def init_font(self):
        """"""
        if self.pygame.font:
            try:
                self.font = self.pygame.font.Font("wmd/VeraMono.ttf", self.fontheight)
            except:
                try:
                    self.font = self.pygame.font.Font(None, self.fontheight)
                except:
                    self.font = 0
                    log(LOG_ERR, "Cannot load font")

    def try_import(self):
        """"""
        try:
            import pygame
            self.ok = 1
            self.pygame = pygame
        except:
            log(LOG_ERR, "Could not import pygame. Set DISABLE_PYGAME=1")
            self.ok = 0

    def scale(self, n):
        """
        Adaptive scaling. It should be modified to gradually revert back to a more precise scale
        if the force hasn't exceeded a certain peak for some time
        """
        sn = (n - self.min) * (self.height / (self.max - self.min))
        return self.height - sn

    def ev_wm_acc(self, force):
        """first 10 (by default) frames are ignored"""
        if self.init > self.init_skip:
            self.init -= 1
            return

        axes = ['x', 'y', 'z']

        fv = []   # sfv: scaled force values
        sfv = []  # ofv: old force values (from one wiimote tick ago)

        for ax in axes:
            v = force[ax]
            fv.append(v)
            sfv.append(self.scale(v))

        self.graphForce(fv, sfv)

    def graphForce(self, fv, sfv):
        """
        graph the next set of x,y,z force values
        frames 10-20 (by default) are used for calculating min/max values, but not graphed
        set self.init_skip to choose the number of frames to be skipped
        """

        if self.init > 0:
            self.init -= 1
        elif self.init == 0:
            self.draw_minmax()
            self.pygame.display.flip()
            self.init -= 1
        else:
            self.draw_lines(sfv)

        self.proc_events()

        # store x,y,z values for next line
        self.ofv = sfv

        # Store new mins and maxs for scaling purposes
        for ax in fv:
            if ax < self.min:
                self.min = ax
            elif ax > self.max:
                self.max = ax

    def draw_lines(self, sfv):
        """draw the lines"""
        tInc = self.tInc  # For every tick, increment t by this value. Higher t, faster scroll. t is used as the x-value

        for i in range(3):
            color = self.axcolors[i]
            t = self.t
            spf = self.spf  # Split the window into four equal horizontal regions

            y2 = self.ofv[i] / spf + (i * self.height / spf)  # This is the y-value of the startpoint (it's also the previous endpoint)
            y1 = sfv[i] / spf + (i * self.height / spf)       # And this is the y-value of the endpoint of the aaline

            yc2 = self.ofv[i] / spf + ((spf - 1) * self.height / spf)  # And these are used for the combined display
            yc1 = sfv[i] / spf + ((spf - 1) * self.height / spf)

            # Let's draw anti-aliased lines
            self.pygame.draw.aaline(self.screen, color, (t, y2), (t + tInc, y1), 1)
            self.pygame.draw.aaline(self.screen, color, (t, yc2), (t + tInc, yc1), 1)

        self.check_time()

        updRect = self.pygame.Rect(t, 0, self.blank_ahead_width, self.height)
        self.pygame.display.update(updRect)

        # increment time counter (x-position on screen)
        self.t += tInc

        # if we have reached end of the screen
        if self.t >= self.width:
            self.end_of_cycle()

    def check_time(self):
        """
        Every second or so, draw a vertical line
        """
        if not self.vsep_period:
            return

        now = time.time()

        if not self.t:
            self.last_vsep = now
        else:
            if now > self.last_vsep + self.vsep_period:
                self.last_vsep = now
                t = self.t
                self.pygame.draw.aaline(self.screen, self.sepcolor, (t, 0), (t, self.height), 1)

    def proc_events(self):
        """
        This processes events, and allows us to resize the window
        """
        pgev = self.pygame.event.poll()
        while pgev:
            if pgev:
                if pgev.type == self.pygame.VIDEORESIZE:
                    self.width = pgev.w
                    self.winheight = pgev.h
                    self.height = self.winheight - self.headerheight
                    self.screen = self.pygame.display.set_mode((self.width, self.winheight), self.pygame.RESIZABLE)
                    self.screen.fill(self.bgcolor)
                    self.draw_minmax()
                    self.draw_separators()
                    self.pygame.display.flip()
                    self.t = 0
                    self.init = 10
                elif pgev.type == self.pygame.QUIT:
                    self.ev.send(EV_SHUTDOWN, '')
            pgev = self.pygame.event.poll()

    def end_of_cycle(self):
        """
        PNG saving requires pygame >= 1.8, otherwise it can only save as TGA !
        """
        if self.save_tga:
            self.pygame.image.save(self.screen, "wii%03d.tga" % self.id)

        self.id += 1
        self.t = 0

        # clear screen
        self.screen.fill(self.bgcolor)
        self.draw_separators()
        self.draw_minmax()

    def draw_minmax(self):
        """
        draw min/max values at the top of the screen
        """
        if self.font:
            textStr = "WMD Accelerometer Graph - Range: [%s, %s] " % (int(self.min), int(self.max))
            mmcolor = self.mmcolor
            text = self.font.render(textStr, 1, mmcolor)
            textpos = text.get_rect(centerx=self. width / 2, top=self.height)
            self.screen.blit(text, textpos)
            self.pygame.display.update(textpos)

    def ev_ui_info(self, msg):
        """"""
        if self.font:
            textStr = msg
            mmcolor = self.mmcolor
            text = self.font.render(textStr, 1, mmcolor)
            textpos = text.get_rect(centerx=self. width / 2, top=self.height + self.fontheight + self.fontpadding)

            if self.prev_ui_info_rect:
                self.screen.fill(self.bgcolor, self.prev_ui_info_rect)

            self.screen.blit(text, textpos)

            if self.prev_ui_info_rect:
                self.pygame.display.update(self.prev_ui_info_rect)
            else:
                self.pygame.display.update(textpos)

            self.prev_ui_info_rect = textpos

    def ev_wmdpower(self, pwrchange):
        """"""
        if (self.tInc + pwrchange) < 0:
            return
        else:
            self.tInc += pwrchange

    def draw_separators(self):
        """"""
        spf = self.spf
        sepcolor = self.sepcolor

        for i in range(spf + 1):
            y = (i * self.height / spf)
            self.pygame.draw.aaline(self.screen, sepcolor, (0, y), (self.width, y), 1)