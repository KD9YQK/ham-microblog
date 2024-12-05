import asyncio
import json
import db_functions
from tcpAPRSIS import get_aprs_pw

clients = []


class types:
    ERROR = 'error'
    ADD_BLOG = 'addblog'
    GET_CALLSIGN = 'getcallsign'
    GET_ALL_MSGS = 'getall'
    GET_MSG_TARGET = 'gettarget'


def process_buffer(data):
    try:
        decoded = json.loads(data)
    except json.decoder.JSONDecodeError:
        print('##########################')
        print('  * TCP/IP - ERROR JSONDecodeError')
        print(data)
        print("###########################")
        return
    ##################################
    # Process Commands
    ##################################
    cmd = decoded["type"]
    val = decoded['value']
    if cmd == types.ADD_BLOG:
        db_functions.add_blog(val['time'], val['callsign'], val['msg'])
    elif cmd == types.GET_CALLSIGN:
        db_functions.bulk_add_blog(val)
    elif cmd == types.GET_ALL_MSGS:
        db_functions.set_tcp_last()
        db_functions.bulk_add_blog(val)


class ClientProtocol(asyncio.Protocol):
    peername = None
    transport: asyncio.BaseTransport
    buffer = b''

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        print("  * TCP/IP - Connected {}".format(self.peername))
        clients.append(self)
        s = db_functions.get_settings()
        blog = db_functions.get_all_time(s['tcplast'])
        for b in blog:
            b.pop('gmt', None)
            b.pop('local', None)
            b.pop('mon', None)
        msg = {'type': types.GET_ALL_MSGS, 'call': s['callsign'], 'id': get_aprs_pw(s['callsign']),
               'value': {'time': s['tcplast'], 'data': blog}}
        db_functions.set_tcp_last()
        self.send_msg(json.dumps(msg).encode())

    def data_received(self, data):
        # For manual telnet.
        if data == b'\r\n':
            return
        self.buffer += data
        if b'<EOF>' in self.buffer:
            s = self.buffer.split(b'<EOF>', maxsplit=2)
            self.buffer = s[1]
            process_buffer(s[0])

    def send_msg(self, msg: bytes):
        client = clients[clients.index(self)]
        client.transport.write(msg)
        client.transport.write(b'<EOF>')

    def connection_lost(self, ex):
        print("  * TCP/IP - Disconnected {}".format(self.peername))
        clients.remove(self)


client_tcp: (asyncio.BaseTransport, asyncio.BaseProtocol) = None


async def do_connect():
    while True:
        if len(clients) > 0:
            await asyncio.sleep(1)
            continue
        try:
            _loop = asyncio.get_event_loop()
            _client_tcp = await _loop.create_connection(ClientProtocol, '157.230.203.194', 8808)
        except OSError:
            await asyncio.sleep(5)
        else:
            await asyncio.sleep(1)
            # break


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(do_connect())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        exit()
