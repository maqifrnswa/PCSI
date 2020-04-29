# Packet Compressed Sensing Imaging (PCSI)
This repository holds the specefication and a usable reference implementation of PCSI.
The respository contains code to simulate PCSI transmission and code to transmit & receive PCSI images using a TNC connected via KISS to transmit AX.25 frames.

PCSI spec v0.0.0 (unreleased, versioning will follow semver 2.0)

Author: KD9PDP

License: GPL-3.0

## What is PCSI?
PCSI is a way of transmitting imaging data over unconnected networks where receiving stations may each receive different random packets (due to corruption from noise or blocked signals) yet each receiving station can individually reconstruct the entire original image with high fidelity only with the packets it received. High quality, full frame images, can be reconstructed with as little as 10% of the original data being transmitted or received. Even if a receiver joins the broadcast mid-transmission, it will be able to reconstruct the full image.

### PCSI Reference Application
This is suitable for a remote amateur radio station on a high altitude balloon or satellite transmitting images back to ground stations. Remote station is assumed to have little computing power, so minimal processing will occur on the remote state. The link is unconnected (i.e., one directional broadcasts) and will lead to corrupted/lost packets.


## How to use
more details coming

pcsiSimulator.py is a command line tool, see "./pcsiSimulator.py --help" for details.

pcsiSerial.py is a work in progress. So far it transmits AX.25 PCSI frames.
