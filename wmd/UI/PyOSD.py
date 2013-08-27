

class PyOSD:
    """"""
    ok = 0

    def __init__(self, disable=0, font="-*-courier-*-*-*-*-34-*-*-*-*-*-*-*"):
        """"""
        if not disable:
            try:
                import pyosd
                self.ok = 1
            except:
                log(LOG_ERR, "Could not import pyosd. Set DISABLE_PYOSD=1")
                return None

            self.p = pyosd.osd(font=font, offset=200, colour="#2222cc")
            self.p.set_align(pyosd.ALIGN_CENTER)

    def show(self, msg):
        if CFG['IO_MODES']['PYOSD'] and self.ok:
            self.p.display(msg)
        else:
            Plot.OSDHack(msg)
