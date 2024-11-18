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
1) ???

## Install
```
git clone https://github.com/KD9YQK/js8-microblog.git
python -m venv js8-microblog
cd js8-microblog
bin/pip install pyjs8call flask aprs3 ax253 kiss3
```
## Run Once to build DB and fill in initial settings
This creates the database and builds the tables. It also asks a series of questions like callsign, which 'modems' to enable, and how time is displayed.

`bin/python setup.py`

## Starting the Daemon
The daemon is what interfaces with JS8Call, and/or the TCP/IP Server. NOTE: JS8Call must be running before starting this daemon. A future update will include the ability to start and run js8call in a headless mode for unattended stations (Linux Only).

`bin/python daemon.py`

## Run Web Frontend
The web frontend is used to start the flask server, so the viewing and creating of posts is possible. In the future, it will be combined into the daemon.

`bin/python webview.py`

Direct browser to http://localhost:5000
