import pickle
from quart import request, render_template
import ax253
import db_functions
import js8Modem
from js8Modem import Command
import tcpModem
import asyncio
import json
from tcpAPRSIS import get_aprs_pw, pad_callsign
import aprsModem
import webview

workers = []


def startup():
    global workers
    settings = db_functions.get_settings()
    daemon.settings = settings
    # JS8Call Modem Loop
    if settings['js8modem']:
        with open('tmp/js8.spots', 'wb') as f:
            pickle.dump({settings['callsign']: {'hear_blog': [], 'hear_not': [], 'heard_blog': [], 'heard_not': [],
                                                'blogger': True}}, f)
        workers.append(loop.create_task(daemon.start_js8modem(settings['js8host'], settings['js8port'])))

    # TCP Modem Loop
    if settings['tcpmodem']:
        try:
            workers.append(loop.create_task(tcpModem.do_connect()))
        except ConnectionRefusedError:
            print("  * TCP/IP - ERROR Unable to connect to TCP Server")

    # APRS Modem Loop
    if settings['aprsmodem']:
        daemon.aprsmodem = aprsModem.Radio(settings['callsign'], settings['aprsssid'], settings['aprshost'],
                                           settings['aprsport'])
        daemon.aprsmodem.LAT = settings['lat']
        daemon.aprsmodem.LON = settings['lon']
        try:
            _rx, _tx, _pos = daemon.aprsmodem.setup(rx_callback=daemon.rx_aprs_callback)
            workers.append(loop.create_task(daemon.aprsmodem.main()))
            workers.append(_rx)
            workers.append(_tx)
            workers.append(_pos)
        except Exception as e:
            print(f"  * APRS - ERROR - {e}")


class Daemon:
    tcpmodem: tcpModem.ClientProtocol
    js8modem: js8Modem.JS8modem
    aprsmodem: aprsModem.Radio
    settings: dict

    async def process_outgoing(self):

        while True:
            js8on = False
            tcpon = False
            aprson = False
            try:
                if self.settings['js8modem'] and self.js8modem is not None:
                    if self.js8modem.js8call.js8call.app.is_running():
                        js8on = True
            except AttributeError:
                pass
            try:
                if self.settings['aprsmodem'] and self.aprsmodem.kiss_protocol is not None:
                    if not self.aprsmodem.kiss_protocol.transport.is_closing():
                        aprson = True
            except AttributeError:
                pass
            try:
                if self.settings['tcpmodem']:
                    if not self.tcpmodem.transport.is_closing():
                        tcpon = True
            except AttributeError:
                pass

            if len(tcpModem.clients) > 0:
                self.tcpmodem = tcpModem.clients[0]
            await asyncio.sleep(1)
            msgs = db_functions.get_outgoing_posts()

            for m in msgs:
                tcp_msg = {'call': self.settings['callsign'], 'id': get_aprs_pw(self.settings['callsign'])}
                if m["command"] == tcpModem.types.ADD_BLOG:
                    if self.settings['js8modem'] and js8on:
                        self.js8modem.broadcast_post(m)
                    if self.settings['tcpmodem'] and tcpon:
                        tcp_msg['type'] = tcpModem.types.ADD_BLOG
                        tcp_msg['value'] = m
                        self.tcpmodem.send_msg(json.dumps(tcp_msg).encode())
                    if self.settings['aprsmodem'] and aprson:
                        tx_msg = {'src': f"{self.settings['callsign']}-{self.settings['aprsssid']}",
                                  'info': f':{pad_callsign("HAMBLG")}:{Command.POST} {m["time"]} {m["msg"]}'}
                        self.aprsmodem.tx_buffer.append(tx_msg)
                elif m["command"] == tcpModem.types.GET_ALL_MSGS:
                    if self.settings['js8modem'] and js8on:
                        self.js8modem.get_posts()
                    if self.settings['tcpmodem'] and tcpon:
                        s: dict = db_functions.get_settings()
                        tcp_msg['type'] = tcpModem.types.GET_ALL_MSGS
                        tmp: int = s['tcplast']
                        tcp_msg['value'] = dict({'time': tmp})
                        self.tcpmodem.send_msg(json.dumps(tcp_msg).encode())
                elif m["command"] == tcpModem.types.GET_CALLSIGN:
                    if self.settings['js8modem'] and js8on:
                        self.js8modem.get_posts_callsign(m['callsign'])
                    if self.settings['tcpmodem'] and tcpon:
                        tcp_msg['type'] = tcpModem.types.GET_CALLSIGN
                        tcp_msg['value'] = {'callsign': m['callsign']}
                        self.tcpmodem.send_msg(json.dumps(tcp_msg).encode())
                    if self.settings['aprsmodem'] and aprson:
                        tx_msg = {'src': f"{self.settings['callsign']}-{self.settings['aprsssid']}",
                                  'info': f':{pad_callsign("HAMBLG")}:{Command.GET_POSTS} {m["callsign"]}'}
                        self.aprsmodem.tx_buffer.append(tx_msg)
                elif m["command"] == tcpModem.types.GET_MSG_TARGET:
                    if self.settings['js8modem'] and js8on:
                        self.js8modem.get_posts_callsign(dest=m['callsign'], callsign=m['msg'])

    async def rx_aprs_callback(self, frame: ax253.Frame):
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
        except IndexError:
            return
        except Exception as e:
            print(f'  * APRS - ERROR - {e}')
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


