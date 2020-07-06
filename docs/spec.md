# Packet Compressed Sensing Imaging (PCSI)

## Pseudorandom Datagram Payload (PDP) Specification

The following is the specification for PDPs for PCSI image transmission.

This enables [PCSI](./index.html) image transfer.

PDP spec v0.0.0 (unreleased, versioning will follow semver 2.0)

Author: KD9PDP

Specification License: [Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/) ![Creative Commons License](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)

### What is PDP?
PDP is a specification for the payloads of data packets such that each packet contains all the information needed to reconstruct a single image. An image is then transmitted as the collection of datagrams. Unlike other packetized transmission formats, the pixels contained in a packet are selected in a pseudorandom, yet deterministic, way. This allows images to be restored using compressed sensing techniques regardless of packet loss. Some unique features enabled by PDP are given in [this page](./details.html).

### PDP Specification Scope
The PDP spec merely defines the packet payload for transmission of a single image. It can be used in any packet protocol or digital mode. Framing is independent of the specification. This allows for the separation of a "session" (consisting of a sending station sending one or more images) from the minimal content required for a single image. The "session" information is in the framing, the image information is in the payload. The payload is designed to be similar to [SSDV](https://ukhas.org.uk/guides:ssdv).

For example, a PDP can be placed as the payload in:
* UDP or TCP (although the benefits of PCSI provide more benefit to multicast UDP packets than connected TCP packets)
* AX.25 amateur radio packets. Transmitted using any mode (e.g., AFSK, PSK, etc.) Therefore it is compatible with APRS, TNCs, digipeaters, software modems (direwolf, fldigi, soundmodem, etc.).
* [SSDV](https://ukhas.org.uk/guides:ssdv)-style framing done in a KISS TNC compatible way. Example implementation is below.

### Example of SSDV-style framing:
While not part of the PDP spec, a simple session framing of PDP can be done in a way that is compatible with KISS TNCs.

|Offset | Name | Size | Description |
| ----- | ---- | ---- | ----------- |
| 0 | Flag | 1 | HDLC flag `0x7e` |
| 1 | Packet Identifier | 1 | ASCII `v` = `0x76` |
| 2 | Callsign/Session ID | 4 | Base-40 encoded callsign or alphanumeric text, following SSDV encoding convention |
| 6 | PDP | N <= 256 | **PDP** data as defined below |
| N+6 | CRC Checksum | 2 | CRC-CCITT following HDLC convention |
| N+8 | Flag | 1 | HDLC flag `0x7e` |

To use it with a KISS TNC, you'd just send the `Packed ID + Callsign + PDP` and let the TNC add the flags and do the checksum.


### PDP Specification Details
Since each packet contains information of the whole frame, each packet **MUST** be the same size (same number of pixels per packet). Total packet size is determined by the framing protocol used. For example, AX.25 packet payloads are 256 bytes by default. The payload contains the following data transmitted in order:

| Offset (bits) | Name | Size (bits) | encoding | Description |
| ------------- | ---- | ----------- | -------- | ----------- |
| 0 | Image ID | 8 | uint8 | Identifies unique images within a PCSI session |
| 8 | Rows  | 8 | uint8 | number of lines in the image divided by 16 (4096 lines max) |
| 16 | Columns | 8 | uint8 | number of columns in the image divided by 16 (4096 columns max) |
| 24 | Packet ID | 16 | uint16 | used as the starting point of the pseudorandom pixel list |
| 32 | Number of YCbCr Pixels | 8 | uint8 |  Number of full color pixels transmitted in this packet |
| 40 | Color depth | 8 | uint8 | Color depth encoded as (color depth/3 -1). e.g., 24bit color = 7. *This only uses 3 bits, so there are 5 bits available for future use* |
| 48 | YCbCr Pixel Data | (Number of YCbCr Pixels)\*(Color bit depth) | uint\? | Full color (YCbCr) pixels listed first as a binary stream. For example, if color is transmitted as 12 bit color, each pixel is 12 bits long with the first 4 corresponding to the Y channel, the next four corresponding to the Cb channel, and the final 4 corresponding to the Cr channel. |
| 48+(Number of YCbCr Pixels)\*(Color bit depth) | Y Pixel Data | N | uint\? | Black and white (Y only) pixels follow in a binary stream of Y values encoded as a uint with the same bit depth as a single channel of the YCbCr pixels. |
| 48+(Number of YCbCr Pixels)\*(Color bit depth)+N | zero padding | Z | `0` | zero padding for byte alignment as needed |


### Packet Payload Preparation
Given a bitmapped image to transfer, follow the following procedures
1. Using a pseudo-random number generator, generate the sequence of pixels to be transmitted
1. Given the number of bits available in the payload (e.g., AX.25 UI frames have 256 bytes minus 7 bytes of image info equals 1992 bits total), the desired chroma compression level, and the desired color bit depth to transmit, determine the list of pixels to transmit that will be full color and solely back and white.
    1. All packets consist of the same number of pixels (e.g., every packet for an image has exactly 25 YCbCr pixels and 75 Y only pixels for a total of 100 pixels. You can choose whatever numbers you want, as long as they are the same for every packet of the image).
1. Prepare the packet payload
    1. Convert full color pixels to YCbCr per ITU-T T.871 https://en.wikipedia.org/wiki/YCbCr#JPEG_conversion and black and white only pixels to Y per the same spec.
    1. If color bit depth is being reduced, approximate the value to be transmitted using rounding. For example, the 8 bit number 200 will be represented as the 4 bit number `round(200/255*127)=100`.


#### Pseudo-random Number Generation for Picking Pixels
Compressed sensing imaging requires that the measurements are uncorrelated in the sparse domain that is used to reconstruct the image. Taking random samples ensures this condition, however, both the transmitter and receiver need to know which pixel values correspond to which pixels in the image. To do this, PCSI uses a [Linear Congruential Generator](https://en.wikipedia.org/wiki/Linear_congruential_generator) as a pseudo-random number generator using gcc's default coefficients (modulus=2^31, a=1103515245, c=12345, starting with a seed=1) and combined with the modern [Fisher Yates shuffle algorithm](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle#The_modern_algorithm) to generate a random list of the pixels to be sent. See reference code for details. This will allow all receivers and the transmitter to generate identical lists of order that pixels will be transmitted. Since every packet has the same number of pixels, the packet ID will give the receiver the starting pixel number from which the list of pixels received in the packet can be extracted.

Pixels are indexed column-first as seen in C, not row first as is typically done in Python. You therefore have to transpose a matrix before selecting and assigning pixels if you are in Python.

#### PCSI Payload base91 Encoding
If transmitting over channels the require/prefer printable ascii text, the entire PDP can be converted to base91 as described below. This is a combination of APRS base91 and basE91 (http://base91.sourceforge.net/). Compared to basE91, this is simpler and deterministic at the cost of slightly more overhead
1. While there are 13 bits or more to convert, read in 13 bits
    1. Convert those 13 bits to two ASCII bytes using \[floor(bits/91)+33\] for first and \[bits%91+33\] for the second byte
1. Next, if there are less than thirteen and 7 or more bits available (the end of the stream)
    1. Read in and zero pad (to the right) the remaining bits so that there are 13 bits total.
    1. Convert those 13 bits to two ASCII bytes using \[floor(bits/91)+33\] for first and \[bits%91+33\] for the second byte
1. If there are 6 or few bits remaining:
    1. Read in and zero pad (to the right) the remaining bits so that there are 6 bits total.
    1. Convert those 6 bits to one ASCII byte using bits+33

### AX.25 and APRS compatible packets
PCSI can be sent as the information field in simple AX.25 UI packets as described above. Additionally, with a few modifications, PCSI may be sent as AX.25 APRS compatible packets. While use of PCSI over APRS VHF frequencies is discouraged, you can set up APRS compatible hardware and software on other frequencies to be used with PCSI. APRS compatible AX.25 packets can be sent by doing the following:
* The AX.25 Destination Address is set to PCSI with an SSID chosen by the user. This indicates a PCSI altnet intended for anyone interested in PCSI to see.
* The information field of the AX.25 packet has the following format following the APRS Spec

| Offset (bytes) | Name | Size (bytes)| Description |
| -------------- | ---- | ----------- | ----------- |
| 0 | APRS Data Type Identifier | 1 | Binary `0x7b` or ASCII "{" for "User-Defined APRS packet format" |
| 1 | APRS User-ID  | 1 |  Binary `0x7b` or ASCII "{" for "User ID undefined (experimental)" |
| 2 | APRS User-Defined | 1 | Binary `0x56` or ASCII `V` for |
| 3 | PDP | N <= 253 | **PDP** data encoded is bit-packed binary or base91 as described above. Complete information field must be < = 256 bytes |


## Reconstructing PCSI Images
There is no specification or standard on how to reconstruct the images. Users can experiment with different methods and find what is appropriate. The reference implementation follows these steps (based off of http://www.pyrunner.com/weblog/2016/05/26/compressed-sensing-python/)
1. Decode all the pixel values and pixel numbers from as many packets as have been successfully received.
1. For each color channel (Y, Cb, Cr), use OLW-QN for basis pursuit https://en.wikipedia.org/wiki/Limited-memory_BFGS#OWL-QN to find the discrete cosine transform (DCT) coefficients that best fit the received data AND minimizes the L1 norm. This is the key to compressed sensing! Reference python implementation uses https://bitbucket.org/rtaylor/pylbfgs/src/master/
1. After finding the DCT coefficients, use the inverse DCT to generate the color channels for the image.
1. Convert from YCbCr to RGB, and save the image!
