import asyncio
import json
import db_functions
from tcpModem import types

clients = []


class ServerProtocol(asyncio.Protocol):
    peername = None
    transport: asyncio.BaseTransport
    buffer: bytes = b''

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info("peername")
        print("connection_made: {}".format(self.peername))
        clients.append(self)

    def data_received(self, data):
        print(data)
        # For manual telnet.
        if data == b'\r\n':
            return
        # Actual code starts here
        self.buffer += data
        if b'<EOF>' in self.buffer:
            s = self.buffer.split(b'<EOF>', maxsplit=2)
            self.buffer = s[1]
            self.process_buffer(s[0])

    def process_buffer(self, data):
        try:
            decoded = json.loads(data)
        except json.decoder.JSONDecodeError:
            print('ERROR - JSONDecodeError')
            retval = {"type": types.ERROR, "value": "JSONDecodeError"}
            print(data)
            self.send_self(json.dumps(retval).encode())
            return
        ##################################
        # Process Commands
        ##################################
        cmd = decoded["type"]
        val: dict = decoded['value']
        if cmd == types.ADD_BLOG:
            db_functions.add_blog(val['time'], val['callsign'], val['msg'])
            self.send_all(data)
        elif cmd == types.GET_CALLSIGN:
            blog = db_functions.get_callsign_blog(val['callsign'], 0)
            for b in blog:
                b.pop('gmt', None)
                b.pop('local', None)
                b.pop('mon', None)
            retval = {"type": types.GET_CALLSIGN, "value": blog}
            self.send_self(json.dumps(retval).encode())
        elif cmd == types.GET_ALL_MSGS:
            blog = db_functions.get_all_time(val['time'])
            for b in blog:
                b.pop('gmt', None)
                b.pop('local', None)
                b.pop('mon', None)
            retval = {"type": types.GET_ALL_MSGS, "value": blog}
            self.send_self(json.dumps(retval).encode())
        else:
            retval = {"type": types.ERROR, "value": "UnknownType"}
            self.send_self(json.dumps(retval).encode())

    def send_self(self, msg: bytes):
        client = clients[clients.index(self)]
        client.transport.write(msg)
        client.transport.write(b'<EOF>')

    def send_all(self, msg: bytes):
        for client in clients:
            if client is not self:
                client.transport.write(msg)
                client.transport.write(b'<EOF>')

    def connection_lost(self, ex):
        print("connection_lost: {}".format(self.peername))
        clients.remove(self)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_server(ServerProtocol, port=8888)
    server = loop.run_until_complete(coro)
    for socket in server.sockets:
        print("serving on {}".format(socket.getsockname()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        exit()