@webview.app.route("/settings", methods=['GET', 'POST'])
async def setting():
    settings = db_functions.get_settings()
    # print(settings)
    if request.method == 'POST':
        data = await request.form
        js8En = False
        aprsEn = False
        tcpEn = False
        if 'js8modem' in data.keys():
            js8En = True
        if 'aprsmodem' in data.keys():
            aprsEn = True
        if 'tcpmodem' in data.keys():
            tcpEn = True
        db_functions.set_settings(callsign=data['callsign'], js8modem=js8En, js8host=data['js8host'],
                                  js8port=int(data['js8port']), js8group=data['js8group'], aprsmodem=aprsEn,
                                  aprshost=data['aprshost'], aprsport=int(data['aprsport']),
                                  aprs_ssid=int(data['aprsssid']), tcpmodem=tcpEn, timezone=data['timezone'].lower(),
                                  lat=data['lat'], lon=data['lon'])
        settings = db_functions.get_settings()
        daemon.settings = settings
        _loop = asyncio.get_event_loop()
        _loop.create_task(restart())
        return await render_template("settings.html", settings=settings, saved=True)
    return await render_template("settings.html", settings=settings, saved=False)


async def restart():
    print('Restarting')
    global workers
    await asyncio.sleep(3)
    for w in workers:
        t = 1
        while not w.done():
            t += 1
            w.cancel()
            await asyncio.sleep(1)
    workers = []
    try:
        daemon.tcpmodem.transport.close()
    except AttributeError:
        pass
    try:
        daemon.aprsmodem.kiss_protocol.transport.close()
        daemon.aprsmodem.kiss_protocol = None
    except AttributeError:
        pass
    try:
        daemon.js8modem.js8call.stop(False)
    except AttributeError:
        pass
    await asyncio.sleep(1)
    try:
        startup()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    print('')
    print('#########################################')
    print('#  Ham Microblog Daemon')
    print('#  Bob KD9YQK - https://www.kd9yqk.com/')
    print('#########################################')
    try:
        daemon = Daemon()

        loop = asyncio.new_event_loop()

        # Outgoing Messages Loop
        listen = loop.create_task(daemon.process_outgoing())
        startup()
        web = loop.run_until_complete(webview.app.run_task(host='0.0.0.0'))

        # Start All Loops
        loop.run_forever()
    except KeyboardInterrupt:
        exit()
