import aprsModem
import asyncio
from ax253 import Frame

radio = aprsModem.Radio


def parse_message(frame: Frame):
    _frm = str(frame)
    sender = _frm.split('>')[0]
    _t = _frm.split('>', 1)[1].split(':', 1)[0].split(',')
    destination = _t[0]
    _t.pop(0)
    path = _t
    message = _frm.split('>', 1)[1].split(':', 1)[1]
    retval = {
        'sender': sender,
        'destination': destination,
        'path': path,
        'info': message
    }
    return retval


def msg_respond(frame):
    frm = parse_message(frame)
    if ':' == frm['info'][0]:
        recip = frm['info'].split(':')[1]
        if recip == radio.MYCALL:
            if '{' in frm['info']:
                if recip == radio.MYCALL:
                    count = frm['info'].split('{')[1]
                    msg = {
                        'src': radio.MYCALL,
                        'dest': "ADZ666",  # ADZ666
                        'info': f':{pad_callsign(frm["sender"])}:ack{count}'
                    }
                    radio.tx_buffer.append(msg)
        else:
            pass
            # radio.kiss_protocol.write(Frame.from_str(frame))


def rx_message(frame: Frame):
    print(f"\033[34m{frame}\033[0m")
    msg_respond(frame)


def ig_message(frame: Frame):
    print(f"\033[33m{frame}\033[0m")
    msg_respond(frame)


async def ainput(prompt: str) -> str:
    return await asyncio.to_thread(input, f'{prompt} ')


async def main_loop():
    _rec, _tx, _ig, _pos = await radio.setup(rx_callback=rx_message, igrx_callback=ig_message)

    c = False
    while True:
        await asyncio.sleep(10)
        cmd_input = 'msg;wxbot;tonight 60506'
        # cmd_input = await ainput("Command>>")
        cmd = cmd_input.split(';')
        if not c:
            try:
                if cmd[0] == 'msg':
                    msg = {
                        'src': radio.MYCALL,
                        'dest': "ADZ666",  # ADZ666
                        'info': f':{pad_callsign(cmd[1].upper())}:{cmd[2]}' + ' {1'
                    }
                    radio.tx_buffer.append(msg)
                    c = True
            except IndexError:
                print('IndexError - You are missing a parameter')
                if cmd[0] == 'msg':
                    print('Usage: msg CALLSIGN message')


def pad_callsign(callsign: str):
    pad = 9 - len(callsign)
    retval = callsign
    for n in range(0, pad):
        retval += ' '
    print(f'*{retval}*')
    return retval


if __name__ == "__main__":
    # Init the radio variable.
    radio = aprsModem.Radio(callsign="KD9YQK-10", host="digipi", igate_pass="20660")
    # Set some custom igate filter params
    radio.ig.filter_params = "b/WXBOT"
    radio.ig.tx_enabled = True
    radio.ig.enabled = True
    # rebuild the igate filter
    radio.ig.set_igate_filter(radio.MYCALL)
    asyncio.run(main_loop())
    print('end')
