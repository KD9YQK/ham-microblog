import ax253
import db_functions
import js8Modem
from js8Modem import Command
import tcpModem
import asyncio
import json
from tcpAPRSIS import get_aprs_pw, pad_callsign
import aprsModem


class Daemon:
    tcpmodem: tcpModem.ClientProtocol
    js8modem: js8Modem.JS8modem
    aprsmodem: aprsModem.Radio
    settings: dict

    async def process_outgoing(self):
        if len(tcpModem.clients) > 0:
            self.tcpmodem = tcpModem.clients[0]
        while True:
            await asyncio.sleep(1)
            msgs = db_functions.get_outgoing_posts()
            for m in msgs:
                tcp_msg = {'call': self.settings['callsign'], 'id': get_aprs_pw(self.settings['callsign'])}
                if m["command"] == tcpModem.types.ADD_BLOG:
                    if self.settings['js8modem']:
                        self.js8modem.broadcast_post(m)
                    if self.settings['tcpmodem']:
                        tcp_msg['type'] = tcpModem.types.ADD_BLOG
                        tcp_msg['value'] = m
                        self.tcpmodem.send_msg(json.dumps(tcp_msg).encode())
                    if self.settings['aprsmodem']:
                        tx_msg = {'src': f"{self.settings['callsign']}-{self.settings['aprsssid']}",
                                  'info': f':{pad_callsign("HAMBLG")}:{Command.POST} {m["time"]} {m["msg"]}'}
                        self.aprsmodem.tx_buffer.append(tx_msg)
                elif m["command"] == tcpModem.types.GET_ALL_MSGS:
                    if self.settings['js8modem']:
                        self.js8modem.get_posts()
                    if self.settings['tcpmodem']:
                        s: dict = db_functions.get_settings()
                        tcp_msg['type'] = tcpModem.types.GET_ALL_MSGS
                        tmp: int = s['tcplast']
                        tcp_msg['value'] = dict({'time': tmp})
                        self.tcpmodem.send_msg(json.dumps(tcp_msg).encode())
                elif m["command"] == tcpModem.types.GET_CALLSIGN:
                    if self.settings['js8modem']:
                        self.js8modem.get_posts_callsign(m['callsign'])
                    if self.settings['tcpmodem']:
                        tcp_msg['type'] = tcpModem.types.GET_CALLSIGN
                        tcp_msg['value'] = {'callsign': m['callsign']}
                        self.tcpmodem.send_msg(json.dumps(tcp_msg).encode())
                    if self.settings['aprsmodem']:
                        tx_msg = {'src': f"{self.settings['callsign']}-{self.settings['aprsssid']}",
                                  'info': f':{pad_callsign("HAMBLG")}:{Command.GET_POSTS} {m["callsign"]}'}
                        self.aprsmodem.tx_buffer.append(tx_msg)
                elif m["command"] == tcpModem.types.GET_MSG_TARGET:
                    if self.settings['js8modem']:
                        self.js8modem.get_posts_callsign(dest=m['callsign'], callsign=m['msg'])

    async def rx_aprs_callback(self, frame: ax253.Frame):
        # return
        frm = str(frame)
        callsign_ssid = str(frame.source)
        callsign = callsign_ssid
        if '-' in callsign:
            callsign = callsign.split('-')[0]
        try:  # If it isn't a message, or parsing isn't correct.
            frm = frm.split('::')[1]
            target = frm.split(':')[0].strip()
            msg = frm.split(':')[1]
            cmd = msg.split(' ')[0]
        except:
            return

        if cmd == Command.POST:
            try:
                mtime = int(msg.split(' ')[1])
                post = msg.split(str(mtime))[1].strip()
                db_functions.add_blog(mtime, callsign, post)
            except ValueError:
                mtime = int(msg.split(' ')[2])
                call = msg.split(' ')[1]
                post = msg.split(str(mtime))[1].strip()
                db_functions.add_blog(mtime, call, post)

        if self.settings['callsign'] not in target:
            return
        tx_msg = {'src': f"{self.settings['callsign']}-{self.settings['aprsssid']}"}
        if '{' in msg:
            msgid = msg.split('{')[1]
            msg = msg.split('{')[0]
            tx_msg['info'] = f':{pad_callsign(callsign_ssid)}:ack{msgid}'
            self.aprsmodem.tx_buffer.append(tx_msg)

        if cmd == Command.GET_POSTS:
            post = db_functions.get_callsign_blog(msg.split(' ')[1], 1)
            tx_msg['info'] = f':{pad_callsign(callsign_ssid)}:{Command.POST} ' \
                             f'{post["callsign"]} {post["time"]} {post["msg"]}'
            self.aprsmodem.tx_buffer.append(tx_msg)

    async def start_js8modem(self, host='127.0.0.1', port=2442):
        try:
            self.js8modem = js8Modem.JS8modem(host=host, port=port)
            while True:
                # await asyncio.sleep(.1)
                self.js8modem.js8call.js8call.app._find_running_js8call_process()
                if self.js8modem.js8call.js8call.app.is_running():
                    if not self.js8modem.js8call.connected():
                        try:
                            self.js8modem.js8call.js8call.app._js8call_proc = None
                            self.js8modem.start()
                        except AttributeError:
                            pass
                await asyncio.sleep(1)

        except RuntimeError:
            print("  * JS8 - ERROR Application not installed or connection issue")
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    print('')
    print('#########################################')
    print('#  Ham Microblog Daemon')
    print('#  Bob KD9YQK - https://www.kd9yqk.com/')
    print('#########################################')
    try:
        settings = db_functions.get_settings()
        daemon = Daemon()
        daemon.settings = settings

        _loop = asyncio.get_event_loop()
        _listen = _loop.create_task(daemon.process_outgoing())

        threads = []
        # JS8Call Modem Thread
        if settings['js8modem']:
            # threads.append(threading.Thread(target=daemon.start_js8modem(settings['js8host'], settings['js8port']),
            #                                args=()).start())
            _js8 = _loop.create_task(daemon.start_js8modem(settings['js8host'], settings['js8port']))

        # TCP Modem Thread
        if settings['tcpmodem']:
            tcphost = '157.230.203.194'
            tcpport = 8808
            try:
                # coro = _loop.create_connection(tcpModem.ClientProtocol, host=tcphost, port=tcpport)
                # _server = _loop.run_until_complete(coro)
                _server = _loop.create_task(tcpModem.do_connect())
                # daemon.tcpmodem = tcpModem.clients[0]
            except ConnectionRefusedError:
                print("  * TCP/IP - ERROR Unable to connect to TCP Server")

        # APRS Modem Thread
        if settings['aprsmodem']:
            daemon.aprsmodem = aprsModem.Radio(settings['callsign'], settings['aprsssid'], settings['aprshost'],
                                               settings['aprsport'])
            daemon.aprsmodem.LAT = settings['lat']
            daemon.aprsmodem.LON = settings['lon']
            _a = _loop.create_task(daemon.aprsmodem.main(daemon.rx_aprs_callback))
        # threads.append(threading.Thread(target=_loop.run_forever()).start())
        _loop.run_forever()
    except KeyboardInterrupt:
        exit()
