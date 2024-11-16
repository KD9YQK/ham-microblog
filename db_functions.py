import sqlite3
import time

hour = 60 * 60
day = hour * 24
expire = day * 3


def get_time():
    return int(time.time())


def build_db():
    con, cur = get_db()
    cur.execute("DROP TABLE IF EXISTS blog")
    cur.execute("DROP TABLE IF EXISTS monitoring")
    cur.execute("DROP TABLE IF EXISTS settings")

    # Creating table for blog
    table = """ CREATE TABLE blog (
                    time INT NOT NULL,
                    callsign VARCHAR(25) NOT NULL,
                    message VARCHAR(255) NOT NULL
                ); """

    cur.execute(table)
    # Creating table for monitoring stations
    table = """ CREATE TABLE monitoring ( callsign VARCHAR(25) NOT NULL ); """
    cur.execute(table)
    # Creating table for setings
    table = """ CREATE TABLE settings ( callsign VARCHAR(25) NOT NULL ); """
    cur.execute(table)
    con.close()


def get_callsign_blog(callsign: str, num: int = 3):
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
            'time': row[0],
            'gmt': time.strftime('%H:%M  (%m-%d-%y)', time.gmtime(row[0])),
            'local': time.strftime('%H:%M  (%m-%d-%y)', time.localtime(row[0])),
            'callsign': callsign,
            'msg': row[1],
            'mon': False
        }
        if callsign in mon:
            post['mon'] = True
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
    row = cur.execute('''SELECT callsign FROM settings''')
    call = ""
    for i in row:
        call = i[0]

    con.close()
    return str(call)


def set_own_callsign(call: str):
    con, cur = get_db()
    cur.execute('''INSERT INTO settings (callsign) VALUES (?)''', (call,))
    con.commit()
    con.close()


if __name__ == "__main__":
    time.strftime('%m-%d-%y %H:%M', time.gmtime(2722454321))
    build_db()
    add_blog(get_time(), "KD9YQK",
             "Today a man knocked on my door and asked for a small donation towards the local swimming pool. I gave him a glass of water.")
    add_blog(get_time() - 100, "KD9YQK", "Ham and Eggs: A day's work for a chicken, a lifetime commitment for a pig.")
    add_blog(get_time() - 150, "KD9UEG",
             "What do you call a dog with no legs? Doesn't matter what you call him, he's not coming.")
    add_blog(get_time() - 1150, "KD9UEG", "Always identify who to blame in an emergency.")
    add_blog(get_time() - 140, "KM6LYW",
             "My wife just found out I replaced our bed with a trampoline; she hit the roof.")
    add_blog(get_time() - 340, "KM6LYW",
             "Smoking will kill you... Bacon will kill you... But, smoking bacon will cure it.")
    add_blog(get_time() - 1250, "KD9YQK", "A liberal is just a conservative that hasn't been mugged yet.")
    add_blog(get_time() - 200, "KD9YQK",
             "My wife likes it when I blow air on her when she's hot, but honestly... I'm not a fan.")
    set_own_callsign('KD9YQK')
