import pyjs8call
import db_functions


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


class modClient(pyjs8call.Client):
    def stop(self, terminate_js8call=True):
        self.online = False
        self.exit_tasks()
        self.js8call.app.terminate_js8call = False
        self.js8call.stop()


class JS8modem:
    js8call: pyjs8call.Client
    is_running = True

    def __init__(self, host='127.0.0.1', port=2442):
        self.js8call = modClient(host=host, port=port)
        self.js8call.callback.register_incoming(self._incoming_callback)
        self.js8call.callback.register_spots(self._new_spots_callback)
        print("* Js8Call Modem Initialized.")
        print(f"* Host: {host} * Port: {port}")

    def start(self):
        self.js8call.start()
        self.js8call.inbox.enable()

    ###########################################
    # Callbacks
    ###########################################
    def _incoming_callback(self, msg):  # Test callback when any msg is received
        print(f" * From: {msg.origin} To: {msg.destination} Message: {msg.text}")
        c = msg.text.split(' ')[0]
        if msg.destination in ['@BLOG', self.js8call.settings.get_station_callsign()]:
            if c == Command.GET_POSTS:
                self._get_posts(msg)
        if c == Command.POST:
            self._add_post(msg)

    def _new_spots_callback(self, spots):  # Callback when a new spot is received.
        _t = self.is_running
        for spot in spots:
            if spot.grid in (None, ''):
                _grid = ' '
            else:
                _grid = ' (' + spot.grid + ') '
        h = self.js8call.hearing()
        allstn = {}
        for stn in h.keys():
            tmp = {'hearing': h[stn], 'heard': self.js8call.station_heard_by(stn)}

            allstn[stn] = tmp
        print(allstn)
            # print('\t--- Spot: {}{}@ {} Hz\t{}L'.format(spot.origin, _grid, spot.offset,
            #                                            time.strftime('%x %X', time.localtime(spot.timestamp))))

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
        prefix = 'POST '
        if len(cut) == 2:
            prefix += f'{blog[0]["callsign"]} '
        message = f"{prefix}{num_to_abc(blog[0]['time'])} {blog[0]['msg']}"

        # respond to origin station with directed message
        self.js8call.send_directed_message(msg.origin, message)

    def _add_post(self, msg):
        _t = self.is_running
        # do not respond in the following cases:
        if msg.text in (None, ''):  # message text is empty
            return
        cut = msg.text.split(' ', maxsplit=3)  # [Command, Callsign or Time, Time or Garbage]
        if len(cut[1]) == 10:  # Timecode detected
            message = msg.text.split(f'{cut[1]} ')[1]
            db_functions.add_blog(abc_to_num(cut[1]), msg.origin, message)
        else:  # Callsign
            message = msg.text.split(f'{cut[2]} ')[1]
            db_functions.add_blog(abc_to_num(cut[2]), cut[1], message)

    #  Broadcast out a new post.
    def broadcast_post(self, post: dict, dest='@BLOG'):
        message = f"{Command.POST} {num_to_abc(post['time'])} {post['msg']}"
        self.js8call.send_directed_message(dest, message)

    def get_posts(self, dest='@BLOG'):
        message = f"{Command.GET_POSTS}"
        self.js8call.send_directed_message(dest, message)

    def get_posts_callsign(self, callsign: str, dest='@BLOG'):
        message = f"{Command.GET_POSTS} {callsign.upper()}"
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
        print("ERROR - JS8Call application not installed or connection issue")
        exit()
