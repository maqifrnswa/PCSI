#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 23:59:08 2020



@author: showard
"""


def numPixelsSent(n, cd, cc, bitsAvailable):
    """
    pixels sent in n packets with color depth cd and chroma compression cc
    bits available is the size available to send in the payload
    """
    numYCbCrPacket = round(bitsAvailable / (2 + cc) * (3 / cd))
    numYPacket = 3. * (bitsAvailable / cd - numYCbCrPacket)
    return int(n*numYCbCrPacket), int(n*numYPacket)
