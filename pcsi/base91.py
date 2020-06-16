#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 23:59:08 2020



@author: showard
"""


from bitstring import BitStream  # maybe use "Bits" instead of "BitStream"?
import bitstring


def bytestoBase91(data):
    """
    this is the way a microcontroller would encode a signal.
    Data must be in 13-bit "bytes." They will be zero padded, so make sure you
    fill that last 13-bit byte enough so that the padded zeros don't become an
    extra pixel value! It just means maximize the number of pixels in the
    payload. Technically can be 13 or 14 bit bytes, but since our data isn't
    byte aligned to anything, we pick 13.

    this is lazy base91, and it works as long as we fill up as many payload
    bits as possible with data

    maybe implement real base91 just for fun? Or even, base9194 where it can be
    either 91 or 94 (or anything in between?) Doesn't really matter though

    data is a BitStream or bytes
    returns BitStream
    """
    base91data = ''
    while data.len - data.pos >= 13:
        bits = data.read('uint:13')
        base91data = base91data + chr((bits // 91) + 33) + chr((bits % 91) + 33)
    # lazy base91, technically it's 6 or 7 depending
    if data.len - data.pos >= 7:  # the number of bits left is greater or equal to 7, less eq to 12
        data = data + BitStream(13 - (data.len - data.pos))  # zero pad
        bits = data.read('uint:13')
        base91data = base91data + chr((bits // 91) + 33) + chr((bits % 91) + 33)
    elif data.len - data.pos > 0:  # number of bits left greater than 0 <= 6
        data = data + BitStream(6 - (data.len - data.pos))  # pad up to 6
        bits = data.read('uint:6')
        base91data = base91data + chr(bits + 33)
    return base91data.encode()


def base91tobytes(data):
    """
    takes and returns BitStream
    """
    decodedData = BitStream('')
    while data.len - data.pos > 8:
        decodedInt = (data.read('uint:8')-33)*91 + data.read('uint:8')-33
        decodedData = decodedData + bitstring.pack('uint:13', decodedInt)
    if (data.len - data.pos) == 8:  # lazy base91
        decodedInt = data.read('uint:8')-33
        decodedData = decodedData + bitstring.pack('uint:6', decodedInt)
    return(decodedData)


def isBase91(data):
    return all((c <= 128) and (c>=33) for c in data)

