#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:39:50 2020

@author: showard
"""

import imageio
# import math  # used for log functions
# from bitstring import BitStream  # maybe use "Bits" instead of "BitStream"?
import bitstring
import cv2
from pcsi.base91 import bytestoBase91
from pcsi.colorconv import numPixelsSent
from pcsi.prandom import shufflePixels


class PCSItxImage:
    def __init__(self,
                 filename,
                 imageID,
                 bitDepth,
                 chromaCompression,
                 infoBytes=256,
                 APRSprefixBytes=False,
                 base91=False):
        # do an inventory, do I need all the variables to be members?
        self.imageID = imageID
        self.bitDepth = bitDepth
        self.chromaCompression = chromaCompression
        self.base91 = base91

        if(APRSprefixBytes):
            self.prefixBytes = b"{{V"
        else:
            self.prefixBytes = b""
        infoBytes = infoBytes - len(self.prefixBytes)
        if base91:
            # if done 13 bits at a time, worst case for base91
            self.totalPayloadBits = 13 * infoBytes // 2 + 6 * infoBytes % 2
        else:
            self.totalPayloadBits = infoBytes*8
        payloadImageBits = self.totalPayloadBits - 8*7  # 7 info header bytes
        Xorig = imageio.imread(filename)
        # must be multiples of 16
        Xorig = Xorig[0:Xorig.shape[0]//16*16,0:Xorig.shape[1]//16*16,:]

        self.XYCbCr = cv2.cvtColor(Xorig, cv2.COLOR_BGR2YCrCb)  # opencv switches the order of B and R, so this works
        self.ny, self.nx, self.nchan = Xorig.shape
        self.numYCbCr, self.numY = numPixelsSent(1,
                                                 bitDepth,
                                                 chromaCompression,
                                                 payloadImageBits)
        self.pixelList = shufflePixels(self.ny, self.nx)
        # First packet number is 0, so the largest one is tot_pix//(pix_packet) -1
        self.largestFullPacketNum = self.ny*self.nx//(self.numYCbCr+self.numY)-1

    def genPayload(self, packetNum):
        header = bitstring.pack(
                'uint:8, uint:8, uint:8, uint:16, uint:8, uint:8',
                self.imageID,
                int(self.ny/16),
                int(self.nx/16),
                packetNum % (self.largestFullPacketNum+1),
                self.numYCbCr,
                int(self.bitDepth/3-1))
        startingPixel = packetNum * (self.numYCbCr + self.numY)

        dataToSend = header
        # pixels are numbered by columns first in PCSI
        # which is consistent with C but not with python, so we transpose first
        for pixelNum in self.pixelList[startingPixel:startingPixel+self.numYCbCr]:
            packString = 'uint:' + str(int(self.bitDepth/3)) + ', uint:' + str(int(self.bitDepth/3)) + ', uint:'+ str(int(self.bitDepth/3))
            Y = round(self.XYCbCr[:,:,0].T.flat[pixelNum] / (2**8-1) * (2**(self.bitDepth/3)-1))
            Cb = round(self.XYCbCr[:,:,1].T.flat[pixelNum] / (2**8-1) * (2**(self.bitDepth/3)-1))
            # Cr = int.to_bytes(int(XYCbCr[:,:,2].flat[pixelNum]),1,"big")
            Cr = round(self.XYCbCr[:,:,2].T.flat[pixelNum] / (2**8-1) * (2**(self.bitDepth/3)-1))
            dataToSend = dataToSend + bitstring.pack(packString, Y, Cb, Cr)
        for pixelNum in self.pixelList[startingPixel+self.numYCbCr:startingPixel+self.numYCbCr+self.numY]:
            Y = round(self.XYCbCr[:,:,0].T.flat[pixelNum] / (2**8-1) * (2**(self.bitDepth/3)-1))
            dataToSend = dataToSend + bitstring.pack('uint:' + str(int(self.bitDepth/3)), Y)
        if self.base91:
            # dataToSend = megaBase91(int.from_bytes(dataToSend,"big"))
            dataToSend = bytestoBase91(dataToSend)
        else:
            dataToSend = dataToSend.tobytes()  # zero pads data so that it fits and makes it bytes for serial port
        return self.prefixBytes + dataToSend  # for APRS, return b'{{v'+ dataToSend # and need to change how many bits are in the info
