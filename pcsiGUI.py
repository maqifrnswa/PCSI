#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 11:36:30 2020

@author: showard
"""

from tkinter import *
from tkinter import ttk, filedialog
import os
import time
import json
import serial.tools.list_ports
from PIL import ImageTk, Image
import imageio
from pcsi.colorconv import numPixelsSent
from pcsi.pcsitximage import PCSItxImage
from pcsi.pcsikisstx import PCSIkissTX
from pcsi.pcsidecoder import PCSIDecoder



root = Tk()
root.title("PCSI Transmit")

defaultPadding="5 3 5 5"

mainframe = ttk.Frame(root, padding=defaultPadding)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

callframe = ttk.Labelframe(mainframe,text="Identification",padding=defaultPadding)
callframe.grid(column=0, row=0, sticky=(N, W, E, S))
#callframe.columnconfigure(0, weight=1)
#callframe.rowconfigure(0, weight=1)

ttk.Label(callframe, text="Callsign:").grid(column=0, row=0, sticky=(N, W, E))
callSign = StringVar()
callSign.set("NOCALL")
ttk.Entry(callframe, textvariable=callSign, width=8).grid(column=0,row=1, sticky=(N,W,E))
destNet = StringVar()
destNet.set("PCSI")
ttk.Label(callframe, text="Dest/Net:").grid(column=0, row=3, sticky=(N, W, E))
ttk.Entry(callframe, textvariable=destNet, width=8).grid(column=0,row=4, sticky=(N,W,E))


packetconfigframe = ttk.Labelframe(mainframe,text="Packet Configuration",padding=defaultPadding)
packetconfigframe.grid(column=0, row=1, sticky=(N, W, E, S))
#packetconfigframe.columnconfigure(0, weight=1)
#packetconfigframe.rowconfigure(0, weight=1)

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
#serialframe.columnconfigure(0, weight=1)
#serialframe.rowconfigure(0, weight=1)

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
s.grid(column=1, row=0, sticky=(N,S))
portsbox.configure(yscrollcommand = s.set)
ttk.Button(serialframe,text="Rescan Ports",command=scanPorts).grid(column=0, row=1,columnspan=2,sticky=(N,W,E))

ser = serial.Serial(port=None, bytesize=8, parity='N', stopbits = 1, timeout = 0)
def connectPort(*args):
    try:
        ser.port = portsbox.get(portsbox.curselection())
        ser.open()
        connectedVar.set("Connected: " + portsbox.get(portsbox.curselection()))# with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
    except serial.SerialException:
        connectedVar.set("Failed to connect")# with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:

ttk.Button(serialframe,text="Connect",command=connectPort).grid(column=0, row=2,columnspan=2,sticky=(N,W,E))
connectedVar = StringVar()
connectedVar.set("Not connected")
ttk.Label(serialframe,textvar=connectedVar).grid(column=0, row=3,columnspan=2,sticky=(N,W,E))


def loadfile(*args):
    filename = filedialog.askopenfilename()
    imagefilename.set(filename)
    imagedata=Image.open(filename)
    dimVar.set(str(imagedata.width)+"x"+str(imagedata.height)+" px")
    imagedata.thumbnail([320,240])
    imagedata=ImageTk.PhotoImage(imagedata)
    imageCanvas.create_image(0,0,image=imagedata, anchor=NW)
    imageCanvas.image=imagedata  # see: http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
    #imageCanvas.image=testing2
 #   imageCanvas.itemconfigure(image=testing2)

    #imageCanvas.create_image(image=myimg)


ttk.Button(mainframe,text="Load Image",command=loadfile).grid(column=1, row=3, sticky=(N, W, E, S))

imageFrame = ttk.Labelframe(mainframe, text="Image preview",padding=defaultPadding)
imageFrame.grid(column=1,row=0, rowspan=3,sticky=(N, W, E, S))
#imageFrame.columnconfigure(0, weight=1)
#imageFrame.rowconfigure(0, weight=1)
imageCanvas = Canvas(imageFrame, width=320, height=240)
imageCanvas.grid(column=1,row=0, rowspan=3,sticky=(N, W))
testing=ImageTk.PhotoImage(Image.open("/home/showard/compressedsensing/PCSI/HAB2sstv.bmp"))
#imageCanvas.create_image(0,0,image=testing, anchor=NW)
#imageCanvas.image=testing

imagedataFrame = ttk.Labelframe(mainframe, text="TX Image Data",padding=defaultPadding)
imagedataFrame.grid(column=2,row=0,sticky=(N, W, E, S))
#imagedataFrame.columnconfigure(0, weight=1)
#imagedataFrame.rowconfigure(0, weight=1)
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

ttk.Label(txinfoFrame, text="Number of Packets:").grid(column=0, row=4, sticky=(N, W, E))
numpacketVar = StringVar()
numpacketVar.set("CURRENTLY NOT USED")
ttk.Entry(txinfoFrame, textvariable=numpacketVar).grid(column=0, row=5, sticky=(N, W, E))

ttk.Label(txinfoFrame, text="Image ID number:").grid(column=0, row=6, sticky=(N, W, E))
imageidVar = StringVar()
imageidVar.set(0)
ttk.Entry(txinfoFrame, textvariable=imageidVar).grid(column=0, row=7, sticky=(N, W, E))

def simulateTX(*args):
    pass
    #numpix = numPixelsSent(1, bitdepthVar.get(), ccVar.get(), infoBytes.get())
ttk.Button(txinfoFrame, text="Simulate", command=simulateTX).grid(column=0, row=8, sticky=(N, W, E))

ttk.Label(txinfoFrame, text="Max Packets/Min:").grid(column=0, row=9, sticky=(N, W, E))
packetrateVar = StringVar()
packetrateVar.set(30)
ttk.Entry(txinfoFrame, textvariable=packetrateVar).grid(column=0, row=10, sticky=(N, W, E))
transmitting = False
def transmitPCSI(*args):
    if callSign.get() == "NOCALL":
        print("Callsign must be set")
        return
    txImage = PCSItxImage(filename=imagefilename.get(),
                      imageID=int(imageidVar.get()),
                      bitDepth=int(bitdepthVar.get()),
                      chromaCompression=int(ccVar.get()),
                      infoBytes=int(infoBytesVar.get()),
                      APRSprefixBytes=bool(aprsPrefix.get()),  # if we change this, we have to change the decode too
                      base91=bool(usebase91.get()))
    kissTX = PCSIkissTX(txImage, ser, callSign.get(), destNet.get(), [])
    kissTX.send(int(numpacketVar.get()), int(packetrateVar.get()))

def transmitStart(*args):
    global transmitting
    global kissTX
    transmitting = True
    txImage = PCSItxImage(filename=imagefilename.get(),
                          imageID=int(imageidVar.get()),
                          bitDepth=int(bitdepthVar.get()),
                          chromaCompression=int(ccVar.get()),
                          infoBytes=int(infoBytesVar.get()),
                          APRSprefixBytes=bool(aprsPrefix.get()),  # if we change this, we have to change the decode too
                          base91=bool(usebase91.get()))
    kissTX = PCSIkissTX(txImage, ser, callSign.get(), destNet.get(), [])
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

rxFrame = ttk.Labelframe(mainframe, text="RX Control",padding=defaultPadding)
rxFrame.grid(column=3,row=0,rowspan=3,sticky=(N, W, E, S))
#rxFrame.columnconfigure(0, weight=1)
#rxFrame.rowconfigure(0, weight=1)


def receiveStart(*args):
    global receiving
    receiving = True
    receiveStatus.set("RX Status: Running")

def receiveStop(*args):
    global receiving
    receiving = False
    receiveStatus.set("RX Status: Stopped")

decoder = PCSIDecoder()
receiving = False
ttk.Button(rxFrame, text = "RX Start", command = receiveStart).grid(column=0, row=0, sticky=N)
ttk.Button(rxFrame, text = "RX Stop", command = receiveStop).grid(column=0, row=1, sticky=N)
receiveStatus = StringVar()
receiveStatus.set("RX Status: Stopped")
ttk.Label(rxFrame, textvariable=receiveStatus).grid(column=0, row=2, sticky=N)
receivedImgs = StringVar()
receivedList = Listbox(rxFrame, listvariable=receivedImgs, height=5)
receivedList.grid(column=0, row=3,sticky=(N,W,E))

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
    choosenImageProgress.set("{0:d} received = {1:3.1f}%".format(pixelsY, 100*pixelsY/(ny*nx)))

def chooseImage(*args):
    choosenImageSelected = receivedList.get(receivedList.curselection())
    choosenImage.set(choosenImageSelected)
    displayArrayImage(choosenImageSelected)

ttk.Button(rxFrame, text = "Select Image Preview", command = chooseImage).grid(column=0, row=2, sticky=N)
choosenImage=StringVar()
ttk.Label(rxFrame, textvar=choosenImage).grid(column=0, row=4, sticky=N)
choosenImageData=StringVar()
ttk.Label(rxFrame, textvar=choosenImageData).grid(column=0, row=5, sticky=N)
choosenImageProgress=StringVar()
ttk.Label(rxFrame, textvar=choosenImageProgress).grid(column=0, row=6, sticky=N)






def processControls(*args):
    print([transmitting,receiving])
    if transmitting & (callSign.get() == "NOCALL"):
            print("Callsign must be set")
            transmitStop()
    elif transmitting:
        global kissTX
        if (time.time_ns() - kissTX.lastTime) > (60/int(packetrateVar.get())*1e9):
            kissTX.sendPacket(kissTX.currentPacket)
            kissTX.currentPacket += 1
            kissTX.lastTime = time.time_ns()
    if receiving:
        print('checking for packet')
        newdata = ser.read(2000)
        print(newdata)
        if newdata:
            decoder.processSerial(newdata)
            receivedImgs.set(list(decoder.Z.keys()))
            for key in decoder.Z.keys():
                print(key)
                print(choosenImage.get())
                if key == choosenImage.get():
                    displayArrayImage(key)
                if not os.path.exists(key):
                    os.makedirs(key)
                imageio.imwrite(key+'/raw.bmp', decoder.Z[key])
                with open(key+'/pixels.json', 'w') as f:
                    json.dump((decoder.pixelsY[key], decoder.pixelsCbCr[key]),f)
    root.after(100, processControls)
    # Maybe make it run faster and just check ticks since last acquisition in
    # transmitting and receiving separately

root.after(1000, processControls)

def closeHandler(*args):
    if ser.is_open:
        ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", closeHandler)
root.mainloop()
