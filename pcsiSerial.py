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
import serial
from pcsi.prandom import shufflePixels
from pcsi.pcsitximage import PCSItxImage
from pcsi.pcsikisstx import PCSIkissTX


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
        self.Z = None
        self.serialBuffer = b''
        self.pixels =[]  # we might need to do Z.T.flat[pixels], because the decode uses transpose
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
                if len(self.pixels) == 0:
                    self.Z = np.zeros((ny,nx,3), dtype='uint8')
                self.Z[:,:,0].flat[pixelID] = pixelYData
                self.Z[:,:,0].flat[pixelID] <<= (8-channelBD)
                self.Z[:,:,1].flat[pixelID[:len(pixelCbData)]] = pixelCbData
                self.Z[:,:,1].flat[pixelID] <<= (8-channelBD)
                self.Z[:,:,2].flat[pixelID[:len(pixelCrData)]] = pixelCrData
                self.Z[:,:,2].flat[pixelID] <<= (8-channelBD)
                # self.Z = self.Z << (8-channelBD)  # (Z >> (8-channelBD) ) << (8-channelBD) # /(2**channelBD-1)*255
                # self.Z = ycbcr2rgb(self.Z.astype(float))
                self.pixels.extend(pixelID)
                self.serialBuffer = raw[-1].tobytes()


txImage = PCSItxImage(filename="HAB2sstv.bmp",
                      imageID=0,
                      packetNum=0,
                      bitDepth=12,
                      chromaCompression=16,
                      infoBytes=256,
                      APRSprefixBytes=True,  # if we change this, we have to change the decode too
                      base91=True)


try:
    with serial.Serial(port='/tmp/kisstnc', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
    # with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
        test = PCSIkissTX(txImage,
                          ser,
                          'KD9PDP-0',
                          'KD9PDP-1',
                          ['WIDE1-1', 'WIDE2-1'])
        test.setPersistence(.65)
        test.setSlotTime(100)
        test.send(5, 30)
        print(ser.read(1000))
        # test.setPersistence(.3)
except serial.SerialException:
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