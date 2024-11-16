# js8-microblog
An attempt at implementing a micro-blog into js8call via API

## Current State
THIS PROJECT IS A WIP AND NOT FULLY DEVELOPED!

The Modem works, but needs to be built upon. Currently only for testing purposes.

The web front-end is fleshed out and near fully functional. Need to interface with the modem, and finish a few minor features like removing 'monitoring' stations from list, and finishing creating a new message.

## Install
```
git clone https://github.com/KD9YQK/js8-microblog.git
python -m venv js8-microblog
cd js8-microblog
bin/pip install pyjs8call flask
```
## Run Once to build DB
`bin/python db_functions.py`

This creates the database and builds the tables. It also fills in with some dummy data for testing.  In the future, this will be changed to a setup file.

## Run JS8Call Modem Daemon
`bin/python daemon.py`

## Run Web Frontend
`bin/python webview.py`

Direct browser to http://localhost:5000
