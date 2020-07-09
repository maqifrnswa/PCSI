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
RPrecompiled GUI packages are available under "releases." 64-bit Windows and 64-bit Linux releases are available, and if someone provides Mac ones I can share them as well.

Bleeding edge development snapshots are available for Windows here: https://ci.appveyor.com/project/maqifrnswa/pcsi. Go to "artifacts" above the console window and choose "pcsiGUI.zip" to download. For cutting edge linux use, just clone this repository and install the needed python packages.

Raspbian CLI packages can be made, eventually, but for now see the build instructions below.

## Build instructions
You can also build/run it yourself. You need the following:
* Python 3 and the following Python packages
  * OpenCV (opencv-python)
  * NumPy
  * ImageIO
  * BitString
  * PyLBFGS (includes pre-built [liblbfgs](https://github.com/chokkan/liblbfgs))
  * PySerial
  * Pillow
  * PyInstaller (optional, if you want to build executable files)

### Windows build instructions
You just need any Python installation/package.
1. install the needed Python packages. Use a venv if you'd like, or just `pip install opencv-python numpy imageio bitstring pylbfgs pyserial pillow'
1. Grab this repository using git (if you have git installed `git clone https://github.com/maqifrnswa/PCSI.git`) or just downloading it from (https://github.com/maqifrnswa/PCSI.git).
1. Enter the directory `cd PCSI` and run the GUI or whatever command you want to use e.g., `python3 pcsiGUI.py`
1. If you want to build your own executable, check out `dist.sh` for hints and `pip install pyinstaller`.

### Linux build instructions
1. Install Python modules above (either pip, virtual env, or distribution packages e.g., `sudo apt-get install python3-numpy`). All should be available except for the rtaylor pylbfgs. Follow the Windows instructions above to download and install it.
1. Download this project, and run the command you'd like, e.g., `python3 pcsiGUI.py`.

### MacOS build instructions
Follow the Linux instructions above, but get the Python modules from Anaconda/Conda (or whatever Python distribution you are comfortable with).
