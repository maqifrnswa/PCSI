#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 18:29:45 2020

From http://www.pyrunner.com/weblog/2016/05/26/compressed-sensing-python/
https://bitbucket.org/rtaylor/pylbfgs/src/master/
PyLBFGS was written by Robert Taylor and is licensed under the MIT license.
"""

import scipy.fftpack as spfft


def dct2(x):
    """Return 2D discrete cosine transform.
    """
    return spfft.dct(
        spfft.dct(x.T, norm='ortho', axis=0).T, norm='ortho', axis=0)


def idct2(x):
    """Return inverse 2D discrete cosine transform.
    """
    return spfft.idct(
        spfft.idct(x.T, norm='ortho', axis=0).T, norm='ortho', axis=0)