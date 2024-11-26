import asyncio
import json
import db_functions
from aprsModem import get_aprs_pw

clients = []


class types:
    ERROR = 'error'
    ADD_BLOG = 'addblog'
    GET_CALLSIGN = 'getcallsign'
    GET_ALL_MSGS = 'getall'


class ClientProtocol(asyncio.Protocol):
    peername = None
    transport: asyncio.BaseTransport
    buffer = b''

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        print("TCP/IP connection_made: {}".format(self.peername))
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
            self.process_buffer(s[0])

    def process_buffer(self, data):
        try:
            decoded = json.loads(data)
        except json.decoder.JSONDecodeError:
            print('##########################')
            print('TCP/IP ERROR - JSONDecodeError')
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

    def send_msg(self, msg: bytes):
        client = clients[clients.index(self)]
        client.transport.write(msg)
        client.transport.write(b'<EOF>')

    def connection_lost(self, ex):
        print("TCP/IP connection_lost: {}".format(self.peername))
        clients.remove(self)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(ClientProtocol, host="157.230.203.194", port=8888)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        exit()
