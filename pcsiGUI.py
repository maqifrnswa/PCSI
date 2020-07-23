#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 11:36:30 2020

@author: showard
"""

from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog
import os
import time
import json
import threading
import serial.tools.list_ports
from PIL import ImageTk, Image
import imageio
import numpy as np
import cv2
from pcsi.pcsitximage import PCSItxImage
from pcsi.pcsikisstx import PCSIkissTX
from pcsi.pcsidecoder import PCSIDecoder
from pcsi.pcsiolw import PCSIolw
import pcsi.sersock


root = tk.Tk()
root.title("PCSI Transmit")

defaultPadding="5 3 5 5"

mainframe = ttk.Frame(root, padding=defaultPadding)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

callframe = ttk.Labelframe(mainframe,text="Identification",padding=defaultPadding)
callframe.grid(column=0, row=0, sticky=(N, W, E, S))

ttk.Label(callframe, text="Callsign:").grid(column=0, row=0, sticky=(N, W, E))
callSign = StringVar()
callSign.set("NOCALL")
ttk.Entry(callframe, textvariable=callSign, width=8).grid(column=0,row=1, sticky=(N,W,E))
destNet = StringVar()
destNet.set("PCSI")
ttk.Label(callframe, text="Dest/Net:").grid(column=0, row=3, sticky=(N, W, E))
ttk.Entry(callframe, textvariable=destNet, width=8).grid(column=0,row=4, sticky=(N,W,E))
digisListVar = StringVar()
ttk.Label(callframe, text="Digis List:").grid(column=0, row=5, sticky=(N, W, E))
ttk.Entry(callframe, textvariable=digisListVar).grid(column=0,row=6, sticky=(N,W,E))


packetconfigframe = ttk.Labelframe(mainframe,text="Packet Configuration",padding=defaultPadding)
packetconfigframe.grid(column=0, row=1, sticky=(N, W, E, S))

aprsPrefix = StringVar()
ttk.Checkbutton(packetconfigframe, text="APRS info prefix", variable=aprsPrefix).grid(column=0,row=0,stick=(N,W,E))
usebase91 = StringVar()
ttk.Checkbutton(packetconfigframe, text="Base91 Encode", variable=usebase91).grid(column=0,row=1,stick=(N,W,E))
ttk.Label(packetconfigframe, text="Packet Info Bytes").grid(column=0, row=2, sticky=(N, W, E))
infoBytesVar = StringVar()
infoBytesVar.set(256)
ttk.Entry(packetconfigframe, textvariable=infoBytesVar, width=8).grid(column=0,row=3, sticky=(N,W,E))


serialframe = ttk.Labelframe(mainframe,text="Serial Config",padding=defaultPadding)
serialframe.grid(column=0, row=2, sticky=(N, W, E, S))

portsVar = StringVar()

def scanPorts(*args):
    portslist = [ port.device for port in serial.tools.list_ports.comports()]
    if os.path.exists('/tmp/kisstnc'):
        portslist.append('/tmp/kisstnc')
    portsVar.set(portslist)

scanPorts()
portsbox = Listbox(serialframe, listvariable=portsVar, height=5)
portsbox.grid(column=0, row=0,sticky=(N,W,E))
s = ttk.Scrollbar(serialframe, orient=VERTICAL, command=portsbox.yview)
s.grid(column=1, row=0, sticky=(N,S,W))
portsbox.configure(yscrollcommand = s.set)
ttk.Button(serialframe,text="Rescan Ports",command=scanPorts).grid(column=0, row=1,columnspan=2,sticky=(N,W,E))

ser = serial.Serial(port=None, bytesize=8, parity='N', stopbits = 1, timeout = 0, rtscts=True)
def connectPort(*args):
    global ser
    if ser.is_open:
        ser.close()
    ser = serial.Serial(port=None, bytesize=8, parity='N', stopbits = 1, timeout = 0, rtscts=True)
    try:
        ser.port = portsbox.get(portsbox.curselection())
        ser.open()
        # Some TNCs don't start with KISS mode, so doing this will turn on KISS
        # If you are already in KISS mode, this won't do anything bad
        ser.write('KISS ON\r'.encode())
        ser.write('RESTART\r'.encode())
        connectedVar.set("Connected: " + portsbox.get(portsbox.curselection()))# with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
    except serial.SerialException:
        connectedVar.set("Failed to connect")# with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:


ttk.Button(serialframe,text="Connect",command=connectPort).grid(column=0, row=2,columnspan=2,sticky=(N,W,E))
connectedVar = StringVar()
connectedVar.set("Not connected")
ttk.Label(serialframe,textvar=connectedVar).grid(column=0, row=3,columnspan=2,sticky=(N,W,E))


kisstcpframe = ttk.Labelframe(mainframe,text="KISS TCP Config",padding=defaultPadding)
kisstcpframe.grid(column=0, row=3, sticky=(N, W, E, S))
ttk.Label(kisstcpframe,text="Host:").grid(column=0, row=0,sticky=(N,W))
ttk.Label(kisstcpframe,text="Port:").grid(column=1, row=0,sticky=(N,W))
tcphostVar = StringVar(value = "localhost")
ttk.Entry(kisstcpframe, textvariable=tcphostVar, width=15).grid(column=0,row=1,sticky=(N,W,E))
tcpportVar = StringVar(value = "8001")
ttk.Entry(kisstcpframe, textvariable=tcpportVar, width=5).grid(column=1,row=1,sticky=(N,W,E))

def connectTCP(*args):
    global ser
    if ser.is_open:
        ser.close()
    tcphost=tcphostVar.get()
    tcpport=int(tcpportVar.get())
    ser = pcsi.sersock.SerSocket()
    ser.connect((tcphost,tcpport))
    ser.settimeout(0)
    tcpconnectedVar.set("Connected to {}:{}".format(tcphost,tcpport))
    # ser.write(b'\xc0\x00\xa0\x86\xa6\x92@@\xe0\x96\x88r\xa0\x88\xa0`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0{{V!"p\\!"$p3\'ik\'2-e:OG7B!5z>s&p,c1yOX(Al<*v4pG{mNeuPwPXN,&`=8;H-1.&Uw]#7zYn@^\\yjNZCUIP4QA+dFZ%Fs{*Y8t$HiZ;#`lG\\=R`q`3;pF&.6!-TX)k7S"z!!7hW8D8+D(SNT`B%OS{/2Q%%&T"3CHb+SgjZ,3esRgr"*"qE_=_,{9<,8,`1r:(\\=$Z.t$X$aTx#m8^0a&mNl8K%RX8h>>]/zESeI>8Q`dzTJ!3S0_GbLPm!"\xc0')


ttk.Button(kisstcpframe,text="Connect",command=connectTCP).grid(column=0, row=2,columnspan=2,sticky=(N,W,E))
tcpconnectedVar = StringVar()
tcpconnectedVar.set("Not connected")
ttk.Label(kisstcpframe,textvar=tcpconnectedVar).grid(column=0, row=3,columnspan=2,sticky=(N,W))


def loadfile(*args):
    filename = filedialog.askopenfilename()
    imagefilename.set(filename)
    imagedata=Image.open(filename)
    croppedString = ""
    # image must be multiples of 16px
    if imagedata.width %16 or imagedata.height%16:
        imagedata = imagedata.crop((0,0,imagedata.width//16*16,imagedata.height//16*16))
        croppedString = "\nImage is CROPPED!"
    dimVar.set(str(imagedata.width)+"x"+str(imagedata.height)+" px" + croppedString)
    imagedata.thumbnail([320,240])
    imagedata=ImageTk.PhotoImage(imagedata)
    imageCanvas.create_image(0,0,image=imagedata, anchor=NW)
    imageCanvas.image=imagedata  # see: http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm


ttk.Button(mainframe,text="Load Image",command=loadfile).grid(column=1, row=3, sticky=(N))#, W, E, S))

imageFrame = ttk.Labelframe(mainframe, text="Image preview",padding=defaultPadding)
imageFrame.grid(column=1,row=0, rowspan=3,sticky=(N, W, E, S))
imageCanvas = Canvas(imageFrame, width=320, height=240)
imageCanvas.grid(column=0,row=0, sticky=(N, W))
imageCanvas2 = Canvas(imageFrame, width=320, height=240)
imageCanvas2.grid(column=0,row=1, sticky=(N, W))

imagedataFrame = ttk.Labelframe(mainframe, text="TX Image Data",padding=defaultPadding)
imagedataFrame.grid(column=2,row=0,sticky=(N, W, E, S))
imagefilename = StringVar()
ttk.Label(imagedataFrame, textvariable=imagefilename, wraplength=200).grid(column=0, row=0, sticky=(N, W))
dimVar = StringVar()
ttk.Label(imagedataFrame, textvariable=dimVar).grid(column=0, row=1, sticky=(N, W))

txinfoFrame = ttk.Labelframe(mainframe, text="Image TX Settings",padding=defaultPadding)
txinfoFrame.grid(column=2,row=1,rowspan=2,sticky=(N, W, E, S))
ttk.Label(txinfoFrame, text="TX Bit Depth:").grid(column=0, row=0, sticky=(N, W, E))
bitdepthVar = StringVar()
bitdepthVar.set("12")
ttk.Entry(txinfoFrame, textvariable=bitdepthVar, width=8).grid(column=0,row=1, sticky=(N,W,E))
ccVar = StringVar()
ccVar.set("20")
ttk.Label(txinfoFrame, text="TX Chroma Compression:").grid(column=0, row=2, sticky=(N, W, E))
ttk.Entry(txinfoFrame, textvariable=ccVar, width=8).grid(column=0,row=3, sticky=(N,W,E))

# below is not implimented yet:
#ttk.Label(txinfoFrame, text="Number of Packets:").grid(column=0, row=4, sticky=(N, W, E))
#numpacketVar = StringVar()
#numpacketVar.set("CURRENTLY NOT USED")
#ttk.Entry(txinfoFrame, textvariable=numpacketVar).grid(column=0, row=5, sticky=(N, W, E))

ttk.Label(txinfoFrame, text="Image ID number:").grid(column=0, row=6, sticky=(N, W, E))
imageidVar = StringVar()
imageidVar.set(0)
ttk.Entry(txinfoFrame, textvariable=imageidVar).grid(column=0, row=7, sticky=(N, W, E))

def simulateTX(*args):
    pass

# Below is not implemented yet
#ttk.Button(txinfoFrame, text="Simulate", command=simulateTX).grid(column=0, row=8, sticky=(N, W, E))

ttk.Label(txinfoFrame, text="Max Packets/Min:").grid(column=0, row=9, sticky=(N, W, E))
packetrateVar = StringVar()
packetrateVar.set(30)
ttk.Entry(txinfoFrame, textvariable=packetrateVar).grid(column=0, row=10, sticky=(N, W, E))
transmitting = False
#def transmitPCSI(*args):
#    if callSign.get() == "NOCALL":
#        print("Callsign must be set")
#        return
#    txImage = PCSItxImage(filename=imagefilename.get(),
#                      imageID=int(imageidVar.get()),
#                      bitDepth=int(bitdepthVar.get()),
#                      chromaCompression=int(ccVar.get()),
#                      infoBytes=int(infoBytesVar.get()),
#                      APRSprefixBytes=bool(aprsPrefix.get()),
#                      base91=bool(usebase91.get()))
#    kissTX = PCSIkissTX(txImage, ser, callSign.get(), destNet.get(), [])
#    kissTX.send(int(numpacketVar.get()), int(packetrateVar.get()))

def transmitStart(*args):
    global transmitting
    global kissTX
    transmitting = True
    txImage = PCSItxImage(filename=imagefilename.get(),
                          imageID=int(imageidVar.get()),
                          bitDepth=int(bitdepthVar.get()),
                          chromaCompression=int(ccVar.get()),
                          infoBytes=int(infoBytesVar.get()),
                          APRSprefixBytes=bool(aprsPrefix.get()),
                          base91=bool(usebase91.get()))
    digisList = []
    digisList = digisListVar.get().replace(" ","").split(",")
    kissTX = PCSIkissTX(txImage, ser, callSign.get(), destNet.get(), digisList)
    transmitStatus.set("TX Status: Running")

def transmitStop(*args):
    global transmitting
    transmitting = False
    transmitStatus.set("TX Status: Stopped")

def transmitCont(*args):
    global transmitting
    transmitting = True
    transmitStatus.set("TX Status: Running")

ttk.Button(txinfoFrame, text="TX Start/Restart", command=transmitStart).grid(column=0, row=11, sticky=(N, W, E))
transmitStatus=StringVar()
ttk.Label(txinfoFrame, textvariable=transmitStatus).grid(column=0, row=12, sticky=(N, W, E))
ttk.Button(txinfoFrame, text="TX Pause", command=transmitStop).grid(column=0, row=13, sticky=(N, W, E))
ttk.Button(txinfoFrame, text="TX Continue", command=transmitCont).grid(column=0, row=14, sticky=(N, W, E))
transmitPercent=StringVar()
ttk.Label(txinfoFrame, textvariable=transmitPercent).grid(column=0, row=15, sticky=(N, W, E))


rxFrame = ttk.Labelframe(mainframe, text="RX Control",padding=defaultPadding)
rxFrame.grid(column=3,row=0,rowspan=3,sticky=(N, W, E, S))


def savedir(*args):
    dirname = filedialog.askdirectory()
    if dirname:
        savedirname.set(dirname)


ttk.Button(rxFrame,text="Choose Directory",command=savedir).grid(column=0, row=0, sticky=(N))#, W, E, S))
savedirname = StringVar(value = os.path.expanduser("~/pcsi-data"))
ttk.Label(rxFrame,textvar=savedirname,wraplength=200).grid(column=0, row=1, sticky=(N))#, W, E, S))


def receiveStart(*args):
    global receiving
    decoder.destFilter = addressFilter.get()
    receiving = True
    receiveStatus.set("RX Status: Running")


def receiveStop(*args):
    global receiving
    receiving = False
    receiveStatus.set("RX Status: Stopped")


decoder = PCSIDecoder()
receiving = False
ttk.Label(rxFrame, text = "Address Filter:").grid(column=0, row=2, sticky=N)
addressFilter = StringVar(value="PCSI")
ttk.Entry(rxFrame, textvariable = addressFilter).grid(column=0, row=3, sticky=N)

ttk.Button(rxFrame, text = "RX Start", command = receiveStart).grid(column=0, row=4, sticky=N)
ttk.Button(rxFrame, text = "RX Stop", command = receiveStop).grid(column=0, row=5, sticky=N)
receiveStatus = StringVar()
receiveStatus.set("RX Status: Stopped")
ttk.Label(rxFrame, textvariable=receiveStatus).grid(column=0, row=6, sticky=N)
receivedImgs = StringVar()
receivedList = Listbox(rxFrame, listvariable=receivedImgs, height=5)
receivedList.grid(column=0, row=7,sticky=(N,W,E))
receiveScroll = ttk.Scrollbar(rxFrame, orient=VERTICAL, command=receivedList.yview)
receiveScroll.grid(column=1, row=7, sticky=(N,S,W))
receivedList.configure(yscrollcommand = receiveScroll.set)


def displayArrayImage(choosenImageSelected):
    imagedata = Image.fromarray(decoder.Z[choosenImageSelected])
    imagedata.thumbnail([320,240])
    imagedata=ImageTk.PhotoImage(imagedata)
    imageCanvas.create_image(0,0,image=imagedata, anchor=NW)
    imageCanvas.image=imagedata
    ny = decoder.nynx[choosenImageSelected][0]
    nx = decoder.nynx[choosenImageSelected][1]
    pixelsY= len(decoder.pixelsY[choosenImageSelected]) # number of pix received, effectively
    choosenImageData.set("{:d}x{:d}={:d}px".format(ny,nx,ny*nx))
    packetsReceived = int(pixelsY/decoder.pixelsPerPacket[choosenImageSelected])
    totalNumPackets = ((ny*nx)//decoder.pixelsPerPacket[choosenImageSelected])
    choosenImageProgress.set("{0:d} packets received = {1:3.1f}%".format(packetsReceived, 100*packetsReceived/totalNumPackets))


def chooseImage(*args):
    choosenImageSelected = receivedList.get(receivedList.curselection())
    choosenImage.set(choosenImageSelected)
    displayArrayImage(choosenImageSelected)


ttk.Button(rxFrame, text = "Select Image Preview", command = chooseImage).grid(column=0, row=8, sticky=N)
choosenImage=StringVar()
ttk.Label(rxFrame, textvar=choosenImage).grid(column=0, row=9, sticky=N)
choosenImageData=StringVar()
ttk.Label(rxFrame, textvar=choosenImageData).grid(column=0, row=10, sticky=N)
choosenImageProgress=StringVar()
ttk.Label(rxFrame, textvar=choosenImageProgress).grid(column=0, row=11, sticky=N)

processing = False


def processStart(*args):
    global processing
    processing = True
    processText.set("Processing PCSI")


def processStop(*args):
    global processing
    processing = False
    processText.set("Stopped PCSI")


ttk.Button(rxFrame, text = "Process PCSI", command = processStart).grid(column=0, row=12, sticky=N)
ttk.Button(rxFrame, text = "Stop PCSI", command = processStop).grid(column=0, row=13, sticky=N)
processText = StringVar()
ttk.Label(rxFrame, textvar=processText).grid(column=0, row=14, sticky=N)


pcsiRunning = False


def pcsiThread(imageSelected, X, nynx, pixelsY, pixelsCbCr):
    global pcsiRunning
    pcsiRunning = True
    Z = np.zeros(X.shape, dtype='uint8')
    ny = nynx[0]
    nx = nynx[1]
    XY = X[:,:,0]
    XCb = X[:,:,1]
    XCr = X[:,:,2]
    riY = pixelsY
    riCbCr = pixelsCbCr
    bY = XY.T.flat[riY].astype(float)
    bCb = XCb.T.flat[riCbCr].astype(float)
    bCr = XCr.T.flat[riCbCr].astype(float)
    # print([bY.shape, len(riY)])
    pcsiSolverY = PCSIolw(nx, ny, bY, riY)
    Z[:,:,0] = pcsiSolverY.go().astype('uint8')# choosenImage.get()
    pcsiSolverCb = PCSIolw(nx, ny, bCb, riCbCr)
    Z[:,:,1] = pcsiSolverCb.go().astype('uint8')# choosenImage.get()
    pcsiSolverCr = PCSIolw(nx, ny, bCr, riCbCr)
    Z[:,:,2] = pcsiSolverCr.go().astype('uint8')# choosenImage.get()
    Z=cv2.cvtColor(Z, cv2.COLOR_YCrCb2BGR)  # open CV switches order of channels, so this works
    imagedata = Image.fromarray(Z)
    imagedata.thumbnail([320,240])
    imagedata=ImageTk.PhotoImage(imagedata)
    imageCanvas2.create_image(0,0,image=imagedata, anchor=NW)
    imageCanvas2.image=imagedata
    imageio.imwrite(savedirname.get()+"/"+imageSelected+'/pcsi_processed.bmp', Z)
    pcsiRunning = False


practicedata = 0  # set to 1 to inject practice data once


def processControls(*args):
    if transmitting & (callSign.get() == "NOCALL"):
        print("Callsign must be set")
        transmitStop()
    elif transmitting & (ser.is_open is False):
        print("Connect to serial port first")
        transmitStop()
    elif transmitting:
        global kissTX
        if (time.time_ns() - kissTX.lastTime) > (60/int(packetrateVar.get())*1e9):
            kissTX.sendPacket(kissTX.currentPacket)
            kissTX.lastTime = time.time_ns()
            numPacketTx = kissTX.currentPacket + 1  # first packet is 0
            totNumPacket = kissTX.txImage.largestFullPacketNum + 1  # first packet is 0
            transmitPercent.set("{0:d} out of {1:d} packets = {2:3.1f}%".format(
                    numPacketTx, totNumPacket,
                    100*numPacketTx/totNumPacket))
            kissTX.currentPacket += 1
    if receiving & (ser.is_open is False):
        print("Connect to serial port first")
        receiveStop()
    elif receiving:
        # print('checking for packet')
        newdata = ser.read(2000)
        global practicedata
        if practicedata:
            newdata = b'\xc0\x00\xa0\x86\xa6\x92@@\xe0\x96\x88r\xa0\x88\xa0`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0{{V!"p\\!"$p3\'ik\'2-e:OG7B!5z>s&p,c1yOX(Al<*v4pG{mNeuPwPXN,&`=8;H-1.&Uw]#7zYn@^\\yjNZCUIP4QA+dFZ%Fs{*Y8t$HiZ;#`lG\\=R`q`3;pF&.6!-TX)k7S"z!!7hW8D8+D(SNT`B%OS{/2Q%%&T"3CHb+SgjZ,3esRgr"*"qE_=_,{9<,8,`1r:(\\=$Z.t$X$aTx#m8^0a&mNl8K%RX8h>>]/zESeI>8Q`dzTJ!3S0_GbLPm!"\xc0'
            practicedata = 0
        #print(newdata)
        if newdata:
            try:
                decoder.processSerial(newdata)
            except Exception as e:
                print("Error decoding: {}".format(e))
            receivedImgs.set(list(decoder.Z.keys()))
            for key in decoder.Z.keys():
                if key == choosenImage.get():
                    displayArrayImage(key)
                if not os.path.exists(savedirname.get()+"/"+key):
                    os.makedirs(savedirname.get()+"/"+key)
                imageio.imwrite(savedirname.get()+"/"+key+'/raw.bmp', decoder.Z[key])
                with open(savedirname.get()+"/"+key+'/pixels.json', 'w') as f:
                    json.dump((list(decoder.pixelsY[key]), list(decoder.pixelsCbCr[key])),f)
    if processing:
        if choosenImage.get():
            if pcsiRunning is False:
                imageSelected = choosenImage.get()
                x = threading.Thread(target=pcsiThread, args=(imageSelected,
                                                              decoder.Z[imageSelected][:],
                                                              decoder.nynx[imageSelected][:],
                                                              list(decoder.pixelsY[imageSelected]),
                                                              list(decoder.pixelsCbCr[imageSelected])))
                x.start()
        else:
            print("Select image to process")
            processStop()
    root.after(100, processControls)

root.after(1000, processControls)

def closeHandler(*args):
    if ser.is_open:
        ser.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", closeHandler)
root.mainloop()
