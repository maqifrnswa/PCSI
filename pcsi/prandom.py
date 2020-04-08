#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 23:59:08 2020



@author: showard
"""


def lcg(seed, modulus=2**31, a=1103515245, c=12345):
    """Linear congruential generator.
    https://en.wikipedia.org/wiki/Linear_congruential_generator
    use gcc's values by default
    """
    return (a * seed + c) % modulus


def shufflePixels(numLines, numCols):
    """
    https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle#The_modern_algorithm
    """
    numPix = numLines*numCols
    pixelList = list(range(numPix))
    seed = 1  # deterministic shuffle!
    for i in range(numPix-1,-1,-1):
        seed=lcg(seed)
        j = seed % (i+1)
        # print("Seed: "+str(seed)+ "  j :" +str(j)+ "  i :" +str(i))
        pixelList[j], pixelList[i] = pixelList[i], pixelList[j]
    return pixelList

