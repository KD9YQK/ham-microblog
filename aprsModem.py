#!/usr/bin/env python3
import asyncio
from ax253 import Frame
import kiss
import aprs

aprs.__author__ = "KD9YQK"
aprs.__distribution__ = "kiss3_async.py"
aprs.__version__ = "1.00"


class igate_params:
    # host = "noam.aprs2.net"
    host = '205.209.228.99'
    port = 14580
    password = ""
    enabled = False
    tx_enabled = False
    filter_dist = "5000"
    filter_params = "t/m"
    filter = ""

    def set_igate_filter(self, _callsign=''):
        # self.filter = f"{self.filter_params}/{callsign}/{self.filter_dist}"
        self.filter = f"{self.filter_params}"#/{self.filter_dist}"


class Radio:
    MYCALL: str
    SSID: str
    LAT = "4145.  N/"
    LON = "08818.  Wl"
    COMMENT = 'Testing some code'

    KISS_HOST: str
    KISS_PORT: str
    kiss_protocol: kiss.KISSProtocol

    tx_buffer = []
    tx_en = True
    pos_enabled = True

    igate_protocol = None
    ig = igate_params()

    def __init__(self, callsign="MYCALL", host="localhost", port="8001", igate_pass=""):
        self.MYCALL = callsign
        self.KISS_HOST = host
        self.KISS_PORT = port
        self.ig.password = igate_pass
        self.ig.set_igate_filter(_callsign=callsign)
        if igate_pass == "":
            self.ig.enabled = False
        else:
            self.ig.enabled = True

    async def igate_rec(self, callback=None):
        while True:
            async for frame in self.igate_protocol.read():
                if callback:
                    callback(frame)
                else:
                    print("igate")
                    print(frame)

    async def receiver(self, callback=None):
        while True:
            async for frame in self.kiss_protocol.read():
                if callback:
                    callback(frame)
                else:
                    print('Message Received')
                    print(frame)

    async def transmitter(self, interval=1.0):
        while True:
            if len(self.tx_buffer) > 0:
                msg = self.tx_buffer[0]
                self.tx_buffer.pop(0)
                frame = Frame.ui(
                    destination=msg['dest'],
                    source=msg['src'],
                    path=["WIDE2-1"],
                    info=msg['info'],
                )
                if self.tx_en:
                    self.kiss_protocol.write(frame)

                if self.ig.enabled and self.ig.tx_enabled:
                    self.igate_protocol.write(frame)
                print('')
                print(frame)
                print('Command>>', flush=False)
            await asyncio.sleep(interval)

    async def send_pos(self, delay=600):
        await asyncio.sleep(10)
        while True:
            msg = {
                'src': 'KD9YQK-10',
                'dest': 'WIDE1-1',
                'info': f'={self.LAT}{self.LON}{self.COMMENT}'
            }
            self.tx_buffer.append(msg)
            await asyncio.sleep(delay)

    async def setup(self, rx_callback=None, igrx_callback=None):
        print(f'Connecting to Direwolf {self.KISS_HOST}:{self.KISS_PORT}')
        transport, self.kiss_protocol = await kiss.create_tcp_connection(
            host=self.KISS_HOST,
            port=self.KISS_PORT,
        )
        print('Connected!')
        if self.ig.enabled:
            print("Connecting to aprs-is")
            transport, self.igate_protocol = await aprs.create_aprsis_connection(
                host=self.ig.host,
                port=self.ig.port,
                user=self.MYCALL,
                passcode=self.ig.password,
                command=f'filter {self.ig.filter}',
            )
            print('Connected!')
            _rec = asyncio.create_task(self.receiver(rx_callback))
            _tx = asyncio.create_task(self.transmitter(interval=1.0))
            if self.ig.enabled:
                _ig = asyncio.create_task(self.igate_rec(igrx_callback))
            else:
                _ig = None
            if self.pos_enabled:
                _pos = asyncio.create_task(self.send_pos())
            else:
                _pos = None
            return _rec, _tx, _ig, _pos

    async def main(self):
        _rec, _tx, _ig, _pos = await self.setup()
        c = 590
        while True:
            await asyncio.sleep(1)
            c += 1
            if c == 600:
                c = 0
                msg = {
                    'src': 'KD9YQK-10',
                    'dest': 'ADZ666',  # TEST
                    'info': f'={self.LAT}N/08818.  Wl Testing some python code'
                }
                self.tx_buffer.append(msg)
                print(self.tx_buffer)
                print("Message Sent")
