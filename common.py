# -*- coding: utf-8 -*-


def tohex(data):
    """Formats a string in hex notation"""
    buf = " ".join(hex(ord(d))[2:].zfill(2) for d in data)
    return buf


def tonum(s):
    """Converts a string to a number"""
    n = 0
    for c in s:
        n += ord(c)
        n <<= 8
    n >>= 8
    return n


def tostr(i):
    """Converts an integer to a string"""
    result = []
    while i:
        result.append(chr(i & 0xFF))
        i >>= 8
    result.reverse()
    return ''.join(result)


def pack(lstBits):
    """Packs a list of bits into a string representation"""
    number = 0x00
    for idx, val in enumerate(lstBits):
        number += int(val) << idx
    b_size = (len(lstBits) + 7) / 8
    strng = ''
    for i in range(b_size):
        i = b_size - 1 - i
        strng += chr((number >> (i * 8)) & 0xFF)
    return strng


def unpack(strData):
    """Unpacks a string into a list of bits - lowest to highest"""
    data = []
    for idx, val in enumerate(strData):
        idx = len(strData) - 1 - idx
        for b in range(8):
            v = ord(strData[idx]) & (1 << b) != 0
            data.append(v)
    return data


def linesplit(socket):
    """For later use, perhaps"""
    buf = socket.recv(4096)
    done = False
    while not done:
        if "\n" in buf:
            (line, buf) = buf.split("\n", 1)
            yield line + "\n"
        else:
            more = socket.recv(4096)
            if not more:
                done = True
            else:
                buf = buf + more
    if buf:
        yield buf