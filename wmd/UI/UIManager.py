from wmd.Common import *
from wmd.UI.PyGame import Grapher


class UIManager:
    """"""
    def __init__(self, cf, ev):
        """"""
        ev.subscribe(UI_INFO, self.ev_ui_info)

        self.ev = ev
        self.cf = cf

        self.grapher = Grapher(ev)

    def ev_ui_info(self, message):
        """"""
        print(message)

    def pre_connect(self):
        """"""
        pass

    def connected(self):
        """"""
        pass

    def log(self, level, msg):
        """"""
        pass
