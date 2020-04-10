#!/usr/bin/env python3
# Adapted from
# http://www.pyrunner.com/weblog/2016/05/26/compressed-sensing-python/

import os
import numpy as np
from pylbfgs import owlqn
import imageio
import scipy.fftpack as spfft
# import matplotlib.pyplot as plt
# from base91 import rgb2ycbcr, ycbcr2rgb, numPixelsSent  # rename this module
from pcsi.colorconv import rgb2ycbcr, ycbcr2rgb, numPixelsSent
import argparse

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


def evaluate(x, g, step):
    """An in-memory evaluation callback."""

    # we want to return two things:
    # (1) the norm squared of the residuals, sum((Ax-b).^2), and
    # (2) the gradient 2*A'(Ax-b)

    # expand x columns-first
    x2 = x.reshape((nx, ny)).T

    # Ax is just the inverse 2D dct of x2
    Ax2 = idct2(x2)

    # stack columns and extract samples
    Ax = Ax2.T.flat[ri].reshape(b.shape)

    # calculate the residual Ax-b and its 2-norm squared
    Axb = Ax - b
    fx = np.sum(np.power(Axb, 2))

    # project residual vector (k x 1) onto blank image (ny x nx)
    Axb2 = np.zeros(x2.shape)
    Axb2.T.flat[ri] = Axb  # fill columns-first

    # A'(Ax-b) is just the 2D dct of Axb2
    AtAxb2 = 2 * dct2(Axb2)
    AtAxb = AtAxb2.T.reshape(x.shape)  # stack columns

    # copy over the gradient vector
    np.copyto(g, AtAxb)

    return fx


parser = argparse.ArgumentParser(description="Command line tool to simulate PCSI",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--imagefile", type=str, default='HAB2sstv.bmp',
                    help="Input image to transmit (24bit color, any filetype)")
#parser.add_argument("imagefile", type=str,
#                    help="Input image to transmit (24bit color, any filetype)")

parser.add_argument("-b", "--bitdepth", type=int, default=24,
                    help="Bit depth transmit (e.g., 24 for 24-bit color)")
parser.add_argument("-N", "--numpackets", type=int, nargs='*', default=100,
                    help="Number of packets to simulate")
parser.add_argument("-c", "--chromacomp", type=int, default=1, nargs='*',
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
bitDepthToRemove = (24-transmittedColorDepth)/3  # per channel

numberPackets = args.numpackets
#numberPackets = (100, ) #, 300, 1000)
chromaCompressionList= args.chromacomp
#chromaCompressionList = (16,)  # chromaCompression is the total number of pix/ YCbCr pix
# sampleSizes are the number of YCbCr and Y only pixels received in n packets



# read original image
# Xorig = imageio.imread('escher_waterfall.jpeg')
# Xorig = imageio.imread('HAB.jpg')
Xorig = imageio.imread(args.imagefile)

imagefileName, ext = args.imagefile.split('.')
if not os.path.exists('results_' + imagefileName):
    os.makedirs('results_' + imagefileName)

if not os.path.exists(args.outfolder):
    os.makedirs(args.outfolder)

Xorig = rgb2ycbcr(Xorig)
ny,nx,nchan = Xorig.shape



for chromaCompression in chromaCompressionList:
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
            continue  # too good of an image
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
            X = np.around(X / 2.**bitDepthToRemove) * 2.**bitDepthToRemove
            X[X>255] = 255


            # create images of mask (for visualization)
            Xm = 255 * np.ones(X.shape)
            Xm.T.flat[ri] = X.T.flat[ri]
            masks[i][:,:,j] = Xm

            # take random samples of image, store them in a vector b
            b = X.T.flat[ri].astype(float)

            # perform the L1 minimization in memory
            Xat2 = owlqn(nx*ny, evaluate, None, 3)

            # transform the output back into the spatial domain
            Xat = Xat2.reshape(nx, ny).T # stack columns
            Xa = idct2(Xat)
            Xa[Xa < 0] = 0
            Xa[Xa>255] = 255
            Z[i][:,:,j] = Xa.astype('uint8')
        Z[i][:,:,:] = ycbcr2rgb(Z[i][:,:,:])
        imageio.imwrite(args.outfolder + '/' + imagefileName + str(numberPackets[i]) +'p_'
                        + str(transmittedColorDepth) + 'b_'
                        + str(chromaCompression) +'.bmp', Z[i])


#Xorig = ycbcr2rgb(Xorig)



#f, ax = plt.subplots(2, 3)#, figsize=(14, 4))
#
#ax[0,0].imshow(Xorig, interpolation='none')
#ax[0,0].axis('off')
##ax[0,0].title.set_text('Orig Image 2h45m')
#ax[0,0].title.set_text('Orig Image 167 mins \n 1000 packets')
#ax[0,1].imshow(Z[0], interpolation='none')
#ax[0,1].axis('off')
##ax[0,1].title.set_text('0h16m')
#ax[0,1].title.set_text('8 mins \n 48 packets')
##ax[0,2].imshow(Z[1], interpolation='none')
##ax[0,2].axis('off')
###ax[0,2].title.set_text('0h33m')
##ax[0,2].title.set_text('16 mins \n 96 packets')
##ax[1,0].imshow(Z[2], interpolation='none')
##ax[1,0].axis('off')
###ax[1,0].title.set_text('0h49m')
##ax[1,0].title.set_text('24 mins \n 144 packets')
##ax[1,1].imshow(Z[3], interpolation='none')
##ax[1,1].axis('off')
###ax[1,1].title.set_text('1h06m')
##ax[1,1].title.set_text('32 mins \n 192 packets')
##ax[1,2].imshow(Z[4], interpolation='none')
##ax[1,2].axis('off')
###ax[1,1].title.set_text('1h22m')
##ax[1,2].title.set_text('40 mins \n 240 packets')
#plt.show()
