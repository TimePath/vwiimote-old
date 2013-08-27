

class LED_Control:
    """"""
    def __init__(self):
        pass

    def startup_seq(self):
        for i in range(4):
            led_off(i)

        DSHORT = 200
        DMID = 30
        DLONG = 200

        F_SWEEP = [
            [DMID, 1],
            [DMID, 1, 2],
            [DMID, 2, 3],
            [DMID, 3, 4],
            [DMID, 4]
        ]

        R_SWEEP = [
            [DMID, 4],
            [DMID, 4, 3],
            [DMID, 3, 2],
            [DMID, 2, 1],
            [DMID, 1]
        ]

        NV = 999

        F_INV_SWEEP = [
            [DSHORT, 1, 2, 3, 4, NV],
            [DLONG, 0, NV],
            [DSHORT, 1],
            [DSHORT, 1, 2],
            [DSHORT, 2, 3],
            [DSHORT, 3, 4],
            [DSHORT, 4, NV],
            [DSHORT, 1, 2, 3, 4, NV]
        ]

        R_INV_SWEEP = deepcopy(F_INV_SWEEP)
        R_INV_SWEEP.reverse()

        BLINK_ALL = [
            [DSHORT, 1, 2, 3, 4],
            [DSHORT, 1, 2, 3, 4],
        ]

        #seq = F_SWEEP + R_SWEEP + F_INV_SWEEP + R_INV_SWEEP
        seq = F_INV_SWEEP + BLINK_ALL  # + R_INV_SWEEP

        ranlen = 75
        rdmin = 5
        rdmax = 35
        vibeluck = 8

        if RANDSEQ:
            for i in range(ranlen):
                l = random.randint(0, 3)
                d = random.randint(rdmin, rdmax) / 1000.0
                vl = random.randint(0, 5)
        #        if vl == 1:
        #            Vibe.toggle()
                led_toggle(l)
                time.sleep(d)

            for l in range(4):
                led_off(l - 1)

        #    Vibe.off()

            time.sleep(0.30)

        for s in seq:
            dur = s[0] / 1000.0
            for i in range(1, len(s)):
                l = s[i]
                if l and l != NV:
                    led_toggle(l - 1)
            try:
                if s.index(NV):
                    time.sleep(dur)
            except:
        #        Vibe.plm( pulses=1, length=dur/2 )
                time.sleep(dur / 2)