# Packet Compressed Sensing Imaging (PCSI)
This repository holds the specefication and a usable reference implementation of PCSI.
The respository contains code to simulate PCSI transmission and code to transmit & receive PCSI images using a TNC connected via KISS to transmit AX.25 frames.

PCSI spec v0.0.0 (unreleased, versioning will follow semver 2.0)

Author: KD9PDP

License: GPL-3.0

## What is PCSI?
PCSI is a way of transmitting imaging data over unconnected networks where receiving stations may each receive different random packets (due to corruption from noise or blocked signals) yet each receiving station can individually reconstruct the entire original image with high fidelity only with the packets it received. High quality, full frame images, can be reconstructed with as little as 10% of the original data being transmitted or received. Even if a receiver joins the broadcast mid-transmission, it will be able to reconstruct the full image.

![Example Screenshot](docs/pcsiusage.png)


## Programs/tools included
**pcsiGUI.py** is a graphical user interface for sending, receiving, and processing PCSI images. See the [documentation here](https://maqifrnswa.github.io/PCSI/) for instructions and videos.

**pcsiSimulator.py** is a command line tool, see "./pcsiSimulator.py --help" for details.

**pcsiSerial.py** is a work in progress. So far it transmits AX.25 PCSI frames.

## How to install
Precompiled GUI packages are available under "releases." 64-bit Windows and 64-bit Linux releases are available, and if someone provides Mac ones I can share them as well.

Raspbian CLI packages can be made, eventually, but for now see the build instructions below.

## Build instructions
You can also build/run it yourself. You need the following:
* liblbfgs (https://github.com/chokkan/liblbfgs)
* Python 3 and the following Python packages
  * OpenCV (opencv-python)
  * NumPy
  * ImageIO
  * BitString
  * PyLBFGS (rtaylor version https://bitbucket.org/rtaylor/pylbfgs)
  * PySerial
  * Pillow
  * PyInstaller (optional, if you want to build executable files)

### Windows build instructions
I used MSYS2 and mingw64 to build on Windows. If you use that, you can follow the same instructions below as if you had Linux/MacOS.
1. Download and install MSYS2 (https://www.msys2.org/)
1. open up `c:\msys2` and run msys2.exe
1. run `pacman -Syu` to update your packages
1. run `pacman -S base-devel git mingw-w64-x86_64-toolchain mingw-w64-x86_64-opencv mingw-w64-x86_64-python-numpy mingw-w64-x86_64-python-pyserial mingw-w64-x86_64-python-pillow mingw-w64-x86_64-python-pip` to install compilers and standard libraries
1. exit the msys2 window, and run `mingw64.exe` in `c:\msys2`
1. Install the remaining Python modules: `pip install bitstring imageio pyinstaller`
1. Go grab liblbgfs `git clone -b patch-1 https://github.com/maqifrnswa/liblbfgs.git` You need to make one change: open up `configure.ac`, find the line `LT_INIT()` and change it to `LT_INIT([win32-dll])`. Now you can run:
   ```
   $ cd liblbfgs
   $ ./autogen.sh
   $ ./configure --enable-sse2
   $ make
   $ make install  # To install libLBFGS library and header.
   ```
1. Grab rtaylor's pylbfgfs `cd ~` then `git clone https://bitbucket.org/rtaylor/pylbfgs.git`.
1. Enter the directory `cd pylbgfs` then build and install by typing `python setup.py install`
1. Grab this repository `cd ~` and `git clone https://github.com/maqifrnswa/PCSI.git`
1. Enter the directory `cd PCSI` and run the GUI or whatever command you want to use e.g., `python3 pcsiGUI.py`
1. If you want to build your own executable, check out `dist.sh` for hints

### Linux build instructions
1. Install Python modules above (either pip, virtual env, or distribution packages e.g., `sudo apt-get install python3-numpy`). All should be available except for the rtaylor pylbfgs. Follow the Windows instructions above to download and install it.
1. To install liblbfgs you can install the distribution version or build your own. On Debian based systems (e.g., Ubuntu, Raspbian), `sudo apt-get instal liblbfgs` will install the library, but it won't have sse2 optimizations (so will be a little slower on desktop computers that have sse2 capabillities). If you have a processor that has SSE2 instructoins (i.e., a desktop computer), you can build and install an optimized, faster library yourself following the instructions https://github.com/chokkan/liblbfgs using `configure --enable-sse2`. Raspberry Pis should just use the distribution version since there is no sse2 on RPis.
1. Download this project, and run the command you'd like, e.g., `python3 pcsiGUI.py`.

### MacOS build instructions
Follow the Linux instructions above, but get the Python modules from Anaconda/Conda (or whatever Python distribution you are comfortable with).
