#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 11:36:30 2020

@author: showard
"""

from tkinter import *
from tkinter import ttk, filedialog
import os
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
callframe.columnconfigure(0, weight=1)
callframe.rowconfigure(0, weight=1)

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
packetconfigframe.columnconfigure(0, weight=1)
packetconfigframe.rowconfigure(0, weight=1)

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
serialframe.columnconfigure(0, weight=1)
serialframe.rowconfigure(0, weight=1)

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
imageFrame.columnconfigure(0, weight=1)
imageFrame.rowconfigure(0, weight=1)
imageCanvas = Canvas(imageFrame, width=320, height=240)
imageCanvas.grid(column=1,row=0, rowspan=3,sticky=(N, W))
testing=ImageTk.PhotoImage(Image.open("/home/showard/compressedsensing/PCSI/HAB2sstv.bmp"))
#imageCanvas.create_image(0,0,image=testing, anchor=NW)
#imageCanvas.image=testing

imagedataFrame = ttk.Labelframe(mainframe, text="Image Data",padding=defaultPadding)
imagedataFrame.grid(column=2,row=0,sticky=(N, W, E, S))
imagedataFrame.columnconfigure(0, weight=1)
imagedataFrame.rowconfigure(0, weight=1)
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
numpacketVar.set(2)
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
packetrateVar.set(60)
ttk.Entry(txinfoFrame, textvariable=packetrateVar).grid(column=0, row=10, sticky=(N, W, E))
def transmitPCSI(*args):
    txImage = PCSItxImage(filename=imagefilename.get(),
                      imageID=int(imageidVar.get()),
                      bitDepth=int(bitdepthVar.get()),
                      chromaCompression=int(ccVar.get()),
                      infoBytes=int(infoBytesVar.get()),
                      APRSprefixBytes=bool(aprsPrefix.get()),  # if we change this, we have to change the decode too
                      base91=bool(usebase91.get()))
    try:
        with serial.Serial(port=portsbox.get(portsbox.curselection()), bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
        # with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
            test = PCSIkissTX(txImage,
                              ser,
                              callSign.get(),
                              destNet.get(),
                              [])
            # test.setPersistence(.65)
            #test.setSlotTime(100)
            test.send(int(numpacketVar.get()), int(packetrateVar.get()))
    except serial.SerialException:
        print('failed to connect to serial port')
        pass

ttk.Button(txinfoFrame, text="TRANSMIT", command=transmitPCSI).grid(column=0, row=11, sticky=(N, W, E))

rxFrame = ttk.Labelframe(mainframe, text="RX Control",padding=defaultPadding)
rxFrame.grid(column=3,row=0,rowspan=3,sticky=(N, W, E, S))
rxFrame.columnconfigure(0, weight=1)
rxFrame.rowconfigure(0, weight=1)

def receivePCSI(*args):
    #probably will have to use the tk.after command to run this periodically
    decoder = PCSIDecoder()
    try:
        with serial.Serial(port=portsbox.get(portsbox.curselection()), bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
        # with serial.Serial(port='/dev/ttyACM0', bytesize=8, parity='N', stopbits = 1, timeout = 1) as ser:
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
    except serial.SerialException:
        print('failed to connect to serial port')
        pass

ttk.Button(rxFrame, text = "RECEIVE", command = receivePCSI).grid(column=0, row=0, sticky=(N, W, E))


root.mainloop()
