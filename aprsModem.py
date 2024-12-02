#!/usr/bin/env python3
import asyncio
from ax253 import Frame
import kiss
import aprs

aprs.__author__ = "KD9YQK"
aprs.__distribution__ = "kiss3_async.py"
aprs.__version__ = "1.00"


class Radio:
    MYCALL: str
    SSID: str
    PATH = ["WIDE1-1", "WIDE2-1"]
    LAT = "4145.  N"
    LON = "08818.  W"
    SYMBOL = "/l"
    COMMENT = 'Ham-Microblog Client https://github.com/KD9YQK/ham-microblog'

    KISS_HOST: str
    KISS_PORT: str
    kiss_protocol: kiss.KISSProtocol

    tx_buffer = []
    tx_en = True
    pos_enabled = True

    def __init__(self, callsign="MYCALL", ssid=0, host="localhost", port="8001"):
        self.MYCALL = callsign
        self.KISS_HOST = host
        self.KISS_PORT = port
        if ssid == 0:
            self.SSID = ''
        else:
            self.SSID = f'-{ssid}'

    async def receiver(self, callback=None):
        while True:
            async for frame in self.kiss_protocol.read():
                if callback:
                    await callback(frame)
                else:
                    print('Message Received')
                    print(frame)

    async def transmitter(self, interval=1.0):
        while True:
            if len(self.tx_buffer) > 0:
                msg = self.tx_buffer[0]
                self.tx_buffer.pop(0)
                frame = Frame.ui(
                    destination='ADZ666',
                    source=msg['src'],
                    path=self.PATH,
                    info=msg['info'],
                )
                if self.tx_en:
                    self.kiss_protocol.write(frame)

                # print(frame)
            await asyncio.sleep(interval)

    async def send_pos(self, delay=600):
        await asyncio.sleep(2)
        while True:
            m = {'src': f'{self.MYCALL}{self.SSID}', 'info': f'={self.LAT}{self.SYMBOL[:1]}{self.LON}{self.SYMBOL[1:]} {self.COMMENT}'}

            self.tx_buffer.append(m)
            await asyncio.sleep(delay)

    async def setup(self, rx_callback=None):
        transport, self.kiss_protocol = await kiss.create_tcp_connection(
            host=self.KISS_HOST,
            port=self.KISS_PORT,
        )
        print(f'Direwolf Connected {transport.get_extra_info("peername")}')
        _rec = asyncio.create_task(self.receiver(rx_callback))
        _tx = asyncio.create_task(self.transmitter(interval=1.0))
        if self.pos_enabled:
            _pos = asyncio.create_task(self.send_pos())
        else:
            _pos = None
        return _rec, _tx, _pos, transport

    async def main(self, rx_callback=None):
        _rec, _tx, _pos, _transport = await self.setup(rx_callback=rx_callback)
        while not _transport.is_closing():
            await asyncio.sleep(1)
        print("bye")



if __name__ == "__main__":
    t = Radio(callsign='KD9YQK', host='192.168.1.103')
    asyncio.run(t.main())
