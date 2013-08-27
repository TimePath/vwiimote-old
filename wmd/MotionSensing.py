from wmd.Common import *


class MSManager:
    """"""
    force_log_maxlen = 20
    force_disturbance = 200
    force_log = []

    quash = {
        'duration': 5,
         'age': 0
         }

    def __init__(self, cf, ev):
        """"""
        self.cf = cf
        self.ev = ev

        self.ev.subscribe(WM_ACC, self.ev_wm_acc)

    def ev_wm_acc(self, force):
        """"""
        if len(self.force_log) > self.force_log_maxlen:
            self.force_log.pop(0)

        self.force_log.append(force)

        disturbances = {}
        last_axv = {}
        i = 0

        axes = ['x', 'y', 'z']

        for f in self.force_log:
            for ax in axes:
                v = f[ax]
                if i == 0:
                    last_axv[ax] = v
                    disturbances[ax] = 0
                else:
                    disturbances[ax] += abs(last_axv[ax] - v)
                    last_axv[ax] = v
            i = i + 1

        disturbed_axes = []

        for ax in axes:
            v = disturbances[ax]
            if v > self.force_disturbance:
                disturbed_axes.append(ax)

        if self.quash['age'] > 0:
            self.quash['age'] -= 1
        elif disturbed_axes:
            log(LOG_FORCE, "I SENSE A GREAT DISTURBANCE IN THE FORCE..." + str(disturbances))
            self.quash['age'] = self.quash['duration']
            log(DEBUG_FORCE, "Force log: " + str(self.force_log))