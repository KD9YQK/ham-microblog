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
```
git clone https://github.com/KD9YQK/ham-microblog.git
python3 -m venv ham-microblog
cd ham-microblog
```

Windows

```
Scripts\pip install pyjs8call flask aprs3 ax253 kiss3
```

Linux

```
bin/pip3 install pyjs8call flask aprs3 ax253 kiss3
```

## Run Once to build DB and fill in initial settings
This creates the database and builds the tables. It also asks a series of questions like callsign, which 'modems' to enable, and how time is displayed.

Windows

```
Scripts\python setup.py
```

Linux

```
bin/python3 setup.py
```

## Starting the Daemon
The daemon is what interfaces with JS8Call, and/or the TCP/IP Server. NOTE: JS8Call must be running before starting this daemon. A future update will include the ability to start and run js8call in a headless mode for unattended stations (Linux Only).

Windows

```
Scripts\python3 daemon.py
```

Linux

```
bin/python3 daemon.py
```

## Starting the Web Frontend
The web frontend currently uses Flask, and due to it's 'blocking' nature, cannot be run in same script as the daemon. I plan to overhaul in a future update to use aiohttp, which 'should' allow everything to play nice together.

Windows

```
Scripts\python3 webview.py
```

Linux

```
bin/python3 webview.py
```

Direct browser to http://localhost:5000
