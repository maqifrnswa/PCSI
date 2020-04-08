# Packet Compressed Sensing Imaging (PCSI)
This repository holds the specefication and a usable reference implementation of PCSI.
PCSI spec v0.0.0 (unreleased, versioning will follow semver 2.0)

## What is PCSI?
PCSI is a way of transmitting imaging data over unconnected networks where receiving stations may each receive different random packets (due to corruption from noise or blocked signals) yet each receiving station can individually reconstruct the entire original image with high fidelity only with the packets it received. High quality, full frame images, can be reconstructed with as little as 10% of the original data being transmitted or received. Even if a receiver joins the broadcast mid-transmission, it will be able to reconstruct the full image.

### PCSI Reference Application
A remote amateur radio station on a high altitude balloon or satellite transmitting images back to ground stations. Remote station is assumed to have little computing power, so minimal processing will occur on the remote state. The link is unconnected (i.e., one directional broadcasts) and will lead to corrupted/lost packets.

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
For the reference application, we will use AX.25 frames which are the defacto amateur radio packet standard.
