#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 23:59:08 2020



@author: showard
"""

import time
from bitstring import BitStream  # maybe use "Bits" instead of "BitStream"?
import bitstring


class PCSIkissTX:
    def __init__(self,
                 txImage,
                 ser,
                 source,
                 destination,
                 digipeaters=[]):
        '''
        source, destination, digipeaters as KD9PDP-0 or KD9PDP.
        Digipeaters optional
        ser is a serial object. Use it with a context manager in the main code
        maxPacketRate: maximum number of packets per second transmitted
        '''
        self.ser = ser
        self.txImage = txImage
        self.lastTime = 0
        digipeaters = list(filter(None, digipeaters))  # remove empty strings
        addressList = [destination, source] + digipeaters

        addressList = [[address.split('-')[0], int(address.split('-')[1])] if len(address.split('-')) == 2
                        else [address.split('-')[0], 0] for address in addressList]
        self.addressHeader = self.ax25ifyAddresses(addressList)
        self.currentPacket = 0

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
        '''
        maxPacketRate in packets per minute
        '''
        for n in range(totalPackets):
            self.sendPacket(n)
            time.sleep(1 / maxPacketRate * 60)

    def sendPacket(self, n):
        n = n %(self.txImage.largestFullPacketNum+1) #  only send full packets
        completePacket = self.addressHeader + self.txImage.genPayload(n)
        kissifiedPacket = self.kissifyPacket(completePacket)
        self.ser.write(kissifiedPacket)
        print(kissifiedPacket)

    def setPersistence(self, persistence):
        '''
        range from 0 to 1
        '''
        assert(persistence < 1)
        P = int(persistence * 255)
        command = bitstring.pack('uint:8', P)
        print(command)
        command.replace('0xdb','0xdbdd',bytealigned=True)
        command.replace('0xc0','0xdbdc',bytealigned=True)
        command = (BitStream('0xC002') + command + BitStream('0xC0')).tobytes()
        print(command)
        self.ser.write(command)

    def setSlotTime(self, slotTime):
        '''
        in ms
        '''
        slotTime = int(slotTime / 10)
        assert(slotTime < 256)
        command = bitstring.pack('uint:8', slotTime)
        print(command)
        command.replace('0xdb','0xdbdd',bytealigned=True)
        command.replace('0xc0','0xdbdc',bytealigned=True)
        command = (BitStream('0xC003') + command + BitStream('0xC0')).tobytes()
        print(command)
        self.ser.write(command)
        time.sleep(3)
