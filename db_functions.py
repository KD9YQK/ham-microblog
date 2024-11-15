import sqlite3
import time

day = 60 * 24  # Time in seconds of complete day
expire = day * 3

def get_time():
    return int(time.time())


def build_db():
    con, cur = get_db()
    cur.execute("DROP TABLE IF EXISTS blog")

    cur.execute(table)
    # Creating table blog
    table = """ CREATE TABLE blog (
                    time INT NOT NULL,
                    callsign VARCHAR(25) NOT NULL,
                    message VARCHAR(255) NOT NULL
                ); """

    cur.execute(table)
    con.close()



def get_callsign_blog(callsign: str, num: int = 3):
    purge_expired__blog()
    con, cur = get_db()
    if num == 0:
        rows = cur.execute('''SELECT time, message FROM blog WHERE callsign = ? ORDER BY time DESC''',
                           (callsign,))
    else:
        rows = cur.execute('''SELECT time, message FROM blog WHERE callsign = ? ORDER BY time DESC LIMIT ?''',
                           (callsign, num,))
    blog = []
    for row in rows:
        post = {
            'time': row[0],
            'callsign': callsign,
            'msg': row[1]
        }
        blog.append(post)
    con.close()
    return blog


def add_blog(mtime: int, call: str, msg: str):
    purge_expired_blog()
    con, cur = get_db()
    cur.execute('''INSERT INTO blog (time, callsign, message) VALUES (?, ?, ?, ?)''',
                (mtime, call, msg,))
    con.commit()
    con.close()


def purge_expired_blog():
    now = get_time()
    con, cur = get_db()
    rows = cur.execute('''SELECT time, callsign FROM blog''')
    for row in rows:
        if expire + row[0] < now:
            cur.execute("DELETE FROM blog WHERE (callsign = ? AND time = ?)", (row[1], row[0]))
    con.commit()
    con.close()


def get_db() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    cur = sqlite3.connect("js8mb.db")
    con = cur.cursor()
    return cur, con


if __name__ == "__main__":
    build_db()
    add_blog(get_time(),"KD9YQK","My Message")
    blog = get_callsign_blog("KD9YQK", 0)
    print(str(blog))

