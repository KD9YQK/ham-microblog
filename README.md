# MMBR
### *** Messages Must Be Received ***
MMBR is a 'micro blog' intended to be used with ham operators and related emcomm groups with the mission of making sure a message gets passed.
The goal is to include many widely used digital protocols to facilitate the passing of 'posts' for everyday use, and especially emergency situations.
With MMBR, a single message can be picked up by a station, and then be dispatched amongst the entire community via JS8call, APRS, TCP/IP, and even through ax.25 packet nodes.

## Current State
The project is in a functional state and is currently in testing.

### Working
1) Web GUI powered by Quart
2) JS88Call 'Modem'
3) APRS 'Modem' via KISS TCP/IP
4) TCP/IP 'Modem'
5) TCP/IP Server
6) CLI client
   - Works with ax.25 packet nodes
   - Can be used by group admins to post on behalf of an emcomm or other ham group.

### WIP
1) Add more APRS functionality to frontend.
2) Add Serial KISS capabilities for TNCs

### Feature Wishlist
1) Adapt to VaraHF Modem

## Install
Windows users will need to install Python and Git before starting. Make sure during the python install to check the box to add to system PATH. JS8Call also needs to be in the system PATH as well. The easiest way to do this is re-install JS8Call and check the box to add to PATH.
1) Python 3.9 or greater - https://www.python.org/downloads/
   - Note: Newest version of python (3.13.1) will need to be run a 2nd time with the 'modify' option to enable the path environment.
2) Git for windows - https://gitforwindows.org/
3) JS8Call - http://files.js8call.com/latest.html
   - If previously installed without adding to PATH; an easy solution is to rerun the installer and select the PATH checkbox.

In the terminal paste the following to download MMBR and create a virtual environment.
```
git clone https://github.com/KD9YQK/ham-microblog.git
cd ham-microblog
python -m venv venv
```

## Run Once to install required python modules.
The following command will install all the required modules into the virtual environment.

### Windows

```
venv\Scripts\pip install -r requirements.txt
```

### Linux

```
venv/bin/pip3 install -r requirements.txt
```

## Starting MMBR
The daemon is what interfaces with JS8Call, APRS, and/or the TCP/IP Server.

### Windows

MMBR can be started by clicking on the `daemon.bat` script file.

### Linux

```
venv/bin/python3 daemon.py
```

Direct your browser to http://localhost:5000
