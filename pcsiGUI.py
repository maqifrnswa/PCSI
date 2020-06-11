#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 11:36:30 2020

@author: showard
"""

from tkinter import *
from tkinter import ttk
import os
import serial.tools.list_ports

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
Button(serialframe,text="Rescan Ports",command=scanPorts).grid(column=0, row=1,columnspan=2,sticky=(N,W,E))



root.mainloop()
