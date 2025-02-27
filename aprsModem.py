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
    LON = "4145.  N"
    LAT = "08818.  W"
    SYMBOL = "/l"
    COMMENT = 'MMBR Client https://kd9yqk.com/mmbr/index.php'

    KISS_HOST: str
    KISS_PORT: str
    kiss_protocol: kiss.KISSProtocol = None

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
            try:
                async for frame in self.kiss_protocol.read():
                    if callback:
                        await callback(frame)
                    else:
                        print('Message Received')
                        print(frame)
            except AttributeError:
                pass
                await asyncio.sleep(1)

    async def transmitter(self, interval=1.0):
        while True:
            try:
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
            except Exception as e:
                print(f'  * APRS - ERROR - {e}')
                pass
            await asyncio.sleep(interval)

    async def send_pos(self, delay=600):
        await asyncio.sleep(30)
        while True:
            try:
                m = {'src': f'{self.MYCALL}{self.SSID}',
                     'info': f'={self.LAT}{self.SYMBOL[:1]}{self.LON}{self.SYMBOL[1:]} {self.COMMENT}'}

                self.tx_buffer.append(m)
            except Exception as e:
                print(f'  * ARPS - POS EROR - {e}')
                pass
            await asyncio.sleep(delay)

    def setup(self, rx_callback=None):
        _loop = asyncio.get_event_loop()

        _rec = _loop.create_task(self.receiver(rx_callback))
        _tx = _loop.create_task(self.transmitter(interval=1.0))
        if self.pos_enabled:
            _pos = _loop.create_task(self.send_pos())
        else:
            _pos = None
        return _rec, _tx, _pos

    async def main(self):
        while True:
            await asyncio.sleep(1)
            if self.kiss_protocol is None or self.kiss_protocol.transport.is_closing():
                try:
                    transport, self.kiss_protocol = await kiss.create_tcp_connection(
                        host=self.KISS_HOST,
                        port=self.KISS_PORT
                    )
                    print(f'  * APRS -  Connected {transport.get_extra_info("peername")}')

                except ConnectionRefusedError:
                    print('  * APRS - Attempting to reconnecting in 5 seconds')
                    print(self.KISS_HOST)
                    await asyncio.sleep(5)
                else:
                    while not transport.is_closing():
                        await asyncio.sleep(1)
                    print(f'  * APRS -  Disconnected {transport.get_extra_info("peername")}')


if __name__ == "__main__":
    t = Radio(callsign='KD9YQK', host='192.168.1.103')
    asyncio.run(t.main())
