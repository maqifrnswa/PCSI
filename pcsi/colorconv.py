#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 23:59:08 2020



@author: showard
"""

import numpy as np

def rgb2ycbcr(imagearray):
    outarray = np.zeros(imagearray.shape)
    outarray[:, :, 0] = np.around(.299 * imagearray[:, :, 0] + .587 * imagearray[:, :, 1] + .114 * imagearray[:, :, 2])
    outarray[:, :, 1] = np.around(128. - (0.168736  * imagearray[:, :, 0]) - (.331264 * imagearray[:, :, 1]) + (.5 * imagearray[:, :, 2]))
    outarray[:, :, 2] = np.around(128.0 + (0.5  * imagearray[:, :, 0]) - (.418688 * imagearray[:, :, 1]) - (.081312 * imagearray[:, :, 2]))
    outarray[outarray<0] = 0
    outarray[outarray>255] = 255
    return outarray.astype(dtype='uint8')


def ycbcr2rgb(imagearray):
    outarray = np.zeros(imagearray.shape)
    outarray[:, :, 0] = np.around(imagearray[:, :, 0] + 1.402 * (imagearray[:, :, 2] - 128.))
    outarray[:, :, 1] = np.around(imagearray[:, :, 0] - 0.344136 * (imagearray[:, :, 1] - 128.) - 0.714136 * (imagearray[:, :, 2] - 128.))
    outarray[:, :, 2] = np.around(imagearray[:, :, 0] + 1.772 * (imagearray[:, :, 1] - 128.))
    outarray[outarray<0] = 0
    outarray[outarray>255] = 255
    return outarray.astype(dtype='uint8') # last step, make it a uint8 for plot


def numPixelsSent(n, cd, cc, bitsAvailable):
    """
    pixels sent in n packets with color depth cd and chroma compression cc
    bits available is the size available to send in the payload
    """
    numYCbCrPacket = round(bitsAvailable / (2 + cc) * (3 / cd))
    numYPacket = 3. * (bitsAvailable / cd - numYCbCrPacket)
    return int(n*numYCbCrPacket), int(n*numYPacket)

