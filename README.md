# Packet Compressed Sensing Imaging (PCSI)
This repository holds the specefication and a usable reference implementation of PCSI.

PCSI spec v0.0.0 (unreleased, versioning will follow semver 2.0)

Author: KD9PDP

License: GPL-3.0

## What is PCSI?
PCSI is a way of transmitting imaging data over unconnected networks where receiving stations may each receive different random packets (due to corruption from noise or blocked signals) yet each receiving station can individually reconstruct the entire original image with high fidelity only with the packets it received. High quality, full frame images, can be reconstructed with as little as 10% of the original data being transmitted or received. Even if a receiver joins the broadcast mid-transmission, it will be able to reconstruct the full image.

### PCSI Reference Application
A remote amateur radio station on a high altitude balloon or satellite transmitting images back to ground stations. Remote station is assumed to have little computing power, so minimal processing will occur on the remote state. The link is unconnected (i.e., one directional broadcasts) and will lead to corrupted/lost packets.

### How to use the software
Demo loading an image and transmitting over a TNC over KISS. Demo the receiving software for listening for packets on KISS and reconstructing the image.

### How does it work (summary)
Using compressed sensing imaging, one can reconstruct full images from random selections of pixels from that image. We therefore transmit random selections of pixels in each packet so that each packet contains information from the entire image, and combining multiple packets improves received image fidelity (e.g., resolution). A good intro is here: http://www.pyrunner.com/weblog/2016/05/26/compressed-sensing-python/.

