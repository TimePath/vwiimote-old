
### DON'T TOUCH THOSE TWO LINES: these are constants for debug levels
LOG_ERR = 1
LOG_INFO = 2
LOG_BTN = 4
LOG_FORCE = 8
LOG_IR = 16
LOG_EV = 32

DEBUG_FORCE = 32
DEBUG_IR = 64
DEBUG_BT_SEND = 128
DEBUG_BT_RECV = 256

DEBUG_IR2 = 512
##
##
## Here you can choose how much logging you want to see
LOG_LEVEL = LOG_ERR | LOG_INFO | LOG_FORCE | LOG_EV | LOG_BTN
#LOG_LEVEL = LOG_ERR | LOG_INFO | LOG_FORCE #| LOG_BTN | LOG_IR   #more stuff
#LOG_LEVEL = LOG_ERR | LOG_INFO     # minimal


def log(level, msg):
    """"""
    if (level & LOG_LEVEL):  # or ( level & EXTRALOGS ):
        print(msg)
