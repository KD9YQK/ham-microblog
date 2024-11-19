import sqlite3
import time

hour = 60 * 60
day = hour * 24
expire = day * 30


def get_time():
    return int(time.time())


def build_db():
    con, cur = get_db()
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
                        time INT NOT NULL,
                        callsign VARCHAR(25) NOT NULL,
                        message VARCHAR(255) NOT NULL
                    ); """

    cur.execute(table)
    # Creating table for monitoring stations
    table = """ CREATE TABLE monitoring ( callsign VARCHAR(25) NOT NULL ); """
    cur.execute(table)
    # Creating table for setings
    table = """ CREATE TABLE settings (
                    id INT,
                    callsign VARCHAR(25), 
                    js8modem BOOL, 
                    aprsmodem BOOL, 
                    tcpmodem BOOL, 
                    timezone VARCHAR(25),
                    tcplast INT 
                ); """
    cur.execute(table)
    cur.execute(''' INSERT INTO settings ( id, callsign, js8modem, aprsmodem, tcpmodem, timezone, tcplast )
                        VALUES (?, ?, ?, ?, ?, ?, ?);''', (0, 'MYCALL', False, False, False, 'gmt', 0,))
    con.commit()
    con.close()


def get_outgoing_posts():
    con, cur = get_db()
    rows = cur.execute('''SELECT time, callsign, message FROM outgoing ORDER BY time ASC''')
    retval = []
    for row in rows:
        post = {
            "time": row[0],
            "callsign": row[1],
            "msg": row[2],
        }
        retval.append(post)
    cur.execute('DELETE FROM outgoing')
    con.commit()
    con.close()
    return retval


def add_outgoing_post(mtime: int, callsign: str, msg: str):
    purge_expired_blog()
    con, cur = get_db()
    cur.execute('''INSERT INTO outgoing (time, callsign, message) VALUES (?, ?, ?)''', (mtime, callsign, msg,))
    con.commit()
    con.close()


def get_all_time(timecode: int):
    purge_expired_blog()
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


def get_callsign_blog(callsign: str, num: int = 1):
    purge_expired_blog()
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
    purge_expired_blog()
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
    purge_expired_blog()
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
    purge_expired_blog()
    con, cur = get_db()
    rows = cur.execute('''SELECT time, callsign FROM blog WHERE callsign = ? AND time = ?''',
                       (callsign, mtime,))
    count = 0
    for _r in rows:
        count += 1
    print(count)
    if count == 0:
        cur.execute('''INSERT INTO blog (time, callsign, message) VALUES (?, ?, ?)''',
                    (mtime, callsign, msg,))
        con.commit()
    con.close()


def bulk_add_blog(posts: list):
    purge_expired_blog()
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


def get_db() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    cur = sqlite3.connect("js8mb.db")
    con = cur.cursor()
    return cur, con


def get_own_callsign():
    con, cur = get_db()
    row = cur.execute('''SELECT callsign FROM settings WHERE id = ?''', (0,))
    call = ""
    for _i in row:
        call = _i[0]

    con.close()
    return call


def set_settings(callsign: str, js8modem=False, aprsmodem=False, tcpmodem=False, timezone='gmt'):
    con, cur = get_db()
    cur.execute('''UPDATE settings SET callsign = ?, js8modem = ?, aprsmodem = ?, tcpmodem = ?, timezone = ? 
                    WHERE id = ?;''', (callsign, js8modem, aprsmodem, tcpmodem, timezone, 0,))
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
    con, cur = get_db()
    row = cur.execute('''SELECT callsign, js8modem, aprsmodem, tcpmodem, timezone, tcplast 
                            FROM settings WHERE (id = ?)''', (0,))
    s = {}
    for r in row:
        s['callsign'] = r[0]
        s['js8modem'] = r[1]
        s['aprsmodem'] = r[2]
        s['tcpmodem'] = r[3]
        s['timezone'] = r[4]
        s['tcplast'] = r[5]
    con.close()
    return s


if __name__ == "__main__":
    build_db()
    t = get_time()
    add_blog(t, "KD9YQK",
             "Today a man knocked on my door and asked for a small donation towards the local swimming pool. I gave him a glass of water.")
    add_blog(t - 100, "KD9YQK", "Ham and Eggs: A day's work for a chicken, a lifetime commitment for a pig.")
    add_blog(t - 150, "KD9UEG",
             "What do you call a dog with no legs? Doesn't matter what you call him, he's not coming.")
    add_blog(t - 1150, "KD9UEG", "Always identify who to blame in an emergency.")
    add_blog(t - 140, "KM6LYW",
             "My wife just found out I replaced our bed with a trampoline; she hit the roof.")
    add_blog(t - 340, "KM6LYW",
             "Smoking will kill you... Bacon will kill you... But, smoking bacon will cure it.")
    add_blog(t - 1250, "KD9YQK", "A liberal is just a conservative that hasn't been mugged yet.")
    l = []
    for i in range(0, 5000):
        l.append({"time": t - 200 - i, "callsign": "KD9YQK", "msg": f"Test Message #{str(i + 1)}"})
    bulk_add_blog(l)
    print(get_own_callsign())
