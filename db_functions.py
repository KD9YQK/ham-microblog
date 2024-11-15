import sqlite3
import time

day = 60 * 24  # Time in seconds of complete day


def get_time():
    return int(time.time())


def build_db():
    con, cur = get_db()
    # Drop the GEEK table if already exists.
    cur.execute("DROP TABLE IF EXISTS my_blog")
    cur.execute("DROP TABLE IF EXISTS all_blog")

    # Creating table my_blog
    table = """ CREATE TABLE my_blog (
                time INT NOT NULL,
                message VARCHAR(255) NOT NULL,
                expire INT NOT NULL
            ); """

    cur.execute(table)
    # Creating table all_blog
    table = """ CREATE TABLE all_blog (
                    time INT NOT NULL,
                    callsign VARCHAR(25) NOT NULL,
                    message VARCHAR(255) NOT NULL,
                    expire INT NOT NULL
                ); """

    cur.execute(table)
    con.close()


def get_my_blog(num: int = 3):
    purge_expired_my_blog()
    con, cur = get_db()
    if num == 0:
        rows = cur.execute('''SELECT time, message, expire FROM my_blog ORDER BY time DESC''')
    else:
        rows = cur.execute('''SELECT time, message, expire FROM my_blog ORDER BY time DESC LIMIT ?''', (num,))
    blog = []
    for row in rows:
        post = {
            'time': row[0],
            'msg': row[1],
            'expire': row[2]
        }
        blog.append(post)
    con.close()
    return blog


def get_my_blog(num: int = 3):
    purge_expired_my_blog()
    con, cur = get_db()
    if num == 0:
        rows = cur.execute('''SELECT time, message, expire FROM my_blog ORDER BY time DESC''')
    else:
        rows = cur.execute('''SELECT time, message, expire FROM my_blog ORDER BY time DESC LIMIT ?''', (num,))
    blog = []
    for row in rows:
        post = {
            'time': row[0],
            'msg': row[1],
            'expire': row[2]
        }
        blog.append(post)
    con.close()
    return blog


def get_callsign_all_blog(callsign: str, num: int = 3):
    purge_expired_all_blog()
    con, cur = get_db()
    if num == 0:
        rows = cur.execute('''SELECT time, message, expire FROM all_blog WHERE callsign = ? ORDER BY time DESC''',
                           (callsign,))
    else:
        rows = cur.execute('''SELECT time, message, expire FROM all_blog WHERE callsign = ? ORDER BY time DESC LIMIT ?''',
                           (callsign, num,))
    blog = []
    for row in rows:
        post = {
            'time': row[0],
            'callsign': callsign,
            'msg': row[1],
            'expire': row[2]
        }
        blog.append(post)
    con.close()
    return blog


def add_all_blog(mtime: int, call: str, msg: str, expire: int):
    purge_expired_all_blog()
    con, cur = get_db()
    cur.execute('''INSERT INTO all_blog (time, callsign, message, expire) VALUES (?, ?, ?, ?)''',
                (mtime, call, msg, expire,))
    con.commit()
    con.close()


def add_my_blog(mtime: int, msg: str, expire: int):
    purge_expired_my_blog()
    con, cur = get_db()
    cur.execute('''INSERT INTO my_blog (time, message, expire) VALUES (?, ?, ?)''',
                (mtime, msg, expire,))
    con.commit()
    con.close()


def purge_expired_all_blog():
    now = get_time()
    con, cur = get_db()
    rows = cur.execute('''SELECT time, callsign, expire FROM all_blog''')
    for row in rows:
        expire = day * row[2]
        if expire + row[0] < now:
            cur.execute("DELETE FROM all_blog WHERE (callsign = ? AND time = ?)", (row[1], row[0]))
    con.commit()
    con.close()


def purge_expired_my_blog():
    now = get_time()
    con, cur = get_db()
    rows = cur.execute('''SELECT time, expire FROM my_blog''')
    for row in rows:
        expire = day * row[1]
        if row[0] + expire < now:
            cur.execute('''DELETE FROM my_blog WHERE 'time" = ?''', (row[0],))
    con.commit()
    con.close()


def get_db() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    cur = sqlite3.connect("js8mb.db")
    con = cur.cursor()
    return cur, con


if __name__ == "__main__":
    build_db()
    add_my_blog(get_time(),"My Message", 1)
    blog = get_my_blog()
    print(str(blog))

