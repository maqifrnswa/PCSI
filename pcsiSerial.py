#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 23:59:08 2020



@author: showard
"""

import re
import os
import numpy as np
# import math  # used for log functions
from bitstring import BitStream  # maybe use "Bits" instead of "BitStream"?
import imageio
import serial
from pcsi.prandom import shufflePixels
from pcsi.pcsitximage import PCSItxImage
from pcsi.pcsikisstx import PCSIkissTX
from pcsi.base91 import isBase91, base91tobytes
from pcsi.pcsidecoder import PCSIDecoder


def parseTNC(packet):
    destAddress = re.search(r'>([A-Z0-9\-]+)', packet).groups()[0]
    return destAddress


txImage = PCSItxImage(filename="HAB2sstv.bmp",
                      imageID=0,
                      bitDepth=12,
                      chromaCompression=16,
                      infoBytes=256,
                      APRSprefixBytes=True,  # if we change this, we have to change the decode too
                      base91=True)


serialport='/tmp/kisstnc'
#serialport='/dev/ttyUSB0'

decoder = PCSIDecoder()
try:
    with serial.Serial(port=serialport, bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
    # with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
        test = PCSIkissTX(txImage,
                          ser,
                          'KD9PDP-0',
                          'PCSI-0',
                          ['WIDE1-1', 'WIDE2-1'])
       # test.setPersistence(.65)
        #test.setSlotTime(100)
        test.send(3, 30)
        # print(ser.read(1000))
        # test.setPersistence(.3)
# receive
    # with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
        while len(decoder.pixelsY) < 1000:  # some threshold for how long to sit for
            print('checking for packet')
            newdata = ser.read(1000)
            print(newdata)
            if newdata:
                decoder.processSerial(newdata)
                for key in decoder.Z:
                    if not os.path.exists(key):
                        os.makedirs(key)
                    imageio.imwrite(key+'/raw.bmp', decoder.Z[key])
                    with open(key+'/pixelsY.npy', 'wb') as f:
                        np.save(f,decoder.pixelsY[key])
                        np.save(f,decoder.pixelsCbCr[key])
        # test.setPersistence(.3)
except serial.SerialException:
    print('failed to connect to serial port')
    pass

#  this stuff for testing:
#dataToSend = txImage.genPayload(0)
#
#completePacket = addressHeader + dataToSend
#kissifiedPacket = kissifyPacket(completePacket)
#print(kissifiedPacket)
#
#decoder = PCISDecoder()
#
#decoder.processSerial(kissifiedPacket)
#imageio.imwrite('testing.bmp',decoder.Z)
#
#dataToSend = txImage.genPayload(1)
#
#
#
#
#completePacket = addressHeader + dataToSend
#kissifiedPacket = kissifyPacket(completePacket)
#
#decoder.processSerial(kissifiedPacket)
#imageio.imwrite('testing2.bmp', decoder.Z)