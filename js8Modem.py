import time

import pyjs8call
import db_functions
import pickle


class Command:  # Commands. Note the space.
    GET_POSTS = 'POST?'
    POST = 'POST'


def num_to_abc(num: int):  # Convert an integer to a string of Letters
    # Numbers transmit slower than letters in JS8Call.
    numVal = {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E', '6': 'F', '7': 'G', '8': 'H', '9': 'I',
              '0': 'J'}  # Convert Numbers to Letters
    tmp = str(num)
    retval = ''
    for l in tmp:
        retval += numVal[l]
    return retval


def abc_to_num(abc: str):  # Convert a string of Letters Back to Numbers
    abcVal = {'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5', 'F': '6', 'G': '7', 'H': '8', 'I': '9',
              'J': '0'}  # Convert Letters back to Numbers
    tmp = ''
    for l in abc:
        tmp += abcVal[l]
    return int(tmp)


class modAppMon(pyjs8call.AppMonitor):

    def _monitor(self):
        """Application monitoring thread."""
        while self._parent.online:
            if not self.is_running() and not self._parent._client.restarting:
                if self.restart:
                    # restart the whole system and reconnect
                    self._parent._client.restart()
                else:
                    # exit if the js8call application is closed
                    self._parent._client.stop()

            time.sleep(1)


class modClient(pyjs8call.Client):
    def stop(self, terminate_js8call=True):
        self.online = False
        self.exit_tasks()
        self.js8call.app.terminate_js8call = False
        self.js8call.stop()
        print('  * JS8 - Disconnected')


