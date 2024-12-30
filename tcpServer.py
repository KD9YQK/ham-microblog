import asyncio
import json
import os.path
import db_functions
from js8Modem import Command
from tcpModem import types
import tcpAPRSIS
from ax253 import Frame

clients = []


def close():
    for c in clients:
        c.transport.close()


class tcpServer:
    aprs: tcpAPRSIS.APRSIS

    async def main(self):
        self.aprs = tcpAPRSIS.APRSIS('HAMBLG')
        _a, _b = await self.aprs.setup(self.aprs_rx_callback)
        while True:
            await self.aprs.send_pos(600)

    async def aprs_rx_callback(self, frame: Frame):
        print(f' * {frame}')
        frm = str(frame)
        callsign_ssid = str(frame.source)
        callsign = callsign_ssid
        if '-' in callsign:
            callsign = callsign.split('-')[0]
        frm = frm.split('::')[1]
        target = frm.split(':')[0].strip()
        if target != 'HAMBLG':
            # print(frame)
            return
        msg = frm.split(':')[1]
        msgid = ""
        if '{' in msg:
            msgid = msg.split('{')[1]
            msg = msg.split('{')[0]
        tx_msg = {'src': target, 'info': f':{tcpAPRSIS.pad_callsign(callsign_ssid)}:ack{msgid}'}
        # self.aprs.tx_buffer.append(tx_msg)
        cmd = msg.split(' ')[0]
        if cmd == Command.GET_POSTS:
            post = db_functions.get_callsign_blog(msg.split(' ')[1], 1)
            if len(post) < 1:
                tx_msg[
                    'info'] = f':{tcpAPRSIS.pad_callsign(callsign_ssid)}:No Posts available for {msg.split(" ")[1]}'
            else:
                tx_msg['info'] = f':{tcpAPRSIS.pad_callsign(callsign_ssid)}:{Command.POST} {post[0]["callsign"]} {post[0]["time"]} {post[0]["msg"]}'
            self.aprs.tx_buffer.append(tx_msg)
        elif cmd == Command.POST:
            try:
                mtime = int(msg.split(' ')[1])
                post = msg.split(str(mtime))[1].strip()
                db_functions.add_blog(mtime, callsign, post)
            except ValueError:
                mtime = int(msg.split(' ')[2])
                call = msg.split(' ')[1]
                post = msg.split(str(mtime))[1].strip()
                db_functions.add_blog(mtime, call, post)

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
            print(data)
            try:
                decoded = json.loads(data)
            except json.decoder.JSONDecodeError:
                print('ERROR - JSONDecodeError')
                retval = {"type": types.ERROR, "value": "JSONDecodeError"}
                self.send_self(json.dumps(retval).encode())
                return
            ##################################
            # Process Commands
            ##################################
            cmd = decoded["type"]
            val: dict = decoded['value']
            call: str = decoded['call']
            aprs_id: int = decoded['id']
            if aprs_id != tcpAPRSIS.get_aprs_pw(call.upper()):
                c: tcpServer.ServerProtocol = clients[clients.index(self)]
                c.transport.close()
                print(f'Kicked {call} Bad PW. Was:{aprs_id} should be {tcpAPRSIS.get_aprs_pw(call.upper())}')
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
                db_functions.bulk_add_blog(val['data'])
                blog = db_functions.get_all_time(val['time'])
                for b in blog:
                    b.pop('gmt', None)
                    b.pop('local', None)
                    b.pop('mon', None)
                retval = {"type": types.GET_ALL_MSGS, "value": blog}
                self.send_self(json.dumps(retval).encode())
                retval = {"type": types.GET_ALL_MSGS, "value": val['data']}
                self.send_all(json.dumps(retval).encode())
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
    print('')
    print('#########################################')
    print('#  MMBR TCP/IP Server')
    print('#  Bob KD9YQK - http://www.kd9yqk.com/')
    print('#########################################')
    if not os.path.exists('mmgr.db'):
        db_functions.build_db()
        print('Database created')

    tcp = tcpServer()
    loop = asyncio.get_event_loop()
    coro = loop.create_server(tcp.ServerProtocol, port=8808)
    server = loop.run_until_complete(coro)
    aprs = loop.create_task(tcp.main())

    print("Serving on {}".format(server.sockets[0].getsockname()))
    # for socket in server.sockets:
    #    print("serving on {}".format(socket.getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        close()
        exit()
