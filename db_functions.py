import sqlite3
import time

hour = 60 * 60
day = hour * 24
expire = day * 30


def get_time():
    return int(time.time())


def build_db():
    con, cur = get_db(err=False)
    cur.execute("DROP TABLE IF EXISTS blog")
    cur.execute("DROP TABLE IF EXISTS monitoring")
    cur.execute("DROP TABLE IF EXISTS settings")
    cur.execute("DROP TABLE IF EXISTS outgoing")

    # Creating table for blog
    table = """ CREATE TABLE blog (
                    time INT NOT NULL,
                    callsign VARCHAR(25) NOT NULL,
                    message VARCHAR(255) NOT NULL
                ); """

    cur.execute(table)
    # Creating table for outgoing messages
    table = """ CREATE TABLE outgoing (
                        time INT,
                        command VARCHAR(25),
                        callsign VARCHAR(25),
                        message VARCHAR(255)
                    ); """

    cur.execute(table)
    # Creating table for monitoring stations
    table = """ CREATE TABLE monitoring ( callsign VARCHAR(25) NOT NULL ); """
    cur.execute(table)
    # Creating table for setings
    table = """ CREATE TABLE settings (
                    id INT,
                    callsign VARCHAR(25), 
                    js8modem BOOL, js8host VARCHAR(25), js8port INT, js8group VARCHAR(25), 
                    aprsmodem BOOL, aprshost VARCHAR(25), aprsport INT, aprsssid INT, lat VARCHAR(25), lon VARCHAR(25), 
                    tcpmodem BOOL, 
                    timezone VARCHAR(25),
                    tcplast INT 
                ); """
    cur.execute(table)
    cur.execute(''' INSERT INTO settings ( id, callsign, js8modem, aprsmodem, tcpmodem, timezone, tcplast, 
                        js8host, js8port, js8group, aprshost, aprsport, aprsssid, lat, lon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
                (0, 'MYCALL', False, False, False, 'gmt', 0, '127.0.0.1', 2442, '@BLOG', '127.0.0.1', 8001, 9,
                 "4145.  N", "08818.  W",))
    con.commit()
    con.close()


def get_outgoing_posts():
    con, cur = get_db()
    rows = cur.execute('''SELECT time, callsign, message, command FROM outgoing ORDER BY time ASC''')
    retval = []
    for row in rows:
        post = {
            "time": row[0],
            "callsign": row[1],
            "msg": row[2],
            "command": row[3]
        }
        retval.append(post)
    cur.execute('DELETE FROM outgoing')
    con.commit()
    con.close()
    return retval


def add_outgoing_post(command: str, mtime: int, callsign: str, msg: str):
    con, cur = get_db()
    cur.execute('''INSERT INTO outgoing (time, callsign, message, command) VALUES (?, ?, ?, ?)''',
                (mtime, callsign, msg, command, ))
    con.commit()
    con.close()


def get_all_time(timecode: int):
    mon = get_monitoring()
    con, cur = get_db()
    rows = cur.execute('''SELECT time, message, callsign FROM blog WHERE time > ? ORDER BY time DESC''', (timecode,))
    retval = []
    for row in rows:
        post = {
            'time': row[0],
            'gmt': time.strftime('%H:%M  (%m-%d-%y)', time.gmtime(row[0])),
            'local': time.strftime('%H:%M  (%m-%d-%y)', time.localtime(row[0])),
            'callsign': row[2],
            'msg': row[1],
            'mon': False
        }
        if row[2] in mon:
            post['mon'] = True
        retval.append(post)
    con.close()
    return retval


def get_bloggers():
    retval = []
    blogs = get_all_time(0)
    for p in blogs:
        if p['callsign'] not in retval:
            retval.append(p['callsign'])
    return retval


def get_callsign_blog(callsign: str, num: int = 1):
    mon = get_monitoring()
    con, cur = get_db()
    if num == 0:
        rows = cur.execute('''SELECT time, message FROM blog WHERE callsign = ? ORDER BY time DESC''',
                           (callsign,))
    else:
        rows = cur.execute('''SELECT time, message FROM blog WHERE callsign = ? ORDER BY time DESC LIMIT ?''',
                           (callsign, num,))
    retval = []
    for row in rows:
        post = {
            "time": row[0],
            "gmt": time.strftime('%H:%M  (%m-%d-%y)', time.gmtime(row[0])),
            "local": time.strftime('%H:%M  (%m-%d-%y)', time.localtime(row[0])),
            "callsign": callsign,
            "msg": row[1],
            "mon": False
        }
        if callsign in mon:
            post["mon"] = True
        retval.append(post)
    con.close()
    return retval


def get_all_blog():
    mon = get_monitoring()
    con, cur = get_db()
    rows = cur.execute('''SELECT time, message, callsign FROM blog ORDER BY time DESC''')
    retval = []
    for row in rows:
        post = {
            'time': row[0],
            'gmt': time.strftime('%H:%M  (%m-%d-%y)', time.gmtime(row[0])),
            'local': time.strftime('%H:%M  (%m-%d-%y)', time.localtime(row[0])),
            'callsign': row[2],
            'msg': row[1],
            'mon': False
        }
        if row[2] in mon:
            post['mon'] = True
        retval.append(post)
    con.close()
    return retval


def get_monitoring_blog():
    mon = get_monitoring()
    con, cur = get_db()

    sql = '''
        SELECT time, message, callsign FROM blog 
        WHERE callsign in ({seq})
        ORDER BY time DESC
    '''.format(seq=','.join(['?'] * len(mon)))

    rows = cur.execute(sql, mon)
    # rows = cur.execute('''SELECT time, message, callsign FROM blog ORDER BY time DESC''')
    retval = []
    for row in rows:
        post = {
            'time': row[0],
            'gmt': time.strftime('%H:%M  (%m-%d-%y)', time.gmtime(row[0])),
            'local': time.strftime('%H:%M  (%m-%d-%y)', time.localtime(row[0])),
            'callsign': row[2],
            'msg': row[1],
            'mon': False
        }
        if row[2] in mon:
            post['mon'] = True
        retval.append(post)
    con.close()
    return retval


def add_blog(mtime: int, callsign: str, msg: str):
    con, cur = get_db()
    rows = cur.execute('''SELECT time, callsign FROM blog WHERE callsign = ? AND time = ?''',
                       (callsign, mtime,))
    count = 0
    for _r in rows:
        count += 1
    if count == 0:
        cur.execute('''INSERT INTO blog (time, callsign, message) VALUES (?, ?, ?)''',
                    (mtime, callsign, msg,))
        con.commit()
    con.close()


def bulk_add_blog(posts: list):
    con, cur = get_db()
    for p in posts:
        mtime = p['time']
        callsign = p['callsign']
        msg = p['msg']
        rows = cur.execute('''SELECT time, callsign FROM blog WHERE callsign = ? AND time = ?''',
                           (callsign, mtime,))
        count = 0
        for _r in rows:
            count += 1
        if count == 0:
            cur.execute('''INSERT INTO blog (time, callsign, message) VALUES (?, ?, ?)''',
                        (mtime, callsign, msg,))
    con.commit()
    con.close()


def add_monitoring(callsign: str):
    con, cur = get_db()
    rows = cur.execute('''SELECT callsign FROM monitoring WHERE callsign = ?''',
                       (callsign,))
    count = 0
    for _r in rows:
        count += 1
    if count == 0:
        cur.execute('''INSERT INTO monitoring (callsign) VALUES (?)''', (callsign,))
        con.commit()
    con.close()


def remove_monitoring(call: str):
    con, cur = get_db()
    cur.execute("DELETE FROM monitoring WHERE (callsign = ?)", (call,))
    con.commit()
    con.close()


def get_monitoring():
    con, cur = get_db()
    mon = []
    rows = cur.execute('''SELECT callsign FROM monitoring''')
    for row in rows:
        mon.append(row[0])
    con.close()
    return mon


def purge_expired_blog():
    now = get_time()
    con, cur = get_db()
    rows = cur.execute('''SELECT time, callsign FROM blog''')
    for row in rows:
        if expire + row[0] < now:
            cur.execute("DELETE FROM blog WHERE (callsign = ? AND time = ?)", (row[1], row[0],))
    con.commit()
    con.close()


def get_db(err = True) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    now = get_time()
    con = sqlite3.connect("microblog.db")
    cur = con.cursor()

    try:
        rows = cur.execute('''SELECT time, callsign FROM blog''')
        for row in rows:
            if expire + row[0] < now:
                cur.execute("DELETE FROM blog WHERE (callsign = ? AND time = ?)", (row[1], row[0],))
        con.commit()
    except sqlite3.OperationalError:
        if err:
            print("  * Error - Database doesn't exist or bad data. Run setup.py to fix")
            exit()
    return con, cur


def get_own_callsign():
    con, cur = get_db()
    row = cur.execute('''SELECT callsign FROM settings WHERE id = ?''', (0,))
    call = ""
    for _i in row:
        call = _i[0]

    con.close()
    return call


def set_settings(callsign: str, js8modem=False, js8host='127.0.0.1', js8port=2442, js8group="@BLOG",
                 aprsmodem=False, aprshost="127.0.0.1", aprsport=8001, aprs_ssid=9, tcpmodem=False, timezone='gmt',
                 lat="", lon=""):
    con, cur = get_db()
    cur.execute('''UPDATE settings 
                    SET callsign = ?, js8modem = ?, aprsmodem = ?, tcpmodem = ?, timezone = ?,
                        js8host = ?, js8port = ?, js8group = ?, 
                        aprshost = ?, aprsport = ?, aprsssid = ?, lat = ?, lon = ? 
                    WHERE id = ?;''',
                (callsign, js8modem, aprsmodem, tcpmodem, timezone, js8host, js8port, js8group, aprshost,
                 aprsport, aprs_ssid, lat, lon, 0,))
    con.commit()
    con.close()


def get_tcp_last():
    con, cur = get_db()
    row = cur.execute('''SELECT tcplast FROM settings WHERE id = ?''', (0,))
    _t = ""
    for r in row:
        _t = r[0]

    con.close()
    return _t


def set_tcp_last():
    con, cur = get_db()
    cur.execute('''UPDATE settings SET tcplast = ? 
                    WHERE id = ?;''', (int(time.time()), 0,))
    con.commit()
    con.close()


def get_settings():
    con, cur = get_db()  # js8host, js8port, js8group, aprshost, aprsport, aprsssid
    row = cur.execute('''SELECT callsign, js8modem, aprsmodem, tcpmodem, timezone, tcplast,
                            js8host, js8port, js8group, aprshost, aprsport, aprsssid, lat, lon
                        FROM settings WHERE (id = ?)''', (0,))
    s = {}
    for r in row:
        s['callsign'] = r[0]
        s['js8modem'] = r[1]
        s['aprsmodem'] = r[2]
        s['tcpmodem'] = r[3]
        s['timezone'] = r[4]
        s['tcplast'] = r[5]

        s['js8host'] = r[6]
        s['js8port'] = r[7]
        s['js8group'] = r[8]
        s['aprshost'] = r[9]
        s['aprsport'] = r[10]
        s['aprsssid'] = r[11]
        s['lat'] = r[12]
        s['lon'] = r[13]
    con.close()
    return s


if __name__ == "__main__":
    print(get_bloggers())