class JS8modem:
    js8call: pyjs8call.Client
    settings = {}
    HOST = "127.0.0.1"
    PORT = 2442
    _dummy = None

    def __init__(self, host='127.0.0.1', port=2442):
        self.HOST = host
        self.PORT = port
        self.js8call = modClient(host=host, port=port)
        self.js8call.js8call.app = modAppMon(self.js8call.js8call.app._parent)
        self.js8call.callback.register_incoming(self._incoming_callback)
        self.js8call.callback.register_spots(self._new_spots_callback)
        self.settings = db_functions.get_settings()
        for i in ['@BLOG', self.settings['js8group']]:
            if i not in self.js8call.settings.get_groups_list():
                self.js8call.settings.add_group(i)
                print(f'  * JS8 - Added {i} to Group list.')

    def start(self):
        self.js8call.start()
        print(f"  * JS8 - Connected ({self.HOST}, {self.PORT})")
        self.js8call.inbox.enable()
        with open('tmp/js8.spots', 'wb') as f:
            pickle.dump({self.js8call.settings.get_station_callsign(True): {'hear_blog': [], 'hear_not': [],
                                                                            'heard_blog': [], 'heard_not': [],
                                                                            'blogger': True}}, f)

    ###########################################
    # Callbacks
    ###########################################
    def _incoming_callback(self, msg):  # Test callback when any msg is received
        if '...' in msg.text:
            print(f'  * JS8 - ERROR Incomplete MSG - {msg.text}')
            return
        c = msg.text.split(' ')[0]
        if msg.destination in ['@BLOG', self.js8call.settings.get_station_callsign(), self.settings['js8group'],
                               self.js8call.settings.get_groups_list()]:
            if c == Command.GET_POSTS:
                self._get_posts(msg)
        if c == Command.POST:
            self._add_post(msg)

    def _new_spots_callback(self, spots):  # Callback when a new spot is received.
        for spot in spots:
            if spot.grid in (None, ''):
                _grid = ' '
            else:
                _grid = ' (' + spot.grid + ') '
            print('\t--- Spot: {}{}@ {} Hz\t{}L'.format(spot.origin, _grid, spot.offset,
                                                        time.strftime('%x %X', time.localtime(spot.timestamp))))

        allstn = {}
        bloggers = db_functions.get_bloggers()
        h_blog = []
        h_not = []
        hear = self.js8call.station_hearing(age=60)
        for stn in hear:
            if stn in bloggers:
                h_blog.append(stn)
            else:
                h_not.append(stn)
        tmp = {'hear_blog': h_blog, 'hear_not': h_not, 'blogger': True}
        h_blog = []
        h_not = []
        for stn in self.js8call.station_heard_by(age=60):
            if stn in bloggers:
                h_blog.append(stn)
            else:
                h_not.append(stn)
        tmp = tmp | {'heard_blog': h_blog, 'heard_not': h_not}
        allstn[self.js8call.settings.get_station_callsign()] = tmp

        for stn in hear:
            h_blog = []
            h_not = []
            for h in self.js8call.station_heard_by(station=stn, age=60):
                if h in bloggers:
                    h_blog.append(h)
                else:
                    h_not.append(h)
            tmp = {'heard_blog': h_blog,
                   'heard_not': h_not,
                   'blogger': False}
            if stn in bloggers:
                tmp['blogger'] = True
            h_blog = []
            h_not = []
            for h in self.js8call.station_hearing(station=stn, age=60):
                if h in bloggers:
                    h_blog.append(h)
                else:
                    h_not.append(h)
                tmp['hear_blog'] = h_blog
                tmp['hear_not'] = h_not
            allstn[stn] = tmp

        with open('tmp/js8.spots', 'wb') as f:
            pickle.dump(allstn, f)

    #####################################
    # Callback Responses
    #####################################
    def _get_posts(self, msg):  # Callback when the POST? command is received
        # do not respond in the following cases:
        if (
                self.js8call.settings.autoreply_confirmation_enabled() or
                msg.text in (None, '')  # message text is empty
        ):
            return
        cut = msg.text.split(' ')  # [Command, ?Callsign?]
        if len(cut) == 2:  # Callsign found, return last record from callsign
            blog = db_functions.get_callsign_blog(cut[1], 1)
        elif len(cut) == 1:  # Only Command, return own last record
            blog = db_functions.get_callsign_blog(self.js8call.settings.get_station_callsign(), 1)
        else:  # There shouldn't be more than 2. Something is wrong.
            return
        if len(blog) < 1:
            return
        prefix = f'{Command.POST}'
        if len(cut) == 2:
            prefix += f'{blog[0]["callsign"]} '
        message = f"{prefix} {num_to_abc(blog[0]['time'])} {blog[0]['msg']}"

        # respond to origin station with directed message
        self.js8call.send_directed_message(msg.origin, message)

    def _add_post(self, msg):
        self._dummy = None
        # do not respond in the following cases:
        if msg.text in (None, ''):  # message text is empty
            return
        cut = msg.text.split(' ', maxsplit=3)  # [Command, Callsign or Time, Time or Garbage]
        try:
            if len(cut[1]) == 10:  # Timecode detected
                message = msg.text.split(f'{cut[1]} ')[1]
                db_functions.add_blog(abc_to_num(cut[1]), msg.origin, message)
            else:  # Callsign
                message = msg.text.split(f'{cut[2]} ')[1]
                db_functions.add_blog(abc_to_num(cut[2]), cut[1], message)
        except KeyError:
            print(f'  * JS8 - ERROR Bad Timecode - {msg.text}')
            return

    #  Broadcast out a new post.
    def broadcast_post(self, post: dict, dest=""):
        if dest == "":
            dest = self.settings['js8group']
        message = f"{Command.POST} {num_to_abc(post['time'])} {post['msg']}"
        self.js8call.send_directed_message(dest, message)

    def broadcast_target_post(self, post: dict, dest=""):
        if dest == "":
            dest = self.settings['js8group']
        message = f"{Command.POST} {post['callsign']} {num_to_abc(post['time'])} {post['msg']}"
        self.js8call.send_directed_message(dest, message)

    def get_posts(self, dest=""):
        if dest == "":
            dest = self.settings['js8group']
        message = f"{Command.GET_POSTS}"
        self.js8call.send_directed_message(dest, message)

    def get_posts_callsign(self, callsign: str, dest=""):
        if dest == "":
            dest = self.settings['js8group']
        message = f"{Command.GET_POSTS}"
        if len(callsign) > 0:
            message += f" {callsign.upper()}"
        self.js8call.send_directed_message(dest, message)


if __name__ == '__main__':
    modem: JS8modem
    try:
        modem = JS8modem(host='127.0.0.1', port=2442)
        modem.start()

        # Loop Forever
        while modem.js8call.online:
            pass

    except RuntimeError:
        print("  * JS8 - ERRR Application not installed or Connection issue")
        exit()
