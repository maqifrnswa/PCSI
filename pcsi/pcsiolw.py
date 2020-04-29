#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 18:17:06 2020

@author: showard
"""

import numpy as np
from pylbfgs import owlqn
from pcsi.discretecos import idct2, dct2


class PCSIolw:
    def __init__(self, nx, ny, b, ri):
        self.nx = nx
        self.ny = ny
        self.b = b
        self.ri = ri

    def evaluate(self, x, g, step):
        """An in-memory evaluation callback."""
        # we want to return two things:
        # (1) the norm squared of the residuals, sum((Ax-b).^2), and
        # (2) the gradient 2*A'(Ax-b)

        # expand x columns-first
        x2 = x.reshape((self.nx, self.ny)).T

        # Ax is just the inverse 2D dct of x2
        Ax2 = idct2(x2)

        # stack columns and extract samples
        Ax = Ax2.T.flat[self.ri].reshape(self.b.shape)

        # calculate the residual Ax-b and its 2-norm squared
        Axb = Ax - self.b
        fx = np.sum(np.power(Axb, 2))

        # project residual vector (k x 1) onto blank image (ny x nx)
        Axb2 = np.zeros(x2.shape)
        Axb2.T.flat[self.ri] = Axb  # fill columns-first

        # A'(Ax-b) is just the 2D dct of Axb2
        AtAxb2 = 2 * dct2(Axb2)
        AtAxb = AtAxb2.T.reshape(x.shape)  # stack columns

        # copy over the gradient vector
        np.copyto(g, AtAxb)

        return fx

    def go(self):
        Xat2 = owlqn(self.nx*self.ny, self.evaluate, None, 5)
        # transform the output back into the spatial domain
        Xat = Xat2.reshape(self.nx, self.ny).T # stack columns
        Xa = idct2(Xat)
        Xa[Xa < 0] = 0
        Xa[Xa>255] = 255
        return Xa