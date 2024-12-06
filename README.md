# ham-microblog
An attempt at implementing a micro-blog into JS8Call and APRS

## Current State
The project is in a functional state and is currently in testing.

### Working
1) Web GUI powered by Quart
2) JS88Call 'Modem'
3) APRS 'Modem' via KISS TCP/IP
4) TCP/IP 'Modem'
5) TCP/IP Server

### WIP
1) Add more functionality to js8call
2) Add more APRS functionality to frontend.
3) Add Serial KISS capabilities for TNCs
4) Create CLI Client for use with packet nodes.

### Feature Wishlist
1) Adapt to VaraHF Modem

## Install
Windows users will need to install Python and Git before starting. Make sure during the python install to check the box to add to system PATH. JS8Call also needs to be in the system PATH as well. The easiest way to do this is re-install JS8Call and check the box to add to PATH.
1) Python 3.9 or greater - https://www.python.org/downloads/
2) Git for windows - https://gitforwindows.org/
3) JS8Call - http://files.js8call.com/latest.html

In the terminal paste the following...
```
git clone https://github.com/KD9YQK/ham-microblog.git
cd ham-microblog
python -m venv venv
```

## Run Once to build DB and fill in initial settings
This creates the database and builds the tables. It also asks a series of questions like callsign, which 'modems' to enable, and how time is displayed.

Windows

```
venv\Scripts\pip install -r requirements.txt
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

Direct browser to http://localhost:5000
