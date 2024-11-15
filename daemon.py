import pyjs8call
import db_functions
import time


class timeValues:
    hour = 60  # Seconds
    day = hour * 24
    week = day * 7
    fortnight = day * 14
    month = week * 4
    year = month * 12
    decade = year * 10


numVal = {'1':'A','2':'B','3':'C','4':'D','5':'E','6':'F','7':'G','8':'H','9':'I','0':'J'}
abcVal = {'A':'1','B':'2','C':'3','D':'4','E':'5','F':'6','G':'7','H':'8','I':'9','J':'0'}

def num_to_abc(num:int):
    tmp = str(num)
    retval = ''
    for l in tmp:
        retval += numVal[l]
    return retval

def abc_to_num(abc:str):
    tmp = ''
    for l in abc:
        tmp += abcVal[l]
    return int(tmp)

def shrink_timecode(timecode:int):
    tmp = num_to_abc(timecode)
    return tmp[-5:]

def expand_timecode(timecode:str):
    t = int(time.time())
    tmp = str(t)[:5]
    for l in timecode:
        tmp += abcVal[l]
    return int(tmp)

class JS8modem:
    js8call: pyjs8call.Client

    def __init__(self, host='127.0.0.1', port=2442):
        self.js8call = pyjs8call.Client(host=host, port=port)
        self.js8call.callback.register_command(' NEWS?', self.cb_news_cmd)
        self.js8call.callback.inbox = self.cb_test
        print("* Js8Call Modem Initialized.")
        print(f"* Host: {host} * Port: {port}")

    def start(self):
        self.js8call.start()
        self.js8call.inbox.enable()

    # Custom Callbacks
    def cb_test(self, msgs):
        for msg in msgs:
            print(f"{msg.origin} - {msg.text}")

    def cb_news_cmd(self, msg):
        # do not respond in the following cases:
        if (
                self.js8call.settings.autoreply_confirmation_enabled() or
                not self.js8call.msg_is_to_me(msg) or  # not directed to local station or configured group
                msg.text in (None, '')  # message text is empty
        ):
            return
        # read the latest news from file
        blog = db_functions.get_my_blog()
        message = f" NEWS {len(blog)}"
        for post in blog:
            message += f" {post['time']}"


        # respond to origin station with directed message
        self.js8call.send_directed_message(msg.origin, message)


if __name__ == '__main__':
    try:
        modem = JS8modem(host="192.168.1.103", port=2442)
    except RuntimeError:
        print("ERROR - JS8Call application not installed")
        #exit()
    modem.start()

    print("sending")
    modem.js8call.send_message(f"TEST {numVal[str(0)]} {shrink_timecode(1111111111)} {shrink_timecode(1111111111)} {shrink_timecode(1111111111)}")
    
    # Main Loop
    while True:
        pass

