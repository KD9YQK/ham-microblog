import db_functions
import js8Modem
import tcpModem
import asyncio
import json
import threading
import webview

class Daemon:
    tcpmodem: tcpModem.ClientProtocol
    js8modem: js8Modem.JS8modem
    settings:dict

    def process_outgoing(self):
        msgs = db_functions.get_outgoing_posts()
        for m in msgs:
            if self.settings['js8modem']:
                self.js8modem.broadcast_post(m)
            if self.settings['tcpmodem']:
                self.tcpmodem.send_msg(json.dumps(m).encode())

    def start_tcpmodem(self, host='127.0.0.1', port=8888):
        try:
            loop = asyncio.get_event_loop()
            coro = loop.create_connection(tcpModem.ClientProtocol, host=host, port=port)
            _server = loop.run_until_complete(coro)
            self.tcpmodem = tcpModem.clients[0]

            #data = {"type": tcpModem.types.GET_ALL_MSGS, "value": {"callsign": "KD9YQK"}}
            #self.tcpmodem.send_msg(json.dumps(data).encode())
        except ConnectionRefusedError:
            print("TCP/IP ERROR - Unable to connect to TCP Server")
            return
        except KeyboardInterrupt:
            exit()
        #try:
        #    loop.run_forever()
        #except KeyboardInterrupt:
        #    exit()

    def start_js8modem(self, host='127.0.0.1', port=2442):
        try:
            self.js8modem = js8Modem.JS8modem(host=host, port=port)
            self.js8modem.start()
            while self.js8modem.js8call.online:
                pass
        except RuntimeError:
            print("JS8Call ERROR - JS8Call application not installed or connection issue")
            return
        except KeyboardInterrupt:
            exit()


if __name__ == "__main__":
    settings = db_functions.get_settings()
    daemon = Daemon()
    daemon.settings = settings
    # Web Frontend Thread
    threads = [threading.Thread(
        target=lambda: webview.app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False))]
    # TCP Modem Thread
    if settings['tcpmodem']:
        threads.append(threading.Thread(target=daemon.start_tcpmodem(), args=()))
    # APRS Modem Thread
    if settings['aprsmodem']:
        pass
    # JS8Call Modem Thread
    if settings['js8modem']:
        threads.append(threading.Thread(target=daemon.start_js8modem(), args=()))

    for t in threads:
        t.start()
    for t in threads:
        t.join()
