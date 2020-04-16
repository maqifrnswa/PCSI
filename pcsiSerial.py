#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 23:59:08 2020



@author: showard
"""

import re
import time
import numpy as np
import imageio
# import math  # used for log functions
from bitstring import BitStream  # maybe use "Bits" instead of "BitStream"?
import bitstring
import serial
from pcsi.base91 import base91tobytes, bytestoBase91, isBase91
from pcsi.colorconv import rgb2ycbcr, ycbcr2rgb, numPixelsSent
from pcsi.prandom import shufflePixels
from pcsi.pcsitximage import PCSItxImage



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


#test1 = color24to13(50,25,120)
#print(test1)
#
#print(bin(base91toBin(test1)))
#print(base91toColor24(test1))
#
#print(shufflePixels(3,2))

addressHeader = ax25ifyAddresses([["PCSI",0],["KD9PDP",0],["WIDE1",1],["WIDE2",1]])
print(addressHeader.hex())  # should be 9c946ea04040e09c6e988a9a406103f0 from AX.25 spec example

txImage = PCSItxImage(filename="HAB2sstv.bmp",
                      imageID=0,
                      packetNum=0,
                      bitDepth=12,
                      chromaCompression=16,
                      infoBytes=256,
                      APRSprefixBytes=True,  # if we change this, we have to change the decode too
                      base91=True)

dataToSend = txImage.genPayload(0)

completePacket = addressHeader + dataToSend
kissifiedPacket = kissifyPacket(completePacket)
print(kissifiedPacket)
#base91dataToSend = megaBase91(int.from_bytes(dataToSend,"big"))  # just an example
#print(base91dataToSend)

# KISS send(txImage, serial port,
# source, destination, digipeaters_list, packet delay)

class PCSIkiss:
    def __init__(self,
                 txImage,
                 ser,
                 source,
                 destination,
                 digipeaters):
        '''
        source, destination, digipeaters as KD9PDP-0 etc.
        ser is a serial object. Use it with a context manager in the main code
        maxPacketRate: maximum number of packets per second transmitted
        '''
        self.ser = ser
        self.txImage = txImage
        addressList = [destination, source] + digipeaters
        print(addressList)


        addressList = [[address.split('-')[0], int(address.split('-')[1])] if len(address.split('-')) == 2
                        else [address.split('-')[0], 0] for address in addressList]
        print(addressList)
        self.addressHeader = self.ax25ifyAddresses(addressList)

    def ax25ifyAddresses(self, addresses):  # address is a string
        """
        addresses is a list of pairs of address strings and ssid ints
        example: addresses = [["dest",0],["source",1],["digi1",0]]
        returns the ax25ified addresses in bytes + control + PID fields!
        """
        ax25Addresses = b''
        for i, address in enumerate(addresses):
            tempAddress = address[0] + " " * (6-len(address[0]))
            tempAddress = tempAddress.encode()
            tempAddress = int.from_bytes(tempAddress, "big") << 1
            """ ssid byte is CRR[SSID]L where C is 1 for the dest address, RR are
            reserved and both are 1 if not implemented and L indicates the last
            address. Dest address C bit is 1, all else are 0 becaus UI frames are
            command frames (fig C4.7, AX.25 spec 2.2)"""
            ssid = address[1] << 1 | 0b01100000  # RR bits
            if i==0:
                ssid |= 0b10000000  # set C bit for destination, UI frames are "command" frames
            elif i==len(addresses)-1:
                ssid |= 0b1  # set last bit to indicate end of addresses
            ax25Addresses = ax25Addresses + int.to_bytes(tempAddress,6,"big") + int.to_bytes(ssid,1,"big")
        return ax25Addresses + int.to_bytes(0x03,1,"big")+ int.to_bytes(0xf0,1,"big")

    def kissifyPacket(self, rawPacket):
        """
        takes a raw packet in bytes and returns an escaped, flagged packet for KISS
        """
        packet = BitStream(rawPacket)
        packet.replace('0xdb','0xdbdd',bytealigned=True)
        packet.replace('0xc0','0xdbdc',bytealigned=True)
        return  (BitStream('0xC000') + packet + BitStream('0xC0')).tobytes()

    def send(self, totalPackets, maxPacketRate):
        for n in range(totalPackets):
            completePacket = self.addressHeader + self.txImage.genPayload(n)
            kissifiedPacket = self.kissifyPacket(completePacket)
            self.ser.write(kissifiedPacket)
            time.sleep(1/maxPacketRate)


try:
    with serial.Serial(port='/tmp/kisstnc', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
    # with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
        test = PCSIkiss(txImage,ser,'KD9PDP-0','KD9PDP-1',['WIDE1-1','WIDE2-1'])
        test.send(2,.3)
        print(ser.read(1000))
except serial.SerialException:
    pass
# ser.close()

decoder = PCISDecoder()

decoder.processSerial(kissifiedPacket)
imageio.imwrite('testing.bmp',decoder.Z)

dataToSend = txImage.genPayload(1)




completePacket = addressHeader + dataToSend
kissifiedPacket = kissifyPacket(completePacket)

decoder.processSerial(kissifiedPacket)
imageio.imwrite('testing2.bmp', decoder.Z)