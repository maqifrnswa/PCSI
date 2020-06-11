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
infoBytes = StringVar()
infoBytes.set("256")
ttk.Entry(packetconfigframe, textvariable=infoBytes, width=8).grid(column=0,row=3, sticky=(N,W,E))


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
ttk.Label(imagedataFrame, textvariable=imagefilename).grid(column=0, row=0, sticky=(N, W))
dimVar = StringVar()
ttk.Label(imagedataFrame, textvariable=dimVar).grid(column=0, row=1, sticky=(N, W))

txinfoFrame = ttk.Labelframe(mainframe, text="Image tx info Data",padding=defaultPadding)
txinfoFrame.grid(column=2,row=1,sticky=(N, W, E, S))
txinfoFrame.columnconfigure(0, weight=1)
txinfoFrame.rowconfigure(0, weight=1)
ttk.Label(txinfoFrame, text="TX Bit Depth:").grid(column=0, row=0, sticky=(N, W, E))
bitdepthVar = StringVar()
bitdepthVar.set("12")
ttk.Entry(txinfoFrame, textvariable=bitdepthVar, width=8).grid(column=0,row=1, sticky=(N,W,E))
ccVar = StringVar()
ccVar.set("20")
ttk.Label(txinfoFrame, text="TX Chroma Compression:").grid(column=0, row=2, sticky=(N, W, E))
ttk.Entry(txinfoFrame, textvariable=ccVar, width=8).grid(column=0,row=3, sticky=(N,W,E))

root.mainloop()
