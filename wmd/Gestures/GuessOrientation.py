def guess_orientation_iter(orien, lowX, lowZ, accX, accZ):
    """"""
    Wei = 0.95
    lowX = (lowX * Wei) + (accX * (1 - Wei))
    lowZ = (lowZ * Wei) + (accZ * (1 - Wei))

    absX = abs(lowX - 128)
    absZ = abs(lowZ - 128)

    if orien == 0 or orien == 2:
        absX -= HYST
    elif orien == 1 or orien == 3:
        absZ -= HYST

    if absZ >= absX:
        if absZ > HYST:
            if lowZ > 128:
                orien = 0
            else:
                orien = 2
    elif absX > absZ:
        if absX > HYST:
            if lowX > 128:
                orien = 3
            else:
                orien = 1

    return [orien, lowX, lowZ]


def guess_orientation(force_log):
    """"""
    orien = 0
    lowX = 128
    lowZ = 160

    for f in force_log:
        (orien, lowX, lowZ) = guess_orientation_iter(orien, lowX, lowZ, f['x'], f['z'])

#    print "orien=%d, lowX=%d, lowZ=%d " % (orien, lowX, lowZ)

    return orien
