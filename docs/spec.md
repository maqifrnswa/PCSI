# Packet Compressed Sensing Imaging (PCSI)

## Pseudorandom Data Packet (PDP) Specification

The following is the specification for PDP packets for image transmission.

This enables [PCSI](./index.html) image transfer.

PDP spec v0.0.0 (unreleased, versioning will follow semver 2.0)

Author: KD9PDP

License: GPL-3.0

### What is PDP?
PDP is a specification for the payloads of data packets such that each packet contains all the information needed to reconstruct the image. An image is then transmitted as the collection of packets. Unlike other packetized transmission formats, the pixels contained in a packet are selected in a pseudorandom, yet deterministic, way. This allows images to be restored using compressed sensing techniques regardless of packet loss. Some unique features enabled by PDP are given in [this page](./details.html).

### PDP Specification Scope
The PDP spec merely defines the packet payload. It can be used in any packet protocol or digital mode. For example
* UDP or TCP (although the benefits of PCSI provide more benefit to multicast UDP packets than connected TCP packets)
* AX.25 amateur radio packets. Transmitted using any mode (e.g., AFSK, PSK, etc.) Therefore it is compatible with APRS, TNCs, digipeaters, software modems (direwolf, fldigi, soundmodem, etc.).

The payload is designed to be similar to [SSDV](https://ukhas.org.uk/guides:ssdv).

### PDP Specification Details
Since each packet contains information of the whole frame, each packet MUST be the same size (same number of pixels per packet). total size is determined by the protocol used. For example, AX.25 packet payloads are 256 bytes by default. The payload contains the following data transmitted in order:

* 1 byte image ID (uint8 from 0-255)
* 1 byte number of lines in the image divided by 16 (uint8 with a max of 4096 lines)
* 1 byte number of columns in the image divided by 16 (uint8 with a max of 4096 columns)
* 2 bytes Packet ID (uint16 0-65535) to be used as the starting point of the pseudorandom pixel list
* 1 byte: Number of full color pixels transmitted (number of YCbCr pixels as uint8 0-255)
* 1 byte: Color depth (uint8) encoded as (color depth/3 -1). e.g., 24bit color = 7. *This only uses 3 bits, so there are 5 bits available for future use*
* N bits: Image data. Binary stream of pixel data in the sequence determined by the pseudorandom number generator algorithim starting with the pixel associated with the Packet ID. First full color (YCbCr) pixels are given, and ALL THE REMAINING BITS of the packet must be used for Y-only (black and white) pixels.
  * Full color (YCbCr) pixels listed first as a binary stream. For example, if color is transmitted as 12 bit color, each pixel is 12 bits long with the first 4 corresponding to the Y channel, the next four corresponding to the Cb channel, and the final 4 corresponding to the Cr channel. The number of YCbCr pixels is given in the header
  * Black and white (Y only) pixels follow in a binary stream of Y values.
  * zero padding for byte alignment as needed for packet protocol.

### Packet Payload Preparation
Given a bitmapped image to transfer, follow the following proceedures
1. Using a pseudo-random number generator, generate the sequence of pixels to be transmitted
1. Given the number of bits available in the payload (e.g., AX.25 UI frames have 256 bytes minus 7 bytes of image info equals 1992 bits total), the desired chroma compression level, and the desired color bit depth to transmit, determine the list of pixels to transmit that will be full color and solely back and white.
  1. All packets consist of the same number of pixels (e.g., every packet for an image has exactly 25 YCbCr pixels and 75 Y only pixels for a total of 100 pixels. You can choose whatever numbers you want, as along as they are the same for every packet of the image).
1. Prepare the packet payload
   1. Convert full color pixels to YCbCr per ITU-T T.871 https://en.wikipedia.org/wiki/YCbCr#JPEG_conversion and black and white only pixels to Y per the same spec.
   1. If color bit depth is being reduced, approximate by value using rounding. For example, the 8 bit number 200 will be represented as the 4 bit number round(200/255*127)=100.


#### Pseudo-random Number Generation for Picking Pixels
Compressed sensing imaging requires that the measurements are uncorellated in the sparse domain that is used to reconstruct the image. Taking random samples ensures this condition, however, both the transmitter and receiver need to know which pixel values correspond to which pixels in the image. To do this, PCSI uses a "Linear Congruential Generator" (https://en.wikipedia.org/wiki/Linear_congruential_generator) as a pseudo-random number generator using gcc's default coefficients (modulus=2^31, a=1103515245, c=12345, starting with a seed=1) and combined with the modern "Fisher Yates shuffle algorithm"  https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle#The_modern_algorithm to generate a random list of the pixels to be sent. See reference code for details. This will allow all receivers and the transmitter to generate identical lists of order that pixels will be transmitted. Since every packet has the same number of pixels, the packet ID will give the receiver the starting pixel number from which the list of pixels received in the packet can be extracted.

Pixels are indexed column-first, not row first as is typically done in Python. You therefore have to transpose a matrix before selecting and assigning pixels if you are in Python.

#### PCSI Payload base91 Encoding
If transmitting over channels the require/prefer printable ascii text, the binary stream can be converted to base91 in the following way. This is combination of APRS base91 and basE91 (http://base91.sourceforge.net/). Compared to basE91, this is simpler and deterministic at the cost of slightly more overhead
1. While there are 13 bits or more to convert, read in 13 bits
   1. Convert those 13 bits to two ASCII bytes using \[floor(bits/91)+33\] for first and \[bits%91+33\] for the second byte
1. Next, if there are less than thirteen and 7 or more bits available (the end of the stream)
   1. Read in and zero pad (to the right) the remaining bits so that there are 13 bits total.
   1. Convert those 13 bits to two ASCII bytes using \[floor(bits/91)+33\] for first and \[bits%91+33\] for the second byte
1. If there are 6 or few bits remaining
   1. Read in and zero pad (to the right) the remaining its so that there are 6 bits total.
   1. Convert those 6 bits to one ASCII byte using bits+33

### AX.25 and APRS compatible packets
PCSI can be sent as the information field in simple AX.25 UI packets as described above. Additionally, with a few modifications, PCSI may be sent as AX.25 APRS compatible packets by the following:
* The AX.25 Destination Address is set to PCSI with an SSID chosen by user. This indicates a PCSI altnet intended for anyone interested in PCSI to see. *IS THIS CORRECT? SHOULD IT BE APZXXX INSTEAD?*
* The information field of the AX.25 packet has the following format
  * 3 Bytes: `` {{V ``
    * Per the APRS spec, `` {{ `` indicates an experimental user-defined packet, and `V` is user defined data format type will we use to indicate "vision." *Maybe V or v could be used to indicate 24 bit or 12 bit color, or to indicate binary or base91?*
  * The total number of bytes in the information field will be less than or equal to 256 bytes.

## Reconstructing PCSI Images
There is no specefication or standard on how to reconstruct the images. Users can experiment with different methods and find what is appropriate. The reference implementation follows these steps (based off of http://www.pyrunner.com/weblog/2016/05/26/compressed-sensing-python/)
1. Decode all the pixel values and pixel numbers from as many packets as have been successfully received.
1. For each color channel (Y, Cb, Cr), use OLW-QN for basis pursuit https://en.wikipedia.org/wiki/Limited-memory_BFGS#OWL-QN to find the discrete cosine transform (DCT) coefficients that best fit the received data AND minimizes the L1 norm. This is the key to compressed sensing! Reference python implementation uses https://bitbucket.org/rtaylor/pylbfgs/src/master/
1. After finding the DCT coefficients, use the inverse DCT to generate the color channels for the image.
1. Convert from YCbCr to RBG, and save the image!
