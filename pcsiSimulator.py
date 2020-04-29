#!/usr/bin/env python3
# Author: Scott Howard KD9PDP
# License: GPL-3.0
# Adapted from
# http://www.pyrunner.com/weblog/2016/05/26/compressed-sensing-python/

import os
import numpy as np
import argparse
import imageio
from pcsi.colorconv import rgb2ycbcr, ycbcr2rgb, numPixelsSent
from pcsi.pcsiolw import PCSIolw

if __name__=="__main__":

    parser = argparse.ArgumentParser(description="Command line tool to simulate PCSI",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--imagefile", type=str, default='HAB2sstv.bmp',
                        help="Input image to transmit (24bit color, any filetype)")
    parser.add_argument("-b", "--bitdepth", type=int, default=12,
                        help="Bit depth transmit (e.g., 24 for 24-bit color)")
    parser.add_argument("-N", "--numpackets", type=int, nargs='*', default=[150],
                        help="Number of packets to simulate")
    parser.add_argument("-c", "--chromacomp", type=int, default=[20], nargs='*',
                        help="Chroma Compression ratio")
    parser.add_argument("-a", "--bitsAvailable", type=int, default=1992,
                        help="Number of bits available in payload for image data")
    parser.add_argument("-o", "--outfolder", type=str, default="results",
                        help="Output folder name")
    args = parser.parse_args()

    print(args.chromacomp)
    # Normally we assume 24 bit color. Can simulate what happens if we transmit
    # lower color depth.
    transmittedColorDepth = args.bitdepth # MULTIPLE OF 3!!
    bitDepthToRemove = int((24-transmittedColorDepth)/3)  # per channel

    numberPackets = args.numpackets  # list of the number of packets sent
    # is the list of chromaCompression is the total number of pix/ YCbCr pix
    chromaCompressionList = args.chromacomp

    # read original image
    Xorig = imageio.imread(args.imagefile)

    imagefileName, ext = args.imagefile.split('.')
    if not os.path.exists('results_' + imagefileName):
        os.makedirs('results_' + imagefileName)

    if not os.path.exists(args.outfolder):
        os.makedirs(args.outfolder)

    Xorig = rgb2ycbcr(Xorig)
    ny,nx,nchan = Xorig.shape

    for chromaCompression in chromaCompressionList:
        # sampleSizes are the number of YCbCr and Y only pixels received in n packets
        print(numberPackets,
                                     transmittedColorDepth,
                                     chromaCompression, args.bitsAvailable)
        sampleSizes = [numPixelsSent(n,
                                     transmittedColorDepth,
                                     chromaCompression,
                                     bitsAvailable = args.bitsAvailable) for n in numberPackets]
        # for each sample size
        Z = [np.zeros(Xorig.shape, dtype='uint8') for s in sampleSizes]
        masks = [np.zeros(Xorig.shape, dtype='uint8') for s in sampleSizes]

        for i,s in enumerate(sampleSizes):

            # create random sampling index vector
            k = sum(s)
            if(k > nx * ny):
                continue  # requested more pixels than in image
            ritotal = np.random.choice(nx * ny, k, replace=False) # random sample of indices

            # for each color channel
            for j in range(nchan):

                if(j==0):  # take more pixels for Y channel
                    ri = ritotal
                else:  # enable sampling fewer pixels for chroma
                    ri = ritotal[:s[0]]

                # extract channel
                X = Xorig[:,:,j].squeeze()

                # simulate color depth transmitted
                X = np.around(
                        np.around(X /(2**8-1) * (2**(transmittedColorDepth/3)-1))
                        / (2**(transmittedColorDepth/3)-1) * (2**8-1)
                        )
                X[X>255] = 255
                # X = (X>>bitDepthToRemove)<<bitDepthToRemove
                # X = np.around(X / ((2**8)-1) * ((2**(transmittedColorDepth/3))-1))

                # create images of mask (for visualization)
                Xm = 255 * np.ones(X.shape)
                Xm.T.flat[ri] = X.T.flat[ri]
                masks[i][:,:,j] = Xm

                # take random samples of image, store them in a vector b
                b = X.T.flat[ri].astype(float)

                # perform the L1 minimization in memory
                pcsiSolver = PCSIolw(nx, ny, b, ri)
                Z[i][:,:,j] = pcsiSolver.go().astype('uint8')

            Z[i][:,:,:] = ycbcr2rgb(Z[i][:,:,:])
            imageio.imwrite(args.outfolder + '/' + imagefileName + str(numberPackets[i]) +'p_'
                            + str(transmittedColorDepth) + 'b_'
                            + str(chromaCompression) +'.bmp', Z[i])