### What are current methods for sending images from balloons/remote control vehicles/rockets/etc.?
* SSTV: A solid method. Can be sent using simple 8-bit mircocontrollers (e.g., HAMShield can do it). Drawbacks: Fading and signal loss means data corruption or loss. Not distributed signal collection.
* MFSK,etc. using fldigi, other packet radio/data modes: Many ways of sending data. Drawbacks: Not easily done on 8 bit controllers (Raspberry Pi can, but I'm aiming for minimalist implementation). Not distributed signal collection, so if you lose signal, you lose data.
* SSDV: UK's HAB community developed a great packet system, software, and relay network similar to APRS just for balloon launches. The system includes "SSDV," a technique to packetize JPEG images, have people from all over collect and upload packets, and have a centralized server reconstruct the packets (http://ssdv.habhub.org/). Info here (https://ukhas.org.uk/guides:ssdv). These packets aren't compatible with APRS, but can be integrated in to it, for example (http://idoroseman.com/ssdv-over-aprs/) and the pecanpico series here (https://github.com/DL7AD). Includes forward error correction (FEC) to recover from some data corruption. Drawbacks: in the US, we don't have a network of repeaters or igates to collect packets. Additionally, decoding/encoding packets with JPEG (technically JIFF file format) is a bit too much for an 8 bit processor with limited RAM. Finally, any lost packet equates to lost data.
* APRS Vision System: At the 1997 DCCC conference, Bob Bruninga, WB4APR, (the original APRS!), proposed "APRS Vision System" (https://www.tapr.org/pdf/DCC1997-APRSvision-WB4APR.pdf). That approach found a way that the APRS network could relay tactical imaging information. The idea was to broadcast APRS packets that contain image information, starting with low spatial frequency content first, then increasingly more frequency content. When the image is "clear enough," the receiver can tell the sender to stop. This way the receiver can possible control or react to the image before the whole image became "clear." Drawbacks: Receiver needs to communicate with sender on missed packets and on stop. Any missed packet at all and whole system fails, which isn't great for APRS.

### What does PCSI do that is special?
* Every packet contains info of the entire image. Starting with the first packet, you get a complete full image (although terrible resolution). As you collect more packets, your resolution improves. If you lose a packet, who cares!
  * Each packet of APRS Vision System also sends info on the whole image, but requires every previous packet to improve resolution. SSDV only sends tiles (JPEG MCUs) in each packet, so it will lose sections of the image if packets are lost. PCSI does not need or care about lost packets! (sounds like magic, but it's math!)
* No computation needed on the balloon! Just pick out random pixels and send them (there's a system to keep track of which random pixels are chosen, because it is pseudo-random)
  * All the other tenchniques requires some decent amount of computational encoding and decoding on the remote station. There is pretty much zero computational effort needed to transmit PCSI.
* If a packet is lost, who cares! If a station starts listening mid-broadcast, it doesn't matter! You'll get the full image either way
  * No other system allows you to join mid-broadcast and still reconstruct the whole image.
* PCSI includes chroma compression and sparse sampling - so it basically is doing JPEG compression without doing any encoding or decoding at the transmitting station.

## PCSI Spec
The PCSI spec merely defines the packet payload. It can be used in any packet protocol. For example, the reference implementation is for APRS compatible AX.25 frames. The payload is designed to be similar to SSDV.

### Packet Payload Preparation
Given a bitmapped image to transfer, follow the following proceedures
1. Using a pseudo-random number generator, generate the sequence of pixels to be transmitted
1. Given the number of bits available in the payload (e.g., AX.25 UI frames have 256 bytes minus 7 bytes of image info equals 1992 bits total), the desired chroma compression level, and the desired color bit depth to transmit, determine the list of pixels to transmit that will be full color and solely back and white.
  1. All packets consist of the same number of pixels (e.g., every packet for an image has exactly 25 YCbCr pixels and 75 Y only pixels for a total of 100 pixels. You can choose whatever numbers you want, as along as they are the same for every packet of the image).
1. Prepare the packet payload
  1. Convert full color pixels to YCbCr per ITU-T T.871 https://en.wikipedia.org/wiki/YCbCr#JPEG_conversion and black and white only pixels to Y per the same spec.
  1. If color bit depth is being reduced, binary shift the pixels for the desired bit depth.

### PCSI Payload Format
* 1 byte image ID (uint8 from 0-255)
* 1 byte number of lines in the image divided by 16 (uint8 with a max of 4096 lines)
* 1 byte number of columns in the image divided by 16 (uint8 with a max of 4096 columns)
* 2 bytes Packet ID (uint16 0-65535) to be used as the starting point of the pseudo-random pixel list
* 1 byte: Number of full color pixels transmitted (number of YCbCr pixels as uint8 0-255)
* 1 byte: Color depth (uint8) encoded as (color depth/3 -1). e.g., 24bit color = 7. *This only uses 3 bits, so there are 5 bits available for future use*
* N bits: Image data. Binary stream of pixel data in the sequence determined by the pseudo random number generator algorithim starting with the pixel associated with the Packet ID. Bit depth for each channel is determined by color depth.
  * Full color (YCbCr) pixels listed first as a binary stream in YCbCr format for the number of full color images determined in the header
  * Black and white (Y only) pixels follow in a binary stream of Y values
  * zero padding for byte alignment as needed for packet protocol. If encoding in base91 (below), zero padding not required.

#### Pseudo-random Number Generation for Picking Pixels
Compressed sensing imaging requires that the measurements are uncorellated in the sparse domain that is used to reconstruct the image. Taking random samples ensures this condition, however, both the transmitter and receiver need to know which pixel values correspond to which pixels in the image. To do this, PCSI uses a "Linear Congruential Generator" (https://en.wikipedia.org/wiki/Linear_congruential_generator) as a pseudo-random number generator using gcc's default coefficients (modulus=2^31, a=1103515245, c=12345, starting with a seed=1) and combined with the modern "Fisher Yates shuffle algorithm"  https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle#The_modern_algorithm to generate a random list of the pixels to be sent. See reference code for details. This will allow all receivers and the transmitter to generate identical lists of order that pixels will be transmitted. Since every packet has the same number of pixels, the packet ID will give the receiver the starting pixel number from which the list of pixels received in the packet can be extracted.

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
  * 3 Bytes: `{{V`
    * Per the APRS spec, {{ indicates an experimental user-defined packet, and V is user defined data format type will we use to indicate "vision." *Maybe V or v could be used to indicate 24 bit or 12 bit color, or to indicate binary or base91?*
  * The total number of bytes in the information field will be less than or equal to 256 bytes.

## Reconstructing PCSI Images
There is no specefication or standard on how to reconstruct the images. Users can experiment with different methods and find what is appropriate. The reference implementation follows these steps (based off of http://www.pyrunner.com/weblog/2016/05/26/compressed-sensing-python/)
1. Decode all the pixel values and pixel numbers from as many packets as have been successfully received.
1. For each color channel (Y, Cb, Cr), use OLW-QN for basis pursuit https://en.wikipedia.org/wiki/Limited-memory_BFGS#OWL-QN to find the discrete cosine transform (DCT) coefficients that best fit the received data AND minimizes the L1 norm. This is the key to compressed sensing! Reference python implementation uses https://bitbucket.org/rtaylor/pylbfgs/src/master/
1. After finding the DCT coefficients, use the inverse DCT to generate the color channels for the image.
1. Convert from YCbCr to RBG, and save the image!
