#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 23:59:08 2020



@author: showard
"""

import re
import numpy as np
# import math  # used for log functions
from bitstring import BitStream  # maybe use "Bits" instead of "BitStream"?
import imageio
import serial
from pcsi.prandom import shufflePixels
from pcsi.pcsitximage import PCSItxImage
from pcsi.pcsikisstx import PCSIkissTX
from pcsi.base91 import isBase91, base91tobytes


def parseTNC(packet):
    destAddress = re.search(r'>([A-Z0-9\-]+)', packet).groups()[0]
    return destAddress


def unkissifyPacket(packet):
    """
    takes packet of 0xC000 PACKET with no end flag. Already split by
    "processSerial"
    takes bitstream, returns bitstream
    """
    del packet[0:16]  # the 0xc000 from the KISS TNC, 0xC0 frame, 0x00 means data from TNC port0
    packet.replace('0xdbdd','0xdb',bytealigned=True)
    packet.replace('0xdbdc','0xc0',bytealigned=True)
    return  packet


def unax25ifyAddresses(packet):
    """
    takes BitStream returns list of addresses and pos after addresses in bitstream
    """
    addresses = []
    done = 0
    while done == False:
        done = packet.peek(56).uint & 0b1
        tmp = packet.read(48).uint >> 1
        tmp = tmp.to_bytes(6, "big").decode('utf-8')
        SSID = (packet.read(8).uint >> 1) & 0xf
        addresses.append(tmp.replace(" ","") + "-" + str(SSID))
    return addresses, packet.pos


class PCISDecoder():
    def __init__(self):
        self.Z = np.zeros([2,2], dtype='uint8')
        self.serialBuffer = b''
        self.pixelsY = []
        self.pixelsCbCr = []
        # self.uninit=1
    def processSerial(self, rawSerial):
        """
        first collect bits from serial in to a BitStream buffer. Then split at 0xC0
        you now have a list of buffers. Discard garbage ones, and keep the last one
        to accumulate more bits in to as they come in. Don't process that last one,
        it might still have stuff in it - save it until the next time through. Pass
        good packets to unkissify
        """
        rawSerial = BitStream(self.serialBuffer+rawSerial)
        raw = [s for s in rawSerial.split('0xc0', bytealigned = True)]
        print(raw)
        for packet in raw[:-1]:
            if len(packet) > 16:
                unkissPacket = unkissifyPacket(packet)
                addresses, unkissPacket.pos = unax25ifyAddresses(unkissPacket)
                print(addresses)
                controlField = unkissPacket.read(8)
                PIDField = unkissPacket.read(8)
                if(unkissPacket.peek(24)==b'{{V'):
                    unkissPacket.read(24)
                if(isBase91(unkissPacket.peek(64).bytes)):
                    unkissPacket = base91tobytes(unkissPacket)
                imageID = unkissPacket.read('uint:8')
                ny= unkissPacket.read('uint:8')*16
                nx= unkissPacket.read('uint:8')*16
                packetNum = unkissPacket.read('uint:16')
                numYCbCr = unkissPacket.read('uint:8')
                channelBD = unkissPacket.read('uint:8')+1
                print([controlField, PIDField, imageID, ny, nx, packetNum, numYCbCr, channelBD])

                # Need to handle bit depth somehow!!


                pixelYData = []
                pixelCbData = []
                pixelCrData = []
                for tmp in range(numYCbCr):
                    pixelYData.append(unkissPacket.read( 'uint:' + str(channelBD)))
                    pixelCbData.append(unkissPacket.read( 'uint:' + str(channelBD)))
                    pixelCrData.append(unkissPacket.read( 'uint:' + str(channelBD)))
                while unkissPacket.len - unkissPacket.pos >= channelBD:
                    pixelYData.append(unkissPacket.read( 'uint:' + str(channelBD)))

                pixelList = shufflePixels(ny,nx)
                startingPixel = packetNum * (len(pixelYData))  # last packet might have fewer!
                pixelID = pixelList[startingPixel:startingPixel+len(pixelYData)]

                # temporarily display and hold image data
                # pixels are counted down a column first, so we transpose image
                # this conversion is "wrong," need to do it as floats

                #print(pixelID)
                #print(pixelYData)
                pixelYData = np.array(pixelYData) / (2**(channelBD)-1) * (2**8-1)
                pixelYData[pixelYData>255]=255

                pixelCbData = np.array(pixelCbData) / (2**(channelBD)-1) * (2**8-1)
                pixelCbData[pixelCbData>255]=255

                pixelCrData = np.array(pixelCrData) / (2**(channelBD)-1) * (2**8-1)
                pixelCrData[pixelCrData>255]=255

                if len(self.pixelsY) == 0:
                    self.Z = np.zeros((ny,nx,3), dtype='uint8')
                self.Z[:,:,0].T.flat[pixelID] = np.around(pixelYData)
                # self.Z[:,:,0].T.flat[pixelID] <<= (8-channelBD)
                self.Z[:,:,1].T.flat[pixelID[:len(pixelCbData)]] = np.around(pixelCbData)
                # self.Z[:,:,1].T.flat[pixelID] <<= (8-channelBD)
                self.Z[:,:,2].T.flat[pixelID[:len(pixelCrData)]] = np.around(pixelCrData)
                # self.Z[:,:,2].T.flat[pixelID] <<= (8-channelBD)
                # self.Z = self.Z << (8-channelBD)  # (Z >> (8-channelBD) ) << (8-channelBD) # /(2**channelBD-1)*255
                # self.Z = ycbcr2rgb(self.Z.astype(float))
                self.pixelsY.extend(pixelID)
                self.pixelsCbCr.extend(pixelID[:len(pixelCrData)])
                self.serialBuffer = raw[-1].tobytes()


txImage = PCSItxImage(filename="HAB2sstv.bmp",
                      imageID=0,
                      packetNum=0,
                      bitDepth=12,
                      chromaCompression=16,
                      infoBytes=256,
                      APRSprefixBytes=True,  # if we change this, we have to change the decode too
                      base91=False)


serialport='/tmp/kisstnc'
#serialport='/dev/ttyUSB0'
# transmit
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
except serial.SerialException:
    print('failed to connect to serial port to tx')
    pass

# receive
decoder = PCISDecoder()
try:
    with serial.Serial(port=serialport, bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
    # with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
        while len(decoder.pixelsY) < 1:  # some threshold for how long to sit for
            print('checking for packet')
            newdata = ser.read(1000)
            print(newdata)
            decoder.processSerial(newdata)
            imageio.imwrite('testing.bmp', decoder.Z)
        # test.setPersistence(.3)
except serial.SerialException:
    print('failed to connect to serial port to rx')
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