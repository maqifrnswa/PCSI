#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 09:29:00 2020

@author: showard

this is a subclass of socket to act like serial
"""

import socket
import select


class SerSocket(socket.socket):
    def __init__(self):
        super().__init__()
        self.is_open = False
    def connect(self, address):
        super().connect(address)
        self.is_open = True
    def write(self, data):
        self.sendall(data)
    def read(self, chunk):
        ready = select.select([self],[],[],0)
        if ready[0]:
            return self.recv(chunk)