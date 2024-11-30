# ham-microblog
An attempt at implementing a micro-blog into js8call and APRS via API

## Current State
THIS PROJECT IS A WIP AND NOT FULLY DEVELOPED!

### Working
1) Web frontend powered by Flask
2) js8call 'Modem'
3) TCP/IP 'Modem'
4) TCP/IP Server

### WIP
1) Add more functionality to js8call
2) Add APRS and APRSIS support

### Feature Wishlist
1) Switch the web frontend from flask to aiohttp to allow merging with the daemon.

## Install
Windows users will need to install Python and Git before starting. Make sure during the python install to check the box to add to system PATH. JS8Call also needs to be in the system PATH as well. The easiest way to do this is re-install JS8Call and check the box to add to PATH.
1) Python 3.9 or greater - https://www.python.org/downloads/
2) Git for windows - https://gitforwindows.org/
3) JS8Call - http://files.js8call.com/latest.html

In the terminal paste the following...
```
git clone https://github.com/KD9YQK/ham-microblog.git
cd ham-microblog
python3 -m venv venv
```

## Run Once to build DB and fill in initial settings
This creates the database and builds the tables. It also asks a series of questions like callsign, which 'modems' to enable, and how time is displayed.

Windows

```
venv\Scripts\python setup.py
```
or you can run by clicking on the `setup.bat` script file.

Linux

```
venv/bin/pip3 install -r requirements.txt
venv/bin/python3 setup.py
```

## Starting the Daemon
The daemon is what interfaces with JS8Call, and/or the TCP/IP Server. NOTE: JS8Call must be running before starting this daemon. A future update will include the ability to start and run js8call in a headless mode for unattended stations (Linux Only).

Windows

```
venv\Scripts\python daemon.py
```
or you can run by clicking on the `daemon.bat` script file.

Linux

```
venv/bin/python3 daemon.py
```

## Starting the Web Frontend
The web frontend currently uses Flask, and due to it's 'blocking' nature, cannot be run in same script as the daemon. I plan to overhaul in a future update to use aiohttp, which 'should' allow everything to play nice together.

Windows

```
venv\Scripts\python webview.py
```
or you can run by clicking on the `webview.bat` script file.

Linux

```
venv/bin/python3 webview.py
```

Direct browser to http://localhost:5000
